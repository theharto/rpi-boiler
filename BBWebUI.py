from datetime import datetime
import flask
import time, os, signal, sys, threading, bjoern
import BBSharedData
from termcolor import cprint

def build_JSON_data(d):
	with d:
		json = '{ "mode":"%s", "server_time":%d,' % (d.mode, int(time.time()))
		json += ' "boiler_on":%d, "pending":%d,' % (d.boiler_on, d.pending)
		
		if d.mode == "count":
			json += ' "countdown_off_time":%d, ' % (int(d.countdown_off_time))
		elif d.mode == "therm":
			json += ' "target_temp":%.1f, ' % (d.target_temp)
		
		json += ' "thermometer_temp":%.1f, "thermometer_update_time":%d }' % (d.thermometer_temp, int(d.thermometer_update_time))
	return json

def build_JSON_settings(d):
	with d:
		return d.settings.toJSON()

class BBWebUI:
	def __init__(self, data, controller):
		print ("BBWebUI.init(", self, ")")
		self.data = data
		self.controller = controller
		self.app = flask.Flask("BerryBoiler")
		self.app.secret_key = 'josephine'
		self.app.config['TEMPLATES_AUTO_RELOAD'] = True
		
		@self.app.before_request
		def before_request():
			cprint(flask.request, "yellow")

		@self.app.route("/")
		def index():
			context = {
				'json_data' : build_JSON_data(self.data),
				'json_settings' : build_JSON_settings(self.data),
			}
			return flask.render_template("index.html", **context)
		
		@self.app.route("/settings")
		def settings():
			context = {
				'json_settings' : build_JSON_settings(self.data),
			}
			return flask.render_template("settings.html", **context)
			
		@self.app.route("/save_setting/<string:key>/<value>")
		def save_setting(key, value):
			self.data.settings.set(key, value)
			return "ok"
		
		@self.app.route("/get_status")
		def get_status():
			return build_JSON_data(self.data)
			
		@self.app.route("/boiler_on/<int:on>")
		def boiler_on(on):
			t = 100.0 if on else 0
			self.controller.add_event("0:0:0", "23:59:59", t, override=True)
	
		@self.app.route("/thermometer/<int:temp>")
		@self.app.route("/thermometer/<float:temp>")
		def thermostat(temp):
			temp = float(temp)
			self.controller.set_thermometer_temp(temp)
			return str(self.data.settings.thermometer_refresh)
			
		@self.app.route("/shutdown")
		def shutdown():
			#self.controller.shutdown()
			cprint("Shutting down...", "yellow")
			time.sleep(0.1) #yield to controller thread to cleanup gpios
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
