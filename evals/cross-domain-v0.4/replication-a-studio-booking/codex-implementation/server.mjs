import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, normalize, resolve } from 'node:path';
const root = resolve('.'); const types = { '.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8' };
createServer((request, response) => { const pathname = request.url === '/' ? '/index.html' : request.url.split('?')[0]; const file = resolve(root, `.${normalize(pathname)}`); if (!file.startsWith(root) || !existsSync(file) || !statSync(file).isFile()) { response.writeHead(404, {'content-type':'text/plain; charset=utf-8'}); response.end('Not found'); return; } response.writeHead(200, {'content-type': types[extname(file)] || 'application/octet-stream'}); createReadStream(file).pipe(response); }).listen(4173, '127.0.0.1', () => console.log('Studio Booking prototype: http://127.0.0.1:4173'));
