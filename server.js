#!/usr/bin/env node
/* 道藏九经 · 静态站点服务器 (Node 原生, 零依赖)
 * 用法: node server.js [--port 8123] [--dir ./site] [--host 0.0.0.0]
 * 特性: 正确 MIME(Content-Type) / 按需 gzip / ETag 304 / 缓存策略 / 安全头 / 404
 */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { URL } = require('url');

const ROOT = path.resolve(__dirname, process.argv.includes('--dir') ? process.argv[process.argv.indexOf('--dir') + 1] : 'site');
const PORT = parseInt(process.env.PORT || (process.argv.includes('--port') ? process.argv[process.argv.indexOf('--port') + 1] : 8123), 10);
const HOST = process.env.HOST || (process.argv.includes('--host') ? process.argv[process.argv.indexOf('--host') + 1] : '0.0.0.0');

const MIME = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8', '.md': 'text/markdown; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json', '.pdf': 'application/pdf',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf'
};
const isCompressible = t => /text|javascript|json|xml|svg/.test(t);
const acceptsGzip = req => req.headers['accept-encoding'] && req.headers['accept-encoding'].toLowerCase().includes('gzip');

function sendErr(res, code, msg) {
  res.writeHead(code, { 'Content-Type': 'text/plain; charset=utf-8', 'X-Content-Type-Options': 'nosniff' });
  res.end(msg);
}

const server = http.createServer((req, res) => {
  let u;
  try { u = new URL(req.url, 'http://x'); } catch (e) { return sendErr(res, 400, 'Bad Request'); }
  let pathname = decodeURIComponent(u.pathname);
  if (pathname.endsWith('/')) pathname += 'index.html';

  const filePath = path.normalize(path.join(ROOT, pathname));
  if (!filePath.startsWith(ROOT)) return sendErr(res, 403, 'Forbidden');

  fs.stat(filePath, (err, st) => {
    if (err || !st.isFile()) return sendErr(res, 404, '404 Not Found');
    const ext = path.extname(filePath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    const isAsset = pathname.startsWith('/assets/') || /\.(css|js|svg|png|ico|woff2?|webmanifest)$/.test(pathname);
    const headers = {
      'Content-Type': type,
      'Cache-Control': isAsset ? 'public, max-age=31536000, immutable' : 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
      'X-Frame-Options': 'SAMEORIGIN'
    };
    const etag = '"' + st.size.toString(16) + '-' + st.mtimeMs.toString(16) + '"';
    headers['ETag'] = etag;
    if (req.headers['if-none-match'] === etag) {
      res.writeHead(304, headers);
      return res.end();
    }
    fs.readFile(filePath, (e2, data) => {
      if (e2) return sendErr(res, 500, 'Internal Error');
      if (acceptsGzip(req) && data.length > 512 && isCompressible(type)) {
        headers['Content-Encoding'] = 'gzip';
        data = zlib.gzipSync(data);
      }
      headers['Content-Length'] = data.length;
      res.writeHead(200, headers);
      res.end(data);
    });
  });
});

server.listen(PORT, HOST, () => {
  console.log('☯ 道藏九经站点已启动');
  console.log('   本地:   http://127.0.0.1:' + PORT + '/');
  console.log('   目录:   ' + ROOT);
});
