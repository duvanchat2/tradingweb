from datetime import date
from app.main import app
from app.models.schema import Office,User
from app.routers.auth import current_registration_code,current_user

def test_office_code_rotates_daily_and_assigns_registration(client,db):
    office=Office(name='Oficina Centro',token_secret='c'*64);db.add(office);db.commit()
    assert current_registration_code(office,date(2026,11,20))!=current_registration_code(office,date(2026,11,21))
    code=current_registration_code(office)
    response=client.post('/api/auth/register',json={'email':'office-client@example.com','password':'A-secure-password-123!','full_name':'Office Client','registration_code':code})
    assert response.status_code==201,response.text
    assert db.get(User,response.json()['id']).office_id==office.id

def test_client_uploads_four_images_and_submits_for_admin_review(client,db,funded):
    user,_,owner=funded;app.dependency_overrides[current_user]=lambda:user
    for kind in ('id_front','id_back','proof_address','selfie'):
        response=client.post('/api/kyc/documents/'+kind,files={'file':('proof.png',b'\x89PNG\r\n\x1a\nsynthetic-image','image/png')})
        assert response.status_code==201,response.text
    assert [item['status'] for item in client.get('/api/kyc/status').json()['documents']]==['pending']*4
    assert client.get('/api/kyc/status').json()['status']=='none'
    assert client.post('/api/kyc/submit').status_code==200
    assert client.get('/api/kyc/status').json()['status']=='pending'
    app.dependency_overrides[current_user]=lambda:owner
    queue=client.get('/api/admin/kyc/queue').json()['items']
    assert len(queue)==4 and all('file_data' not in item for item in queue)
    image=client.get('/api/admin/kyc/documents/'+str(queue[0]['id'])+'/image')
    assert image.status_code==200 and image.headers['content-type']=='image/png'

def test_kyc_requires_all_documents_before_submission(client,funded):
    user,_,_=funded;app.dependency_overrides[current_user]=lambda:user
    response=client.post('/api/kyc/submit')
    assert response.status_code==422
    assert client.get('/api/kyc/status').json()['status']=='none'
