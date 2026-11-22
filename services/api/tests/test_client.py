from decimal import Decimal

from app.models.schema import Notification, PaymentMethod, Ticket, TicketMessage, Transaction


def test_account_summary_and_transactions_are_scoped(client, db, funded):
    user, other, _ = funded
    summary = client.get('/api/account')
    assert summary.status_code == 200
    assert summary.json()['user']['id'] == user.id
    assert len(summary.json()['accounts']) == 9
    assert all(Decimal(str(row['balance'])) == Decimal('1000') for row in summary.json()['accounts'])

    transactions = client.get('/api/account/transactions?limit=5')
    assert transactions.status_code == 200
    assert len(transactions.json()['items']) == 5
    account_ids = {row['account_id'] for row in transactions.json()['items']}
    assert account_ids.issubset({row['id'] for row in summary.json()['accounts']})
    assert not any(row['account_id'] == other.id for row in transactions.json()['items'])


def test_deposit_request_is_pending_and_does_not_credit_balance(client, db, funded):
    user, _, _ = funded
    before = {row['currency']: row['balance'] for row in client.get('/api/account').json()['accounts']}
    response = client.post('/api/payments/deposit-request', json={
        'currency': 'USDT', 'amount': '25', 'network': 'DEMO', 'method': 'simulated-transfer'
    })
    assert response.status_code == 201, response.text
    assert response.json()['status'] == 'pending'
    assert response.json()['execution_status'] == 'simulated'
    assert {row['currency']: row['balance'] for row in client.get('/api/account').json()['accounts']} == before
    requests = client.get('/api/payments/requests').json()['items']
    assert requests[0]['id'] == response.json()['id'] and requests[0]['user_id'] == user.id


def test_notifications_are_scoped_and_can_be_marked_read(client, db, funded):
    user, other, _ = funded
    own = Notification(user_id=user.id, scope='one', type='info', title='Own', body='Synthetic', is_read=False)
    global_notice = Notification(user_id=None, scope='all', type='warning', title='All', body='Demo', is_read=False)
    foreign = Notification(user_id=other.id, scope='one', type='info', title='Foreign', body='Hidden', is_read=False)
    db.add_all([own, global_notice, foreign]); db.commit()
    rows = client.get('/api/notifications?unread=true').json()['items']
    assert {row['title'] for row in rows} == {'Own', 'All'}
    assert client.post(f'/api/notifications/{own.id}/read').status_code == 200
    db.refresh(own); assert own.is_read is True
    assert client.post(f'/api/notifications/{foreign.id}/read').status_code == 404


def test_ticket_creation_and_messages_are_private(client, db, funded):
    user, other, _ = funded
    created = client.post('/api/tickets', json={'subject': 'Ayuda demo', 'body': 'Mensaje sintético'})
    assert created.status_code == 201, created.text
    ticket_id = created.json()['id']
    assert db.get(Ticket, ticket_id).user_id == user.id
    assert db.query(TicketMessage).filter_by(ticket_id=ticket_id).count() == 1
    assert client.get('/api/tickets').json()['items'][0]['id'] == ticket_id
    assert client.get(f'/api/tickets/{ticket_id}/messages').status_code == 200

    foreign = Ticket(user_id=other.id, subject='Foreign')
    db.add(foreign); db.commit()
    assert client.get(f'/api/tickets/{foreign.id}/messages').status_code == 404


def test_bank_method_encrypts_full_account_and_only_returns_mask(client, db, funded):
    response = client.post('/api/payments/methods', json={
        'type': 'bank', 'label': 'Bancolombia', 'holder_name': 'Cliente Demo',
        'bank_country': 'Colombia', 'bank_id': 7, 'bank_name': 'Bancolombia',
        'bank_account': '123456789012',
    })
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload['account_last4'] == '9012'
    assert 'bank_account' not in payload and 'bank_account_encrypted' not in payload
    row = db.get(PaymentMethod, payload['id'])
    assert row.bank_account_encrypted
    assert '123456789012' not in row.bank_account_encrypted


def test_live_chat_reuses_conversation_and_exposes_staff_reply(client, db, funded):
    _, _, staff = funded
    first = client.post('/api/chat/messages', json={'body': 'Hola desde la cuenta de prueba'})
    assert first.status_code == 201, first.text
    ticket_id = first.json()['ticket']['id']
    second = client.post('/api/chat/messages', json={'body': 'Segundo mensaje'})
    assert second.status_code == 201 and second.json()['ticket']['id'] == ticket_id
    db.add(TicketMessage(ticket_id=ticket_id, sender_id=staff.id, body='Respuesta del administrador'))
    db.commit()
    conversation = client.get('/api/chat').json()
    assert [item['body'] for item in conversation['items']] == [
        'Hola desde la cuenta de prueba', 'Segundo mensaje', 'Respuesta del administrador'
    ]
