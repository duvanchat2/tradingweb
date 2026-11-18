(() => {
  const translations = {
    en: {
      'Funciones':'Features','Activos':'Assets','Staking':'Staking','Seguridad':'Security','Preguntas':'FAQ',
      'Iniciar sesión':'Sign in','Abrir wallet':'Open wallet','Entrar':'Enter','Español':'Spanish','Português':'Portuguese',
      'PLATAFORMA CRIPTO GLOBAL · SEGURA':'GLOBAL CRYPTO PLATFORM · SECURE','Opera, ahorra':'Trade, save','y envía cripto':'and send crypto','con claridad total':'with total clarity',
      'Wallet unificada para swap, CDT y transferencias. Experiencia clara, comisiones desde 0.1% y control desde tu oficina digital.':'Unified wallet for swaps, fixed-term crypto and transfers. Clear experience, fees from 0.1% and control from your digital office.',
      'Crear cuenta gratis':'Create free account','KYC verificado':'Verified KYC','Cifrado E2E':'E2E encryption','Swap ágil':'Fast swaps','CDT cripto':'Crypto term deposit','Soporte 24/7':'24/7 support',
      'BALANCE TOTAL':'TOTAL BALANCE','esta semana':'this week','Wallet asegurada · Verificada':'Secured wallet · Verified','EN VIVO':'LIVE',
      'Usuarios activos':'Active users','Volumen mensual':'Monthly volume','Países':'Countries','Comisión swap':'Swap fee',
      'FUNCIONES PRINCIPALES':'MAIN FEATURES','Todo lo que necesitas':'Everything you need','en una wallet':'in one wallet','Diseñada para Latinoamérica y el mundo. Simple para empezar, potente para':'Designed for Latin America and the world. Simple to start, powerful enough to','operar día a día.':'use every day.',
      'Wallet multi-cripto':'Multi-crypto wallet','Gestiona las principales criptomonedas desde un panel unificado, con saldos y precios en tiempo real.':'Manage leading cryptocurrencies from one unified dashboard with real-time balances and prices.',
      'Swap instantáneo':'Instant swap','Intercambia criptos a tasa de mercado con comisión transparente del 0.1%.':'Exchange crypto at market rates with a transparent 0.1% fee.',
      'Bloquea fondos por un plazo y recibe rendimiento en porcentaje, como un ahorro digital.':'Lock funds for a term and earn a percentage yield, like digital savings.',
      'Seguridad de nivel bancario':'Bank-grade security','Verificación KYC, cifrado de sesiones, monitoreo de IP y rate-limiting anti brute-force.':'KYC verification, encrypted sessions, IP monitoring and anti-brute-force rate limiting.',
      'Transfer Int.':'International transfers','Métodos bancarios internacionales con flujo claro por país y banco.':'International banking methods with a clear flow by country and bank.','Soporte humano':'Human support','Tickets internos y respuesta con seguimiento de tu oficina.':'Internal tickets and tracked responses from your office.',
      'MERCADO':'MARKET','Precios claros para':'Clear prices to','decidir con confianza':'decide with confidence','Cotizaciones en vivo · actualizadas con frecuencia':'Live quotes · frequently updated','Activo':'Asset','Precio':'Price','Comprar':'Buy',
      'EMPIEZA EN 3 PASOS':'START IN 3 STEPS','Tu primera operación':'Your first trade','en menos de 5 minutos':'in under 5 minutes','Crea tu cuenta':'Create your account','Deposita o compra':'Deposit or buy','Opera y gana':'Trade and earn',
      'CDT / STAKING':'TERM DEPOSIT / STAKING','Pon tus criptos a':'Put your crypto to','trabajar para ti':'work for you','Hacer stake':'Start staking','APY ANUAL':'ANNUAL APY',
      'Tu dinero,':'Your money,','protegido como':'protected as it','debe ser':'should be','Acceso seguro':'Secure access','KYC verificado':'Verified KYC','Cifrado y rate-limiting':'Encryption and rate limiting','Monitoreo de IP':'IP monitoring','Auditoría de plataforma':'Platform audit',
      'AYUDA':'HELP','Preguntas frecuentes':'Frequently asked questions','Empieza a operar':'Start trading','en minutos':'in minutes','Únete a más de 48,000 usuarios que ya manejan sus criptos con Global Efecty.':'Join more than 48,000 users already managing their crypto with Global Efecty.','Ya tengo cuenta':'I already have an account',
      'Wallet cripto global. Clara, segura y lista para':'Global crypto wallet. Clear, secure and ready to','operar desde cualquier lugar.':'use from anywhere.','Abrir cuenta':'Open account','PRODUCTO':'PRODUCT','Wallet':'Wallet','Mercado':'Market','PLATAFORMA':'PLATFORM','Cómo empezar':'Getting started','Crear cuenta':'Create account','COMPAÑÍA':'COMPANY','Soporte':'Support','Contacto':'Contact','Términos':'Terms','Privacidad':'Privacy','Fee de swap':'Swap fee','Soporte humano':'Human support','Custodia y seguridad':'Custody and security','Precios en vivo':'Live prices','Operación global':'Global operation','Todos los derechos reservados.':'All rights reserved.','Las criptomonedas son activos volátiles. Invierte solo lo que estés dispuesto a perder.':'Cryptocurrencies are volatile assets. Only invest what you are willing to lose.',
      'Conectando con el mercado…':'Connecting to the market…','Última referencia disponible · actualización temporalmente no disponible':'Last available reference · update temporarily unavailable','Datos de mercado actualizados · fuente pública':'Market data updated · public source'
    },
    pt: {
      'Funciones':'Funções','Activos':'Ativos','Staking':'Staking','Seguridad':'Segurança','Preguntas':'FAQ',
      'Iniciar sesión':'Iniciar sessão','Abrir wallet':'Abrir wallet','Entrar':'Entrar','Español':'Espanhol','English':'Inglês',
      'PLATAFORMA CRIPTO GLOBAL · SEGURA':'PLATAFORMA CRIPTO GLOBAL · SEGURA','Opera, ahorra':'Opere, economize','y envía cripto':'e envie cripto','con claridad total':'com total clareza',
      'Wallet unificada para swap, CDT y transferencias. Experiencia clara, comisiones desde 0.1% y control desde tu oficina digital.':'Wallet unificada para swap, investimento a prazo e transferências. Experiência clara, taxas a partir de 0,1% e controle pelo seu escritório digital.',
      'Crear cuenta gratis':'Criar conta grátis','KYC verificado':'KYC verificado','Cifrado E2E':'Criptografia E2E','Swap ágil':'Swap rápido','CDT cripto':'Investimento cripto','Soporte 24/7':'Suporte 24/7',
      'BALANCE TOTAL':'SALDO TOTAL','esta semana':'esta semana','Wallet asegurada · Verificada':'Wallet segura · Verificada','EN VIVO':'AO VIVO',
      'Usuarios activos':'Usuários ativos','Volumen mensual':'Volume mensal','Países':'Países','Comisión swap':'Taxa de swap',
      'FUNCIONES PRINCIPALES':'FUNÇÕES PRINCIPAIS','Todo lo que necesitas':'Tudo o que você precisa','en una wallet':'em uma wallet','Diseñada para Latinoamérica y el mundo. Simple para empezar, potente para':'Criada para a América Latina e o mundo. Simples para começar, poderosa para','operar día a día.':'operar todos os dias.',
      'Wallet multi-cripto':'Wallet multcripto','Gestiona las principales criptomonedas desde un panel unificado, con saldos y precios en tiempo real.':'Gerencie as principais criptomoedas em um painel unificado, com saldos e preços em tempo real.',
      'Swap instantáneo':'Swap instantâneo','Intercambia criptos a tasa de mercado con comisión transparente del 0.1%.':'Troque criptos à taxa de mercado com comissão transparente de 0,1%.',
      'Bloquea fondos por un plazo y recibe rendimiento en porcentaje, como un ahorro digital.':'Bloqueie fundos por um prazo e receba rendimento percentual, como uma poupança digital.',
      'Seguridad de nivel bancario':'Segurança de nível bancário','Verificación KYC, cifrado de sesiones, monitoreo de IP y rate-limiting anti brute-force.':'Verificação KYC, sessões criptografadas, monitoramento de IP e limitação contra força bruta.',
      'Transfer Int.':'Transferência internacional','Métodos bancarios internacionales con flujo claro por país y banco.':'Métodos bancários internacionais com fluxo claro por país e banco.','Soporte humano':'Suporte humano','Tickets internos y respuesta con seguimiento de tu oficina.':'Tickets internos e respostas acompanhadas pelo seu escritório.',
      'MERCADO':'MERCADO','Precios claros para':'Preços claros para','decidir con confianza':'decidir com confiança','Cotizaciones en vivo · actualizadas con frecuencia':'Cotações ao vivo · atualizadas frequentemente','Activo':'Ativo','Precio':'Preço','Comprar':'Comprar',
      'EMPIEZA EN 3 PASOS':'COMECE EM 3 PASSOS','Tu primera operación':'Sua primeira operação','en menos de 5 minutos':'em menos de 5 minutos','Crea tu cuenta':'Crie sua conta','Deposita o compra':'Deposite ou compre','Opera y gana':'Opere e ganhe',
      'CDT / STAKING':'RENDA / STAKING','Pon tus criptos a':'Coloque suas criptos para','trabajar para ti':'trabalhar para você','Hacer stake':'Fazer staking','APY ANUAL':'APY ANUAL',
      'Tu dinero,':'Seu dinheiro,','protegido como':'protegido como','debe ser':'deve ser','Acceso seguro':'Acesso seguro','KYC verificado':'KYC verificado','Cifrado y rate-limiting':'Criptografia e rate limiting','Monitoreo de IP':'Monitoramento de IP','Auditoría de plataforma':'Auditoria da plataforma',
      'AYUDA':'AJUDA','Preguntas frecuentes':'Perguntas frequentes','Empieza a operar':'Comece a operar','en minutos':'em minutos','Únete a más de 48,000 usuarios que ya manejan sus criptos con Global Efecty.':'Junte-se a mais de 48.000 usuários que já administram suas criptos com a Global Efecty.','Ya tengo cuenta':'Já tenho uma conta',
      'Wallet cripto global. Clara, segura y lista para':'Wallet cripto global. Clara, segura e pronta para','operar desde cualquier lugar.':'operar de qualquer lugar.','Abrir cuenta':'Abrir conta','PRODUCTO':'PRODUTO','Wallet':'Wallet','Mercado':'Mercado','PLATAFORMA':'PLATAFORMA','Cómo empezar':'Como começar','Crear cuenta':'Criar conta','COMPAÑÍA':'EMPRESA','Soporte':'Suporte','Contacto':'Contato','Términos':'Termos','Privacidad':'Privacidade','Fee de swap':'Taxa de swap','Soporte humano':'Suporte humano','Custodia y seguridad':'Custódia e segurança','Precios en vivo':'Preços ao vivo','Operación global':'Operação global','Todos los derechos reservados.':'Todos os direitos reservados.','Las criptomonedas son activos volátiles. Invierte solo lo que estés dispuesto a perder.':'Criptomoedas são ativos voláteis. Invista apenas o que estiver disposto a perder.',
      'Conectando con el mercado…':'Conectando ao mercado…','Última referencia disponible · actualización temporalmente no disponible':'Última referência disponível · atualização temporariamente indisponível','Datos de mercado actualizados · fuente pública':'Dados de mercado atualizados · fonte pública'
    }
  };
  Object.assign(translations.en, {
    'una wallet':'one wallet','Cifrado AES–256':'AES–256 encryption','KYC en minutos':'KYC in minutes','Sesiones cifradas HTTPS':'Encrypted HTTPS sessions',
    'menos de 5 minutos':'under 5 minutes','Regístrate con email y país. Verifica tu identidad en minutos con el KYC integrado.':'Register with your email and country. Verify your identity in minutes with integrated KYC.','Recibe cripto en tu wallet o solicita un depósito a través de los métodos disponibles.':'Receive crypto in your wallet or request a deposit through the available methods.','Intercambia con un solo clic o haz staking para generar rendimientos pasivos.':'Swap with one click or stake to generate passive returns.','Rendimiento transparente · plazos claros · retiro al vencer':'Transparent returns · clear terms · withdraw at maturity',
    'Cumplimos con las mejores prácticas del sector cripto. Tu privacidad y la integridad de tus fondos son lo primero.':'We follow crypto industry best practices. Your privacy and the integrity of your funds come first.','Inicio de sesión protegido con cifrado HTTPS y control de intentos.':'Login protected with HTTPS encryption and attempt controls.','Documento de identidad y prueba de domicilio para cumplimiento AML.':'Identity document and proof of address for AML compliance.','Sesiones HTTPS-only, cookies Secure + HttpOnly, anti brute-force.':'HTTPS-only sessions, Secure + HttpOnly cookies and anti-brute-force protection.','Registramos cada login y notificamos accesos desde ubicaciones inusuales.':'We log every sign-in and notify you of access from unusual locations.','Código revisado, infraestructura monitoreada 24/7 y backups automáticos diarios.':'Reviewed code, infrastructure monitored 24/7 and automatic daily backups.','Diarios cifrados':'Encrypted daily','No vendemos data':'We do not sell data','Cumplimiento':'Compliance',
    '¿Global Efecty maneja fondos reales?':'Does Global Efecty handle real funds?','No. Esta versión es un entorno demo: sus saldos y operaciones son únicamente simulados.':'No. This version is a demo environment: balances and operations are simulated only.','¿Puedo crear una cuenta gratis?':'Can I create a free account?','Sí. El registro está disponible y las cuentas nuevas comienzan con todos sus saldos en cero.':'Yes. Registration is available and new accounts start with all balances at zero.','¿Qué puedo practicar?':'What can I practice?','Consulta de mercado, órdenes, swap, rendimientos, depósitos, retiros, notificaciones y soporte.':'Market quotes, orders, swaps, yields, deposits, withdrawals, notifications and support.','¿Dónde inicio sesión?':'Where do I sign in?','En el portal cliente ubicado en':'In the client portal at',
    '© 2026 Global Efecty. Todos los derechos reservados.':'© 2026 Global Efecty. All rights reserved.'
  });
  Object.assign(translations.pt, {
    'una wallet':'uma wallet','Cifrado AES–256':'Criptografia AES–256','KYC en minutos':'KYC em minutos','Sesiones cifradas HTTPS':'Sessões HTTPS criptografadas',
    'menos de 5 minutos':'em menos de 5 minutos','Regístrate con email y país. Verifica tu identidad en minutos con el KYC integrado.':'Cadastre-se com e-mail e país. Verifique sua identidade em minutos com o KYC integrado.','Recibe cripto en tu wallet o solicita un depósito a través de los métodos disponibles.':'Receba cripto na sua wallet ou solicite um depósito pelos métodos disponíveis.','Intercambia con un solo clic o haz staking para generar rendimientos pasivos.':'Troque com um clique ou faça staking para gerar rendimentos passivos.','Rendimiento transparente · plazos claros · retiro al vencer':'Rendimento transparente · prazos claros · saque no vencimento',
    'Cumplimos con las mejores prácticas del sector cripto. Tu privacidad y la integridad de tus fondos son lo primero.':'Seguimos as melhores práticas do setor cripto. Sua privacidade e a integridade dos seus fundos vêm primeiro.','Inicio de sesión protegido con cifrado HTTPS y control de intentos.':'Login protegido com criptografia HTTPS e controle de tentativas.','Documento de identidad y prueba de domicilio para cumplimiento AML.':'Documento de identidade e comprovante de endereço para conformidade AML.','Sesiones HTTPS-only, cookies Secure + HttpOnly, anti brute-force.':'Sessões somente HTTPS, cookies Secure + HttpOnly e proteção contra força bruta.','Registramos cada login y notificamos accesos desde ubicaciones inusuales.':'Registramos cada login e notificamos acessos de locais incomuns.','Código revisado, infraestructura monitoreada 24/7 y backups automáticos diarios.':'Código revisado, infraestrutura monitorada 24/7 e backups automáticos diários.','Diarios cifrados':'Diários criptografados','No vendemos data':'Não vendemos dados','Cumplimiento':'Conformidade',
    '¿Global Efecty maneja fondos reales?':'A Global Efecty utiliza fundos reais?','No. Esta versión es un entorno demo: sus saldos y operaciones son únicamente simulados.':'Não. Esta versão é um ambiente de demonstração: saldos e operações são apenas simulados.','¿Puedo crear una cuenta gratis?':'Posso criar uma conta grátis?','Sí. El registro está disponible y las cuentas nuevas comienzan con todos sus saldos en cero.':'Sim. O cadastro está disponível e novas contas começam com todos os saldos zerados.','¿Qué puedo practicar?':'O que posso praticar?','Consulta de mercado, órdenes, swap, rendimientos, depósitos, retiros, notificaciones y soporte.':'Cotações, ordens, swaps, rendimentos, depósitos, saques, notificações e suporte.','¿Dónde inicio sesión?':'Onde inicio a sessão?','En el portal cliente ubicado en':'No portal do cliente em',
    '© 2026 Global Efecty. Todos los derechos reservados.':'© 2026 Global Efecty. Todos os direitos reservados.'
  });
  const root = document.documentElement;
  const switcher = document.querySelector('#language-switcher');
  const toggle = switcher?.querySelector('.language-toggle');
  const menu = document.querySelector('#language-menu');
  const code = document.querySelector('#current-language-code');
  const originals = new WeakMap();
  let activeLanguage = 'es';

  function translateTextNode(node, language) {
    const current = node.nodeValue.trim();
    if (!current) return;
    if (!originals.has(node)) originals.set(node, current);
    const original = originals.get(node);
    let translated = language === 'es' ? original : translations[language]?.[original];
    if (!translated && language !== 'es') {
      const decorated = original.match(/^([^\p{L}\p{N}¿©]*)(.+)$/u);
      const translatedBody = decorated && translations[language]?.[decorated[2]];
      if (translatedBody) translated = decorated[1] + translatedBody;
    }
    if (!translated) return;
    node.nodeValue = node.nodeValue.replace(current, translated);
  }
  function applyLanguage(language) {
    activeLanguage = ['es','en','pt'].includes(language) ? language : 'es';
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) translateTextNode(node, activeLanguage);
    root.lang = activeLanguage;
    document.documentElement.lang = activeLanguage;
    code.textContent = activeLanguage.toUpperCase();
    menu.querySelectorAll('[data-language]').forEach((item) => item.setAttribute('aria-current', String(item.dataset.language === activeLanguage)));
    localStorage.setItem('landing-language', activeLanguage);
  }
  function closeMenu() {
    menu.hidden = true;
    toggle.setAttribute('aria-expanded', 'false');
  }
  toggle?.addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    toggle.setAttribute('aria-expanded', String(!menu.hidden));
  });
  menu?.addEventListener('click', (event) => {
    const item = event.target.closest('[data-language]');
    if (!item) return;
    applyLanguage(item.dataset.language);
    closeMenu();
  });
  document.addEventListener('click', (event) => { if (!switcher.contains(event.target)) closeMenu(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeMenu(); });
  const saved = localStorage.getItem('landing-language');
  const preferred = navigator.language?.toLowerCase().startsWith('pt') ? 'pt' : navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'es';
  applyLanguage(saved || preferred);
  new MutationObserver(() => applyLanguage(activeLanguage)).observe(document.querySelector('#market-state'), {childList:true, subtree:true});
})();
