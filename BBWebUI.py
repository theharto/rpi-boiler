import logging
log = logging.getLogger(__name__)

import os, bjoern, flask, json
import BBSettings, BBController, BBWebPush

class BBWebUI:
	def __init__(self, controller):
		self.controller = controller
		self.app = flask.Flask("BerryBoiler")
		self.app.secret_key = 'josephine'
		self.app.config['TEMPLATES_AUTO_RELOAD'] = True
		
		@self.app.before_request
		def before_request():
			log.info("%s from %s", str(flask.request), flask.request.environ['HTTP_X_REAL_IP'])
		
		@self.app.route("/sw.js")
		def server_worker():
			log.info("here")
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
