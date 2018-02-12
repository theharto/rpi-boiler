import logging
log = logging.getLogger(__name__)

import os, bjoern, flask, json, random
import BBSettings, BBController, BBWebPush, BBUtils

SESSION_COOKIE_NAME = "rpi-boiler_session"
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60 # 30 days

class BBWebUI:
	def __init__(self, controller):
		self.controller = controller
		self.app = flask.Flask("BerryBoiler")
		self.app.config['TEMPLATES_AUTO_RELOAD'] = True		
		self.authorised_sessions = {}
		
		@self.app.before_request
		def before_request():
			client_ip = flask.request.environ['HTTP_X_REAL_IP']
			log.info("%s from %s", str(flask.request), client_ip)
			
			if client_ip == "127.0.0.1" or flask.request.path.startswith(("/login", "/static", "/logout")):
				return None
			
			log.info("cookies = %s", str(flask.request.cookies))
			log.info("auth_sess = %s", str(self.authorised_sessions))
			
			session = flask.request.cookies.get(SESSION_COOKIE_NAME)
			log.info("Session = %s", session)
			
			if not session:
				log.info("No session, redirected")
				return flask.redirect("/login", code=302)
			
			if session not in self.authorised_sessions:
				log.info("Session not authorised, redirected")
				return flask.redirect("/login", code=302)
				
			if self.authorised_sessions[session] != client_ip:
				log.info("Client IP does not match login")
				return flask.redirect("/login")
			
			log.info("Authorised " + session)
		
		@self.app.route("/login", methods=['GET', 'POST'])
		def login():
			context = {}
			
			if 'pw' in flask.request.form:
				if flask.request.form['pw'] == self.controller.settings.get('session_password'):
					client_ip = flask.request.environ['HTTP_X_REAL_IP']
					session_hash = BBUtils.session_hash(self.controller.settings.get('crypto_key'), client_ip)
					self.authorised_sessions[session_hash] = client_ip
					resp = flask.redirect("/")
					resp.set_cookie(SESSION_COOKIE_NAME, session_hash, SESSION_COOKIE_AGE)
					print("resp? = %s", str(resp))
					return resp
				else:
					context['error'] = "Wrong password"
			
			return flask.render_template("login.html", **context)
		
		@self.app.route("/logout")
		def logout():
			self.authorised_sessions = []
			return flask.redirect("/login")
		
		@self.app.route("/sw.js")
		def server_worker():
			return flask.send_file("static/sw.js")
		
		@self.app.route("/")
		def index():
			context = {
				'json_data' : self.controller.get_status_json(),
				'json_settings' : self.controller.settings.get_json()
			}
			return flask.render_template("index.html", **context)
		
		@self.app.route("/settings")
		def settings():
			context = {
				'json_settings' : self.controller.settings.get_json()
			}
			return flask.render_template("settings.html", **context)
			
		@self.app.route("/save_setting/<string:key>/<value>")
		def save_setting(key, value):
			self.controller.settings.set(key, value)
			return "ok"
		
		@self.app.route("/get_status")
		def get_status():
			return self.controller.get_status_json()
		
		@self.app.route("/set_override_event/<int:start>/<int:end>/<temp>")
		def set_override_event(start, end, temp):
			self.controller.set_override_event(start, end, float(temp))
			return self.controller.get_status_json()
		
		@self.app.route("/del_override_event")
		def del_override_event():
			self.controller.del_override_event()
			return self.controller.get_status_json()
		
		@self.app.route("/therm/<string:id>/<t>")
		@self.app.route("/therm/<string:id>/<t>/<h>")
		def thermostat(id, t, h=0):
			self.controller.set_therm_temp(float(t))
			return str(self.controller.settings.get('therm_refresh'))
		
		@self.app.route("/shutdown")
		def shutdown():
			log.info("Shutdown received")
			os.kill(os.getpid(), 2) #send SIGINT (ctrl-c) bjoern to shutdown with cleanup
			return "<p>Shutting down...<p><a href='/'>/index</a><br><a href='/settings'>/settings</a>"
			
		@self.app.route("/push_subscribe", methods=['POST'])
		def push_subscribe():
			sub = json.loads(flask.request.form['sub_json'])
			BBWebPush.add_subscription(sub['endpoint'], sub['keys']['auth'], sub['keys']['p256dh'])
			return "ok"
		
		@self.app.route("/button")
		def button():
			#BBWebPush.push()
			return "ok"
			
	def start(self):
		log.info("Starting bjoern server")
		try:
			bjoern.run(self.app, "127.0.0.1", 8001)
		except (KeyboardInterrupt, TypeError):
			log.info("bjoern received ctrl-c")
		except Exception as e:
			log.exception("bjoern threw exception")
		log.info("Ending bjoern server")
