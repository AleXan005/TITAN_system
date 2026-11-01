const http = require("http");
const fs = require("fs");
const path = require("path");

const PUERTO = 3000;
const API = { host: "localhost", port: 8000 };
const TIPOS = { ".html": "text/html", ".js": "text/javascript", ".jsx": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml" };

http.createServer((req, res) => {
  if (req.url.startsWith("/api/")) {
    const proxy = http.request({ ...API, path: req.url, method: req.method, headers: req.headers }, (r) => {
      res.writeHead(r.statusCode, r.headers);
      r.pipe(res);
    });
    proxy.on("error", () => { res.writeHead(502); res.end(); });
    return req.pipe(proxy);
  }
  const ruta = path.join(__dirname, req.url === "/" ? "index.html" : decodeURIComponent(req.url.split("?")[0]));
  if (!ruta.startsWith(__dirname)) { res.writeHead(403); return res.end(); }
  fs.readFile(ruta, (err, data) => {
    if (err) { res.writeHead(404); return res.end("No encontrado"); }
    res.writeHead(200, { "Content-Type": TIPOS[path.extname(ruta)] || "application/octet-stream" });
    res.end(data);
  });
}).listen(PUERTO, () => console.log(`TITAN frontend en http://localhost:${PUERTO}`));
