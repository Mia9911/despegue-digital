#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 BOT-CYCLE — el guardián nocturno de Despegue Digital.
Corre en GitHub Actions cada 10 minutos, atiende lo que haya pendiente
en Telegram y se va. Así el bot NUNCA duerme del todo, aunque la torre
principal esté en reposo. (La torre = respuestas instantáneas; este
guardián = respuestas en máximo 10 minutos, 24/7/365.)
"""
import json, os, base64, urllib.request

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GH = os.environ.get("GITHUB_TOKEN", "")
API_T = "https://api.telegram.org/bot" + TOKEN + "/"
REPO = "https://api.github.com/repos/Mia9911/despegue-digital"
JEFA = 1227661387

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

LINKS = {}
if os.path.exists("links-de-pago.json"):
    try:
        LINKS = json.load(open("links-de-pago.json", encoding="utf-8"))
    except Exception:
        pass

TXT_START = (
    "🚀 ¡Bienvenido/a a DESPEGUE DIGITAL!\n"
    "Diseño y marketing que VENDEN, para negocios de Cuba y la diáspora.\n\n"
    "🎁 Kit Exprés Digital — $9 (entrega inmediata)\n"
    "⚡ Kit de Ventas Exprés — $125 (24 horas)\n"
    "🚀 Pack Resurrección IG + WhatsApp — $250 (24-48h) — el más pedido\n\n"
    "✅ Garantía: plazo incumplido = reembolso total.\n"
    "🛒 Tienda online: " + LINKS.get("vitrina", "en línea pronto") + "\n\n"
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
    "🛒 Tienda: " + LINKS.get("vitrina", "") + "\n"
    "🎁 Muestra gratis: /muestra"
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
    "👑 Línea privada de la Jefa — guardián nocturno activo.\n"
    "(Si esto responde, es que la torre principal descansa, pero el imperio "
    "sigue de pie. Para respuesta instantánea, la Jefa escribe MOTOR en el chat "
    "de Arena y El Económico despierta.)"
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

# ---- offset persistente en el repo ----
offset, sha = 0, None
try:
    d = gh("GET", "/contents/bot-offset.txt")
    offset = int(base64.b64decode(d["content"]).decode().strip() or "0")
    sha = d.get("sha")
except Exception:
    pass

res = tg("getUpdates", {"timeout": 0, "offset": offset})
updates = res.get("result", [])
nuevo_offset = offset

for u in updates:
    nuevo_offset = max(nuevo_offset, u["update_id"] + 1)
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
                                   "manicur", "tienda de")):
            tg("sendMessage", {"chat_id": JEFA, "text":
                "🔥 PROSPECTO: %s (@%s) dice: %s" % (nombre, username, texto[:120])})

    if bajo.startswith("/start"):
        r = TXT_JEFA if es_jefa else TXT_START
    elif bajo.startswith(("/precios",)) or "precio" in bajo or "cuanto" in bajo or "cuánto" in bajo:
        r = TXT_PRECIOS
    elif bajo.startswith("/muestra") or "muestra" in bajo or "gratis" in bajo:
        r = TXT_MUESTRA
    elif bajo.startswith("/garantia"):
        r = TXT_GARANTIA
    elif bajo.startswith("/soporte"):
        r = TXT_SOPORTE
    elif bajo.startswith("/vitrina") or "tienda" in bajo:
        r = "🛒 Tienda online: " + (LINKS.get("vitrina") or "en línea pronto") + "\nPrecios: /precios · Muestra gratis: /muestra"
    elif any(k in bajo for k in ("quiero", "comprar", "me interesa", "empezar", "reserv")):
        r = txt_cierre()
        if not es_jefa:
            tg("sendMessage", {"chat_id": JEFA, "text":
                "💰 CLIENTE INTERESADO: %s (@%s) — ya recibió los links de cobro." % (nombre, username)})
    elif es_jefa:
        r = TXT_JEFA
    else:
        r = ("¡Gracias por escribir, " + nombre + "! 😊 Para atenderte al segundo:\n"
             "💰 /precios — precios y packs\n🎁 /muestra — muestra gratis\n"
             "🛒 /vitrina — la tienda\n\nO cuéntame qué necesitas y te oriento.")
    tg("sendMessage", {"chat_id": chat_id, "text": r})

if nuevo_offset != offset or sha is None:
    content = base64.b64encode(str(nuevo_offset).encode()).decode()
    payload = {"message": "offset %s" % nuevo_offset, "content": content, "branch": "main"}
    if sha:
        payload["sha"] = sha
    try:
        gh("PUT", "/contents/bot-offset.txt", payload)
    except Exception as e:
        print("offset save fail:", e)

print("guardian: %d updates atendidos" % len(updates))
