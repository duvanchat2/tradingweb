import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { adminGet, csrfValue } from "../../../lib/session";
import ActionForm from "../../../components/ActionForm";
import AdminIcon from "../../../components/AdminIcon";
import RegistrationCode from "../../../components/RegistrationCode";
export const dynamic = "force-dynamic";
type Row = Record<string, any>;
type Search = Record<string, string | undefined>;
const titles: Record<string, string> = {
  dashboard: "Resumen",
  users: "Usuarios",
  offices: "Oficinas",
  production: "Producción",
  notifications: "Notificaciones",
  kyc: "KYC / Documentos",
  payments: "Pagos",
  "payment-methods": "Métodos vinculados",
  cards: "Tarjetas",
  swaps: "Swaps",
  credit: "Agregar fondos",
  "deposit-wallets": "Wallets depósito",
  "stake-plans": "Planes stake",
  "stake-positions": "Solicitudes CDT",
  chats: "Chats",
  tickets: "Tickets",
  help: "Centro de ayuda",
  ranking: "Ranking",
};
const descriptions: Record<string, string> = {
  users: "Busca y gestiona los clientes de tu oficina.",
  production: "Consulta el rendimiento y los movimientos de tu oficina.",
  notifications: "Mantén informados a los clientes sobre la actividad de sus cuentas.",
  kyc: "Revisa documentos de identidad y el estado de verificación.",
  payments: "Revisa solicitudes de depósitos y retiros antes de resolverlas.",
  cards: "Consulta los métodos de tarjeta vinculados por los clientes.",
  swaps: "Gestiona las solicitudes de intercambio pendientes.",
  credit: "Registra ajustes manuales con trazabilidad y confirmación.",
  "deposit-wallets": "Configura las direcciones de depósito que ven los clientes.",
  "stake-plans": "Consulta los planes CDT y sus condiciones.",
  chats: "Atiende conversaciones de los clientes de tu oficina.",
  tickets: "Responde las solicitudes de soporte de tus clientes.",
  help: "Guías para administrar cuentas y operaciones.",
  ranking: "Actividad de los clientes dentro del ámbito de tu oficina.",
};
const currencies = [
  "BTC",
  "ETH",
  "USDT",
  "USDC",
  "BNB",
  "XRP",
  "SOL",
  "TRX",
  "DOGE",
];
function Table({
  rows,
  columns,
}: {
  rows: Row[];
  columns: [string, string][];
}) {
  if (!rows.length)
    return <div className="empty">No hay registros para estos filtros.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map(([key, title]) => (
              <th key={key}>{title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map(([key]) => (
                <td key={key}>
                  {key === "user_id" ? (
                    <Link href={"/user/" + row[key]}>{row[key]}</Link>
                  ) : key === "id" && row.email ? (
                    <Link href={"/user/" + row.id}>{row.id}</Link>
                  ) : typeof row[key] === "boolean" ? (
                    row[key] ? (
                      "Sí"
                    ) : (
                      "No"
                    )
                  ) : (
                    String(row[key] ?? "—")
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function Currency() {
  return (
    <label>
      Moneda
      <select name="currency" defaultValue="USDT">
        {currencies.map((c) => (
          <option key={c}>{c}</option>
        ))}
      </select>
    </label>
  );
}
function Note({
  name = "note",
  value = "",
}: {
  name?: string;
  value?: string;
}) {
  return (
    <label>
      Nota del equipo
      <textarea
        name={name}
        defaultValue={value}
        maxLength={2000}
        required={name === "note"}
      />
    </label>
  );
}
function Pager({
  data,
  section,
  search,
}: {
  data: Row;
  section: string;
  search: Search;
}) {
  const query = (page: number) => {
    const params = new URLSearchParams();
    Object.entries(search).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
    params.set("page", String(page));
    return "/" + section + "?" + params;
  };
  return (
    <div className="pagination">
      <span>
        {data.total} registros · Página {data.page} de {Math.max(1, data.pages)}
      </span>
      {data.page > 1 && <Link href={query(data.page - 1)}>← Anterior</Link>}
      {data.page < data.pages && (
        <Link href={query(data.page + 1)}>Siguiente →</Link>
      )}
    </div>
  );
}
function ReviewDocument({ doc, csrf }: { doc: Row; csrf: string }) {
  return (
    <article className="card" key={doc.id}>
      <h3>
        {doc.doc_type} · #{doc.id}
      </h3>
      <p>
        Usuario <Link href={"/user/" + doc.user_id}>#{doc.user_id}</Link> ·{" "}
        {doc.status}
      </p>
      {doc.mime_type ? (
        <img
          className="kyc-preview"
          src={"/admin/backend/kyc/" + doc.id}
          alt={"Documento " + doc.doc_type}
        />
      ) : (
        <p className="muted">Archivo heredado: {doc.file_path}</p>
      )}
      <ActionForm
        action="kyc_document"
        csrf={csrf}
        initial={{ user_id: doc.user_id, document_id: doc.id }}
        label="Guardar revisión"
      >
        <label>
          Decisión
          <select name="decision" defaultValue="pending">
            <option value="pending">Pendiente</option>
            <option value="approved">Aprobado</option>
            <option value="rejected">Rechazado</option>
          </select>
        </label>
        <Note name="review_note" value={doc.review_note || ""} />
      </ActionForm>
    </article>
  );
}
function WalletForm({ row, csrf }: { row?: Row; csrf: string }) {
  return (
    <ActionForm
      action="deposit_wallet_save"
      csrf={csrf}
      initial={{ wallet_id: row?.id || 0 }}
      label={row ? "Guardar wallet" : "Crear wallet"}
    >
      <label>
        Etiqueta
        <input name="label" required defaultValue={row?.label} />
      </label>
      <label>
        Moneda
        <select name="currency" defaultValue={row?.currency || "USDT"}>
          {currencies.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
      </label>
      <label>
        Red
        <input name="network" required defaultValue={row?.network || "DEMO"} />
      </label>
      <label>
        Dirección
        <input name="address" required defaultValue={row?.address} />
      </label>
      <label>
        Estado
        <select
          name="is_active"
          defaultValue={row?.is_active === false ? "false" : "true"}
        >
          <option value="true">Activa</option>
          <option value="false">Inactiva</option>
        </select>
      </label>
    </ActionForm>
  );
}
function metrics(data: Row) {
  return (
    <div className="metrics">
      {[
        ["users_new", "Clientes nuevos"],
        ["pending_payments", "Pagos pendientes"],
        ["pending_kyc", "Documentos pendientes"],
        ["swaps_count", "Swaps"],
        ["tickets_open", "Tickets abiertos"],
      ].map(([key, label]) => (
        <article className="card" key={key}>
          <span>{label}</span>
          <strong>{data[key]}</strong>
        </article>
      ))}
    </div>
  );
}
export default async function Page({
  params,
  searchParams,
}: {
  params: { section?: string[] };
  searchParams: Search;
}) {
  const segments = params.section || [];
  if (!segments.length) redirect("/dashboard");
  const section = segments[0],
    csrf = csrfValue();
  const query = new URLSearchParams();
  Object.entries(searchParams).forEach(([k, v]) => {
    if (v) query.set(k, v);
  });
  const returnTo =
    "/admin/" + segments.join("/") + (query.size ? "?" + query : "");
  const get = (path: string) => adminGet("/api/admin/" + path, returnTo);
  if (
    section === "user" &&
    segments.length === 2 &&
    /^\d+$/.test(segments[1])
  ) {
    const data = await get("users/" + segments[1]);
    return (
      <>
        <div className="page-heading">
          <div>
            <span className="eyebrow">PERFIL DEL CLIENTE</span>
            <h1>{data.profile.full_name}</h1>
            <p>
              {data.profile.email} · KYC {data.profile.kyc_status}
            </p>
          </div>
          <Link href="/users">← Usuarios</Link>
        </div>
        <section className="card">
          <h2>Cuentas</h2>
          <Table
            rows={data.accounts}
            columns={[
              ["currency", "Moneda"],
              ["type", "Cuenta"],
              ["balance", "Saldo"],
            ]}
          />
        </section>
        <h2>Documentos</h2>
        <div className="grid">
          {data.documents.map((doc: Row) => (
            <ReviewDocument key={doc.id} doc={doc} csrf={csrf} />
          ))}
        </div>
        <section className="card">
          <h2>Últimos 100 asientos</h2>
          <Table
            rows={data.transactions}
            columns={[
              ["id", "Asiento"],
              ["kind", "Tipo"],
              ["currency", "Moneda"],
              ["amount", "Importe firmado"],
              ["original_transaction_id", "Original vinculado"],
              ["status", "Estado"],
            ]}
          />
        </section>
        <section className="card">
          <h2>Corregir un movimiento de cuenta principal</h2>
          <p>
            El importe indica la magnitud final deseada. Se añade una corrección
            compensatoria; el original se conserva.
          </p>
          <ActionForm
            csrf={csrf}
            action="credit_correct"
            label="Crear corrección"
          >
            <label>
              ID del asiento original
              <input name="transaction_id" type="number" min="1" required />
            </label>
            <label>
              Importe corregido
              <input
                name="amount"
                type="number"
                min="0"
                step="0.00000001"
                required
              />
            </label>
            <Note />
          </ActionForm>
        </section>
      </>
    );
  }
  if (!titles[section] || segments.length !== 1) notFound();
  let content;
  if (section === "payments") {
    const status = searchParams.status || "pending";
    const paymentQuery = new URLSearchParams(query);
    paymentQuery.set("status", status);
    const data = await get("payments?" + paymentQuery);
    content = (
      <>
        <form className="filters" action="/admin/payments">
          <label>
            Estado
            <select name="status" defaultValue={status}>
              {["pending", "approved", "rejected", "reverted"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <button>Filtrar</button>
        </form>
        {!data.items.length && (
          <div className="empty">No hay pagos en esta cola.</div>
        )}
        <div className="grid">
          {data.items.map((p: Row) => (
            <article className="card" key={p.id}>
              <h2>
                Solicitud #{p.id} · {p.currency}
              </h2>
              <p>
                <Link href={"/user/" + p.user_id}>Cliente #{p.user_id}</Link> ·{" "}
                {p.method === "simulated-withdrawal" ? "Retiro" : "Depósito"} ·{" "}
                <span className="pill">{p.status}</span>
              </p>
              <p className="muted">
                Estado de fondos:{" "}
                {
                  {
                    unsettled: "Sin liquidar",
                    credited: "Depósito acreditado",
                    paid: "Retiro liquidado",
                    released: "Fondos devueltos",
                  }[p.ledger_resolution as string]
                }{" "}
                · {p.network}
              </p>
              <ActionForm
                csrf={csrf}
                action="payment_review"
                initial={{ request_id: p.id }}
                label="Guardar revisión"
              >
                <label>
                  Monto aprobado
                  <input
                    name="amount"
                    type="number"
                    step="0.00000001"
                    min="0.00000001"
                    defaultValue={p.amount_approved || p.amount_requested}
                    readOnly={
                      p.method === "simulated-withdrawal" ||
                      p.status !== "pending"
                    }
                  />
                </label>
                <Note name="staff_note" value={p.staff_note || ""} />
                <label>
                  Decisión
                  <select name="decision">
                    {p.status === "pending" ? (
                      <>
                        <option value="approved">Aprobar</option>
                        <option value="rejected">Rechazar</option>
                      </>
                    ) : (
                      <option value="revert">
                        Reabrir revisión (sin mover saldos)
                      </option>
                    )}
                  </select>
                </label>
              </ActionForm>
            </article>
          ))}
        </div>
        <Pager data={data} section={section} search={searchParams} />
      </>
    );
  } else if (section === "swaps") {
    const data = await get("swaps?" + query);
    content = (
      <>
        <p>
          Las solicitudes pendientes no mueven saldo hasta la aprobación de la
          oficina.
        </p>
        <div className="grid">
          {data.items.map((row: Row) => (
            <article className="card" key={row.id}>
              <h2>
                Swap #{row.id} · {row.from_currency}/{row.to_currency}
              </h2>
              <p>
                <Link href={"/user/" + row.user_id}>
                  Cliente #{row.user_id}
                </Link>{" "}
                · <span className="pill">{row.status}</span>
              </p>
              <p>
                {row.from_amount} {row.from_currency} → {row.to_amount}{" "}
                {row.to_currency}
              </p>
              <p className="muted">
                Tasa {row.rate} · Comisión {row.fee} {row.from_currency}
              </p>
              {row.status === "pending" ? (
                <ActionForm
                  action="swap_review"
                  csrf={csrf}
                  initial={{ swap_id: row.id }}
                  label="Guardar decisión"
                >
                  <label>
                    Decisión
                    <select name="decision">
                      <option value="approved">Aprobar y ejecutar</option>
                      <option value="rejected">Rechazar</option>
                    </select>
                  </label>
                  <Note name="staff_note" value={row.staff_note || ""} />
                </ActionForm>
              ) : (
                <p className="muted">Nota: {row.staff_note || "Sin nota"}</p>
              )}
            </article>
          ))}
        </div>
        <Pager data={data} section={section} search={searchParams} />
      </>
    );
  } else if (section === "stake-positions") {
    const data = await get("stake-positions?" + query);
    content = (
      <>
        <p>
          La inversión se descuenta únicamente cuando la oficina aprueba la
          solicitud.
        </p>
        <div className="grid">
          {data.items.map((row: Row) => (
            <article className="card" key={row.id}>
              <h2>
                CDT #{row.id} · Plan #{row.plan_id}
              </h2>
              <p>
                <Link href={"/user/" + row.user_id}>
                  Cliente #{row.user_id}
                </Link>{" "}
                · <span className="pill">{row.status}</span>
              </p>
              <p className="money">{row.amount}</p>
              {row.status === "pending" ? (
                <ActionForm
                  action="stake_review"
                  csrf={csrf}
                  initial={{ position_id: row.id }}
                  label="Guardar decisión"
                >
                  <label>
                    Decisión
                    <select name="decision">
                      <option value="approved">Aprobar y bloquear saldo</option>
                      <option value="rejected">Rechazar</option>
                    </select>
                  </label>
                  <Note name="staff_note" value={row.staff_note || ""} />
                </ActionForm>
              ) : (
                <p className="muted">Nota: {row.staff_note || "Sin nota"}</p>
              )}
            </article>
          ))}
        </div>
        <Pager data={data} section={section} search={searchParams} />
      </>
    );
  } else if (section === "kyc") {
    const data = await get("kyc/queue?" + query);
    content = (
      <>
        <p>
          Revisión por documento. Para consultar documentos rechazados, abre el
          perfil del usuario.
        </p>
        <div className="grid">
          {data.items.map((doc: Row) => (
            <ReviewDocument key={doc.id} doc={doc} csrf={csrf} />
          ))}
        </div>
        {!data.items.length && (
          <div className="empty">No hay documentos pendientes.</div>
        )}
        <Pager data={data} section={section} search={searchParams} />
      </>
    );
  } else if (section === "credit") {
    content = (
      <section className="card narrow">
        <h2>Ajuste manual de saldo</h2>
        <p>
          Se registra un asiento compensado con tesorería y una nota de
          auditoría.
        </p>
        <ActionForm action="credit" csrf={csrf} label="Registrar ajuste">
          <label>
            Usuario (ID, correo o referido)
            <input name="user" required />
          </label>
          <Currency />
          <label>
            Red
            <input name="network" defaultValue="DEMO" required />
          </label>
          <label>
            Importe
            <input
              name="amount"
              type="number"
              step="0.00000001"
              min="0.00000001"
              required
            />
          </label>
          <label>
            Operación
            <select name="operation">
              <option value="credit">Crédito</option>
              <option value="debit">Débito</option>
            </select>
          </label>
          <Note />
        </ActionForm>
      </section>
    );
  } else if (section === "deposit-wallets") {
    const data = await get("deposit-wallets");
    content = (
      <>
        <section className="card narrow">
          <h2>Nueva wallet</h2>
          <WalletForm csrf={csrf} />
        </section>
        <div className="grid">
          {data.items.map((row: Row) => (
            <article className="card" key={row.id}>
              <h2>
                {row.label} · #{row.id}
              </h2>
              <WalletForm row={row} csrf={csrf} />
              {row.is_active && (
                <ActionForm
                  action="deposit_wallet_delete"
                  csrf={csrf}
                  initial={{ wallet_id: row.id }}
                  label="Desactivar wallet"
                >
                  <p>
                    Se conserva el registro y se retira del listado de wallets
                    activas.
                  </p>
                </ActionForm>
              )}
            </article>
          ))}
        </div>
      </>
    );
  } else if (section === "notifications") {
    const data = await get("notifications?" + query);
    content = (
      <>
        <section className="card narrow">
          <h2>Enviar notificación interna</h2>
          <ActionForm
            action="send_notification"
            csrf={csrf}
            label="Enviar a destinatarios del ámbito"
          >
            <label>
              Destinatarios
              <select name="scope">
                <option value="one">Un cliente</option>
                <option value="office">Mi oficina</option>
                <option value="all">Todos en mi ámbito</option>
              </select>
            </label>
            <label>
              ID cliente (para un destinatario)
              <input name="user_id" type="number" min="1" />
            </label>
            <label>
              Filtro KYC
              <select name="kyc_filter">
                <option value="">Todos los estados</option>
                {["none", "pending", "verified", "rejected"].map((v) => (
                  <option key={v}>{v}</option>
                ))}
              </select>
            </label>
            <label>
              Título
              <input name="title" maxLength={200} required />
            </label>
            <label>
              Tipo
              <select name="type">
                {["info", "success", "warning"].map((v) => (
                  <option key={v}>{v}</option>
                ))}
              </select>
            </label>
            <label>
              Mensaje
              <textarea name="body" maxLength={5000} required />
            </label>
          </ActionForm>
        </section>
        <section className="card">
          <h2>Envíos recientes</h2>
          <Table
            rows={data.items}
            columns={[
              ["user_id", "Cliente"],
              ["title", "Título"],
              ["type", "Tipo"],
              ["scope", "Ámbito"],
              ["created_at", "Fecha"],
            ]}
          />
          <Pager data={data} section={section} search={searchParams} />
        </section>
      </>
    );
  } else if (section === "offices") {
    const [data, me] = await Promise.all([
      get("offices"),
      adminGet("/api/auth/me", returnTo),
    ]);
    content = (
      <>
        {me.role === "superworker" && (
          <div className="grid">
            <section className="card">
              <h2>Crear oficina</h2>
              <ActionForm
                action="office_create"
                csrf={csrf}
                label="Crear oficina"
              >
                <label>
                  Nombre
                  <input name="name" minLength={2} required />
                </label>
              </ActionForm>
            </section>
            <section className="card">
              <h2>Crear Admin Oficina</h2>
              <ActionForm
                action="office_admin_create"
                csrf={csrf}
                label="Crear administrador"
              >
                <label>
                  Oficina
                  <select name="office_id">
                    {data.items.map((o: Row) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Nombre
                  <input name="full_name" required />
                </label>
                <label>
                  Correo
                  <input name="email" type="email" required />
                </label>
                <label>
                  Contraseña temporal
                  <input
                    name="password"
                    type="password"
                    minLength={12}
                    required
                  />
                </label>
              </ActionForm>
            </section>
          </div>
        )}
        <div className="grid">
          {data.items.map((office: Row) => (
            <section className="card" key={office.id}>
              <h2>{office.name}</h2>
              <p>
                Código vigente: <code>{office.registration_code}</code>
              </p>
              <ActionForm
                action="office_features"
                csrf={csrf}
                initial={{ office_id: office.id }}
                label="Guardar permisos"
              >
                <label>
                  Trading
                  <select
                    name="trading_enabled"
                    defaultValue={String(office.trading_enabled)}
                  >
                    <option value="true">Habilitado</option>
                    <option value="false">Deshabilitado</option>
                  </select>
                </label>
                <label>
                  Swap
                  <select
                    name="swap_enabled"
                    defaultValue={String(office.swap_enabled)}
                  >
                    <option value="true">Habilitado</option>
                    <option value="false">Deshabilitado</option>
                  </select>
                </label>
                <label>
                  Retiros
                  <select
                    name="withdrawals_enabled"
                    defaultValue={String(office.withdrawals_enabled)}
                  >
                    <option value="true">Habilitado</option>
                    <option value="false">Deshabilitado</option>
                  </select>
                </label>
              </ActionForm>
              {me.role === "superworker" && (
                <ActionForm
                  action="office_delete"
                  csrf={csrf}
                  initial={{ office_id: office.id }}
                  label="Eliminar oficina"
                >
                  <p className="muted">
                    Sólo se elimina si no tiene usuarios asignados.
                  </p>
                </ActionForm>
              )}
            </section>
          ))}
        </div>
      </>
    );
  } else if (section === "users") {
    const data = await get("users?" + query);
    content = (
      <>
        <form className="filters" action="/admin/users">
          <label>
            Buscar
            <input
              name="q"
              defaultValue={searchParams.q}
              placeholder="Nombre, correo o teléfono"
            />
          </label>
          <label>
            KYC
            <select name="kyc" defaultValue={searchParams.kyc || ""}>
              <option value="">Todos</option>
              {["none", "pending", "verified", "rejected"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label>
            País
            <input name="country" defaultValue={searchParams.country} />
          </label>
          <label>
            Activo
            <select name="active" defaultValue={searchParams.active || ""}>
              <option value="">Todos</option>
              <option value="true">Sí</option>
              <option value="false">No</option>
            </select>
          </label>
          <button>Buscar</button>
        </form>
        <section className="card">
          <Table
            rows={data.items}
            columns={[
              ["id", "ID"],
              ["full_name", "Nombre"],
              ["email", "Correo"],
              ["country", "País"],
              ["role", "Rol"],
              ["office_id", "Oficina"],
              ["kyc_status", "KYC"],
              ["is_active", "Activo"],
              ["created_at", "Registro"],
            ]}
          />
          <Pager data={data} section={section} search={searchParams} />
        </section>
      </>
    );
  } else if (section === "dashboard" || section === "production") {
    const productionQuery = new URLSearchParams();
    for (const name of ["from", "to"])
      if (searchParams[name]) productionQuery.set(name, searchParams[name]!);
    const data = await get("production?" + productionQuery);
    if (section === "dashboard") {
      const [me, offices, wallets, users, payments, swaps, stakes] = await Promise.all([
        adminGet('/api/auth/me', returnTo), get('offices'), get('deposit-wallets'),
        get("users?page_size=8"), get("payments?page_size=6"), get("swaps?page_size=6"), get("stake-positions?page_size=1"),
      ]);
      const ownOffice = offices.items.find((office: Row) => office.id === me.office_id);
      const registrationOffices = me.role === 'superworker'
        ? offices.items.filter((office: Row) => office.is_active)
        : ownOffice?.is_active ? [ownOffice] : [];
      const total = (amounts: Row) => Object.values(amounts).reduce((sum: number, value) => sum + Number(value || 0), 0);
      const dashboardMetrics: [string, string, string | number][] = [
        ["Usuarios", "users", data.users_new], ["Pagos pendientes", "payments", data.pending_payments],
        ["KYC pendientes", "kyc", data.pending_kyc], ["Tickets abiertos", "tickets", data.tickets_open],
        ["Swaps", "swaps", data.swaps_count], ["Depósitos", "payments", total(data.deposits_by_currency).toLocaleString('es-CO', {maximumFractionDigits: 2})],
        ["Retiros", "payments", total(data.withdrawals_by_currency).toLocaleString('es-CO', {maximumFractionDigits: 2})],
        ["CDT solicitados", "stake-positions", stakes.total ?? 0],
      ];
      content = <>
        <section className="admin-hero"><span className="admin-hero-kicker">◈ Panel de control</span><h1>Resumen de tu oficina</h1><p>Vista general de usuarios, pagos y actividad de Global Efecty.</p><div className="admin-hero-chips"><span>● En vivo</span><span>{data.users_new} usuarios registrados</span><span>{data.pending_payments} pagos pendientes</span></div><div className="admin-hero-actions"><Link href="/credit">Agregar fondos</Link><Link href="/users">Buscar usuarios</Link></div></section>
        <div className="admin-banner-grid">
          {registrationOffices.length ? registrationOffices.map((office: Row) =>
            <section className="admin-banner-card" key={office.id}>
              <span className="admin-banner-icon"><AdminIcon name="offices"/></span>
              <div><small>CÓDIGO DE REGISTRO DE HOY · {office.name}</small><strong>{office.registration_code}</strong><p>3 letras y 3 números. Se renueva a las 00:00, hora de Colombia.</p></div>
              <RegistrationCode code={office.registration_code}/>
            </section>
          ) : <section className="admin-banner-card"><span className="admin-banner-icon"><AdminIcon name="offices"/></span><div><small>CÓDIGO DE REGISTRO</small><strong>Sin oficina activa</strong><p>Crea una oficina para obtener un código.</p></div><Link href="/offices">Gestionar →</Link></section>}
          <section className="admin-banner-card"><span className="admin-banner-icon"><AdminIcon name="deposit-wallets"/></span><div><small>WALLETS DE DEPÓSITO</small><strong>{wallets.items.filter((wallet: Row) => wallet.is_active).length} activas</strong><p>Direcciones disponibles para recibir depósitos.</p></div><Link href="/deposit-wallets">Gestionar →</Link></section>
        </div>
        <div className="admin-metric-grid">{dashboardMetrics.map(([label, route, value]) => <Link href={'/' + route} className="card admin-metric" key={label}><span className="admin-metric-icon"><AdminIcon name={route} size={19}/></span><span>{label}</span><strong>{String(value ?? 0)}</strong><small>Ver detalles →</small></Link>)}</div>
        <div className="admin-dashboard-grid">
          <section className="card"><h2>Últimos registros</h2><div className="admin-record-list">{users.items.length ? users.items.map((user: Row) => <Link href={'/user/' + user.id} key={user.id} className="admin-record"><span className="admin-record-icon"><AdminIcon name="users"/></span><span><strong>{user.full_name}</strong><small>{user.email}</small></span><span className="admin-record-status">{user.kyc_status || 'Sin enviar'}</span></Link>) : <div className="empty">Aún no hay clientes en esta oficina.</div>}</div><Link className="section-more" href="/users">Ver todos →</Link></section>
          <section className="card"><h2>Solicitudes de pago</h2><div className="admin-record-list">{payments.items.length ? payments.items.map((payment: Row) => <Link href="/payments" key={payment.id} className="admin-record"><span className="admin-record-icon"><AdminIcon name="payments"/></span><span><strong>Solicitud #{payment.id}</strong><small>{payment.currency} · {payment.type || 'Pago'}</small></span><span className="admin-record-status">{payment.status}</span></Link>) : <div className="empty">No hay solicitudes.</div>}</div><Link className="section-more" href="/payments">Atender pagos →</Link></section>
          <section className="card"><h2>Swaps recientes</h2><div className="admin-record-list">{swaps.items.length ? swaps.items.map((swap: Row) => <Link href="/swaps" key={swap.id} className="admin-record"><span className="admin-record-icon"><AdminIcon name="swaps"/></span><span><strong>{swap.from_currency} → {swap.to_currency}</strong><small>Solicitud #{swap.id}</small></span><span className="admin-record-status">{swap.status}</span></Link>) : <div className="empty">No hay intercambios recientes.</div>}</div></section>
          <section className="card"><h2>Actividad por moneda</h2>{[["Depósitos", data.deposits_by_currency], ["Retiros", data.withdrawals_by_currency], ["Swaps", data.swap_volume_by_currency]].map(([label, totals]) => <div className="admin-activity-row" key={label as string}><span>{label as string}</span><strong>{Object.keys(totals as Row).length ? Object.entries(totals as Row).map(([currency, amount]) => `${amount} ${currency}`).join(' · ') : 'Sin movimientos'}</strong></div>)}</section>
        </div>
        <section className="card"><h2>Accesos rápidos</h2><div className="admin-shortcuts">{[["users", "Usuarios"], ["credit", "Agregar fondos"], ["payments", "Pagos"], ["kyc", "KYC"], ["chats", "Chat en vivo"], ["tickets", "Tickets"], ["stake-plans", "Planes stake"]].map(([route, label]) => <Link href={'/' + route} key={route}><AdminIcon name={route}/>{label}</Link>)}</div></section>
      </>;
    } else {
    content = (
      <>
        {section === "production" && (
          <form className="filters" action="/admin/production">
            <label>
              Desde (UTC)
              <input
                type="datetime-local"
                name="from"
                defaultValue={searchParams.from}
              />
            </label>
            <label>
              Hasta (UTC)
              <input
                type="datetime-local"
                name="to"
                defaultValue={searchParams.to}
              />
            </label>
            <button>Actualizar métricas</button>
          </form>
        )}
        {metrics(data)}
        <div className="grid">
          {[
            ["deposits_by_currency", "Depósitos"],
            ["withdrawals_by_currency", "Retiros liquidados"],
            ["swap_volume_by_currency", "Volumen de swaps"],
          ].map(([key, label]) => (
            <section className="card" key={key}>
              <h2>{label}</h2>
              {Object.entries(data[key]).length ? (
                Object.entries(data[key]).map(([currency, value]) => (
                  <p className="money" key={currency}>
                    {String(value)} {currency}
                  </p>
                ))
              ) : (
                <p className="muted">Sin movimientos en este período.</p>
              )}
            </section>
          ))}
        </div>
      </>
    );
    }
  } else if (section === "help") {
    content = (
      <div className="grid">
        {[
          [
            "¿Cómo revisar un retiro?",
            "En Pagos revisa el monto exacto bloqueado. Aprobar liquida escrow a tesorería; rechazar devuelve a main.",
          ],
          [
            "¿Qué significa reabrir?",
            "Sólo cambia la cola a pendiente. No mueve saldos ni revierte una liquidación. Una decisión incompatible con lo ya liquidado se bloquea.",
          ],
          [
            "¿Cómo corregir un saldo?",
            "Abre un usuario y utiliza el ID del asiento de su cuenta principal. El importe corregido añade un asiento; el historial nunca se edita.",
          ],
          [
            "¿Por qué no veo un cliente?",
            "Staff sólo ve clientes de su oficina. Superworker tiene alcance global.",
          ],
          [
            "¿Qué ocurre al reintentar?",
            "El formulario conserva su clave mientras no cambies los campos. Reintentar no duplica el efecto. Nueva operación inicia una intención distinta.",
          ],
        ].map(([title, body]) => (
          <article className="card" key={title}>
            <h2>{title}</h2>
            <p>{body}</p>
          </article>
        ))}
      </div>
    );
  } else if (section === "chats" || section === "tickets") {
    const data = await get("tickets?" + query);
    let messages: Row[] = [];
    const selected = searchParams.ticket;
    if (selected && /^\d+$/.test(selected))
      messages = (await get("tickets/" + selected + "/messages")).items;
    const visible =
      section === "chats"
        ? data.items.filter((t: Row) => t.subject === "Chat en vivo")
        : data.items.filter((t: Row) => t.subject !== "Chat en vivo");
    content = (
      <>
        <section className="card">
          <Table
            rows={visible}
            columns={[
              ["id", "Ticket"],
              ["user_id", "Cliente"],
              ["subject", "Asunto"],
              ["status", "Estado"],
            ]}
          />
          <div className="quick-links">
            {visible.map((t: Row) => (
              <Link key={t.id} href={"/" + section + "?ticket=" + t.id}>
                Abrir conversación #{t.id}
              </Link>
            ))}
          </div>
          <Pager data={data} section={section} search={searchParams} />
        </section>
        {selected && (
          <section className="card">
            <h2>Mensajes #{selected}</h2>
            {messages.length ? (
              messages.map((m) => (
                <article key={m.id} className="message">
                  <strong>Usuario #{m.sender_id}</strong>
                  <p>{m.body}</p>
                  <small>{m.created_at}</small>
                </article>
              ))
            ) : (
              <div className="empty">
                Esta conversación aún no tiene mensajes.
              </div>
            )}
            <ActionForm
              action="ticket_reply"
              csrf={csrf}
              initial={{ ticket_id: Number(selected) }}
              label="Enviar respuesta"
            >
              <label>
                Respuesta
                <textarea name="body" maxLength={5000} required />
              </label>
            </ActionForm>
          </section>
        )}
      </>
    );
  } else {
    const endpoints: Record<string, string> = {
      cards: "cards",
      "payment-methods": "payment-methods",
      "stake-plans": "stake-plans",
      ranking: "ranking",
    };
    const data = await get(endpoints[section] + "?" + query);
    const columns: Record<string, [string, string][]> = {
      cards: [["id", "ID"]],
      "payment-methods": [
        ["id", "ID"],
        ["user_id", "Cliente"],
        ["type", "Tipo"],
        ["label", "Alias"],
        ["holder_name", "Titular"],
        ["bank_country", "País"],
        ["bank_id", "ID banco"],
        ["bank_name", "Banco"],
        ["account_last4", "Cuenta · últimos 4"],
        ["card_brand", "Marca"],
        ["card_last4", "Tarjeta · últimos 4"],
        ["network", "Red"],
        ["wallet_address", "Wallet"],
        ["is_active", "Activo"],
      ],
      "stake-plans": [
        ["id", "ID"],
        ["currency", "Moneda"],
        ["apy", "APY"],
        ["min_amount", "Mínimo"],
        ["term_days", "Días"],
        ["is_active", "Activo"],
      ],
      ranking: [
        ["user_id", "Cliente"],
        ["full_name", "Nombre"],
        ["virtual_usdt_balance", "Saldo USDT"],
      ],
    };
    content = (
      <section className="card">
        <p className="muted">
          {section === "ranking"
            ? "Ordenado por saldo USDT del ámbito del equipo."
            : "Vista de sólo lectura."}
        </p>
        <Table rows={data.items} columns={columns[section]} />
        {data.total !== undefined && (
          <Pager data={data} section={section} search={searchParams} />
        )}
      </section>
    );
  }
  return (
    <>
      {section !== "dashboard" && <div className={section === "users" ? "page-heading" : "section-hero"}><span className="section-hero-icon"><AdminIcon name={section} size={25}/></span><div><h1>{titles[section]}</h1><p>{descriptions[section] || "Administra esta sección de la plataforma."}</p></div></div>}
      {content}
    </>
  );
}
