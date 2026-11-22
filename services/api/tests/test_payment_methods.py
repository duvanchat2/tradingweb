from decimal import Decimal

from sqlalchemy import select

from app.models.schema import PaymentMethod, PaymentRequest, StakePlan


def bank_payload(label='Cuenta principal'):
    return {
        'type': 'bank', 'label': label, 'holder_name': 'Cliente Sintético',
        'bank_country': 'Colombia', 'bank_id': 1, 'bank_name': 'Bancolombia',
        'account_type': 'Ahorros', 'account_last4': '1234',
    }


def test_client_can_link_list_and_soft_delete_payment_methods(client, db, funded):
    bank = client.post('/api/payments/methods', json=bank_payload())
    card = client.post('/api/payments/methods', json={
        'type': 'card', 'label': 'Tarjeta demo', 'holder_name': 'Cliente Sintético',
        'card_brand': 'Visa', 'card_last4': '4242',
    })
    crypto = client.post('/api/payments/methods', json={
        'type': 'crypto', 'label': 'Wallet demo', 'holder_name': 'Cliente Sintético',
        'network': 'TRC20', 'wallet_address': 'synthetic-wallet-address',
    })
    assert [response.status_code for response in (bank, card, crypto)] == [201, 201, 201]
    assert len(client.get('/api/payments/methods').json()['items']) == 3
    assert client.delete(f"/api/payments/methods/{card.json()['id']}").status_code == 200
    assert len(client.get('/api/payments/methods').json()['items']) == 2
    assert db.get(PaymentMethod, card.json()['id']).is_active is False


def test_card_pan_and_cvv_are_rejected_and_never_persisted(client, db, funded):
    payload = {
        'type': 'card', 'label': 'No guardar', 'holder_name': 'Cliente Sintético',
        'card_brand': 'Visa', 'card_last4': '4242', 'card_number': '4242424242424242', 'cvv': '123',
    }
    assert client.post('/api/payments/methods', json=payload).status_code == 422
    assert db.scalar(select(PaymentMethod)) is None


def test_withdrawal_uses_an_owned_linked_method(client, db, funded):
    method = client.post('/api/payments/methods', json=bank_payload()).json()
    response = client.post('/api/payments/withdrawal-request', json={
        'currency': 'USDT', 'amount': '25', 'payment_method_id': method['id'],
    })
    assert response.status_code == 201, response.text
    assert response.json()['payment_method_id'] == method['id']
    request = db.get(PaymentRequest, response.json()['id'])
    assert request.destination_address == 'Bancolombia ••••1234'
    assert request.network == 'BANK'


def test_cdt_lists_and_accepts_all_active_supported_currency_plans(client, db, funded):
    btc = StakePlan(currency='BTC', apy=Decimal('8.2'), min_amount=Decimal('0.005'), term_days=30, is_active=True)
    usdt = StakePlan(currency='USDT', apy=Decimal('9.5'), min_amount=Decimal('100'), term_days=90, is_active=True)
    inactive = StakePlan(currency='ETH', apy=Decimal('12.5'), min_amount=Decimal('0.05'), term_days=60, is_active=False)
    db.add_all([btc, usdt, inactive]); db.commit()
    plans = client.get('/api/stake/plans').json()
    assert [row['id'] for row in plans] == [btc.id, usdt.id]
    assert client.post('/api/stake/positions', json={'plan_id': btc.id, 'amount': '0.005'}).status_code == 201
    assert client.post('/api/stake/positions', json={'plan_id': inactive.id, 'amount': '0.05'}).status_code == 422
