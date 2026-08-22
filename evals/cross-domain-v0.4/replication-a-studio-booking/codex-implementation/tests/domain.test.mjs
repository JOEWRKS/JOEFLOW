import test from 'node:test';
import assert from 'node:assert/strict';
import { createPriceSnapshot, formatKrw, updateRate, canChangeOrCancel, transitionWithReason, deliveryOutcome, replayMutation } from '../src/domain.js';

test('rates, copied snapshot, won display and 48-hour boundary are deterministic', () => {
  assert.equal(updateRate(60000, 60001).ok, false);
  const snapshot=createPriceSnapshot({start:'2026-08-21T03:00:00+09:00',end:'2026-08-21T05:00:00+09:00',room:{id:'ROOM-A',hourlyRate:60000},equipment:[{id:'CAM-A',quantity:1,hourlyRate:20000}]});
  assert.equal(snapshot.total,160000);assert.equal(formatKrw(snapshot.total),'₩160,000');
  assert.equal(canChangeOrCancel('2026-08-23T00:00:00+09:00',new Date('2026-08-21T00:00:00+09:00')),true);
});
test('reason guard and generic idempotency preserve the original result',()=>{assert.equal(transitionWithReason({},'').ok,false);const ledger=new Map();let n=0;assert.equal(replayMutation(ledger,'x',()=>({value:++n})).value,1);assert.equal(replayMutation(ledger,'x',()=>({value:++n})).value,1);assert.equal(deliveryOutcome({bookingCommitted:true,delivered:false}).bookingCommitted,true);});
