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
"""
import json, os, base64, urllib.request
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
    elif any(k in bajo for k in ("pagué", "pague", "ya pag", "pagado", "pague el", "realicé el pago")):
        recibo_n = datetime.now(CUBA).strftime("%d%m-%H%M") + str(datetime.now(CUBA).second)
        r = TXT_KIT_PAGADO + "\n🧾 RECIBO Nº " + recibo_n[:9] + " — guárdalo como prueba de tu compra."
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
