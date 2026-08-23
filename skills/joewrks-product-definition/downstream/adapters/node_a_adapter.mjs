import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const requestPath = process.env.JOEWRKS_REQUEST_JSONL;
const responsePath = process.env.JOEWRKS_RESPONSE_JSONL;
const sourceRoot = process.env.JOEWRKS_FROZEN_SOURCE_ROOT;
if (!requestPath || !responsePath || !sourceRoot) throw new Error('JSONL paths and frozen source root are required');

const requests = fs.readFileSync(requestPath, 'utf8').split(/\r?\n/).filter(Boolean).map(JSON.parse);

function node() {
  return { innerHTML: '', textContent: '', className: '', value: '', dataset: {}, setAttribute() {}, focus() {} };
}

const app = node();
const nav = node();
const controls = node();
const status = node();
const role = node();
role.value = 'Customer';
const loseAuthority = node();
const heading = node();
const reason = node();
globalThis.document = {
  querySelector(selector) {
    return {
      '#app': app,
      '#screen-nav': nav,
      '#role-controls': controls,
      '#status': status,
      '#role': role,
      '#lose-authority': loseAuthority,
      '#screen-heading': heading,
      '#reason': reason,
    }[selector] ?? node();
  },
};

await import(pathToFileURL(path.join(sourceRoot, 'src', 'app.js')).href);

function readback() {
  const match = app.innerHTML.match(/<pre class="state-readback"[^>]*>([\s\S]*?)<\/pre>/);
  if (!match) throw new Error('public UI did not render state readback');
  return JSON.parse(match[1]);
}

function snapshot(value) {
  return {
    authoritative_state: { bookings: value.bookings, policies: value.policies },
    revision: value.version,
    history: [],
    business_side_effects: [],
    delivery_effects: value.deliveries,
  };
}

const responses = [];
for (const request of requests) {
  const beforeValue = readback();
  const action = request.command?.input?.action;
  if (request.command?.type !== 'PUBLIC_ACTION' || typeof action !== 'string') throw new Error('unsupported A adapter command');
  app.onclick({ target: { dataset: { action } } });
  const afterValue = readback();
  const failed = status.className.includes('error');
  responses.push({
    ...request,
    record_kind: 'execution_evidence',
    before: snapshot(beforeValue),
    result: {
      status: failed ? 'rejected' : 'committed',
      code: failed ? 'PUBLIC_ERROR' : 'PUBLIC_SUCCESS',
      visible_status: status.textContent,
      trace: {
        public_invocation: action,
        handler: 'handle',
        domain_command: 'executeAction',
        readback: 'rendered state-readback',
      },
    },
    after: snapshot(afterValue),
    deltas: {
      history: [],
      business_side_effects: [],
      delivery_effects: afterValue.deliveries.slice(beforeValue.deliveries.length),
    },
  });
}

fs.writeFileSync(responsePath, responses.map((record) => JSON.stringify(record)).join('\n') + '\n', 'utf8');
