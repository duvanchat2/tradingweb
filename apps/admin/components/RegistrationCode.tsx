"use client";

import { useState } from "react";

export default function RegistrationCode({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }
  return <button className="admin-code-copy" type="button" onClick={copy} aria-label={`Copiar código ${code}`}>{copied ? "Copiado" : "Copiar"}</button>;
}
