import type { SVGProps } from 'react';
import { Bell, ChartNoAxesCombined, CreditCard, Headphones, LayoutDashboard, ListRestart, LogOut, MessagesSquare, PiggyBank, Repeat2, Settings, ShieldCheck, Sun, WalletCards, type LucideIcon } from 'lucide-react';

const icons:Record<string,LucideIcon>={dashboard:LayoutDashboard,bell:Bell,wallet:WalletCards,swap:Repeat2,stake:PiggyBank,market:ChartNoAxesCombined,transactions:ListRestart,payments:CreditCard,chat:MessagesSquare,support:Headphones,settings:Settings,verification:ShieldCheck,logout:LogOut,sun:Sun};
export function PanelIcon({name,...props}:{name:string}&SVGProps<SVGSVGElement>){const Icon=icons[name]||LayoutDashboard;return <Icon aria-hidden="true" strokeWidth={1.8} {...props}/>}

const coinFiles: Record<string, string> = { BTC: 'bitcoin.png', ETH: 'ethereum.png', USDT: 'tether.png', BNB: 'bnb.png', USDC: 'usdc.png', SOL: 'solana.png', XRP: 'xrp.png', DOGE: 'dogecoin.png', TRX: 'tron.png' };
export function CryptoIcon({ symbol, size = 38 }: { symbol: string; size?: number }) {
  const code = String(symbol || '').toUpperCase().replace(/[^A-Z]/g, '');
  const file = coinFiles[code];
  if (!file) return <span className="crypto-fallback" style={{ width: size, height: size }}>{code.slice(0, 1)}</span>;
  return <img className="crypto-icon" src={`/app/coins/${file}`} width={size} height={size} alt={`${code} icono`} />;
}
