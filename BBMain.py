import os, logging, sys, threading

#
# Handle args
#
log_to_stdout = False
stderr_to_log = True
for arg in sys.argv:
	if arg == '-h':
		print('useage:\n\t-h (help)\n\t-l (log to stdout)\n\t-e (do not send stderr to log)')
		sys.exit(0)
	if arg == '-l':
		log_to_stdout = True
	if arg == '-e':
		stderr_to_log = False

#
# Set up logging
#
log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
log_level = logging.INFO
log_datefmt = '%m/%d/%y %H:%M:%S'
log_handlers = [logging.FileHandler("logs/bb.log")]
if log_to_stdout:
	log_handlers.append(logging.StreamHandler())
logging.basicConfig(format = log_format, level = log_level, datefmt = log_datefmt, handlers = log_handlers)
log = logging.getLogger("BBMain")
# rename levels to 4 char
logging.addLevelName(50, "CRIT")
logging.addLevelName(40, "ERRO")
logging.addLevelName(30, "WARN")
logging.addLevelName(10, "DEBG")

#
# Import other project modules after log is set up
#
import BBController, BBWebUI, BBUtils

if stderr_to_log:
	sys.stderr = BBUtils.ErrorLogger()

log.info("*********************")
log.info("berry boiler starting")
log.info("*********************")

os.chdir(os.path.dirname(os.path.abspath(__file__))) # change wd to location of script1
log.info("dir = %s", os.getcwd())

controller = BBController.BBController()
wui = BBWebUI.BBWebUI(controller)

controller.start() # runs in new thread

log.info("Threads")
for t in threading.enumerate():
	log.info("\t\t" + t.name)

wui.start() # runs in this (main) thread
controller.shutdown()
controller.join()

log.info("berry boiler main thread ending")
log.info("Threads still running:")
for t in threading.enumerate():
	log.info("\t\t" + t.name)
