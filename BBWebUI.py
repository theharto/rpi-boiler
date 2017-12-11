from datetime import datetime
import flask
import time, os, signal, sys, threading, bjoern
import urllib.request
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
		
def shutting_down():
	print("Shutting down...")
	urllib.request.urlopen("http://127.0.0.1/instant_shutdown")

class BBWebUI:
	def __init__(self, data, controller):
		print ("BBWebUI.init(", self, ")")
		self.data = data
		self.controller = controller
		self.app = flask.Flask("BerryBoiler")
		self.app.secret_key = 'josephine'
		
		@self.app.before_request
		def before_request():
			cprint(flask.request, "yellow")
			flask.request.bb_shutdown = False
		
		@self.app.teardown_request
		def teardown_request(e=None):
			if flask.request.bb_shutdown:
				cprint("Shuting down...", "yellow")
				time.sleep(0.1) #yield to controller thread to cleanup gpios
				#os.kill(os.getpid(), signal.SIGINT)

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
		
		@self.app.route("/set_settings")
		def set_settings():
			with self.data:
				self.data.settings.client_refresh = max(5, min(600, int(request.args.get("client_refresh"))))
				self.data.settings.thermometer_refresh = max(5, min(3600, int(request.args.get("thermometer_refresh"))))
				self.data.settings.controller_tick = max(1, min(600, int(request.args.get("controller_tick"))))
				self.data.settings.debug_mode = ("1" == request.args.get("debug_mode"))
				self.data.settings.test_mode = ("1" == request.args.get("test_mode"))
				self.data.settings.hysteresis = max(0.2, min(2.0, float(request.args.get("hysteresis"))))
				self.data.settings.min_switching = max(30, min(600, int(request.args.get("min_switching"))))
				print ("set_settings ", self.data.settings)
			return build_JSON_settings(self.data)
		
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
			self.controller.shutdown()
			cprint("/shutdown...", "yellow")
			time.sleep(0.1) #yield to controller thread to cleanup gpios
			os.kill(os.getpid(), signal.SIGINT)
			return "<p>Shutting down...<p><a href='/'>/index</a>"


	def start(self):
		print ("Starting bjoern server")
		bjoern.run(self.app, "0.0.0.0", 8001)
		print ("BBWebUI.start() -- ended --")

if __name__ == "__main__":
	import BBMain
	BBMain.go()