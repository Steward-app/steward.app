// Load libraries needed by core site
import jquery from 'jquery';
import parsleyjs from 'parsleyjs';
import bootstrap from 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

(function() {
  if('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
               .then(function(registration) {
               console.log('Service Worker Registered');
               return registration;
      })
      .catch(function(err) {
        console.error('Unable to register service worker.', err);
      });
      navigator.serviceWorker.ready.then(function(registration) {
        console.log('Service Worker Ready');
      });
    });
  }
})();

let deferredPrompt;
const btnAdd = document.querySelector('#btnAdd');

window.addEventListener('beforeinstallprompt', (e) => {
  console.log('beforeinstallprompt event fired');
  e.preventDefault();
  deferredPrompt = e;
  btnAdd.style.visibility = 'visible';
});

window.addEventListener('appinstalled', (evt) => {
  app.logEvent('app', 'installed');
});

// register Parsley
jquery('form').parsley({ successClass: 'is-valid', errorClass: 'is-invalid'});
