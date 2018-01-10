import os,logging

log = logging.getLogger(__name__)

import BBController
import BBWebUI

## change working directory to where script is
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\n------------------")
print("-- berry_boiler --")
print("------------------")

print("pwd =", os.getcwd())

controller = BBController.BBController()
wui = BBWebUI.BBWebUI(controller)

controller.start() # runs in new thread
wui.start() # runs in this (main) thread

# send shutdown to controller
controller.shutdown()