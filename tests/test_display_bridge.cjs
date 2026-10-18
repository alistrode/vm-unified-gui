'use strict';
const assert = require('node:assert/strict');
const bridge = require('../source/display-bridge.js');
const registry = [{id:'A',hostname:'actual-container-a'},{id:'B',hostname:'actual-container-b'}];
assert.equal(bridge.containerFor({'client-machine':'actual-container-b',title:'[A] misleading title'},registry),'B');
assert.equal(bridge.containerFor({title:'[A] arbitrary window'},registry),null);
assert.equal(bridge.containerFor({'client-machine':new TextEncoder().encode('actual-container-a')},registry),'A');
const boxes = bridge.positions([{id:1,container:'A'},{id:2,container:'A'},{id:3,container:'B'},{id:4,container:'C'}],1200,600);
assert.equal(boxes.length,4);
for(const box of boxes){assert.ok(box.x>=0&&box.y>=0);assert.ok(box.x+box.width<=1200);assert.ok(box.y+box.height<=600)}
const a=boxes.filter(box=>[1,2].includes(box.id));assert.ok(a[0].y+a[0].height<=a[1].y);
assert.equal(bridge.positions([{id:1,container:null}],1200,600).length,0);
console.log('Display grouping, container identity and non-overlapping layout checks passed.');
