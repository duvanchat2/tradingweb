'use client';

import ClientActionForm from './ClientActionForm';
import { PanelIcon } from './PanelIcons';

type Message = { id:number; sender_id:number; body:string; created_at:string };

export default function LiveChat({csrf, messages, userId}:{csrf:string;messages:Message[];userId:number}) {
  return <section className="live-chat-card">
    <header><div><h2><PanelIcon name="chat"/> Chat en vivo</h2><p>Habla en tiempo real con el equipo de tu oficina. Esto no crea un ticket de soporte.</p></div><span><b>EN ESPERA</b> <i/> Esperando agente de servicio al cliente</span></header>
    <div className="chat-messages" aria-live="polite">
      {messages.length ? messages.map(message=><article className={message.sender_id===userId?'mine':'staff'} key={message.id}><p>{message.body}</p><small>{new Date(message.created_at).toLocaleString('es-CO')}</small></article>) : <div className="chat-welcome"><PanelIcon name="chat"/><p>Chat iniciado. Un asesor de tu oficina te atenderá por este medio.</p></div>}
    </div>
    <ClientActionForm action="chat_message" csrf={csrf} label="Enviar mensaje"><label className="sr-only">Mensaje</label><textarea name="body" placeholder="Escribe tu mensaje..." required maxLength={5000}/><small>Puedes escribir tu consulta; los mensajes llegan al panel de administración.</small></ClientActionForm>
  </section>;
}
