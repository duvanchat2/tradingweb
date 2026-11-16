import 'server-only';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes, timingSafeEqual } from 'node:crypto';


export const API = process.env.API_INTERNAL_URL || 'http://api:8000';
const accessName = 'tw_client_access';
const refreshName = 'tw_client_refresh';
export const csrfName = 'tw_client_csrf';
const cookieOptions = {
  httpOnly: true,
  sameSite: 'strict' as const,
  secure: process.env.WEB_COOKIE_SECURE === 'true',
  path: '/app',
};


export function csrfValue() {
  return cookies().get(csrfName)?.value || '';
}


export function setTokens(
  response: NextResponse,
  tokens: { access_token: string; refresh_token: string; expires_in: number },
) {
  response.cookies.set(accessName, tokens.access_token, {...cookieOptions, maxAge: tokens.expires_in});
  response.cookies.set(refreshName, tokens.refresh_token, {...cookieOptions, maxAge: 7 * 24 * 3600});
}


export function clearTokens(response: NextResponse) {
  for (const name of [accessName, refreshName, csrfName]) {
    response.cookies.set(name, '', {...cookieOptions, maxAge: 0});
  }
}


export function ensureCsrf(response: NextResponse) {
  const value = csrfValue() || randomBytes(32).toString('hex');
  response.cookies.set(csrfName, value, {...cookieOptions, maxAge: 7 * 24 * 3600});
  return value;
}


export function publicURL(request: NextRequest, path: string) {
  const scheme = request.headers.get('x-forwarded-proto') === 'https' ? 'https' : 'http';
  return new URL(path, `${scheme}://${request.headers.get('host')}`);
}


function sameOrigin(request: NextRequest) {
  const origin = request.headers.get('origin');
  if (!origin) return false;
  try {
    return new URL(origin).host === request.headers.get('host');
  } catch {
    return false;
  }
}


export function validCsrf(request: NextRequest, value: string) {
  const expected = csrfValue();
  return sameOrigin(request)
    && expected.length >= 32
    && value.length === expected.length
    && timingSafeEqual(Buffer.from(value), Buffer.from(expected));
}


export async function apiFetch(path: string, token?: string, options: RequestInit = {}) {
  return fetch(API + path, {
    ...options,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-Confirm': 'true',
      ...(token ? {Authorization: `Bearer ${token}`} : {}),
      ...options.headers,
    },
  });
}


export async function refreshTokens() {
  const refreshToken = cookies().get(refreshName)?.value;
  if (!refreshToken) return null;
  const response = await apiFetch('/api/auth/refresh', undefined, {
    method: 'POST',
    body: JSON.stringify({refresh_token: refreshToken}),
  });
  return response.ok ? response.json() : null;
}


export function accessToken() {
  return cookies().get(accessName)?.value;
}


export async function clientGet(path: string, returnTo = '/app/dashboard') {
  const access = accessToken();
  if (!access) redirect(`/session/refresh?next=${encodeURIComponent(returnTo)}`);
  const response = await apiFetch(path, access);
  if (response.status === 401) redirect(`/session/refresh?next=${encodeURIComponent(returnTo)}`);
  if (response.status === 403) redirect('/login?error=client');
  if (!response.ok) throw new Error('No se pudo cargar la información. Intenta de nuevo.');
  return response.json();
}
