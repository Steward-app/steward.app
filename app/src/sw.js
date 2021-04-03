console.log('Hello from sw.js');

import { registerRoute } from 'workbox-routing';
import {
  NetworkFirst,
  StaleWhileRevalidate,
  CacheFirst,
} from 'workbox-strategies';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';
import {ExpirationPlugin} from 'workbox-expiration';

if (registerRoute) {
  console.log(`Yay! Workbox is loaded 🎉`);

  registerRoute(
    ({ request }) =>
      request.destination === 'style' ||
      request.destination === 'script' ||
      request.destination === 'worker',
    new StaleWhileRevalidate({
      cacheName: 'static-resources',
      plugins: [ new CacheableResponsePlugin({ statuses: [200] })]
    }),
  );

  registerRoute(
    /\.(?:png|gif|jpg|jpeg|svg|ico)$/,
    new CacheFirst({
      cacheName: 'images',
      plugins: [
        new ExpirationPlugin({
          maxEntries: 60,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 Days
        }),
      ],
    }),
  );
} else {
  console.log(`Boo! Workbox didn't load 😬`);
}
