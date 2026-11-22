import type { ReactNode } from 'react';

const paths: Record<string, ReactNode> = {
  dashboard: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  users: <><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M17 5a3 3 0 0 1 0 6m1 3a5 5 0 0 1 3 5v1"/></>,
  offices: <><rect x="4" y="7" width="16" height="14" rx="1"/><path d="M8 7V3h8v4M9 21v-5h6v5M8 11h1m6 0h1"/></>,
  production: <path d="M3 17l6-6 4 4 8-9M3 21h18"/>,
  notifications: <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>,
  kyc: <><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16h6m3-6h4m-4 3h3"/></>,
  payments: <><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M3 9h3m12 6h3"/></>,
  'payment-methods': <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 15h4"/></>,
  cards: <><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/></>,
  swaps: <path d="M4 7h16m-4-4 4 4-4 4M20 17H4m4-4-4 4 4 4"/>,
  credit: <><circle cx="12" cy="12" r="9"/><path d="M12 6v12m3-9H9a2 2 0 0 0 0 4h6a2 2 0 0 1 0 4H9"/></>,
  'deposit-wallets': <><rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 10h18M16 15h2"/></>,
  'stake-plans': <path d="M12 21v-9m0 4c-5 0-8-3-8-8 5 0 8 3 8 8Zm0-4c0-5 3-8 8-8 0 5-3 8-8 8Z"/>,
  'stake-positions': <><rect x="4" y="6" width="16" height="13" rx="2"/><path d="M8 3v6m8-6v6M4 11h16"/></>,
  chats: <><path d="M20 11a7 7 0 0 1-7 7H8l-4 3v-6a7 7 0 1 1 16-4Z"/><path d="M8 10h8m-8 3h5"/></>,
  tickets: <><path d="M4 5h16v5a2 2 0 0 0 0 4v5H4v-5a2 2 0 0 0 0-4V5Z"/><path d="M12 5v14"/></>,
  help: <><circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 1 1 4 3c-1 .5-1 1-1 2m0 3h.01"/></>,
  ranking: <path d="M3 21h18M5 21v-7h4v7m2 0V9h4v12m2 0V4h4v17"/>,
  menu: <path d="M4 7h16M4 12h16M4 17h16"/>,
  close: <path d="M5 5l14 14M19 5 5 19"/>,
  logout: <><path d="M10 4H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5M15 8l4 4-4 4m4-4H9"/></>,
  chevron: <path d="m9 6 6 6-6 6"/>,
};

export default function AdminIcon({name, size = 19}: {name: string; size?: number}) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.dashboard}</svg>;
}
