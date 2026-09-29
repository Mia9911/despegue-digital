#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 BOT-CYCLE v3 — EL SEGUNDO JEFE DE VERDAD
Corre en GitHub Actions cada 10 minutos, PARA SIEMPRE:
  1. Atiende 1-a-1 a cada cliente (precios, muestra, cierre, links de cobro)
  2. LIBRETA DE PROSPECTOS: guarda TODO lo que escriba cada cliente en
     prospectos.json → El Económico lo lee solo cuando la Jefa escriba REVISION
     (la Jefa ya NO tiene que reenviar nada)
  3. ENTREGA AUTOMÁTICA del Kit $9: cliente dice "pagué" → recibe su kit YA
  4. ENTREGA DE MUESTRAS: cuando El Económico fabrica muestras y las pone en
     muestras.json, el guardián se las entrega al cliente SOLO
  5. Posts diarios en grupos (17-21h Cuba) + avisos a la Jefa
  6. CAZA-FINA LaborX: API publica cada hora -> trabajos NUEVOS a la Jefa
"""
import json
import re, os, base64, urllib.request
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GH = os.environ.get("GITHUB_TOKEN", "")
JEFA = int(os.environ.get("JEFA_CHAT_ID", "1227661387"))
CANAL_ID = int(os.environ.get("CANAL_CHAT_ID", "-1004446713229"))
API_T = "https://api.telegram.org/bot" + TOKEN + "/"
REPO = "https://api.github.com/repos/Mia9911/despegue-digital"
CUBA = timezone(timedelta(hours=-4))
KIT_URL = "https://mia9911.github.io/despegue-digital/kit-express.html"

def tg(method, params):
    req = urllib.request.Request(API_T + method, data=json.dumps(params).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def gh(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(REPO + path, data=data, method=method,
        headers={"Authorization": "Bearer " + GH,
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
        return json.loads(body) if body else {}

def gh_get_file(path):
    d = gh("GET", "/contents/" + path)
    return json.loads(base64.b64decode(d["content"]).decode()), d.get("sha")

def gh_put_file(path, obj, sha=None, msg="update"):
    payload = {"message": msg, "content": base64.b64encode(
        json.dumps(obj, ensure_ascii=False, indent=1).encode()).decode(), "branch": "main"}
    if sha:
        payload["sha"] = sha
    gh("PUT", "/contents/" + path, payload)

LINKS = {}
try:
    LINKS, _ = gh_get_file("links-de-pago.json")
except Exception:
    pass
VITRINA = LINKS.get("vitrina", "https://mia9911.github.io/despegue-digital/")

# ---------------- TEXTOS ----------------
TXT_START = (
    "🚀 ¡Bienvenido/a a DESPEGUE DIGITAL!\n"
    "Diseño y marketing que VENDEN, para negocios de Cuba y la diáspora.\n\n"
    "🎁 Kit Exprés Digital — $9 (entrega inmediata)\n"
    "⚡ Kit de Ventas Exprés — $125 (24 horas)\n"
    "🚀 Pack Resurrección IG + WhatsApp — $250 (24-48h) — el más pedido\n\n"
    "✅ Garantía: plazo incumplido = reembolso total.\n"
    "🛒 Tienda online: " + VITRINA + "\n\n"
    "Cuéntame: ¿cuál es tu negocio y qué vendes? 😊"
)
TXT_PRECIOS = (
    "💰 PRECIOS — DESPEGUE DIGITAL\n\n"
    "🎁 Kit Exprés Digital — $9 USD\n"
    "30 respuestas rápidas de WhatsApp + 10 fórmulas de bio + 7 plantillas de posts. "
    "Entrega inmediata al pagar.\n\n"
    "⚡ Kit de Ventas Exprés — $125 USD\n"
    "WhatsApp Business montado y listo + perfil en Google Maps + piezas de diseño + "
    "textos que venden. Entrega en 24 horas.\n\n"
    "🚀 Pack Resurrección IG + WhatsApp — $250 USD\n"
    "12 piezas de diseño + tu Instagram ordenado y profesional + WhatsApp Business "
    "completo + 30 respuestas rápidas. Entrega en 24-48 horas. EL MÁS PEDIDO.\n\n"
    "✅ Garantía: plazo incumplido = reembolso total.\n"
    "🛒 Tienda: " + VITRINA + "\n🎁 Muestra gratis: /muestra"
)
TXT_MUESTRA = (
    "🎁 ¡Vamos con tu MUESTRA GRATIS!\n"
    "Solo respóndeme esto:\n\n"
    "1️⃣ Nombre de tu negocio\n"
    "2️⃣ Qué vendes o ofreces\n"
    "3️⃣ Tu Instagram o WhatsApp\n\n"
    "En menos de 24 horas recibes 2 piezas diseñadas para TU negocio. "
    "Sin costo, sin compromiso, sin trucos."
)
TXT_GARANTIA = (
    "✅ GARANTÍA DESPEGUE DIGITAL\n\n"
    "Si incumplimos el plazo de entrega, te devolvemos el 100% de tu pago. "
    "Sin letra pequeña.\n\n"
    "Trabajamos con 50% de adelanto y 50% al entregar. "
    "Cada cliente recibe la fecha exacta de entrega por escrito."
)
TXT_SOPORTE = (
    "🛡️ DEPARTAMENTO DE SOPORTE\n\n"
    "Cuéntanos qué pasó: escribe aquí tu nombre, tu pedido y el problema. "
    "Respondemos en menos de 24 horas (normalmente en menos de 2).\n\n"
    "La Jefa revisa cada caso personalmente."
)
TXT_JEFA = (
    "👑 Línea de la Jefa — el imperio está de guardia.\n"
    "Todo lo que escriban los clientes queda grabado en la libreta y El Económico "
    "lo revisa cuando escribas REVISION en el chat de Arena.\n"
    "Para respuesta instantánea, escríbele allí. 🏰"
)
TXT_KIT_PAGADO = (
    "🎉 ¡Pago anotado! Aquí está tu KIT EXPRÉS DIGITAL, al instante:\n\n"
    + KIT_URL + "\n\n"
    "Ábrelo y guárdalo: 30 respuestas de WhatsApp + 10 bios + 7 plantillas, "
    "listas para copiar y pegar.\n"
    "Si tienes cualquier duda usando el kit, escríbeme aquí mismo.\n"
    "Bienvenido/a a DESPEGUE DIGITAL 🚀 (mi jefa confirma tu pago en minutos)\n\n"
    "🎁 Cuando lo pruebes, Califícanos: escribe /calificar y déjanos tus "
    "estrellas. Ayudas a crecer a un negocio cubano ⭐"
)
TXT_CALIFICAR = (
    "⭐ ¡Gracias por querer calificarnos!\n\n"
    "Escríbenos en un solo mensaje:\n"
    "1️⃣ Tus estrellas (1 a 5)\n"
    "2️⃣ Tu opinión sobre lo que compraste\n"
    "3️⃣ Tu nombre y tu negocio (como quieres que aparezca)\n\n"
    "Ejemplo: \"⭐⭐⭐⭐⭐ Me encantó el kit, lo uso todos los días. "
    "— Yanet, Dulcería Yanet de Camagüey\"\n\n"
    "Con tu permiso, tu reseña se publica en nuestra tienda 🛒"
)

def txt_cierre():
    r = ("🔥 ¡Excelente! Así reservamos tu cupo:\n\n"
         "1️⃣ Eliges: Kit $9 · Kit Ventas $125 · Pack Resurrección $250\n"
         "2️⃣ Reservas con 50% de adelanto\n"
         "3️⃣ Empezamos HOY con fecha de entrega por escrito\n\n"
         "✅ Plazo incumplido = reembolso total.\n"
         "💳 Pago 100% seguro con QvaPay (si no tienes cuenta, la creas gratis en 2 minutos).\n\n")
    if LINKS.get("kit"):   r += "💳 Kit $9:\n" + LINKS["kit"] + "\n\n"
    if LINKS.get("packB"): r += "💳 Kit Ventas $125 (adelanto $62.50):\n" + LINKS["packB"] + "\n\n"
    if LINKS.get("packA"): r += "💳 Pack Resurrección $250 (adelanto $125):\n" + LINKS["packA"] + "\n"
    return r

# ---------------- PRODUCTO: PACK PLANTILLAS $4 (25/9) ----------------
LINK_PLANTILLAS_PAGO = "https://www.qvapay.com/pay/90e8b817-84a4-41c6-8f78-db08d614c096"
LINK_PLANTILLAS_PROD = "https://mia9911.github.io/despegue-digital/plantillas-whatsapp.html"
TXT_PLANTILLAS = (
    "📦 PACK DE PLANTILLAS WHATSAPP — $4 USD\n\n"
    "20 mensajes listos para copiar y pegar en tu negocio:\n"
    "✅ Bienvenidas, menús con precios, cobros, promos, seguimiento…\n"
    "✅ Entrega AL INSTANTE (link directo, tuyo para siempre)\n\n"
    "💳 Pagar aquí (QvaPay — tarjeta o saldo):\n"
    + LINK_PLANTILLAS_PAGO + "\n\n"
    "Cuando pagues, escríbeme \"pagué plantilla\" y te lo entrego al segundo. 🚀"
)
TXT_PLANTILLAS_OK = (
    "🎉 ¡RECIBIDO! Aquí está tu PACK DE PLANTILLAS:\n\n"
    "📦 " + LINK_PLANTILLAS_PROD + "\n\n"
    "Guárdalo en favoritos — es tuyo para siempre.\n"
    "💡 Tip: cópialas a tus \"Respuestas rápidas\" y atiendes en segundos.\n"
    "Cualquier duda, aquí estoy. ¡A vender! 💰"
)

# ---------------- PRODUCTO: CALCULADORA (25/9, idea de la Jefa) ----------------
LINK_CALC_PAGO = "https://www.qvapay.com/pay/63b2090d-b3a7-4214-a64d-fa8f85d50c71"
LINK_CALC_WEB = "https://mia9911.github.io/despegue-digital/calculadora.html"
LINK_CALC_PRO = "https://github.com/Mia9911/despegue-digital/raw/main/CalculadoraPRO.xlsx"
TXT_CALCULADORA = (
    "\U0001F9EE CALCULADORA DEL VENDEDOR — GRATIS:\n\n"
    "Pon cuánto te cost\u00f3 y a cu\u00e1nto vendes... y mira tu GANANCIA REAL con la "
    "comisi\u00f3n de la transferencia ya descontada. Tambi\u00e9n te dice a cu\u00e1nto vender "
    "para ganar lo que quieras.\n\n"
    "\U0001F4F1 Versi\u00f3n web gratis (se abre y listo):\n" + LINK_CALC_WEB + "\n\n"
    "\U0001F4E6 Versi\u00f3n PRO en Excel (offline, ilimitada) — $3 USD:\n" + LINK_CALC_PAGO + "\n"
    "Al pagar escríbeme \"pagué calculadora\" y te la entrego al segundo. \U0001F680"
)
TXT_CALCULADORA_OK = (
    "\U0001F9EE \U0001F389 ¡RECIBIDO! Aquí está tu CALCULADORA PRO:\n\n"
    "\U0001F4C2 " + LINK_CALC_PRO + "\n\n"
    "(Se descarga el Excel. Funciona SIN internet en Excel, WPS o Google Sheets.\n"
    "Abre la hoja \"Como usarla\" primero.)\n"
    "Cualquier duda, aquí estoy. ¡A ganar bien! \U0001F4B0"
)

LINK_LIBRETA = "https://mia9911.github.io/despegue-digital/libreta.html"
TXT_LIBRETA = (
    "\U0001F4D3 LA LIBRETA DEL VENDEDOR — GRATIS:\n\n"
    "La herramienta que lleva la cuenta de tu negocio: registra tus productos, toca \U0001F4B8 "
    "cada vez que vendes y mira cu\u00e1nto ganaste HOY — con la comisi\u00f3n de la transferencia "
    "ya descontada.\n\n"
    "\U0001F3AF Meta del d\u00eda · \U0001F4C8 tus \u00faltimos 7 d\u00edas · \U0001F4B1 conversor de monedas.\n\n"
    "Todo gratis, sin cuenta y funciona sin internet:\n" + LINK_LIBRETA + "\n\n"
    "\U0001F680 Y si quieres la Calculadora PRO en Excel ($3), escr\u00edbeme \"calculadora\"."
)

LINK_RULETA = "https://mia9911.github.io/despegue-digital/ruleta.html"
TXT_RULETA = (
    "\U0001F3B0 LA RULETA DE DESPEGUE DIGITAL — GRATIS:\n\n"
    "Gira 1 vez al d\u00eda y gana premios de verdad: descuentos en plantillas, kit y calculadora, "
    "muestras gratis y consultas de marketing.\n\n"
    "Sin dinero, sin apuestas — solo premios de nuestra tienda:\n" + LINK_RULETA + "\n\n"
    "\U0001F3B0 Gira tuya aqu\u00ed \U0001F680"
)
TXT_PREMIO_OK = (
    "\U0001F3B0\U0001F389 ¡PREMIO REGISTRADO!\n\n"
    "Mia te escribe enseguida para entregarte tu premio. Si no te llega en unas horas, "
    "escr\u00edbeme \"premio\" otra vez o b\u00fascala en IG: @despegue_digitalmarketing \U0001F49C"
)

# ---------------- AUTOVENTA DE PREMIOS (V12.2) ----------------
# La Jefa crea estos 3 cobros UNA VEZ en qvapay.com (Cobros -> Crear cobro)
# y los pega aqui -> desde ese momento la ruleta es 100% automatica:
LINK_PREMIO_PRO1 = "https://www.qvapay.com/pay/508bd240-9d95-493a-8c1e-397cff9fe84c"
LINK_PREMIO_PLANTA10 = "https://www.qvapay.com/pay/e18fc122-36f8-40c0-bb66-b1a4d346e6de"
LINK_PREMIO_KIT15 = "https://www.qvapay.com/pay/4f9afb61-8715-4e9a-a63b-06e42be38466"

def crear_cobro_qvapay(amount, desc, remote_id):
    """Crea una factura en QvaPay (endpoint oficial /v2/create_invoice) y
    devuelve su URL de pago. None si falla."""
    try:
        _id = os.environ.get("QVAPAY_APP_ID", "")
        _sec = os.environ.get("QVAPAY_APP_SECRET", "")
        if not (_id and _sec):
            return None
        _body = json.dumps({"amount": amount, "description": desc,
                            "remote_id": remote_id}).encode()
        _req = urllib.request.Request("https://api.qvapay.com/v2/create_invoice",
            data=_body, headers={"app-id": _id, "app-secret": _sec,
                                 "Accept": "application/json",
                                 "Content-Type": "application/json",
                                 "User-Agent": "Mozilla/5.0"}, method="POST")
        with urllib.request.urlopen(_req, timeout=20) as _r:
            _d = json.loads(_r.read().decode())
        return _d.get("url") or None
    except Exception as _e:
        print("crear cobro fail:", _e)
        return None

TXT_INTAKE_GRANDE = (
    "\U0001F525 \u00a1GENIAL! Para fabricar tu pedido a la medida necesito 4 datos:\n\n"
    "1\ufe0f\u20e3 Nombre de tu negocio y qu\u00e9 vendes\n"
    "2\ufe0f\u20e3 Tu Instagram o WhatsApp (para ver tu estilo)\n"
    "3\ufe0f\u20e3 Qu\u00e9 colores o estilo te representa\n"
    "4\ufe0f\u20e3 Para cu\u00e1ndo lo necesitas\n\n"
    "Escr\u00edbemelos aqu\u00ed mismo, todos juntos o uno por uno. La F\u00c1BRICA arranca en "
    "cuanto respondas: Mia te escribe para confirmar tu pago y en 24-48 horas tienes "
    "todo listo. \U0001F680"
)

# ---------------- POSTS PARA GRUPOS ----------------
IG = "@despegue_digitalmarketing"
PROMOS = [
    ("🚀 ¿Tu negocio vende por WhatsApp... pero tu Instagram parece abandonado?\n"
     "Eso te está costando clientes TODOS los días.\n\n"
     "En DESPEGUE DIGITAL lo arreglamos en 24-48h: contenido que vende + WhatsApp "
     "ordenado + clientes que llegan solos.\n\n"
     "🎁 Muestra GRATIS de 2 piezas para tu negocio, sin compromiso.\n"
     "🤖 Atención inmediata 24/7 → t.me/Despeguedijitalbot\n"
     "🛒 Packs y precios → " + VITRINA + "\n"
     "📸 " + IG),
    ("⬅️ ANTES: bio vacía, precios por DM, clientes que preguntan y desaparecen.\n"
     "➡️ DESPUÉS: perfil que vende, catálogo claro, respuestas al instante.\n\n"
     "48 horas separan lo uno de lo otro. 🚀\n\n"
     "🎁 Muestra gratis para TU negocio: escribe /muestra a nuestro asistente\n"
     "🤖 t.me/Despeguedijitalbot\n"
     "🛒 Ver packs → " + VITRINA),
    ("📦 NEGOCIO ATENDIDO 24/7 — sin contratar a nadie.\n\n"
     "✅ Contenido profesional para tu marca (desde $9)\n"
     "✅ Tu WhatsApp Business montado y ordenado\n"
     "✅ Garantía total: plazo incumplido = reembolso\n\n"
     "Todo por internet. Entrega en 24-48h. Cobro fácil.\n"
     "🤖 Precios y muestra gratis al instante → t.me/Despeguedijitalbot\n"
     "📸 " + IG),
]
BIENVENIDA_GRUPO = (
    "👋 ¡Hola a todos! Soy el asistente de DESPEGUE DIGITAL 🚀\n\n"
    "Ayudo a negocios cubanos a vender más por internet:\n"
    "🎁 Muestra GRATIS de 2 piezas para tu negocio — solo escribirme\n"
    "🤖 Precios al instante, atención 24/7 → t.me/Despeguedijitalbot\n"
    "🛒 Tienda online: " + VITRINA + "\n\n"
    "(Publicaré 1 post al día, sin spam. Si algún admin prefiere que me vaya, "
    "me lo dice y salgo sin drama 🙏)"
)

# ---------------- ESTADO ----------------
offset, sha_offset = 0, None
try:
    d = gh("GET", "/contents/bot-offset.txt")
    offset = int(base64.b64decode(d["content"]).decode().strip() or "0")
    sha_offset = d.get("sha")
except Exception:
    pass

grupos, sha_grupos = {"grupos": {}}, None
try:
    grupos, sha_grupos = gh_get_file("grupos-bot.json")
except Exception:
    pass

def guardar_grupos():
    try:
        gh_put_file("grupos-bot.json", grupos, sha_grupos, "grupos update")
    except Exception as e:
        print("grupos save fail:", e)

# ---------------- ENTREGA DE MUESTRAS FABRICADAS POR EL ECONÓMICO ----------------
try:
    muestras, sha_mu = gh_get_file("muestras.json")
    pendientes = muestras.get("pendientes", [])
    for m in pendientes:
        try:
            tg("sendMessage", {"chat_id": m["chat_id"], "text": m["texto"]})
            tg("sendMessage", {"chat_id": JEFA, "text":
                "🎁 MUESTRA ENTREGADA automáticamente a " + m.get("nombre", "?") +
                " (@" + m.get("username", "-") + ")"})
        except Exception as e:
            print("muestra fail:", e)
    if pendientes:
        muestras["pendientes"] = []
        gh_put_file("muestras.json", muestras, sha_mu,
                    "muestras entregadas: %d" % len(pendientes))
except Exception as e:
    print("muestras:", e)

# ---------------- RONDA DE ATENCIÓN ----------------
res = tg("getUpdates", {"timeout": 0, "offset": offset})
updates = res.get("result", [])
nuevo_offset = offset
libreta_nueva = []   # todo lo que escriban los clientes queda grabado

for u in updates:
    nuevo_offset = max(nuevo_offset, u["update_id"] + 1)

    mcm = u.get("my_chat_member")
    if mcm:
        chat = mcm.get("chat", {})
        cid = str(chat.get("id"))
        titulo = chat.get("title") or ""
        status = (mcm.get("new_chat_member") or {}).get("status")
        g = grupos["grupos"].get(cid, {"title": titulo, "username": chat.get("username") or "",
                                       "activo": True, "ultima": "", "posts": 0})
        g["title"] = titulo or g.get("title", "")
        if status in ("member", "administrator") and chat.get("type") in ("group", "supergroup"):
            era_nuevo = cid not in grupos["grupos"]
            g["activo"] = True
            grupos["grupos"][cid] = g
            if era_nuevo:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "📢 EL BOT ENTRÓ AL GRUPO: %s\nMañana empiezo: 1 post al día en hora de oro (17-21h)." % titulo})
                try:
                    tg("sendMessage", {"chat_id": int(cid), "text": BIENVENIDA_GRUPO})
                    g["posts"] = g.get("posts", 0) + 1
                except Exception as e:
                    print("bienvenida fail:", e)
        elif status in ("left", "kicked"):
            g["activo"] = False
            grupos["grupos"][cid] = g
            tg("sendMessage", {"chat_id": JEFA, "text":
                "👋 Me quitaron del grupo %s. Sin drama — sigo con los demás." % titulo})
        continue

    if u.get("channel_post"):
        continue

    m = u.get("message")
    if not m:
        continue
    chat_id = m["chat"]["id"]
    nombre = (m.get("from") or {}).get("first_name") or "amigo/a"
    username = (m.get("from") or {}).get("username") or ""
    texto = (m.get("text") or "").strip()
    bajo = texto.lower()
    es_jefa = (chat_id == JEFA)

    if m.get("photo"):
        try:
            tg("sendMessage", {"chat_id": chat_id,
                "text": "📸 ¡Foto recibida! El equipo la revisa en minutos."})
        except Exception as e:
            print("foto reply fail:", e)
        if not es_jefa:
            libreta_nueva.append({"chat_id": chat_id, "nombre": nombre,
                                  "username": username, "texto": "[FOTO]",
                                  "ts": datetime.now(CUBA).isoformat()})
            tg("sendMessage", {"chat_id": JEFA, "text":
                "📸 %s (@%s) mandó una foto al bot (queda en la libreta)." % (nombre, username)})
        continue

    # ---- LIBRETA: todo mensaje de cliente queda grabado ----
    if not es_jefa and texto:
        libreta_nueva.append({"chat_id": chat_id, "nombre": nombre,
                              "username": username, "texto": texto[:500],
                              "ts": datetime.now(CUBA).isoformat()})

    if bajo.startswith("/start"):
        r = TXT_JEFA if es_jefa else TXT_START
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "👀 VISITA NUEVA: %s (@%s) — ya la atiendo (y queda en la libreta)." % (nombre, username)})
    elif bajo.startswith("/precios") or "precio" in bajo or "cuanto" in bajo or "cuánto" in bajo:
        r = TXT_PRECIOS
    elif bajo.startswith("/muestra") or "muestra" in bajo or "gratis" in bajo:
        r = TXT_MUESTRA
    elif bajo.startswith("/garantia"):
        r = TXT_GARANTIA
    elif bajo.startswith("/soporte"):
        r = TXT_SOPORTE
    elif bajo.startswith("/vitrina") or "tienda" in bajo:
        r = "🛒 Tienda online: " + VITRINA + "\nPrecios: /precios · Muestra: /muestra"
    elif "premio" in bajo or "ruleta" in bajo or "giré" in bajo or "girar" in bajo:
        _cod = None
        for _c in ("PRO1", "PLANTA10", "KIT15", "MUESTRA", "CONSUL10"):
            if _c.lower() in bajo:
                _cod = _c
                break
        if es_jefa:
            r = TXT_RULETA
        elif _cod == "MUESTRA":
            r = TXT_MUESTRA
            tg("sendMessage", {"chat_id": JEFA, "text":
                "\U0001F3B0 %s (@%s) gan\u00f3 la MUESTRA en la ruleta \u2014 respondi\u00f3 el "
                "formulario (su texto queda en la libreta del bot). \U0001F381" % (nombre, username)})
        elif _cod == "CONSUL10":
            r = ("\U0001F9D1\u200D\U0001F4BC \u00a1Consulta ganada! Mia te escribe HOY para agendar tus "
                 "10 minutos de marketing gratis. Ten a mano: qu\u00e9 vendes y tu mayor duda "
                 "de ventas. \U0001F4AC")
            tg("sendMessage", {"chat_id": JEFA, "text":
                "\U0001F3B0 %s (@%s) gan\u00f3 la CONSULTA (10 min) \u2014 agr\u00e9gale d\u00eda y hora "
                "cuando puedas. \U0001F381" % (nombre, username)})
        elif _cod in ("PRO1", "PLANTA10", "KIT15"):
            _p = {"PRO1": ("la Calculadora PRO en Excel", 2, "2.00", "3"),
                  "PLANTA10": ("el Pack de Plantillas WhatsApp", 3.6, "3.60", "4"),
                  "KIT15": ("el Kit Expr\u00e9s Digital", 7.65, "7.65", "9")}[_cod]
            _l = {"PRO1": LINK_PREMIO_PRO1, "PLANTA10": LINK_PREMIO_PLANTA10,
                  "KIT15": LINK_PREMIO_KIT15}[_cod]
            _rid = "premio-%s-%s" % (_cod.lower(), datetime.now(CUBA).strftime("%d%m%H%M%S"))
            _url_pago = crear_cobro_qvapay(_p[1], "PREMIO RULETA " + _cod + " - " + _p[0], _rid) or _l
            if _url_pago:
                r = ("\U0001F389 Tu premio: " + _p[0] + " \u2014 en vez de $" + _p[3] +
                     ", pagas $" + _p[2] + ".\n\n"
                     "Tu link de pago (descuento ya aplicado):\n" + _url_pago + "\n\n"
                     "Al pagar escr\u00edbeme: pagu\u00e9 premio " + _cod)
                if not es_jefa:
                    tg("sendMessage", {"chat_id": JEFA, "text":
                        "\U0001F3B0\U0001F4B0 %s (@%s) gan\u00f3 %s \u2014 le gener\u00e9 SU link de $%s. "
                        "Cuando pague salta la alarma. \U0001F680" % (nombre, username, _cod, _p[2])})
            else:
                r = ("\U0001F389 Tu premio: " + _p[0] + " \u2014 en vez de $" + _p[3] +
                     ", pagas $" + _p[2] + ".\n\n"
                     "Mia te manda tu link de pago con el descuento en unos minutos "
                     "\U0001F4B3 (gu\u00e1rdate el c\u00f3digo " + _cod + ").")
                tg("sendMessage", {"chat_id": JEFA, "text":
                    ("\U0001F3B0 %s (@%s) gan\u00f3 %s ($%s) \u2014 m\u00e1ndale su link de cobro con "
                     "descuento YA, o p\u00e9game el link y lo dejo autom\u00e1tico para siempre.") %
                    (nombre, username, _cod, _p[2])})
        elif "premio" in bajo:
            r = TXT_PREMIO_OK
            tg("sendMessage", {"chat_id": JEFA, "text":
                "\U0001F3B0 %s (@%s) gir\u00f3 LA RULETA y gan\u00f3 \u2014 revisa su mensaje y "
                "entr\u00e9gale el premio \U0001F381" % (nombre, username)})
        else:
            r = TXT_RULETA
    elif "libreta" in bajo or "inventario" in bajo or "vendi" in bajo or "cuenta de ventas" in bajo:
        r = TXT_LIBRETA
    elif "calculadora" in bajo or "cálcul" in bajo or "ganancia" in bajo:
        if any(k in bajo for k in ("pagué", "pague", "ya pag", "pagado", "realicé el pago")):
            r = TXT_CALCULADORA_OK
            if not es_jefa:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F9EE %s (@%s) pagó la CALCULADORA PRO ($3) → entregada al instante." % (nombre, username)})
        else:
            r = TXT_CALCULADORA
    elif "plantilla" in bajo:
        if any(k in bajo for k in ("pagué", "pague", "ya pag", "pagado", "pague el", "realizé el pago", "realicé el pago")):
            r = TXT_PLANTILLAS_OK
            if not es_jefa:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "📦 %s (@%s) pagó el PACK PLANTILLAS ($4) → entregado al instante." % (nombre, username)})
        else:
            r = TXT_PLANTILLAS
    elif "pagué premio" in bajo or "pague premio" in bajo or "pagado premio" in bajo:
        _cod2 = None
        for _c in ("PRO1", "PLANTA10", "KIT15"):
            if _c.lower() in bajo:
                _cod2 = _c
                break
        if _cod2 == "PRO1":
            r = TXT_CALCULADORA_OK
            if not es_jefa:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F3C6 VENTA CON PREMIO: %s (@%s) pag\u00f3 la PRO con descuento ($2) \u2192 entregada." % (nombre, username)})
        elif _cod2 == "PLANTA10":
            r = TXT_PLANTILLAS_OK
            if not es_jefa:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F3C6 VENTA CON PREMIO: %s (@%s) pag\u00f3 PLANTILLAS con descuento ($3.60) \u2192 entregado." % (nombre, username)})
        elif _cod2 == "KIT15":
            _rn = datetime.now(CUBA).strftime("%d%m-%H%M") + str(datetime.now(CUBA).second)
            r = TXT_KIT_PAGADO + "\n\U0001F9FE RECIBO N\u00ba " + _rn[:9] + " \u2014 gu\u00e1rdalo como prueba de tu compra."
            if not es_jefa:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F3C6 VENTA CON PREMIO: %s (@%s) pag\u00f3 el KIT con descuento ($7.65) \u2192 entregado." % (nombre, username)})
        else:
            r = ("\U0001F3B0 \u00bfCu\u00e1l fue tu premio? M\u00e1ndame el c\u00f3digo (PRO1, PLANTA10 o "
                 "KIT15) y te entrego al segundo. \U0001F680")
    elif (any(k in bajo for k in ("resurrección", "resurreccion", "vendedor", "kit de ventas", "a medida", "personalizad"))
          and any(k in bajo for k in ("pagué", "pague", "ya pag", "pagado", "compré", "quiero", "empezar", "me interesa", "listo"))):
        r = TXT_INTAKE_GRANDE
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "\U0001F525 PEDIDO GRANDE EN CAMINO: %s (@%s) \u2014 le ped\u00ed los 4 datos del brief. "
                "Sus respuestas caen en la libreta y la f\u00e1brica las recoge en la pr\u00f3xima "
                "revisi\u00f3n. T\u00fa solo verificas el pago. \U0001F680" % (nombre, username)})
    elif any(k in bajo for k in ("pagué", "pague", "ya pag", "pagado", "pague el", "realicé el pago")):
        recibo_n = datetime.now(CUBA).strftime("%d%m-%H%M") + str(datetime.now(CUBA).second)
        r = TXT_KIT_PAGADO + "\n🧾 RECIBO Nº " + recibo_n[:9] + " — guárdalo como prueba de tu compra." + "\n🎁 BONUS incluido: Pack de Plantillas WhatsApp → " + LINK_PLANTILLAS_PROD
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "💰 %s (@%s) dice que PAGÓ → le entregué el Kit YA. Verifica el pago "
                "cuando puedas (escribe COBRO en el chat de Arena)." % (nombre, username)})
    elif bajo.startswith("/calificar") or "estrella" in bajo or "califico" in bajo or "calificación" in bajo or "calificacion" in bajo or bajo.startswith("⭐"):
        r = TXT_CALIFICAR
    elif any(k in bajo for k in ("quiero", "comprar", "me interesa", "empezar", "reserv")):
        r = txt_cierre()
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "💰 CLIENTE INTERESADO: %s (@%s) — ya recibió los links de cobro." % (nombre, username)})
    elif es_jefa:
        r = TXT_JEFA
    elif m["chat"].get("type") == "private":
        r = ("¡Gracias por escribir, " + nombre + "! 😊 Para atenderte al segundo:\n"
             "💰 /precios · 🎁 /muestra · 🛒 /vitrina\n\n"
             "O cuéntame qué necesitas y te oriento.")
    else:
        r = None  # en grupos solo respondo a palabras clave, no a todo lo que se escriba
    if r:
        try:
            tg("sendMessage", {"chat_id": chat_id, "text": r})
        except Exception as e:
            print("reply fail:", chat_id, e)

# ---------------- GUARDAR LIBRETA ----------------
if libreta_nueva:
    try:
        try:
            prov, sha_p = gh_get_file("prospectos.json")
        except Exception:
            prov, sha_p = {"mensajes": []}, None
        prov.setdefault("mensajes", []).extend(libreta_nueva)
        prov["mensajes"] = prov["mensajes"][-500:]
        gh_put_file("prospectos.json", prov, sha_p,
                    "libreta: +%d mensajes" % len(libreta_nueva))
    except Exception as e:
        print("libreta fail:", e)

# ---------------- POSTS DIARIOS EN GRUPOS ----------------
ahora_cuba = datetime.now(CUBA)
hoy = ahora_cuba.strftime("%Y-%m-%d")
hora = int(ahora_cuba.strftime("%H"))
publicados = 0
if 17 <= hora < 23:
    variant = ahora_cuba.timetuple().tm_yday % len(PROMOS)
    for cid, g in grupos["grupos"].items():
        if g.get("activo") and g.get("ultima") != hoy:
            try:
                tg("sendMessage", {"chat_id": int(cid), "text": PROMOS[variant]})
                g["ultima"] = hoy
                g["posts"] = g.get("posts", 0) + 1
                publicados += 1
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "📢 Post diario publicado en: %s" % g.get("title", cid)})
            except Exception as e:
                print("post grupo fail:", cid, e)

    # ---- V6: post diario en NUESTRO CANAL (auto, para siempre) ----
    canal = grupos.get("_canal") or {}
    if canal.get("ultima") != hoy:
        try:
            tg("sendMessage", {"chat_id": CANAL_ID,
                "text": PROMOS[variant] +
                        "\n👥 Comunidad de negocios → t.me/DespegueDigitalCuba"})
            grupos["_canal"] = {"ultima": hoy}
            publicados += 1
            tg("sendMessage", {"chat_id": JEFA, "text":
                "📢 Post diario publicado en el CANAL @DespegueDigitalMia."})
        except Exception as e:
            print("canal post fail:", e)

# ---------------- V8: AGENDA MATUTINA A LA JEFA (8-10 AM Cuba) ----------------
CAPTIONS_IG = [
    ("post-libreta.jpg",
     "\U0001F4D3 \u00bfCU\u00c1NTO VENDISTE HOY?\n\n"
     "La Libreta del Vendedor — GRATIS: registra tus productos, toca \U0001F4B8 cada vez que vendes, "
     "y mira tu ganancia REAL del d\u00eda (comisi\u00f3n descontada), tu meta y tus \u00faltimos 7 d\u00edas.\n\n"
     "Sin cuenta. Sin internet. Sin mensualidades. Hecha para Cuba \U0001F1E8\U0001F1FA\n\n"
     "\U0001F4F1 Link en la bio \U0001F680\n\n"
     "#NegociosCuba #Emprendedores #Ventas #Cuba #WhatsAppBusiness #MarketingDigital"),
    ("post-antes-despues.jpg",
     "⬅️ ANTES: bio vacía, precios por privado, clientes que preguntan y desaparecen.\n"
     "➡️ DESPUÉS: perfil que vende, catálogo claro, respuestas al instante.\n\n"
     "48 horas separan lo uno de lo otro. 🚀\n"
     "🎁 ¿Ver tu ANTES convertido en DESPUÉS? Muestra GRATIS → link en la bio\n\n"
     "#AntesYDespues #MarketingDigital #NegociosCuba #EmprendedoresCuba"),
    ("post-kit.jpg",
     "⚡ ¿Empezar a vender más HOY sin gastar mucho?\n\n"
     "El Kit Exprés Digital ($9): 30 respuestas de WhatsApp que venden + 10 bios que "
     "convierten + 7 plantillas de posts. Descarga inmediata.\n\n"
     "🛒 Link en la bio · Garantía total 💛\n\n"
     "#KitDigital #WhatsAppBusiness #VentasPorInternet #Cuba #MarketingDigital"),
    ("post-pack-a.jpg",
     "🚀 Tu presencia online COMPLETA renacida en 24-48h.\n\n"
     "Pack Resurrección: contenido PRO diseñado para tu marca + catálogo con precios + "
     "calendario de 2 semanas sin pensar.\n\n"
     "✅ Plazo incumplido = reembolso total. 🛒 Link en la bio\n\n"
     "#MarketingDigital #NegociosCuba #InstagramParaNegocios #Emprendedores"),
    ("captura-pantalla-plantillas.jpg",
     "📦 NUEVO: Pack de 20 plantillas de WhatsApp listas para copiar y pegar — $4.\n\n"
     "Bienvenidas, menús con precios, cobros amables, promos flash, seguimiento… "
     "todo lo que tu negocio necesita decir, YA ESCRITO.\n\n"
     "Entrega al instante. 🛒 Link en la bio\n\n"
     "#WhatsAppBusiness #Plantillas #VentasFaciles #Cuba #NegociosInteligentes"),
    ("captura-calculadora.jpg",
     "\U0001F9EE ¿A cu\u00e1nto ganas DE VERDAD con cada venta? (pista: la comisi\u00f3n de la transferencia se come algo)\n\nCalculadora del vendedor cubano — GRATIS: pon costo y precio, y mira tu ganancia real. Y si quieres ganar X, te dice a cu\u00e1nto vender.\n\n\U0001F4F1 Link en la bio \U0001F680\n\n#NegociosCuba #Emprendedores #Ventas #Cuba #WhatsAppBusiness #MarketingDigital"),
    ("logo-despegue.jpg",
     "👋 Domingo: día de descansar Y de planear.\n\n"
     "Esta semana: tu Instagram y tu WhatsApp pueden dejar de perder clientes. "
     "Todo empieza con una muestra gratis (link en la bio).\n\n"
     "¿Hablamos esta semana? Te leo 💛\n\n"
     "#EmprendedoresCuba #NegociosOnline #MarketingDigital #Cuba"),
]
if hora >= 8 and grupos.get("_agenda", {}).get("ultima") != hoy:
    try:
        img, cap = CAPTIONS_IG[ahora_cuba.weekday() % 7]
        _paso1 = "1️⃣ IG (2 min) — publica con la imagen '%s':\n\n%s" % (img, cap)
        try:
            tg("sendPhoto", {"chat_id": JEFA,
                "photo": "https://raw.githubusercontent.com/Mia9911/despegue-digital/main/imagenes/" + img,
                "caption": cap})
            _paso1 = ("1️⃣ IG (2 min) — la FOTO y el CAPTION ya te llegaron arriba ⬆️ "
                      "(guárdalas en tu teléfono y publica).")
        except Exception:
            pass
        tg("sendMessage", {"chat_id": JEFA, "text":
            "☀️ TU PLAN DE HOY (10-15 minutos en total):\n\n"
            + _paso1 +
            "\n\n2️⃣ Revisa Telegram: yo te avisé de cada interesado (si hay).\n"
            "3️⃣ Murales pendientes (5 min c/u): los que te falten.\n"
            "4️⃣ LaborX (2 min): revisa tus propuestas y mensajes → laborx.com/dashboard\n5️⃣ Recuerda: Revolico se renueva cada 3-4 días — yo te aviso.\n\n"
            "El resto del día, la máquina trabaja sola. 🤖\n— Tu Económico"})
        grupos["_agenda"] = {"ultima": hoy}
    except Exception as e:
        print("agenda fail:", e)


# ---------------- V9: ALARMA DE PAGOS QVAPAY (cada 10 min) ----------------
try:
    QP_ID = os.environ.get("QVAPAY_APP_ID", "")
    QP_SEC = os.environ.get("QVAPAY_APP_SECRET", "")
    if QP_ID and QP_SEC:
        _req = urllib.request.Request("https://api.qvapay.com/v2/transactions",
            data=b"", headers={"app-id": QP_ID, "app-secret": QP_SEC,
                               "Accept": "application/json", "Content-Type": "application/json",
                               "User-Agent": "Mozilla/5.0"}, method="POST")
        with urllib.request.urlopen(_req, timeout=20) as _r:
            _txs = json.loads(_r.read().decode()).get("transactions", [])
        _ya = grupos.get("_pagos", {}).get("total", 0)
        if len(_txs) > _ya:
            for _tx in _txs[_ya:]:
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F4B0\U0001F4B0\U0001F4B0 ¡PAGO RECIBIDO EN QVAPAY!\n%s" %
                    json.dumps(_tx, ensure_ascii=False)[:300]})
        grupos["_pagos"] = {"total": len(_txs)}
except Exception as e:
    print("qvapay check fail:", e)

# ---------------- V12.4: RADAR LABORX "CAZA-FINA" (API publica, cada hora) ----------------
# 29/9 DESCUBIERTA LA API PUBLICA de LaborX (sin login, solo feeds publicos):
#   GET api.laborx.com/simple-jobs/list?limit=100  -> trabajos precio fijo ($15+)
#   GET api.laborx.com/vacancy/list?limit=100      -> vacantes de largo plazo
#   GET api.laborx.com/gig/get?id=122772           -> vitrina de la Jefa (vistas/clicks)
# REGLA DE HIERRO: los endpoints /me/* (aplicar, notificaciones, retiros) piden el
# token de SU cuenta y el punto 4.1(h) de los Terminos de LaborX PROHIBE "any
# automated use of the Website or its Services". NUNCA automatizar su cuenta (en
# juego estan su reputacion y su dinero del escrow). El bot SOLO lee feeds
# publicos (lo mismo que ver la web) y le manda los matches con todo listo para
# que ella aplique con un toque. Velocidad: cada hora, trabajos con menos de 26h.
try:
    def _api_lx(_path):
        _rq = urllib.request.Request("https://api.laborx.com/" + _path,
                                     headers={"Accept": "application/json",
                                              "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(_rq, timeout=25) as _rh:
            return json.loads(_rh.read().decode("utf-8", "ignore"))
    _utc_now = datetime.utcnow()
    _hora_id = _utc_now.strftime("%Y-%m-%dT%H")
    _rad = grupos.get("_radar_lx", {}) or {}
    if _rad.get("hora") != _hora_id:
        LX_VERBOS = ["social", "instagram", "content", "community", "marketing",
                     "caption", "copywrit", "whatsapp", "facebook", "spanish",
                     "design", "telegram", "moderat", "discord", "influencer",
                     "tiktok", "youtube"]
        LX_VAC_VERBOS = ["community", "moderat", "telegram", "discord",
                         "social media", "social-media", "instagram",
                         "content creat", "content writ", "marketing assist",
                         "marketing special", "marketing manag", "spanish",
                         "whatsapp", "caption", "influencer", "chat support",
                         "community manager"]
        LX_MALOS = ["rent", "flash", "must-be-in", "in-the-usa", "usa-or-canada",
                    "uk-only", "account-for", "verify", "kyc",
                    "native-chinese", "native-vietnamese", "native-korean",
                    "native-japanese", "fluent-in-german", "native-german",
                    "native-french", "native-russian", "voice-over", "voiceover"]
        LX_TRAP_DESC = ["developer account", "anydesk", "old live account",
                        "referral code", "followers for sale", "account with"]
        LX_SPAM_DESC = ["for hire", "hire me", "for sale", "serious buyer",
                        "time for sale", "don't hesitate to message"]
        LX_IDIOMAS = ["native chinese", "native vietnamese", "cantonese",
                      "fluent german", "native korean", "native japanese",
                      "native german", "native french"]
        LX_SENIOR = ["10+ years", "8+ years", "senior software",
                     "full-stack developer", "principal engineer"]
        _vistos = set(_rad.get("vistos", []))
        _nuevos = []
        # --- 1) trabajos de precio fijo (los $20 / $100 / $500) ---
        try:
            _jobs = ((_api_lx("simple-jobs/list?limit=100").get("result")
                      or {}).get("jobs") or [])
            for _j in _jobs:
                _id = "j%s" % _j.get("id")
                _slug = _j.get("slug", "")
                try:
                    _fpub = datetime.strptime(
                        _j.get("first_published_at", "2000-01-01 00:00:00"),
                        "%Y-%m-%d %H:%M:%S")
                except Exception:
                    _fpub = _utc_now - timedelta(days=99)
                _edad = (_utc_now - _fpub).total_seconds()
                if _id in _vistos or not (-600 < _edad < 26 * 3600):
                    _vistos.add(_id)
                    continue
                _tit = (_slug + " " + _j.get("name", "")).lower()
                if not any(_v in _tit for _v in LX_VERBOS):
                    _vistos.add(_id)
                    continue
                if any(_m in _slug for _m in LX_MALOS):
                    _vistos.add(_id)
                    continue
                if float(_j.get("budget") or 0) < 15:
                    _vistos.add(_id)
                    continue
                _blob = ("%s %s" % (_j.get("name", ""),
                                    _j.get("description", ""))).lower()
                if (any(_m in _blob for _m in LX_TRAP_DESC) or
                        any(_m in _blob for _m in LX_SPAM_DESC) or
                        any(_m in _blob[:400] for _m in
                            ("i'm a", "i am a", "i help", "i specialize",
                             "i offer")) or
                        any(_m in _blob for _m in LX_IDIOMAS)):
                    _vistos.add(_id)
                    continue
                _vistos.add(_id)
                _nuevos.append({"tipo": "job", "slug": _slug,
                                "titulo": _j.get("name", "") or _slug,
                                "dinero": "$%.0f" % float(_j.get("budget") or 0),
                                "edad": max(_edad, 0), "desc": _blob[:400],
                                "resenas": ((_j.get("user") or {})
                                            .get("reviews_count", 0) or 0)})
        except Exception as _e:
            print("radar lx jobs fail:", _e)
        # --- 2) vacantes de largo plazo SOLO remotas (ingreso recurrente) ---
        try:
            _vacs = ((_api_lx("vacancy/list?limit=100").get("result")
                      or {}).get("vacancies") or [])
            for _vac in _vacs:
                _id = "v%s" % _vac.get("id")
                _slug = _vac.get("slug", "")
                try:
                    _fpub = datetime.strptime(
                        _vac.get("created_at", "2000-01-01 00:00:00"),
                        "%Y-%m-%d %H:%M:%S")
                except Exception:
                    _fpub = _utc_now - timedelta(days=99)
                _edad = (_utc_now - _fpub).total_seconds()
                if _id in _vistos or not (-600 < _edad < 26 * 3600):
                    _vistos.add(_id)
                    continue
                if not _vac.get("position_remote"):
                    _vistos.add(_id)
                    continue
                _blob = ("%s %s" % (_vac.get("name", ""),
                                    _vac.get("description", ""))).lower()
                if not any(_k in (_slug + " " + _blob[:300])
                           for _k in LX_VAC_VERBOS):
                    _vistos.add(_id)
                    continue
                _sa = float(_vac.get("salary_from") or 0)
                _sb = float(_vac.get("salary_to") or 0)
                if _sa > 50000:
                    _vistos.add(_id)
                    continue
                if (any(_m in _slug for _m in LX_MALOS) or
                        any(_m in _blob for _m in LX_TRAP_DESC) or
                        any(_m in _blob for _m in LX_IDIOMAS) or
                        any(_m in _blob for _m in LX_SENIOR)):
                    _vistos.add(_id)
                    continue
                _vistos.add(_id)
                _din = ("$%.0f-$%.0f/a\u00f1o" % (_sa, _sb)) if _sb > 0 \
                    else "salario a negociar"
                _nuevos.append({"tipo": "vac", "slug": _slug,
                                "titulo": _vac.get("name", "") or _slug,
                                "dinero": _din,
                                "edad": max(_edad, 0), "desc": _blob[:400],
                                "resenas": ((_vac.get("user") or {})
                                            .get("reviews_count", 0) or 0)})
        except Exception as _e:
            print("radar lx vac fail:", _e)
        _nuevos.sort(key=lambda _x: _x["edad"])
        if _nuevos:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "\U0001F3F9 CAZA LABORX \u2014 %d trabajo(s) NUEVO(s) que te "
                "pueden servir (reci\u00e9n publicados):" % len(_nuevos[:3])})
        for _n in _nuevos[:3]:
            _mins = int(_n["edad"] / 60)
            _hace = ("hace %d min" % _mins) if _mins < 90 \
                else ("hace %d h" % (_mins // 60))
            _url = ("https://laborx.com/jobs/%s" if _n["tipo"] == "job"
                    else "https://laborx.com/vacancies/%s") % _n["slug"]
            _msg = ("\U0001F4CC %s\n\U0001F4B0 %s \u00b7 publicado %s\n"
                    "\u2b50 cliente: %d rese\u00f1a(s)\n\U0001F517 %s"
                    % (_n["titulo"], _n["dinero"], _hace, _n["resenas"], _url))
            _d = re.sub(r"<[^>]{0,120}>", " ", _n["desc"])
            _d = re.sub(r"\s+", " ", _d).strip()
            if len(_d) > 40:
                _msg += "\n\U0001F4C4 De qu\u00e9 trata: %s..." % _d[:200]
            _msg += ("\n\n\u00bfTe gusta? P\u00e9gamelo aqu\u00ed y te fabrico "
                     "la propuesta en ingl\u00e9s lista para enviar. \U0001F680")
            tg("sendMessage", {"chat_id": JEFA, "text": _msg})
        # --- 3) vitrina de la Jefa en LaborX (API publica, sin tocar su cuenta) ---
        try:
            _g = (_api_lx("gig/get?id=122772").get("result") or {})
            _gv = int(_g.get("views") or 0)
            _gc = int(_g.get("chat_clicks") or 0)
            _ant = _rad.get("gig") or {}
            if _ant and (_ant.get("v") != _gv or _ant.get("c") != _gc):
                tg("sendMessage", {"chat_id": JEFA, "text":
                    "\U0001F440 Tu vitrina LaborX ('10 ready-to-post social "
                    "media designs') va en %d vista(s) y %d click(s) al chat. "
                    "Si te escriben, responde en menos de 1 hora!" % (_gv, _gc)})
            _rad["gig"] = {"v": _gv, "c": _gc}
        except Exception as _e:
            print("radar lx gig fail:", _e)
        _rad["hora"] = _hora_id
        _rad["vistos"] = sorted(_vistos)[-500:]
        grupos["_radar_lx"] = _rad
        print("radar lx api:", len(_nuevos), "nuevos,", len(_vistos), "vistos")
except Exception as _e:
    print("radar lx fail:", _e)

# ---------------- GUARDAR ESTADO ----------------
if nuevo_offset != offset or sha_offset is None:
    try:
        payload = {"message": "offset %s" % nuevo_offset, "branch": "main",
                   "content": base64.b64encode(str(nuevo_offset).encode()).decode()}
        if sha_offset:
            payload["sha"] = sha_offset
        gh("PUT", "/contents/bot-offset.txt", payload)
    except Exception as e:
        print("offset save fail:", e)
if grupos.get("grupos"):
    guardar_grupos()

print("guardian v3: %d updates, %d libreta, %d posts hoy" %
      (len(updates), len(libreta_nueva), publicados))
