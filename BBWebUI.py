import logging
log = logging.getLogger(__name__)

import os, json, random
import bjoern
import bottle
import BBSettings, BBController, BBWebPush, BBUtils, BBAuth

app = bottle.Bottle()
bottle.debug(True)

@app.hook("before_request")
def before_request():
	#client_ip = bottle.request.environ['HTTP_X_REAL_IP']
	client_ip = bottle.request.remote_route[0]
	log.info("<%s %s> from %s", bottle.request.method, bottle.request.url, client_ip)
	
	if client_ip == "127.0.0.1" or bottle.request.path.startswith(("/login", "/static")):
		return None
	
	log.info("cookies = %s", str(bottle.request.cookies.__dict__))
	log.info("auth_sess = %s", str(app.authorised_sessions))
	
	session_key = bottle.request.cookies.get(app.settings.get('cookie_name'))
	
	if not session_key:
		log.info("No session, redirected")
		return bottle.redirect("/login")
	
	if session_key not in app.authorised_sessions:
		log.info("Session not authorised, redirected")
		return bottle.redirect("/login")
	
	log.info("Authorised " + session_key)

@app.route("/login", method=['GET', 'POST'])
def login():
	if 'pw' not in bottle.request.forms:
		return bottle.template("templates/login.html")
	
	if bottle.request.forms['pw'] != app.settings.get('session_password'):
		return bottle.template("templates/login.html", error="Wrong password")
	
	cookie_name = app.settings.get('cookie_name')
	cookie_ttl = app.settings.get('cookie_ttl')
	session_key = BBUtils.random_token(32)
	app.authorised_sessions.append(session_key)	
	bottle.response.set_cookie(cookie_name, session_key, max_age=cookie_ttl)
	return bottle.redirect("/")

@app.route("/logout")
def logout():
	app.authorised_sessions = []
	bottle.response.set_cookie(app.settings.get('cookie_name'), "", expires=0)
	return bottle.redirect("/login")

@app.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root='static/')

@app.route("/sw.js")
def server_worker():
	return bottle.static_file("sw.js", root='static/')

@app.route("/")
def index():
	context = {
		'json_data' : app.controller.get_status_json(),
		'json_settings' : app.settings.get_json(),
		'random_token' : BBUtils.random_token(4)
	}
	return bottle.template("templates/index.html", **context)

@app.route("/settings")
def settings():
	context = {
		'json_settings' : app.settings.get_json(),
		'random_token' : BBUtils.random_token(4)
	}
	return bottle.template("templates/settings.html", **context)

@app.route("/save_setting/<key>/<value>")
def save_setting(key, value):
	app.settings.set(key, value)
	return "ok"

@app.route("/get_status")
def get_status():
	return app.controller.get_status_json()

@app.route("/set_override_event/<start:int>/<end:int>/<temp:float>")
def set_override_event(start, end, temp):
	app.controller.set_override_event(start, end, float(temp))
	return app.controller.get_status_json()

@app.route("/del_override_event")
def del_override_event():
	app.controller.del_override_event()
	return app.controller.get_status_json()

@app.route("/toggle/<i>")
def toggle(i):
	app.controller.toggle()
	return "ok"

@app.route("/therm/<id>/<t>")
@app.route("/therm/<id>/<t>/<h>")
def thermostat(id, t, h=0):
	app.controller.set_therm_temp(float(t))
	return str(app.settings.get('therm_refresh'))

@app.route("/shutdown")
def shutdown():
	log.info("Shutdown received")
	os.kill(os.getpid(), 2) #send SIGINT (ctrl-c) bjoern to shutdown with cleanup
	return "<p>Shutting down...<p><a href='/'>/index</a><br><a href='/settings'>/settings</a>"

@app.route("/push_subscribe", methods=['POST'])
def push_subscribe():
	sub = json.loads(bottle.request.form['sub_json'])
	BBWebPush.add_subscription(sub['endpoint'], sub['keys']['auth'], sub['keys']['p256dh'])
	return "ok"

@app.route("/reset_default_settings")
def reset_default_settings():
	app.settings.reset_to_defaults()
	return "ok"

@app.route("/button")
def button():
	#BBWebPush.push()
	return "ok"

def start(controller):
	global app
	
	app.controller = controller
	app.settings = controller.settings
	app.authorised_sessions = []
	
	log.info("Starting bjoern server")
	try:
		bjoern.run(app, "127.0.0.1", 8001)
	except (KeyboardInterrupt, TypeError):
		log.info("bjoern received ctrl-c")
	except Exception as e:
		log.exception("bjoern threw exception")
	log.info("Ending bjoern server")
