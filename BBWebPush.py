from pywebpush import webpush, WebPushException
import logging
log = logging.getLogger(__name__)

VAPID_PUBLIC = "BE7r63OP8ElMToEKBGbWdV3tPFdLfvnchkNFulx-ygWT5TtAYuq45BU7bNanipjhkc46DEyT8hYqtkJixaNFuoI"
VAPID_PRIVATE = "2NPFuZlohuyjzmplHKlMd-St5JNUIUBSBOt5uerq0uo"

subscriptions = []
	
def add_subscription(endpoint, auth, p256dh):
	sub = {}
	sub['endpoint'] = endpoint
	sub['keys'] = {}
	sub['keys']['auth'] = auth
	sub['keys']['p256dh'] = p256dh
	subscriptions.append(sub)
	#log.info("subs = %s", str(subscriptions))
	return

def push():
	log.info("push")
	for sub in subscriptions:
		try:
			r = webpush(sub, data="test push", vapid_private_key=VAPID_PRIVATE, vapid_claims={"sub":"mailto:info@homefire.cf"})
			print("pushed ", r)
		except WebPushException as ex:
			print("Push exception {}", repr(ex))





