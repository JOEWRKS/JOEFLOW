import fs from 'node:fs';
import { executeCommand } from '@frozen-b-engine';
import { createSeedState } from '@frozen-b-seed';
import { timelineEntriesForRole } from '@frozen-b-selectors';

function clone(value: any): any { return structuredClone(value); }

function decode(value: any): any {
  if (Array.isArray(value)) return value.map(decode);
  if (value && typeof value === 'object') {
    if (Object.keys(value).length === 1 && '$number' in value) {
      if (value.$number === 'NaN') return Number.NaN;
      if (value.$number === '+Infinity') return Number.POSITIVE_INFINITY;
      if (value.$number === '-Infinity') return Number.NEGATIVE_INFINITY;
      throw new Error(`unknown typed number ${value.$number}`);
    }
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, decode(item)]));
  }
  return value;
}

function encode(value: any): any {
  if (typeof value === 'number' && !Number.isFinite(value)) {
    return { $number: Number.isNaN(value) ? 'NaN' : value > 0 ? '+Infinity' : '-Infinity' };
  }
  if (Array.isArray(value)) return value.map(encode);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, encode(item)]));
  return value;
}

function pointerTokens(pointer: string): string[] {
  if (!pointer.startsWith('/')) throw new Error(`invalid setup pointer ${pointer}`);
  return pointer.slice(1).split('/').map((token) => token.replaceAll('~1', '/').replaceAll('~0', '~'));
}

function applyPatch(root: any, patch: any) {
  const tokens = pointerTokens(patch.pointer);
  const leaf = tokens.pop()!;
  let target = root;
  for (const token of tokens) target = target[Array.isArray(target) ? Number(token) : token];
  const value = decode(patch.value);
  if (Array.isArray(target) && leaf === '-') target.push(value);
  else target[Array.isArray(target) ? Number(leaf) : leaf] = value;
}

function targetVersion(state: any, targetId: string): number {
  return state.claims[targetId]?.version
    ?? state.users[targetId]?.version
    ?? state.categories[targetId]?.version
    ?? state.invitations[targetId]?.version
    ?? state.deliveries.find((item: any) => item.id === targetId)?.version
    ?? state.fileGrants.find((item: any) => item.id === targetId)?.version
    ?? 0;
}

function snapshot(state: any, targetId: string) {
  return encode({
    authoritative_state: {
      users: state.users,
      claims: state.claims,
      files: state.files,
      fileGrants: state.fileGrants,
      adjustments: state.adjustments,
      categories: state.categories,
      invitations: state.invitations,
    },
    revision: targetVersion(state, targetId),
    history: state.auditEvents,
    business_side_effects: { warnings: state.warnings, exports: state.exports },
    delivery_effects: state.deliveries,
  });
}

function nonFiniteInputs(value: any, pointer = ''): any[] {
  if (typeof value === 'number' && !Number.isFinite(value)) {
    return [{ pointer: pointer || '/', classification: Number.isNaN(value) ? 'NaN' : value > 0 ? '+Infinity' : '-Infinity' }];
  }
  if (Array.isArray(value)) return value.flatMap((item, index) => nonFiniteInputs(item, `${pointer}/${index}`));
  if (value && typeof value === 'object') return Object.entries(value).flatMap(([key, item]) => nonFiniteInputs(item, `${pointer}/${key.replaceAll('~', '~0').replaceAll('/', '~1')}`));
  return [];
}

test('external JSONL adapter invokes the frozen engine and selectors', () => {
  const requestPath = process.env.JOEWRKS_REQUEST_JSONL!;
  const responsePath = process.env.JOEWRKS_RESPONSE_JSONL!;
  const requests = fs.readFileSync(requestPath, 'utf8').split(/\r?\n/).filter(Boolean).map(JSON.parse);
  let state = createSeedState();
  const responses: any[] = [];
  for (const request of requests) {
    if (request.setup?.reset) state = createSeedState();
    for (const patch of request.setup?.patches ?? []) applyPatch(state, patch);
    const command = decode(request.command);
    const beforeState = clone(state);
    const before = snapshot(beforeState, command.targetId ?? '');
    const wasReplay = Boolean(command.idempotencyKey && state.idempotency[command.idempotencyKey]);
    const runtimeInputs = nonFiniteInputs(command.input ?? {});
    let rawResult: any;
    let query: any;
    if (command.type === 'HARNESS_QUERY_TIMELINE') {
      query = timelineEntriesForRole(state, command.input.role, command.input.actorId);
      rawResult = { state, outcome: { status: 'committed', code: 'QUERY_RESULT', message: 'Actual selector result.', targetVersion: targetVersion(state, command.targetId) }, auditEventIds: [], deliveryEventIds: [], changedFields: [] };
    } else {
      rawResult = executeCommand(state, command);
      state = rawResult.state;
    }
    const after = snapshot(state, command.targetId ?? '');
    const historyDelta = state.auditEvents.slice(beforeState.auditEvents.length);
    const deliveryDelta = state.deliveries.slice(beforeState.deliveries.length);
    const businessChanged = JSON.stringify({ warnings: beforeState.warnings, exports: beforeState.exports }) !== JSON.stringify({ warnings: state.warnings, exports: state.exports });
    responses.push(encode({
      ...request,
      record_kind: 'execution_evidence',
      before,
      result: { ...rawResult.outcome, replay: wasReplay, runtime_non_finite_inputs: runtimeInputs, ...(query ? { query } : {}) },
      after,
      deltas: {
        history: historyDelta,
        business_side_effects: businessChanged ? { before: beforeState.warnings, after: state.warnings } : [],
        delivery_effects: deliveryDelta,
      },
    }));
  }
  fs.writeFileSync(responsePath, responses.map((record) => JSON.stringify(record)).join('\n') + '\n', 'utf8');
});
