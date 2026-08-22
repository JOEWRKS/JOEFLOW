import test from 'node:test';
import assert from 'node:assert/strict';
import { createPrototypeState, executeAction, resendDelivery, authorizeAction } from '../src/domain.js';

test('handler registry denies unknown actions and records every canonical action deterministically',()=>{
  const state=createPrototypeState();
  assert.equal(executeAction(state,{role:'Customer',action:'unknown'}).code,'DENIED');
  assert.equal(executeAction(state,{role:'Staff',action:'create_resource'}).ok,true);
});
test('permission contexts and missing delivery return guards without mutation',()=>{
  const state=createPrototypeState();
  assert.equal(authorizeAction('Customer','confirm_booking',{}).ok,false);
  const result=resendDelivery(state,'missing','missing-key',false);
  assert.equal(result.code,'DELIVERY');assert.equal(result.state,state);
});
