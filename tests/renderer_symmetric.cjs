/* Geometry contract for the actual circle small-multiples implementation. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(path.join(__dirname, "../hyperknowledge/visualization/html.py"), "utf8");
const geometry = source.slice(source.indexOf("function symmetricRowCounts("), source.indexOf("function symmetricContourPanel("));
const wrapper = source.slice(source.indexOf("function interactiveContourHypergraphPanel("), source.indexOf("function membershipBoundaryContourPanel("));
const helper = name => source.split(/\r?\n/).find(line => line.startsWith(`function ${name}(`));
const drawDeclaration = source.slice(source.indexOf("function symmetricContourPanel(")).split(/\r?\n/).find(line => line.trimStart().startsWith("const draw=()=>marks.forEach"));
assert.ok(drawDeclaration, "The actual circle-position draw function must be exercised");
function context(count, { orphan = false, pairwise = false, unresolved = false } = {}) {
  const assertions = Array.from({ length: count }, (_, i) => ({ id: `H${String(i).padStart(2, "0")}`, topology: "hyperedge", predicate: `Relation ${i}` }));
  const members = assertions.flatMap((assertion, i) => ["shared", ...Array.from({ length: 2 + i % 6 }, (_, j) => `n${i}-${j}`)].flatMap((node, ordinal) => [{ assertion_id: assertion.id, node_id: node, role: "participant", ordinal }, ...(node === "shared" ? [{ assertion_id: assertion.id, node_id: node, role: "author", ordinal: ordinal + 100 }] : [])]));
  if (pairwise) { assertions.push({ id: "P", topology: "pairwise", predicate: "pair" }); members.push({ assertion_id: "P", node_id: "pair-left", role: "member" }, { assertion_id: "P", node_id: "pair-right", role: "member" }); }
  const ids = [...new Set([...members.map(member => member.node_id), ...(orphan ? ["orphan"] : [])])];
  if (unresolved && assertions.length) members.push({ assertion_id: assertions[0].id, node_id: "missing", role: "unresolved", resolved: false });
  const DATA = { nodes: ids.map(id => ({ id, label: id })), assertions, members, manifest: { presentation: { contour_layout: "symmetric_circles" } } };
  const scope = { DATA, byNode: new Map(DATA.nodes.map(row => [row.id, row])), byAssertion: new Map(assertions.map(row => [row.id, row])), membersByAssertion: new Map(assertions.map(row => [row.id, members.filter(member => member.assertion_id === row.id)])), activeMembers: () => DATA.members, activeAssertions: () => DATA.assertions, activeNodes: () => DATA.nodes, symmetricContourPanel: () => "symmetric", membershipBoundaryContourPanel: () => "membership" };
  vm.createContext(scope); vm.runInContext([helper("assertionMembers"), helper("isHyperedge"), helper("nativeHyperedgeDegree"), geometry, wrapper].join("\n"), scope); return scope;
}
function close(actual, expected, label) { assert.ok(Math.abs(actual - expected) < 1e-8, `${label}: ${actual} != ${expected}`); }
function positions(scope, tile) {
  scope.tile = tile; scope.marks = tile.members.map(() => ({ setAttribute(name, value) { this[name] = value; } }));
  vm.runInContext(`{${drawDeclaration}\ndraw();}`, scope);
  return scope.marks.map(mark => { const values = mark.transform.match(/translate\(([^ ]+) ([^)]+)\)/); return { x: Number(values[1]), y: Number(values[2]) }; });
}
const passed = [];
function test(name, callback) { callback(); passed.push(name); }
test("all grids have centered rows, equal circles, and finite nonoverlapping cells", () => {
  for (const width of [1320, 1600]) for (let count = 1; count <= 16; count++) {
    const s = context(count), layout = s.symmetricEnvelopeLayout(s.DATA.assertions, width, 900);
    assert.equal(layout.tiles.length, count); assert.equal(layout.rowCounts.reduce((a, b) => a + b, 0), count);
    assert.ok(Number.isFinite(layout.width) && Number.isFinite(layout.height));
    for (let row = 0; row < layout.rowCounts.length; row++) {
      const tiles = layout.tiles.filter(tile => tile.row === row);
      close(tiles.reduce((sum, tile) => sum + tile.cx, 0) / tiles.length, layout.width / 2, "row center");
      for (let column = 0; column < tiles.length; column++) {
        const tile = tiles[column], mirror = tiles[tiles.length - column - 1];
        close(tile.cx + mirror.cx, layout.width, "horizontal reflection"); close(tile.cy, mirror.cy, "shared row axis"); close(tile.radius, layout.tiles[0].radius, "common radius");
        assert.ok(tile.cx - tile.radius >= 0 && tile.cx + tile.radius <= layout.width);
        assert.ok(tile.cy - tile.radius >= 0 && tile.cy + tile.radius <= layout.height);
      }
    }
    for (let i = 0; i < layout.tiles.length; i++) for (let j = i + 1; j < layout.tiles.length; j++) {
      const a = layout.tiles[i], b = layout.tiles[j]; assert.ok(Math.hypot(a.cx - b.cx, a.cy - b.cy) >= a.radius + b.radius);
    }
  }
});
test("fourteen relations use balanced 5-4-5 rows or 7-7 rows on a wide canvas", () => {
  const s = context(14), layout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1320, 900);
  assert.deepEqual(Array.from(layout.rowCounts), [5, 4, 5]);
  const wide = s.symmetricEnvelopeLayout(s.DATA.assertions, 1786, 900);
  assert.deepEqual(Array.from(wide.rowCounts), [7, 7]);
  assert.ok(wide.height < 800);
});
test("repeated occurrences preserve every canonical relation-node membership exactly", () => {
  const s = context(14), before = JSON.stringify(s.DATA), layout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1320, 900);
  const actual = layout.tiles.flatMap(tile => tile.members.map(node => `${tile.assertion.id}|${node.id}`)).sort();
  const expected = [...new Set(s.DATA.members.map(member => `${member.assertion_id}|${member.node_id}`))].sort();
  assert.deepEqual(Array.from(actual), expected); assert.equal(layout.tiles.filter(tile => tile.members.some(node => node.id === "shared")).length, 14); assert.equal(JSON.stringify(s.DATA), before);
});
test("descending distinct arity order is deterministic and does not mutate source arrays", () => {
  const s = context(14), before = JSON.stringify(s.DATA), first = s.symmetricEnvelopeLayout(s.DATA.assertions, 1600, 900), second = s.symmetricEnvelopeLayout([...s.DATA.assertions].reverse(), 1600, 900);
  const order = Array.from(first.tiles, tile => tile.assertion.id); assert.deepEqual(order, Array.from(second.tiles, tile => tile.assertion.id));
  for (let i = 1; i < first.tiles.length; i++) assert.ok(first.tiles[i - 1].members.length >= first.tiles[i].members.length);
  assert.equal(JSON.stringify(s.DATA), before);
});
test("actual draw places every member on its circle with equal angular slots", () => {
  const s = context(14), layout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1600, 900);
  for (const tile of layout.tiles) {
    const points = positions(s, tile), expectedChord = 2 * tile.radius * Math.sin(Math.PI / points.length);
    points.forEach((point, index) => { close(Math.hypot(point.x - tile.cx, point.y - tile.cy), tile.radius, "circle radius"); const next = points[(index + 1) % points.length]; close(Math.hypot(point.x - next.x, point.y - next.y), expectedChord, "equal angular slot chord"); });
    close(points[0].x, tile.cx, "first member x"); close(points[0].y, tile.cy - tile.radius, "first member north");
    tile.rotation += Math.PI / 7; const rotated = positions(s, tile); rotated.forEach(point => close(Math.hypot(point.x - tile.cx, point.y - tile.cy), tile.radius, "rotated drag radius"));
  }
});
test("selected entity is consistently first without changing unrelated memberships", () => {
  const s = context(14), before = JSON.stringify(s.DATA), selected = "n7-1", layout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1320, 900, selected);
  for (const tile of layout.tiles) if (tile.members.some(node => node.id === selected)) assert.equal(tile.members[0].id, selected);
  const sharedLayout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1320, 900, "shared"); assert.ok(sharedLayout.tiles.every(tile => tile.members[0].id === "shared"));
  assert.equal(JSON.stringify(s.DATA), before);
});
test("empty data is finite and does not invent circles or members", () => {
  const s = context(0), layout = s.symmetricEnvelopeLayout([], 1320, 900); assert.equal(layout.tiles.length, 0); assert.equal(layout.rowCounts.length, 0); assert.ok(Number.isFinite(layout.width) && Number.isFinite(layout.height)); assert.equal(s.interactiveContourHypergraphPanel(), "symmetric");
});
test("orphan entities and mixed relations retain the lossless legacy layout", () => {
  assert.equal(context(3, { orphan: true }).interactiveContourHypergraphPanel(), "membership");
  assert.equal(context(3, { pairwise: true }).interactiveContourHypergraphPanel(), "membership");
  const s = context(3); delete s.DATA.manifest.presentation; assert.equal(s.interactiveContourHypergraphPanel(), "membership");
});
test("missing entities never create phantom rendered occurrences", () => {
  const s = context(3, { unresolved: true }), layout = s.symmetricEnvelopeLayout(s.DATA.assertions, 1320, 900); assert.ok(layout.tiles.every(tile => tile.members.every(node => s.byNode.has(node.id)))); assert.ok(layout.tiles.every(tile => tile.members.every(node => node.id !== "missing")));
});
console.log(JSON.stringify({ passed, gridCases: 32 }));
