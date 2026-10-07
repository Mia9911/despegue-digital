#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BATERÍA DE PRUEBAS DEL BOT (QA) — El Económico 25/9
Inyecta updates falsos al cerebro del bot (sin tocar Telegram real)
y captura TODO lo que respondería. Re-ejecutable en cada REVISION.
"""
import urllib.request, urllib.error, json, io, os
from datetime import datetime, timedelta

# ------------------ CASOS DE PRUEBA (como clientes reales) ------------------
U = lambda uid, m: {"update_id": uid, **m}
def msg(uid, text, chat_id=111, chat_type="private", nombre="Pedro", username="pedro86", extra=None):
    m = {"message_id": uid, "from": {"first_name": nombre, "username": username},
         "chat": {"id": chat_id, "type": chat_type, "title": "Grupo Test" if chat_type != "private" else ""},
         "date": 0}
    if text is not None: m["text"] = text
    if extra: m.update(extra)
    return {"update_id": uid, "message": m}

UPDATES = [
    msg(9001, "/start"),                                          # 1 cliente nuevo
    msg(9002, "precio"),                                          # 2 precios
    msg(9003, "cuanto cuesta el kit"),                            # 3 precios (variante)
    msg(9004, "quiero una muestra gratis"),                       # 4 muestra
    msg(9005, "plantilla"),                                       # 5 info plantillas
    msg(9006, "ya pague plantilla"),                              # 6 ENTREGA plantillas
    msg(9030, "cuanto cuesta el kit de menu?"),                   # 30 info KIT MENÚ PRO
    msg(9031, "pagué kit"),                                       # 30b ENTREGA kit menú
    msg(9007, "ya pague"),                                        # 7 ENTREGA kit + recibo + bonus
    msg(9008, "quiero comprar el pack"),                          # 8 interesado → links cobro
    msg(9009, "⭐⭐⭐⭐⭐ excelente servicio"),                     # 9 calificar
    msg(9010, "precio", chat_id=-100999, chat_type="supergroup"), # 10 grupo CON keyword → responde
    msg(9011, "hola a todos", chat_id=-100999, chat_type="supergroup"), # 11 grupo SIN keyword → callado
    msg(9012, None, chat_id=-100999, chat_type="supergroup", extra={"sender_chat": {"id": -100999}}), # 12 servicio vacío → sin crash
    msg(9013, None, extra={"photo": [{"file_id": "x"}]}),         # 13 foto → confirmación + aviso
    msg(9014, "hola", chat_id=1227661387, nombre="Mia", username="jefa"),  # 14 la Jefa → su menú
    msg(9015, "PREMIO KIT15"),                                     # 15 ganador ruleta → SU link de cobro
    msg(9016, "quiero patrocinio para mi marca"),                  # 16 sponsor → info + aviso a Jefa
    msg(9017, "imperio"),                                          # 17 boost → info + SU link $2
    msg(9018, "ya pague imperio"),                                 # 18 pagó boost → código IMPERIOX2
    msg(9019, "arena"),                                            # 19 torneo → info con bolsa
    msg(9020, "arena 3470"),                                       # 20 reporta marca → confirmación + aviso
    msg(9021, "donar"),                                            # 21 donación → link $1
    msg(9022, "bolsa +5", chat_id=1227661387, nombre="Mia", username="jefa"),  # 22 Jefa suma a la bolsa
    msg(9023, "cuanto cuesta el pago seguro"),                  # 23 pago seguro → info (gana a 'cuanto')
    msg(9024, "quiero usar escrow para una venta"),             # 24 escrow → info + aviso a Jefa
]

# ------------------ MONKEYPATCH (Internet falso) ------------------
SENT = []
class FakeResp:
    def __init__(self, data): self._d = data.encode() if isinstance(data, str) else data
    def read(self): return self._d
    def __enter__(self): return self
    def __exit__(self, *a): return False

real_urlopen = urllib.request.urlopen
def fake_urlopen(req, timeout=None):
    url = getattr(req, "full_url", str(req))
    if "getUpdates" in url:
        return FakeResp(json.dumps({"ok": True, "result": UPDATES}))
    if "sendMessage" in url:
        SENT.append(json.loads(req.data.decode()))
        return FakeResp(json.dumps({"ok": True, "result": {"message_id": len(SENT)}}))
    if "api.github.com" in url:
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, io.BytesIO(b'{"message":"Not Found"}'))
    if "create_invoice" in url:
        return FakeResp(json.dumps({"url": "https://www.qvapay.com/pay/test-invoice", "transaction_uuid": "t"}))
    if "api.qvapay.com" in url:
        return FakeResp(json.dumps({"transactions": []}))
    if "visitor-badge" in url:
        return FakeResp('<svg xmlns="http://www.w3.org/2000/svg"><text>99</text></svg>')
    if "api.laborx.com" in url:
        if "simple-jobs/list" in url:
            return FakeResp(json.dumps({"code": 200, "result": {"jobs": [
                {"id": 99001, "slug": "community-moderator-for-crypto-99001", "stage": 1,
                 "name": "Community moderator for crypto", "budget": 20,
                 "description": "Need a Telegram community moderator, daily engagement, spanish a plus.",
                 "first_published_at": (datetime.utcnow() - timedelta(minutes=40)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 3}},
                {"id": 99002, "slug": "old-instagram-marketing-99002", "stage": 1,
                 "name": "Instagram marketing", "budget": 100,
                 "description": "Social media marketing manager for my brand, content creation.",
                 "first_published_at": (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 1}},
                {"id": 99003, "slug": "telegram-growth-helper-99003", "stage": 1,
                 "name": "Telegram growth helper", "budget": 30,
                 "description": "I have a developer account with old live account for sale, anydesk needed.",
                 "first_published_at": (datetime.utcnow() - timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 0}},
            ]}}))
        if "vacancy/list" in url:
            return FakeResp(json.dumps({"code": 200, "result": {"vacancies": [
                {"id": 88001, "slug": "remote-community-manager-88001", "stage": 1, "position_remote": 1,
                 "name": "Community Manager (Remote)", "salary_from": 1200, "salary_to": 2400, "salary_type": 1,
                 "description": "Manage our Telegram and Discord community, social media content weekly.",
                 "created_at": (datetime.utcnow() - timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 2}},
                {"id": 88003, "slug": "remote-marketing-vp-88003", "stage": 1, "position_remote": 1,
                 "name": "VP Marketing and social media", "salary_from": 95000, "salary_to": 155000, "salary_type": 1,
                 "description": "Lead our marketing team, social media strategy, community growth, senior leadership.",
                 "created_at": (datetime.utcnow() - timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 0}},
                {"id": 88002, "slug": "office-marketing-assistant-88002", "stage": 1, "position_remote": 0,
                 "name": "Marketing assistant office", "salary_from": 0, "salary_to": 0,
                 "description": "Community manager in our office in Berlin, full time on site.",
                 "created_at": (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                 "user": {"reviews_count": 0}},
            ]}}))
        return FakeResp(json.dumps({"code": 200, "result": {"views": 7, "chat_clicks": 1}}))
    return real_urlopen(req, timeout=timeout)

# ------------------ EJECUTAR EL CEREBRO REAL ------------------
urllib.request.urlopen = fake_urlopen
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test:test")
os.environ.setdefault("PRUEBA_TEST", "1")
os.environ.setdefault("QVAPAY_APP_ID", "qa-id")
os.environ.setdefault("QVAPAY_APP_SECRET", "qa-secret")
src = open(os.path.join(os.path.dirname(__file__), "bot-cycle.py"), encoding="utf-8").read()
try:
    exec(compile(src, "bot-cycle.py", "exec"), {"__name__": "__main__"})
    CRASH = None
except Exception as e:
    CRASH = "%s: %s" % (type(e).__name__, e)
urllib.request.urlopen = real_urlopen

# ------------------ EVALUACIÓN ------------------
def to(cid):  # respuestas enviadas a un chat
    return [s["text"] for s in SENT if s["chat_id"] == cid]
JEFA = 1227661387
GRUPO = -100999
CLI = 111

tests = []
def t(nombre, cond): tests.append((nombre, bool(cond)))

r = to(CLI)
t("1. /start → saludo de bienvenida", any("bienvenid" in x.lower() or "despegue" in x.lower() for x in r[:2]))
t("1b. /start → aviso VISITA NUEVA a la Jefa", any("VISITA NUEVA" in x for x in to(JEFA)))
t("2. 'precio' → menú de precios", any("$9" in x or "Kit Exprés" in x for x in r))
t("3. 'cuanto cuesta' → precios (keyword)", sum(1 for x in r if "$9" in x or "Kit Exprés" in x) >= 2)
t("4. 'muestra gratis' → info de muestra", any("muestra" in x.lower() and ("2 piezas" in x.lower() or "gratis" in x.lower()) for x in r))
t("5. 'plantilla' → info + link de pago", any("90e8b817" in x for x in r))
t("6. 'ya pague plantilla' → ENTREGA (link producto)", any("plantillas-whatsapp.html" in x for x in r))
t("6b. …y aviso a la Jefa del pago $4", any("PLANTILLAS" in x and "$4" in x for x in to(JEFA)))
t("7. 'ya pague' → kit + RECIBO + BONUS plantillas", any("RECIBO Nº" in x and "plantillas-whatsapp.html" in x for x in r))
t("7b. …y aviso PAGÓ a la Jefa", any("PAGÓ" in x for x in to(JEFA)))
t("8. 'quiero comprar' → cierre con links de cobro", any("qvapay.com/pay" in x for x in r))
t("8b. …y aviso CLIENTE INTERESADO", any("CLIENTE INTERESADO" in x for x in to(JEFA)))
t("9. estrellas → invitación a calificar", any("calific" in x.lower() for x in r))
t("10. grupo 'precio' → responde EN el grupo", any("$9" in x or "Kit Exprés" in x for x in to(GRUPO)))
t("11. grupo sin keyword → bot CALLADO (no spam)", not any("Gracias por escribir" in x for x in to(GRUPO)))
t("12. mensaje de servicio vacío → SIN CRASH", CRASH is None)
t("13. foto → confirmación + aviso a Jefa", any("Foto recibida" in x for x in r) and any("foto" in x.lower() for x in to(JEFA)))
t("14. Jefa → su menú de jefa (TXT_JEFA)", any("jefa" in x.lower() or "comando" in x.lower() or "REVISION" in x for x in to(JEFA)))
t("15. CERO falsos 'Gracias por escribir' en grupo", not any(x.startswith("¡Gracias por escribir") for x in to(GRUPO)))
t("16. El cerebro corrió completo SIN morir", CRASH is None)
t("17. 'PREMIO KIT15' → SU link de cobro con descuento", any("test-invoice" in x for x in r))
t("17b. …y aviso a la Jefa del premio con link generado", any("KIT15" in x and "link" in x.lower() for x in to(JEFA)))
t("19. 'patrocinio' → info de anuncios + aviso PATROCINIO a la Jefa", any("RED DESPEGUE" in x for x in r) and any("PATROCINIO" in x for x in to(JEFA)))
t("20. 'imperio' → info BOOST + SU link $2 + aviso", any("PAQUETE EMPRESARIO" in x and "test-invoice" in x for x in r) and any("BOOST" in x for x in to(JEFA)))
t("21. 'ya pague imperio' → código IMPERIOX2 + aviso VENTA BOOST", any("IMPERIOX2" in x for x in r) and any("VENTA BOOST" in x for x in to(JEFA)))
t("22. 'arena' → info del torneo con bolsa", any("LA ARENA" in x and "$" in x for x in r))
t("23. 'arena 3470' → marca registrada + aviso con puntos", any("Marca registrada" in x and "3470" in x for x in r) and any("3470" in x for x in to(JEFA)))
t("24. 'donar' → link de donación $1", any("BOLSA" in x.upper() and "test-invoice" in x for x in r))
t("25. Jefa 'bolsa +5' → intento de actualización (o aviso de reintento)", any("bolsa" in x.lower() or "BOLSA" in x for x in to(JEFA)))
t("26. 'cuanto cuesta el pago seguro' → info PAGO SEGURO (no precios)", any("PAGO SEGURO DESPEGUE" in x for x in r))
t("27. 'escrow' → info + aviso TRANSACCIÓN a la Jefa", any("PAGO SEGURO" in x for x in r) and any("PAGO SEGURO" in x for x in to(JEFA)))
t("28. REPORTE DIARIO de la prueba (visitas + cobrado) a la Jefa", any("DE LA PRUEBA" in x and "Visitas" in x for x in to(JEFA)))
t("29. /start promociona la SALA de juegos", any("juegos.html" in x for x in r))
t("30. 'kit de menú' → info KIT MENÚ PRO + link $7", any("KIT MENÚ PRO" in x and "6df3c031" in x for x in r))
t("30b. 'pagué kit' → ENTREGA al instante + aviso $7 a la Jefa", any("kit-menu-pro" in x for x in r) and any("KIT MENÚ PRO" in x and "$7" in x for x in to(JEFA)))
LXAL = [x for x in to(JEFA) if "laborx.com/jobs/" in x or "laborx.com/vacancies/" in x]
t("18. Radar LaborX API: job NUEVO que matchea → alerta con link y $", any("community-moderator-for-crypto" in x and "$20" in x for x in LXAL))
t("18b. …la trampa 'developer account' NO se alerta", not any("telegram-growth-helper" in x for x in LXAL))
t("18c. …job viejo (3 días) NO se alerta", not any("old-instagram-marketing" in x for x in LXAL))
t("18d. …vacante REMOTA que matchea sí se alerta", any("remote-community-manager" in x for x in LXAL))
t("18e. …vacante de OFICINA (no remota) no se alerta", not any("office-marketing-assistant" in x for x in LXAL))
t("18f. …vacante senior de $95k/año no se alerta (no es su nivel)", not any("remote-marketing-vp" in x for x in LXAL))
t("18g. …aviso del monitor de su vitrina LaborX (click chat = siempre)", any("vitrina" in x.lower() for x in to(JEFA)))

print()
print("=" * 56)
ok = sum(1 for _, c in tests if c)
for nombre, cond in tests:
    print(("✅ PASS" if cond else "❌ FAIL"), "|", nombre)
print("=" * 56)
print("RESULTADO: %d/%d pruebas superadas%s" % (ok, len(tests), " — BOT SANO ✅" if ok == len(tests) else " — HAY QUE ARREGLAR ❌"))
if CRASH: print("CRASH:", CRASH)
