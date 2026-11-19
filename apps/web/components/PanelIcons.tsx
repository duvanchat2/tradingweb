import type { SVGProps } from 'react';

const paths: Record<string, string> = {
  dashboard: 'M3 3h7v7H3V3Zm11 0h7v4h-7V3ZM3 14h7v7H3v-7Zm11-3h7v10h-7V11Z',
  bell: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4', wallet: 'M3 6h16a2 2 0 0 1 2 2v11H5a2 2 0 0 1-2-2V6Zm0 3h18m-5 4h3v3h-3z',
  swap: 'm7 7-4 4 4 4m-4-4h14m0-4 4 4-4 4', stake: 'M5 7h14l-1 14H6L5 7Zm3 0V4h8v3m-8 5h8m-8 4h6', market: 'M4 19V9m5 10V5m5 14v-7m5 7V3',
  transactions: 'M4 7h15m-4-4 4 4-4 4M20 17H5m4-4-4 4 4', payments: 'M3 6h18v12H3V6Zm0 4h18M7 15h3', chat: 'M4 4h16v12H8l-4 4V4Z',
  support: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Zm-4-9v-2a4 4 0 0 1 8 0v2m-8 0v4h3m5-4v4h-3', settings: 'M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm8-3.5 2-1-2-4-2 .5-1.5-1L16 4h-4l-.5 2.5-1.5 1L8 7 6 11l2 1v2l-2 1 2 4 2-.5 1.5 1L12 22h4l.5-2.5 1.5-1 2 .5 2-4-2-1v-2Z',
  verification: 'M12 3 4 6v5c0 5 3.4 8.7 8 10 4.6-1.3 8-5 8-10V6l-8-3Zm-3 9 2 2 4-5', logout: 'M10 5H4v14h6m4-4 4-3-4-3m4 3H8', sun: 'M12 4V2m0 20v-2m8-8h2M2 12h2m13.7-5.7 1.4-1.4M4.9 19.1l1.4-1.4m11.4 0 1.4 1.4M4.9 4.9l1.4 1.4M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10Z',
};

export function PanelIcon({ name, ...props }: { name: string } & SVGProps<SVGSVGElement>) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}><path d={paths[name] || paths.dashboard} /></svg>;
}

const coinFiles: Record<string, string> = { BTC: 'bitcoin.png', ETH: 'ethereum.png', USDT: 'tether.png', BNB: 'bnb.png', USDC: 'usdc.png', SOL: 'solana.png', XRP: 'xrp.png', DOGE: 'dogecoin.png', TRX: 'tron.png' };
export function CryptoIcon({ symbol, size = 38 }: { symbol: string; size?: number }) {
  const code = String(symbol || '').toUpperCase().replace(/[^A-Z]/g, '');
  const file = coinFiles[code];
  if (!file) return <span className="crypto-fallback" style={{ width: size, height: size }}>{code.slice(0, 1)}</span>;
  return <img className="crypto-icon" src={`/coins/${file}`} width={size} height={size} alt={`${code} icono`} />;
}
