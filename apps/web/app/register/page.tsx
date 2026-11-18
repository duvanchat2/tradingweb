import Link from 'next/link';
import RegisterForm from '../../components/RegisterForm';

export const dynamic = 'force-dynamic';

const errors: Record<string, string> = {
  exists: 'Este correo ya está registrado. Inicia sesión con tu cuenta.',
  password: 'Las contraseñas deben coincidir y tener entre 12 y 128 caracteres.',
  invalid: 'Revisa los datos ingresados e inténtalo de nuevo.',
  unavailable: 'No se pudo confirmar el registro. Intenta nuevamente; si tu cuenta ya se creó, podrás iniciar sesión.',
};

export default function Register({ searchParams }: { searchParams: { error?: string } }) {
  return <main className="register-shell">
    <section className="register-card">
      <div className="register-brand" aria-label="Global Efecty">
        <svg viewBox="0 0 64 48" role="img" aria-hidden="true">
          <path d="M12 35C18 7 46 6 52 35M11 35c13-18 29-18 42 0M32 5v38" />
          <circle cx="32" cy="5" r="4" /><circle cx="11" cy="35" r="4" /><circle cx="53" cy="35" r="4" />
        </svg>
        <strong>global efecty</strong>
      </div>
      <h1>Crea tu wallet</h1>
      <p className="register-lead">Empieza a operar con cripto en minutos.</p>
      {searchParams.error && <p className="notice error" role="alert">{errors[searchParams.error] || errors.invalid}</p>}
      <RegisterForm />
      <p className="auth-link">¿Ya tienes cuenta? <Link href="/login">Iniciar sesión</Link></p>
    </section>
  </main>;
}
