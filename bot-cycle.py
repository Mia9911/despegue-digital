#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 BOT-CYCLE v2 — GUARDIÁN COMPLETO DE DESPEGUE DIGITAL
Corre en GitHub Actions cada 10 minutos, PARA SIEMPRE:
  1. Atiende 1-a-1 a cada cliente (precios, muestra, cierre, links de cobro)
  2. Detecta cuándo lo agregan a un GRUPO → saluda y queda registrado
  3. Publica 1 post al día por grupo (17:00-21:00 hora Cuba, sin spam)
  4. Avisa a la Jefa de cada prospecto, cliente interesado y foto
  5. Detecta si lo expulsan de un grupo y lo desactiva sin drama
"""
import json, os, base64, urllib.request
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GH = os.environ.get("GITHUB_TOKEN", "")
JEFA = int(os.environ.get("JEFA_CHAT_ID", "1227661387"))
API_T = "https://api.telegram.org/bot" + TOKEN + "/"
REPO = "https://api.github.com/repos/Mia9911/despegue-digital"
CUBA = timezone(timedelta(hours=-4))

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

# ---------------- TEXTOS 1-A-1 ----------------
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
    "👑 Línea de la Jefa — guardián activo (respondo cada 10 min).\n"
    "Para respuesta instantánea y muestras, la Jefa escribe a El Económico "
    "en el chat de Arena. Yo nunca duermo más de 10 minutos. 🏰"
)

def txt_cierre():
    r = ("🔥 ¡Excelente! Así reservamos tu cupo:\n\n"
         "1️⃣ Eliges: Kit $9 · Kit Ventas $125 · Pack Resurrección $250\n"
         "2️⃣ Reservas con 50% de adelanto\n"
         "3️⃣ Empezamos HOY con fecha de entrega por escrito\n\n"
         "✅ Plazo incumplido = reembolso total.\n\n")
    if LINKS.get("kit"):   r += "💳 Kit $9:\n" + LINKS["kit"] + "\n\n"
    if LINKS.get("packB"): r += "💳 Kit Ventas $125 (adelanto $62.50):\n" + LINKS["packB"] + "\n\n"
    if LINKS.get("packA"): r += "💳 Pack Resurrección $250 (adelanto $125):\n" + LINKS["packA"] + "\n"
    return r

# ---------------- POSTS PARA GRUPOS (1 por día, rotando) ----------------
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

# ---------------- RONDA DE ATENCIÓN ----------------
res = tg("getUpdates", {"timeout": 0, "offset": offset})
updates = res.get("result", [])
nuevo_offset = offset

for u in updates:
    nuevo_offset = max(nuevo_offset, u["update_id"] + 1)

    # --- agregado / expulsado de grupos ---
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

    # --- canal (si la Jefa lo hace admin de otro) ---
    if u.get("channel_post"):
        ch = u["channel_post"].get("chat", {})
        tg("sendMessage", {"chat_id": JEFA, "text":
            "📢 Post detectado en el canal %s — el bot ya está adentro." % (ch.get("title") or "")})
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
        tg("sendMessage", {"chat_id": chat_id,
            "text": "📸 ¡Foto recibida! El equipo la revisa en minutos."})
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "📸 %s (@%s) mandó una foto al bot." % (nombre, username)})
        continue

    if not es_jefa:
        if bajo.startswith("/start"):
            tg("sendMessage", {"chat_id": JEFA, "text":
                "👀 VISITA NUEVA: %s (@%s)" % (nombre, username)})
        if any(k in bajo for k in ("mi negocio", "tengo un", "vendo", "mi tienda",
                                   "cafeter", "barber", "salon", "salón", "dulcer",
                                   "manicur", "tienda de", "tengo una")):
            tg("sendMessage", {"chat_id": JEFA, "text":
                "🔥 PROSPECTO: %s (@%s) dice: %s" % (nombre, username, texto[:120])})

    if bajo.startswith("/start"):
        r = TXT_JEFA if es_jefa else TXT_START
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
    elif any(k in bajo for k in ("quiero", "comprar", "me interesa", "empezar", "reserv")):
        r = txt_cierre()
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "💰 CLIENTE INTERESADO: %s (@%s) — ya recibió los links de cobro." % (nombre, username)})
    elif es_jefa:
        r = TXT_JEFA
    else:
        r = ("¡Gracias por escribir, " + nombre + "! 😊 Para atenderte al segundo:\n"
             "💰 /precios · 🎁 /muestra · 🛒 /vitrina\n\n"
             "O cuéntame qué necesitas y te oriento.")
    tg("sendMessage", {"chat_id": chat_id, "text": r})

# ---------------- PUBLICACIÓN DIARIA EN GRUPOS (hora de oro Cuba) ----------------
ahora_cuba = datetime.now(CUBA)
hoy = ahora_cuba.strftime("%Y-%m-%d")
hora = int(ahora_cuba.strftime("%H"))
publicados = 0
if 17 <= hora < 21:
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

print("guardian v2: %d updates, %d posts hoy" % (len(updates), publicados))
