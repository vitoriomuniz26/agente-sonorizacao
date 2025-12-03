// Service Worker para PWA - AudioAgora Sonorização
const CACHE_NAME = 'audioagora-v1';
const urlsToCache = [
    '/',
    '/static/style.css',
    '/static/audioagorasonorização+-640w (2).png',
    '/static/manifest.json'
];

// Instalação do Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker: Instalando...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: Cache aberto');
                return cache.addAll(urlsToCache);
            })
            .catch(err => console.log('Service Worker: Erro ao cachear:', err))
    );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker: Ativado');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log('Service Worker: Limpando cache antigo');
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
    // Não cachear requisições POST (formulários)
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Retorna do cache se encontrado
                if (response) {
                    return response;
                }
                // Senão, busca da rede
                return fetch(event.request);
            })
            .catch(() => {
                // Se offline e não estiver no cache, retorna página offline
                console.log('Service Worker: Offline, recurso não encontrado no cache');
            })
    );
});
