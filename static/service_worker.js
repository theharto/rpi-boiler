/*
*	service_worker.js
*/

self.addEventListener('install', event => {
	console.log("sw install", event);
});

self.addEventListener('activate', event => {
	console.log("sw activate", event);
});

self.addEventListener('fetch', event => {
	console.log("sw fetch", event);
	//event.respondWith(new Response("Hello world!"));
});

/*
self.addEventListener('push', function(event) {
	console.log(`sw Push had this data: "${event.data.text()}"`);

	const title = 'Push Codelab';
	const options = {
		body: 'Yay it works.',
		icon: 'images/icon.png',
		badge: 'images/badge.png'
	};
	event.waitUntil(self.registration.showNotification(title, options));
});
*/

self.addEventListener('notificationclick', event => {
	event.notification.close();	
});