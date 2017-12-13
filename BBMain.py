import BBController
import BBWebUI

def go():
	controller = BBController.BBController()
	wui = BBWebUI.BBWebUI(controller)
	
	controller.start() # runs in new thread
	wui.start() # runs in this (main) thread
	
	# send shutdown to controller
	controller.shutdown()
	
if __name__ == "__main__":
	go()