import type { ReactNode } from 'react';
import PanelShell from '../../components/PanelShell';
import { csrfValue } from '../../lib/session';

export default function PanelLayout({ children }: { children: ReactNode }) {
  return <PanelShell csrf={csrfValue()}>{children}</PanelShell>;
}
