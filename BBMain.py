import os, logging, sys

#
# Set up logging
#
log_format = '%(asctime)s %(levelname)s %(module)s: %(message)s'
log_level = logging.INFO
log_datefmt = '%m/%d/%y %H:%M:%S'
log_handlers = [logging.FileHandler("bb.log")]
for arg in sys.argv:
	if arg == '-h':
		print('useage:\n\t-h (help)\n\t-l (log to stdout)');
		sys.exit(0)
	if arg == '-l':
		log_handlers.append(logging.StreamHandler())
logging.basicConfig(format = log_format, level = log_level, datefmt = log_datefmt, handlers = log_handlers)
log = logging.getLogger(__name__)

#
# Import other project modules after log is set up
#
import BBController, BBWebUI

log.info("*********************")
log.info("berry boiler starting")
log.info("*********************")

os.chdir(os.path.dirname(os.path.abspath(__file__))) # change wd to location of script1
log.info("dir = %s", os.getcwd())

controller = BBController.BBController()
wui = BBWebUI.BBWebUI(controller)

controller.start() # runs in new thread
wui.start() # runs in this (main) thread

controller.shutdown()
controller.join()

log.info("berry boiler main thread ending")