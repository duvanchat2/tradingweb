import Link from 'next/link';
import RegisterForm from '../../components/RegisterForm';
export const dynamic='force-dynamic';
const errors:Record<string,string>={exists:'Este correo ya está registrado. Inicia sesión con tu cuenta.',password:'Las contraseñas deben coincidir y tener entre 12 y 128 caracteres.',invalid:'Revisa tu nombre, correo y contraseña e inténtalo de nuevo.',unavailable:'No se pudo confirmar el registro. Intenta nuevamente; si tu cuenta ya se creó, podrás iniciar sesión.'};
export default function Register({searchParams}:{searchParams:{error?:string}}){
 return <main className="login-shell"><section className="login-card"><div className="brand"><span>GE</span><div><strong>Global Efecty</strong><small>Digital Asset Desk</small></div></div><p className="eyebrow">CREA TU CUENTA</p><h1>Tu cuenta, en un solo lugar</h1><p className="muted">Accede a tu portafolio y a las herramientas de trading.</p>{searchParams.error&&<p className="notice error" role="alert">{errors[searchParams.error]||errors.invalid}</p>}<RegisterForm/><p className="auth-link">¿Ya tienes cuenta? <Link href="/login">Iniciar sesión</Link></p></section></main>;
}
