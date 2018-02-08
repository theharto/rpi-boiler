/*
*	service_worker.js
*/

self.addEventListener('install', event => {
	console.log("sw install", event);
});

self.addEventListener('activate', event => {
	console.log("sw activate", event);
});

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

self.addEventListener('notificationclick', event => {
	event.notification.close();	
});

/*
self.addEventListener('fetch', function(event) {
	console.log("fetch", event.request.url);
	if (event.request.url == "https://homefire.cf/?sw") {
		event.respondWith(new Response("Unable to communicate with heating server"));
		return
	}
  
  event.respondWith(
    caches.open('mysite-dynamic').then(function(cache) {
      return cache.match(event.request).then(function (response) {
        return response || fetch(event.request).then(function(response) {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});
*/