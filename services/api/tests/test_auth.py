import secrets
from app.models.schema import User
from app.core.config import Settings
import pytest

def credentials():
    return {'email':'new@example.com','password':secrets.token_urlsafe(20)}

def test_registration_login_rotation_logout(client):
    body = credentials()
    response = client.post('/api/auth/register',json={**body,'full_name':'Demo','role':'superworker'})
    assert response.status_code == 201
    assert response.json()['role'] == 'client'
    assert 'password_hash' not in response.json()
    assert client.post('/api/auth/register',json={**body,'full_name':'Demo'}).status_code == 409
    assert client.post('/api/auth/login',json={**body,'password':secrets.token_urlsafe(24)}).status_code == 401
    response = client.post('/api/auth/login',json=body)
    assert response.status_code == 200
    pair = response.json()
    headers = {'Authorization':'Bearer '+pair['access_token']}
    assert client.get('/api/auth/me',headers=headers).json()['email'] == body['email']
    assert client.get('/api/auth/me',headers={'Authorization':'Bearer '+pair['refresh_token']}).status_code == 401
    rotated = client.post('/api/auth/refresh',json={'refresh_token':pair['refresh_token']})
    assert rotated.status_code == 200
    headers = {'Authorization':'Bearer '+rotated.json()['access_token']}
    assert client.post('/api/auth/logout',headers=headers).status_code == 204
    assert client.get('/api/auth/me',headers=headers).status_code == 401
    assert client.post('/api/auth/refresh',json={'refresh_token':rotated.json()['refresh_token']}).status_code == 401

def test_refresh_replay_revokes_session(client):
    body = credentials()
    client.post('/api/auth/register',json={**body,'full_name':'Demo'})
    pair = client.post('/api/auth/login',json=body).json()
    rotated = client.post('/api/auth/refresh',json={'refresh_token':pair['refresh_token']}).json()
    assert client.post('/api/auth/refresh',json={'refresh_token':pair['refresh_token']}).status_code == 401
    assert client.get('/api/auth/me',headers={'Authorization':'Bearer '+rotated['access_token']}).status_code == 401

def test_demo_guard_and_disabled_user(client,db):
    assert client.get('/api/meta').json() == {'demo_mode':True,'message':'Entorno de simulación'}
    client.headers.pop('X-Demo-Confirm')
    assert client.get('/api/meta').status_code == 428
    assert client.post('/api/auth/register',json={}).status_code == 428
    client.headers['X-Demo-Confirm'] = 'true'
    body = credentials()
    user_id = client.post('/api/auth/register',json={**body,'full_name':'Demo'}).json()['id']
    user = db.get(User,user_id); user.is_active=False; db.commit()
    assert client.post('/api/auth/login',json=body).status_code == 401

@pytest.mark.parametrize('key',[None,'a-license-does-not-enable-live'])
def test_live_mode_refused(key):
    with pytest.raises(ValueError): Settings(demo_mode=False,live_license_key=key)
