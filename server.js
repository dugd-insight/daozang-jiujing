#!/usr/bin/env node
/* 道藏九经 · 静态站点服务器 (Node 原生, 零依赖)
 * 用法: node server.js [--port 8123] [--dir ./site] [--host 0.0.0.0]
 * 特性: 正确 MIME / gzip / 缓存策略 / 安全路径 / 404 / 目录浏览禁止
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

function send(res, code, body, type, extra) {
  const headers = Object.assign({ 'Content-Type': type }, extra || {});
  if (body && !extra || !extra || extra['Content-Encoding'] === undefined) {
    // gzip 文本
    const buf = Buffer.isBuffer(body) ? body : Buffer.from(body, 'utf8');
    if (buf.length > 512 && /text|javascript|json|xml|svg/.test(type)) {
      headers['Content-Encoding'] = 'gzip';
      res.writeHead(code, headers);
      res.end(zlib.gzipSync(buf));
      return;
    }
    headers['Content-Length'] = buf.length;
    res.writeHead(code, headers);
    res.end(buf);
    return;
  }
  res.writeHead(code, headers);
  res.end(body);
}

const server = http.createServer((req, res) => {
  let u;
  try { u = new URL(req.url, 'http://x'); } catch (e) { return send(res, 400, 'Bad Request', 'text/plain; charset=utf-8'); }
  let pathname = decodeURIComponent(u.pathname);
  if (pathname.endsWith('/')) pathname += 'index.html';

  // 安全: 禁止目录穿越
  const filePath = path.normalize(path.join(ROOT, pathname));
  if (!filePath.startsWith(ROOT)) return send(res, 403, 'Forbidden', 'text/plain; charset=utf-8');

  fs.stat(filePath, (err, st) => {
    if (err || !st.isFile()) return send(res, 404, '404 Not Found', 'text/plain; charset=utf-8');
    const ext = path.extname(filePath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    const isAsset = pathname.startsWith('/assets/') || /.(css|js|svg|png|ico|woff2?|webmanifest)$/.test(pathname);
    const headers = {
      'Cache-Control': isAsset ? 'public, max-age=31536000, immutable' : 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
      'X-Frame-Options': 'SAMEORIGIN'
    };
    // 带 ETag 做 304
    const etag = '"' + st.size.toString(16) + '-' + st.mtimeMs.toString(16) + '"';
    headers['ETag'] = etag;
    if (req.headers['if-none-match'] === etag) {
      res.writeHead(304, headers);
      return res.end();
    }
    fs.readFile(filePath, (e2, data) => {
      if (e2) return send(res, 500, 'Internal Error', 'text/plain; charset=utf-8');
      headers['Content-Length'] = data.length;
      if (data.length > 512 && /text|javascript|json|xml|svg/.test(type)) {
        headers['Content-Encoding'] = 'gzip';
        res.writeHead(200, headers);
        return res.end(zlib.gzipSync(data));
      }
      res.writeHead(200, headers);
      res.end(data);
    });
  });
});

server.listen(PORT, HOST, () => {
  console.log('☯ 道藏九经站点已启动');
  console.log('   本地:   http://127.0.0.1:' + PORT + '/');
  console.log('   目录:   ' + ROOT);
  console.log('   Ctrl+C 停止');
});
