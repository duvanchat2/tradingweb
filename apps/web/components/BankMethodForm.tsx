'use client';

import { useMemo, useState } from 'react';
import ClientActionForm from './ClientActionForm';
import transferBanks from '../data/transfer-banks.json';

type Bank = { id: number; name: string };
const banks = transferBanks as Record<string, Bank[]>;
const preferred = ['Colombia', 'México', 'Argentina', 'Chile', 'Perú', 'Venezuela', 'Ecuador', 'Brasil', 'Panamá'];
const countries = [...preferred.filter((country) => banks[country]), ...Object.keys(banks).filter((country) => !preferred.includes(country)).sort((a, b) => a.localeCompare(b))];

export default function BankMethodForm({ csrf }: { csrf: string }) {
  const [country, setCountry] = useState('');
  const [bankId, setBankId] = useState('');
  const rows = useMemo(() => transferBanks[country as keyof typeof transferBanks] || [], [country]);
  const selected = rows.find((bank) => String(bank.id) === bankId);

  return <ClientActionForm action="payment_method_create" csrf={csrf} initial={{ type: 'bank' }} label="Agregar método bancario">
    <div className="transfer-type"><span>🌐</span><b>Transferencia internacional</b></div>
    <label>País
      <select name="bank_country" value={country} onChange={(event) => { setCountry(event.target.value); setBankId(''); }} required>
        <option value="">Selecciona el país</option>
        {countries.map((name) => <option key={name} value={name}>{name}</option>)}
      </select>
    </label>
    <label>Banco
      <select name="bank_id" value={bankId} onChange={(event) => setBankId(event.target.value)} disabled={!country} required>
        <option value="">{country ? 'Selecciona el banco' : 'Primero selecciona un país'}</option>
        {rows.map((bank) => <option key={bank.id} value={bank.id}>{bank.name}</option>)}
      </select>
    </label>
    <input type="hidden" name="bank_name" value={selected?.name || ''} />
    <label>Alias<input name="label" placeholder="Mi cuenta principal" required /></label>
    <label>Nombre del titular<input name="holder_name" placeholder="Nombre completo del titular" required /></label>
    <label>Tipo de cuenta<select name="account_type"><option>Ahorros</option><option>Corriente</option><option>Cuenta internacional</option></select></label>
    <label>Últimos 4 dígitos de la cuenta<input name="account_last4" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} placeholder="1234" required /></label>
    <small className="safe-note">Por seguridad no almacenamos el número bancario completo en este entorno.</small>
  </ClientActionForm>;
}
