"use client";

import { useState } from "react";

export default function CopyAddress({ address }: { address: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(address);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }
  return <button className="admin-code-copy" type="button" onClick={copy} aria-label="Copiar dirección de depósito">{copied ? "Copiada" : "Copiar"}</button>;
}
