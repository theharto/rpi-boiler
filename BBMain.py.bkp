from BBSharedData import *
from BBController import *
from BBWebUI import *

def go():
	data = BBSharedData()
	controller = BBController(data)
	wui = BBWebUI(data, controller)
	
	controller.start() # runs in new thread
	wui.start() # runs in this (main) thread
	
	# send shutdown to controller
	controller.shutdown()
	
if __name__ == "__main__":
	go()