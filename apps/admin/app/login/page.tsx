import LoginForm from '../../components/LoginForm';
export const dynamic='force-dynamic';
export default function Login({searchParams}:{searchParams:{error?:string}}){
 const errors:Record<string,string>={invalid:'Correo o contraseña incorrectos.',staff:'Este acceso requiere un usuario staff o superworker.',unavailable:'El servicio no está disponible. Intenta de nuevo.'};
 return <main className="login"><div className="card"><span className="pill">GLOBAL EFECTY</span><h1>Acceso del equipo</h1><p>Accede al panel del equipo.</p>{searchParams.error&&<p role="alert" className="notice error">{errors[searchParams.error]||'No se pudo iniciar sesión.'}</p>}<LoginForm/></div></main>;
}
