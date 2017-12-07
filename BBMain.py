#from BBSharedData import *
import BBSharedData
import BBController
import BBWebUI

def go():
	data = BBSharedData.BBSharedData()
	controller = BBController.BBController(data)
	wui = BBWebUI.BBWebUI(data, controller)
	
	controller.start() # runs in new thread
	wui.start() # runs in this (main) thread
	
	# send shutdown to controller
	controller.shutdown()
	
if __name__ == "__main__":
	go()