import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const text = (file) => readFileSync(resolve(root, file), 'utf8');

test('browser source has semantic landmarks, live feedback, dialog confirmation, responsive and reduced-motion support', () => {
  const html = text('index.html'); const css = text('styles.css'); const app = text('src/app.js');
  assert.match(html, /<main/); assert.match(html, /<nav/); assert.match(html, /aria-live=/);
  assert.match(app, /<dialog/); assert.match(app, /data-screen-id/); assert.match(app, /data-action/);
  assert.match(css, /prefers-reduced-motion/); assert.match(css, /@media \(max-width: 700px\)/); assert.match(css, /:focus-visible/);
});

test('browser source states its explicit prototype boundaries', () => {
  assert.match(text('index.html'), /시뮬레이션|검증되지 않음/);
});
