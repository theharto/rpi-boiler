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
		
		@self.app.route("/set_mode/<mode>")
		def set_mode(mode):
			self.controller.set_mode(mode)
			return build_JSON_data(self.data)
		
		@self.app.route("/switch/<string:s>")
		def switch(s):
			self.controller.switch(s == "on")
			return build_JSON_data(self.data)
		
		@self.app.route("/count/<int:off_time>")
		def count(off_time):
			self.controller.count(off_time)
			return build_JSON_data(self.data)
		
		@self.app.route("/therm/<int:temp>")
		@self.app.route("/therm/<float:temp>")
		def therm(temp):
			self.controller.therm(temp)
			return build_JSON_data(self.data)
		
		"""    
		@self.app.route("/add_schedule/<int:on>/<int:off>")
		def add_schedule(on, off):
			flash("on = %d, off = %d" % (on, off))
			#todo - test valid on, off values
			with self.status.lock:
				self.status.schedule.append(BBPeriod(on, off))
			self.wake_controller_thread()
			return redirect(url_for("index"))
		
		@self.app.route("/del_schedule/<int:id>")
		def del_schedule(id):
			with self.status.lock:
				for p in self.status.schedule:
					if p.id == id:
						self.status.schedule.remove(p)
						flash("removed active period [%d]" % id)
			return redirect(url_for("index"))
		"""
	
		@self.app.route("/thermometer/<int:temp>")
		@self.app.route("/thermometer/<float:temp>")
		def thermostat(temp):
			temp = float(temp)
			self.controller.thermometer(temp)
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
		except KeyboardInterrupt:
			pass
		cprint("Ending bjoern server", "yellow")

if __name__ == "__main__":
	import BBMain
	BBMain.go()