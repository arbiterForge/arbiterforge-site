/* CI preview: serve the composed output, never source templates. */
const { createServer } = require('node:http');
const { readFile, stat, realpath } = require('node:fs/promises');
const { resolve, sep, extname } = require('node:path');
const { gzipSync } = require('node:zlib');
const root = resolve(process.env.SITE_ROOT || '../../_site');
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.avif': 'image/avif', '.woff2': 'font/woff2',
  '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
};
async function sendFile(request, response, path, status = 200) {
  const actual = await realpath(path);
  if (!actual.startsWith(root + sep)) throw new Error('Path outside output');
  let body = await readFile(actual);
  const type = types[extname(actual)] || 'application/octet-stream';
  const headers = { 'Content-Type': type, 'Cache-Control': 'no-cache' };
  if (/(text|javascript|json|xml)/.test(type) && /\bgzip\b/.test(request.headers['accept-encoding'] || '')) {
    body = gzipSync(body); headers['Content-Encoding'] = 'gzip'; headers.Vary = 'Accept-Encoding';
  }
  headers['Content-Length'] = body.length;
  response.writeHead(status, headers);
  response.end(request.method === 'HEAD' ? undefined : body);
}
createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname);
    let path = resolve(root, '.' + pathname);
    if (path !== root && !path.startsWith(root + sep)) throw new Error('Path outside output');
    const info = await stat(path);
    if (info.isDirectory()) {
      if (!pathname.endsWith('/')) { response.writeHead(301, { Location: pathname + '/' }); response.end(); return; }
      path = resolve(path, 'index.html');
    }
    await sendFile(request, response, path);
  } catch (_) {
    try { await sendFile(request, response, resolve(root, '404.html'), 404); }
    catch (_) { response.writeHead(404); response.end('Not found'); }
  }
}).listen(4174, '127.0.0.1', () => console.log('Composed site ready on http://127.0.0.1:4174'));
