import { NextRequest, NextResponse } from 'next/server';
import {
  accessToken,
  apiFetch,
  refreshTokens,
  setTokens,
  validCsrf,
} from '../../../lib/session';


type Payload = Record<string, unknown>;
type Spec = {path: string; method: 'POST' | 'DELETE'; body?: Payload};


function pick(payload: Payload, names: string[]) {
  return Object.fromEntries(names.filter(name => payload[name] !== undefined).map(name => [name, payload[name]]));
}


function operation(payload: Payload): Spec | null {
  switch (payload.action) {
    case 'order':
      return {path: '/api/orders', method: 'POST', body: pick(payload, ['pair', 'side', 'qty', 'type', 'price'])};
    case 'cancel_order':
      return {path: `/api/orders/${Number(payload.order_id)}`, method: 'DELETE'};
    case 'swap':
      return {path: '/api/swaps', method: 'POST', body: {
        from_currency: payload.from_currency,
        to_currency: payload.to_currency,
        amount: payload.amount,
      }};
    case 'stake':
      return {path: '/api/stake/positions', method: 'POST', body: pick(payload, ['plan_id', 'amount'])};
    case 'withdrawal':
      return {path: '/api/payments/withdrawal-request', method: 'POST', body: pick(payload, ['currency', 'amount', 'payment_method_id', 'network', 'destination_address'])};
    case 'deposit_request':
      return {path: '/api/payments/deposit-request', method: 'POST', body: pick(payload, ['currency', 'amount', 'payment_method_id'])};
    case 'payment_method_create':
      return {path: '/api/payments/methods', method: 'POST', body: pick(payload, ['type', 'label', 'holder_name', 'bank_country', 'bank_id', 'bank_name', 'bank_account', 'card_brand', 'card_last4', 'network', 'wallet_address'])};
    case 'payment_method_delete':
      return {path: `/api/payments/methods/${Number(payload.payment_method_id)}`, method: 'DELETE'};
    case 'notification_read':
      return {path: `/api/notifications/${Number(payload.notification_id)}/read`, method: 'POST', body: {}};
    case 'ticket':
      return {path: '/api/tickets', method: 'POST', body: pick(payload, ['subject', 'body'])};
    case 'chat_message':
      return {path: '/api/chat/messages', method: 'POST', body: pick(payload, ['body'])};
    case 'password_change':
      return {path: '/api/auth/password', method: 'POST', body: pick(payload, ['current_password', 'new_password'])};
    case 'revoke_others':
      return {path: '/api/auth/sessions/revoke-others', method: 'POST', body: {}};
    case 'revoke_session':
      return {path: `/api/auth/sessions/${encodeURIComponent(String(payload.session_id))}`, method: 'DELETE'};
    case 'kyc_submit':
      return {path: '/api/kyc/submit', method: 'POST', body: {}};
    default:
      return null;
  }
}


function detail(value: unknown) {
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return value.map(item => item?.msg || 'Dato inválido').join(' · ');
  return 'No se pudo completar la operación.';
}


export async function POST(request: NextRequest) {
  if (!validCsrf(request, request.headers.get('x-csrf-token') || '')) {
    return NextResponse.json({detail: 'Confirmación CSRF inválida'}, {status: 403});
  }
  let payload: Payload;
  try { payload = await request.json(); }
  catch { return NextResponse.json({detail: 'Solicitud inválida'}, {status: 400}); }
  const spec = operation(payload);
  if (!spec) return NextResponse.json({detail: 'Acción no permitida'}, {status: 400});
  const options: RequestInit = {method: spec.method};
  if (spec.body !== undefined) options.body = JSON.stringify(spec.body);
  let response = await apiFetch(spec.path, accessToken(), options);
  let tokens = null;
  if (response.status === 401) {
    tokens = await refreshTokens();
    if (tokens) response = await apiFetch(spec.path, tokens.access_token, options);
  }
  const raw = await response.text();
  let parsed: any = {};
  try { parsed = raw ? JSON.parse(raw) : {}; } catch { parsed = {}; }
  const result = NextResponse.json(
    response.ok ? {...parsed, message: 'Operación guardada.'} : {detail: detail(parsed.detail)},
    {status: response.status},
  );
  result.headers.set('Cache-Control', 'no-store');
  if (tokens) setTokens(result, tokens);
  return result;
}
