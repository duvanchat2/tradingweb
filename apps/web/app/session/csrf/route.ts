import { NextRequest, NextResponse } from 'next/server';
import { ensureCsrf } from '../../../lib/session';


export const dynamic = 'force-dynamic';


export async function GET(request: NextRequest) {
  if (request.headers.get('sec-fetch-site') === 'cross-site') {
    return NextResponse.json({error: 'Solicitud no permitida'}, {status: 403});
  }
  const seed = NextResponse.json({});
  const token = ensureCsrf(seed);
  return new NextResponse(JSON.stringify({csrf: token}), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
      'Set-Cookie': seed.headers.get('set-cookie') || '',
    },
  });
}
