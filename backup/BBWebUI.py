from gevent import monkey; monkey.patch_all()
from gevent import wsgi
from gevent.wsgi import WSGIServer
import gevent
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from BBSharedData import *
import werkzeug.serving
import copy

def build_JSON_data(d):
	with d:
		json = '{ "mode":"%s", "time":%d,' % (d.mode, int(time.time()))
		json += ' "boiler_on":%d,' % (d.boiler_on)
		
		if d.mode == "count":
			json += ' "countdown_end":%d, ' % (int(d.countdown_end))
		elif d.mode == "therm":
			json += ' "target_temp":%.1f, ' % (d.target_temp)
		
		json += ' "thermometer_temp":%.1f, "thermometer_update_time":%d }' % (d.thermometer_temp, int(d.thermometer_update_time))
	return json

def build_JSON_settings(d):
	with d:
		return d.settings.toJSON()

class BBWebUI:
	def __init__(self, data, controller):
		print "BBWebUI.init(", self, ")"
		self.data = data
		self.controller = controller
		self.app = Flask("BerryBoiler")
		self.app.secret_key = 'josephine'
		
		@self.app.route("/")
		def index():
			context = {
				'json_data' : build_JSON_data(self.data),
				'json_settings' : build_JSON_settings(self.data),
			}
			return render_template("index.html", **context)
		
		@self.app.route("/settings")
		def settings():
			context = {
				'json_settings' : build_JSON_settings(self.data),
			}
			return render_template("settings.html", **context)
		
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
		
		@self.app.route("/count/<int:seconds>")
		def count(seconds):
			# max 12 hours, minimum 5 minutes
			seconds = min(seconds, 12 * 60 * 60)
			if seconds < (5 * 60):
				seconds = 0
			
			with self.data:
				self.data.mode = "count"
				self.data.countdown_off_time = time.time() + seconds
				self.data.boiler_on = seconds > 0
				response = build_JSON_data(self.data)
			self.data.wake_controller()
			return response
		
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
			return self.data.thermometer_refresh
			
		@self.app.route("/shutdown")
		def shutdown():
			# shutdown via gevent or built-in flask server
			func = request.environ.get('werkzeug.server.shutdown')
			if func is None:
				self.http_server.stop()
			else:
				func()
			self.controller.shutdown()
			return "!! SHUTDOWN !!<p><a href='/'>index</a>"

	#reloader does not seem to work
	#@werkzeug.serving.run_with_reloader
	def start(self):
		print "BBWebUI.start()"
		#self.app.run(host="0.0.0.0", port=80, debug=False) # runs in this thread
		
		# run with gevent server
		self.http_server = WSGIServer(('', 80), self.app)
		self.http_server.serve_forever()
		print "BBWebUI.start() -- ended --"

if __name__ == "__main__":
	import BBMain
	BBMain.go()