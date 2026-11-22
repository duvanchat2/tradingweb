from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from app.models.schema import AuditLog, KYCDocument, User
from app.routers.auth import DB, current_user

router = APIRouter(prefix='/api/kyc', tags=['kyc'])
Client = Annotated[User, Depends(current_user)]
REQUIRED = ('id_front', 'id_back', 'proof_address', 'selfie')
ALLOWED = {'image/jpeg', 'image/png', 'image/webp'}
MAX_BYTES = 5 * 1024 * 1024
def valid_signature(mime: str, content: bytes) -> bool:
    return ((mime == 'image/jpeg' and content.startswith(b'\xff\xd8\xff')) or
            (mime == 'image/png' and content.startswith(b'\x89PNG\r\n\x1a\n')) or
            (mime == 'image/webp' and len(content) >= 12 and content[:4] == b'RIFF' and content[8:12] == b'WEBP'))

@router.get('/status')
def status(user: Client, db: DB):
    docs = {row.doc_type: row for row in db.scalars(select(KYCDocument).where(
        KYCDocument.user_id == user.id, KYCDocument.doc_type.in_(REQUIRED))).all()}
    return {'status': user.kyc_status, 'documents': [
        {'doc_type': kind, 'status': docs[kind].status if kind in docs else 'missing',
         'review_note': docs[kind].review_note if kind in docs else None}
        for kind in REQUIRED
    ]}

@router.post('/documents/{doc_type}', status_code=201)
async def upload_document(doc_type: str, user: Client, db: DB, file: UploadFile = File(...)):
    if doc_type not in REQUIRED: raise HTTPException(422, 'Unsupported document type')
    if file.content_type not in ALLOWED: raise HTTPException(422, 'Only JPEG, PNG or WebP images are accepted')
    content = await file.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES: raise HTTPException(422, 'Image must be between 1 byte and 5 MB')
    if not valid_signature(file.content_type, content): raise HTTPException(422, 'File content does not match the declared image type')
    doc = db.scalar(select(KYCDocument).where(KYCDocument.user_id == user.id, KYCDocument.doc_type == doc_type))
    if doc is None:
        doc = KYCDocument(user_id=user.id, doc_type=doc_type, file_path='database://kyc', status='pending')
        db.add(doc)
    doc.original_name = (file.filename or 'document')[:255]
    doc.mime_type = file.content_type
    doc.file_data = content
    doc.status = 'pending'; doc.review_note = None; doc.reviewer_id = None; doc.reviewed_at = None
    user.kyc_status = 'none'
    db.add(AuditLog(actor_id=user.id, action='kyc.upload', entity='kyc_documents', after_json={'doc_type':doc_type,'size':len(content)}))
    db.commit(); db.refresh(doc)
    return {'id':doc.id, 'doc_type':doc.doc_type, 'status':doc.status}

@router.post('/submit')
def submit_verification(user: Client, db: DB):
    if user.kyc_status in ('pending','verified'):
        raise HTTPException(409, 'Verification is already submitted')
    docs = db.scalars(select(KYCDocument).where(KYCDocument.user_id == user.id)).all()
    by_type = {doc.doc_type:doc for doc in docs}
    if not all(kind in by_type and by_type[kind].status in ('pending','approved') for kind in REQUIRED):
        raise HTTPException(422, 'Upload all four documents before submitting')
    user.kyc_status = 'pending'
    db.add(AuditLog(actor_id=user.id, action='kyc.submit', entity='users', entity_id=user.id))
    db.commit()
    return {'status':'pending'}
