/* Execute the real single-hyperedge reader helpers, not a test-only renderer. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const source = fs.readFileSync(path.join(__dirname, "../hyperknowledge/visualization/html.py"), "utf8");
function actualFunction(name) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `Missing actual renderer function ${name}`);
  const end = source.indexOf("\nfunction ", start + 1);
  assert.ok(end > start, `Cannot find function boundary for ${name}`);
  return source.slice(start, end);
}
const names = ["assertionMembers", "isHyperedge", "structuralMetrics", "readerEdges", "readerCurrentEdge", "readerSyncSelection", "readerNodeRadius", "readerLayout"];
const helpers = names.map(actualFunction).join("\n");
const drawDeclaration = actualFunction("singleHyperedgePanel").split(/\r?\n/).find(line => line.trimStart().startsWith("const draw=()=>marks.forEach"));
assert.ok(drawDeclaration, "Tests must execute the actual reader SVG positioning code");

function context(definitions = [
  { id: "E1", ids: ["A", "A", "B"] },
  { id: "E2", ids: ["A", "C"] },
  { id: "E3", ids: ["B", "C", "D"] },
], { isolates = ["isolated"] } = {}) {
  const assertions = definitions.map(({ id, topology = "hyperedge" }) => ({ id, predicate: id, topology }));
  const members = definitions.flatMap(({ id, ids }) => ids.map((node_id, ordinal) => ({ assertion_id: id, node_id, ordinal, role: `role-${ordinal}` })));
  const ids = [...new Set([...members.map(member => member.node_id), ...isolates])];
  const DATA = { nodes: ids.map(id => ({ id, label: id })), assertions, members };
  const scope = {
    DATA,
    byNode: new Map(DATA.nodes.map(node => [node.id, node])),
    byAssertion: new Map(assertions.map(assertion => [assertion.id, assertion])),
    membersByAssertion: new Map(assertions.map(assertion => [assertion.id, members.filter(member => member.assertion_id === assertion.id)])),
    readerState: { assertionId: null, nodeId: null, sort: "shared" },
    structuralMetricCache: null,
    activeMembers: () => { throw new Error("Global metrics must not read selection-filtered members"); },
    activeAssertions: () => { throw new Error("Global metrics must not read selection-filtered assertions"); },
    activeNodes: () => { throw new Error("Global metrics must not read selection-filtered nodes"); },
  };
  vm.createContext(scope);
  vm.runInContext(helpers, scope);
  return scope;
}
function plain(value) { return JSON.parse(JSON.stringify(value)); }
function close(actual, expected, message) { assert.ok(Math.abs(actual - expected) < 1e-8, `${message}: ${actual} != ${expected}`); }
function actualPositions(scope, layout) {
  scope.layout = layout;
  scope.marks = Array.from(layout.members, () => ({ setAttribute(name, value) { this[name] = value; } }));
  vm.runInContext(`{${drawDeclaration}\ndraw();}`, scope);
  return scope.marks.map(mark => {
    const point = mark.transform.match(/^translate\(([-\d.e+]+) ([-\d.e+]+)\)$/);
    assert.ok(point, `Invalid actual SVG transform: ${mark.transform}`);
    return { x: Number(point[1]), y: Number(point[2]) };
  });
}
const passed = [];
function test(name, callback) { callback(); passed.push(name); }

test("the complete current renderer script parses as JavaScript", () => {
  const start = source.indexOf("<script>") + "<script>".length;
  const end = source.indexOf("</script>", start);
  assert.ok(start >= "<script>".length && end > start);
  new vm.Script(source.slice(start, end), { filename: "hyperknowledge-renderer.js" });
});

test("global degree, arity and shared members count identities rather than roles", () => {
  const s = context(), before = JSON.stringify(s.DATA), metrics = s.structuralMetrics();
  assert.deepEqual(["A", "B", "C", "D", "isolated"].map(id => metrics.nodes.get(id).degree), [2, 2, 2, 1, 0]);
  assert.deepEqual(["E1", "E2", "E3"].map(id => plain(metrics.edges.get(id))), [
    { members: 2, shared: 2, neighbors: 2 },
    { members: 2, shared: 2, neighbors: 2 },
    { members: 3, shared: 2, neighbors: 2 },
  ]);
  assert.equal(s.assertionMembers("E1").filter(member => member.node_id === "A").length, 2, "Both roles remain intact");
  assert.equal(metrics.maxDegree, 2);
  assert.equal(JSON.stringify(s.DATA), before);
});

test("equal membership sets with different assertion IDs remain distinct relations", () => {
  const s = context([{ id: "first", ids: ["A", "B"] }, { id: "second", ids: ["A", "B"] }]);
  const metrics = s.structuralMetrics();
  assert.equal(metrics.edges.size, 2);
  assert.equal(metrics.nodes.get("A").degree, 2);
  assert.deepEqual(Array.from(metrics.nodes.get("A").edges).sort(), ["first", "second"]);
  assert.equal(metrics.edges.get("first").neighbors, 1, "The shared second relation is counted once, not once per member");
});

test("explicit two-member hyperedges are included without adding binary views or members", () => {
  const s = context([{ id: "H", ids: ["A", "B"] }, { id: "P", topology: "pairwise", ids: ["A", "C"] }]);
  assert.deepEqual(Array.from(s.readerEdges(), edge => edge.id), ["H"]);
  assert.equal(s.structuralMetrics().nodes.get("A").degree, 1);
  assert.equal(s.structuralMetrics().nodes.get("C").degree, 0);
  assert.deepEqual(Array.from(s.readerLayout(s.byAssertion.get("H")).members), ["A", "B"]);
});

test("isolates and empty data have zero degree and no fabricated current hyperedge", () => {
  const s = context([]), metrics = s.structuralMetrics();
  assert.equal(metrics.nodes.get("isolated").degree, 0);
  assert.equal(metrics.maxDegree, 1);
  assert.equal(metrics.edges.size, 0);
  assert.equal(s.readerCurrentEdge(), null);
  assert.equal(s.readerState.assertionId, null);
  assert.deepEqual(Array.from(s.readerEdges()), []);
});

test("edge sorting is descending, stable under input order, and keeps ties honest", () => {
  const defs = [{ id: "Z", ids: ["A", "B"] }, { id: "A", ids: ["A", "B"] }, { id: "M", ids: ["B", "C", "D"] }];
  const s = context(defs), reverse = context([...defs].reverse()), before = JSON.stringify(s.DATA);
  for (const sort of ["shared", "members", "neighbors"]) {
    s.readerState.sort = reverse.readerState.sort = sort;
    const rows = s.readerEdges();
    assert.deepEqual(Array.from(rows, edge => edge.id), Array.from(reverse.readerEdges(), edge => edge.id));
    for (let i = 1; i < rows.length; i++) assert.ok(s.structuralMetrics().edges.get(rows[i - 1].id)[sort] >= s.structuralMetrics().edges.get(rows[i].id)[sort]);
    assert.equal(s.structuralMetrics().edges.get("A")[sort], s.structuralMetrics().edges.get("Z")[sort], "Stable ordering must not alter tied metric values");
  }
  assert.equal(JSON.stringify(s.DATA), before);
});

test("a ubiquitous node makes adjacent-edge counts tie without arbitrary importance weights", () => {
  const s = context([{ id: "one", ids: ["hub", "A"] }, { id: "two", ids: ["hub", "A", "B"] }, { id: "three", ids: ["hub", "C", "D", "E"] }]);
  const metrics = s.structuralMetrics();
  assert.equal(metrics.nodes.get("hub").degree, 3);
  assert.deepEqual(["one", "two", "three"].map(id => metrics.edges.get(id).neighbors), [2, 2, 2]);
  assert.deepEqual(["one", "two", "three"].map(id => metrics.edges.get(id).shared), [2, 2, 1]);
  assert.deepEqual(["one", "two", "three"].map(id => metrics.edges.get(id).members), [2, 3, 4]);
});

test("filtering to a node leaves global degree and node size unchanged", () => {
  const s = context(), global = s.structuralMetrics(), radius = s.readerNodeRadius(global.nodes.get("A").degree, global.maxDegree);
  s.readerSyncSelection("node", "D");
  assert.deepEqual(Array.from(s.readerEdges(), edge => edge.id), ["E3"]);
  assert.equal(s.readerCurrentEdge().id, "E3");
  assert.equal(s.structuralMetrics(), global);
  assert.equal(s.structuralMetrics().nodes.get("A").degree, 2);
  assert.equal(s.readerNodeRadius(global.nodes.get("A").degree, global.maxDegree), radius);
  s.readerSyncSelection("node", "isolated");
  assert.equal(s.readerCurrentEdge(), null);
  assert.equal(s.readerState.assertionId, null);
  assert.equal(s.structuralMetrics(), global);
});

test("current edge remains selected when valid and falls back when excluded", () => {
  const s = context();
  s.readerState.assertionId = "E2";
  s.readerSyncSelection("node", "A");
  assert.equal(s.readerCurrentEdge().id, "E2");
  s.readerState.sort = "members";
  assert.equal(s.readerCurrentEdge().id, "E2", "Sorting must not silently change a valid selection");
  s.readerSyncSelection("node", "D");
  assert.equal(s.readerCurrentEdge().id, "E3");
  s.readerState.assertionId = "not-an-edge";
  assert.equal(s.readerCurrentEdge().id, "E3");
});

test("selecting an unrelated hyperedge clears a stale node filter", () => {
  const s = context();
  s.readerSyncSelection("node", "D");
  s.readerSyncSelection("assertion", "E1");
  assert.equal(s.readerState.nodeId, null);
  assert.equal(s.readerCurrentEdge().id, "E1");
  assert.equal(s.readerEdges().length, 3);
  s.readerSyncSelection("node", "A");
  s.readerSyncSelection("assertion", "E2");
  assert.equal(s.readerState.nodeId, "A", "A valid node filter should survive related-edge selection");
  assert.equal(s.readerCurrentEdge().id, "E2");
});

test("two-member actual SVG positions are exactly opposite on a horizontal diameter", () => {
  const s = context(), layout = s.readerLayout(s.byAssertion.get("E1")), points = actualPositions(s, layout);
  assert.equal(points.length, 2, "Duplicate roles cannot create a third position");
  close(points[0].y, layout.cy, "left member centered vertically");
  close(points[1].y, layout.cy, "right member centered vertically");
  close(points[0].x, layout.cx - layout.radius, "left member");
  close(points[1].x, layout.cx + layout.radius, "right member");
  close(points[0].x + points[1].x, 2 * layout.cx, "horizontal reflection");
});

test("three through twenty-four members have exact equal-angle slots, even after rotation", () => {
  for (const count of Array.from({ length: 22 }, (_, i) => i + 3)) {
    const s = context([{ id: "H", ids: Array.from({ length: count }, (_, i) => `N${i}`) }]);
    for (const [width, height] of [[390, 460], [760, 620], [1920, 1080]]) {
      const layout = s.readerLayout(s.byAssertion.get("H"), width, height);
      assert.equal(layout.members.length, count);
      for (const rotation of [-Math.PI / 2, 0.41]) {
        layout.rotation = rotation;
        const points = actualPositions(s, layout), chord = 2 * layout.radius * Math.sin(Math.PI / count);
        points.forEach((point, i) => {
          close(Math.hypot(point.x - layout.cx, point.y - layout.cy), layout.radius, "regular circle radius");
          const next = points[(i + 1) % count];
          close(Math.hypot(point.x - next.x, point.y - next.y), chord, "equal angular chord");
          assert.ok(point.x >= 0 && point.x <= layout.width && point.y >= 0 && point.y <= layout.height);
        });
        assert.ok(chord >= 132 - 1e-8, "Even large hyperedges keep member circles apart");
      }
    }
  }
});

test("global degree orders members and controls area monotonically, independent of name length", () => {
  const s = context([{ id: "E1", ids: ["B", "A"] }, { id: "E2", ids: ["A", "C", "D"] }]);
  const edge = s.byAssertion.get("E1"), before = JSON.stringify(s.DATA), first = s.readerLayout(edge);
  assert.deepEqual(Array.from(first.members), ["A", "B"]);
  assert.equal(JSON.stringify(s.DATA), before, "Layout does not edit source nodes or member roles");
  s.byNode.get("A").label = "这是一个很长的展示名称，但不能因此被画成结构上更重要的节点";
  assert.deepEqual(plain(s.readerLayout(edge)), plain(first));
  close(s.readerNodeRadius(0, 14), 31, "readable isolate minimum");
  close(s.readerNodeRadius(1, 14), 31, "degree-one baseline");
  close(s.readerNodeRadius(14, 14), 52, "global maximum size");
  close(s.readerNodeRadius(1, 1), 31, "single-degree graph is finite");
  for (let degree = 2; degree <= 14; degree++) assert.ok(s.readerNodeRadius(degree, 14) > s.readerNodeRadius(degree - 1, 14));
  const areas = [1, 2, 3].map(degree => s.readerNodeRadius(degree, 14) ** 2);
  close(areas[1] - areas[0], areas[2] - areas[1], "area, not radius, has equal increments");
});

console.log(JSON.stringify({ passed, geometryCases: 66 }));
