from datetime import datetime
import time, os, signal, sys, threading, bjoern, flask
from termcolor import cprint

import BBSettings, BBController

class BBWebUI:
	def __init__(self, controller):
		print ("BBWebUI.init(", self, ")")
		self.controller = controller
		self.app = flask.Flask("BerryBoiler")
		self.app.secret_key = 'josephine'
		self.app.config['TEMPLATES_AUTO_RELOAD'] = True
		
		@self.app.before_request
		def before_request():
			cprint(flask.request.environ['HTTP_X_REAL_IP'] + ":" + str(flask.request), "yellow")

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
			
		@self.app.route("/set_override_event/<int:start>/<int:end>/<float:temp>")
		def set_override_event(start, end, temp):
			self.controller.set_override_event(start, end, temp)
			return self.controller.get_status_json()
	
		@self.app.route("/thermometer/<int:temp>")
		@self.app.route("/thermometer/<float:temp>")
		def thermostat(temp):
			temp = float(temp)
			self.controller.set_thermometer_temp(temp)
			return str(self.controller.settings.get('thermometer_refresh'))
			
		@self.app.route("/shutdown")
		def shutdown():
			self.controller.shutdown()
			cprint("Shutting down...", "yellow")
			self.controller.join()
			os.kill(os.getpid(), signal.SIGINT) #signal bjoern to shutdown with cleanup
			return "<p>Shutting down...<p><a href='/'>/index</a><br><a href='/settings'>/settings</a>"

	def start(self):
		cprint("Starting bjoern server", "yellow")
		try:
			bjoern.run(self.app, "0.0.0.0", 8001)
		except (KeyboardInterrupt, TypeError):
			cprint("CTRL-C", "magenta")
			pass
		cprint("Ending bjoern server", "yellow")
