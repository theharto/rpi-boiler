from flask import Flask
import platform
import bjoern

application = Flask(__name__)

@application.route("/")
def hello():
	v = platform.python_version()
	print("PYTHON = ", v)
	return "<h1 style='color:blue'>Hello There!" + v + "</h1>"

if __name__ == "__main__":
	#application.run(host='0.0.0.0')
	bjoern.run(application, "0.0.0.0", 8000)