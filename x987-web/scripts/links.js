#!/usr/bin/env node
const http = require('http');
const https = require('https');

const targets = [
  { name: 'API', url: 'http://localhost:4000/api/health' },
  { name: 'Ranking', url: 'http://localhost:4000/api/ranking/latest' },
  { name: 'Frontend', url: 'http://localhost:5173/' },
];
const includeStorybook = process.argv.slice(2).includes('storybook');
if (includeStorybook) targets.push({ name: 'Storybook', url: 'http://localhost:6006/' });

function ping(url) {
  return new Promise(resolve => {
    const lib = url.startsWith('https') ? https : http;
    const req = lib.get(url, res => {
      res.resume();
      resolve(res.statusCode && res.statusCode < 500);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(1500, () => { req.destroy(); resolve(false); });
  });
}

async function waitAll() {
  const ready = new Set();
  process.stdout.write('Waiting for services to be ready');
  let dots = 0;
  const tick = setInterval(() => {
    dots = (dots + 1) % 4;
    process.stdout.write('\rWaiting for services to be ready' + '.'.repeat(dots) + ' '.repeat(3 - dots));
  }, 400);

  while (ready.size < targets.length) {
    for (const t of targets) {
      if (ready.has(t.name)) continue;
      const ok = await ping(t.url);
      if (ok) ready.add(t.name);
    }
    await new Promise(r => setTimeout(r, 600));
  }
  clearInterval(tick);

  const link = u => `\u001b]8;;${u}\u001b\\${u}\u001b]8;;\u001b\\`;
  console.log('\n\n\x1b[1mAll services ready\x1b[0m');
  console.log('• API:      ' + link('http://localhost:4000/api/health'));
  console.log('• Ranking:  ' + link('http://localhost:4000/api/ranking/latest'));
  console.log('• Frontend: ' + link('http://localhost:5173/'));
  if (includeStorybook) console.log('• Storybook: ' + link('http://localhost:6006/'));
  console.log('');

  // Auto-open default browser on macOS/Linux/Windows
  try {
    const { exec } = require('child_process');
    const openCmd = process.platform === 'darwin' ? 'open' : process.platform === 'win32' ? 'start' : 'xdg-open';
    exec(`${openCmd} http://localhost:5173/`);
    if (includeStorybook) exec(`${openCmd} http://localhost:6006/`);
  } catch {}
}

waitAll().catch(() => {});
