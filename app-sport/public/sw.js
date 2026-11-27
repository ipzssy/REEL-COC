const C = "fitbeat-v1", FILES = ["./", "index.html", "app.js", "style.css", "manifest.json", "icon.svg", "music/playlist.json"];
self.addEventListener("install", (e) => e.waitUntil(caches.open(C).then((c) => c.addAll(FILES))));
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
