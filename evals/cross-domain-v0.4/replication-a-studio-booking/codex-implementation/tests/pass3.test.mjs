import test from 'node:test';
import assert from 'node:assert/strict';
import { ACTION_LABELS, SCREEN_SCHEMAS } from '../src/ui-contract.js';
import { SCREENS } from '../src/catalog.js';
test('all 78 actions have unique Korean labels and all 27 screens have schemas',()=>{const actions=SCREENS.flatMap(s=>s.actions);assert.equal(Object.keys(ACTION_LABELS).length,78);assert.equal(new Set(actions.map(a=>ACTION_LABELS[a])).size,78);assert.equal(Object.keys(SCREEN_SCHEMAS).length,27);});
