"use client";

import { useState } from "react";
import ActionForm from "./ActionForm";

const assets = [
  ["BTC", "Bitcoin", ["BTC"]], ["ETH", "Ethereum", ["ERC20"]],
  ["USDT", "Tether", ["TRC20", "ERC20", "BEP20", "POLYGON", "SOLANA"]],
  ["BNB", "BNB", ["BEP20"]], ["USDC", "USD Coin", ["ERC20", "BEP20", "POLYGON", "SOLANA"]],
  ["XRP", "XRP", ["XRP"]], ["SOL", "Solana", ["SOLANA"]],
  ["TRX", "TRON", ["TRC20"]], ["DOGE", "Dogecoin", ["DOGE"]],
] as const;

export default function FundsForm({ csrf }: { csrf: string }) {
  const [currency, setCurrency] = useState("USDT");
  const networks: readonly string[] = assets.find((asset) => asset[0] === currency)?.[2] || ["TRC20"];
  return <ActionForm action="credit" csrf={csrf} label="↗ Aplicar movimiento" showReset={false}
    confirmMessage="¿Confirmas este movimiento manual? Se registrará en el ledger y se mostrará al cliente."
    className="admin-funds-form">
    <label>Usuario (ID o email)<input name="user" placeholder="3 o demo@globalefecty.com" required autoComplete="off" /></label>
    <div className="admin-funds-two">
      <label>Moneda<select name="currency" value={currency} onChange={(event) => setCurrency(event.target.value)}>
        {assets.map(([symbol, name]) => <option key={symbol} value={symbol}>{symbol} — {name}</option>)}
      </select></label>
      <label>Red<select name="network" key={currency} defaultValue={networks[0]}>
        {networks.map((network) => <option key={network} value={network}>{network}</option>)}
      </select></label>
    </div>
    <label>Monto<input name="amount" type="number" inputMode="decimal" min="0.00000001" step="0.00000001" placeholder="0.00" required /></label>
    <fieldset className="admin-funds-operation"><legend>Operación</legend>
      <label><input type="radio" name="operation" value="credit" defaultChecked /><span>↑ Acreditar</span></label>
      <label><input type="radio" name="operation" value="debit" /><span>↓ Debitar</span></label>
    </fieldset>
    <label>Nota <small>(visible para el usuario)</small><input name="note" placeholder="Ej: ajuste de saldo · regalo · ajuste KYC…" maxLength={2000} required /></label>
  </ActionForm>;
}
