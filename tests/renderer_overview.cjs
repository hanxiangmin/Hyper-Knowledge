/* Contracts for the real canonical-identity radial hypergraph overview. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const root = path.join(__dirname, "..");
const source = fs.readFileSync(path.join(root, "hyperknowledge/visualization/html.py"), "utf8");
function actualFunction(name) {
  const start = source.indexOf(`function ${name}(`), end = source.indexOf("\nfunction ", start + 1);
  assert.ok(start >= 0 && end > start, `Missing full implementation of ${name}`);
  return source.slice(start, end);
}
const helpers = ["assertionMembers", "isHyperedge", "structuralMetrics", "overviewLayout", "overviewEdgeMetrics", "overviewLinkPoint", "overviewLinkPath", "overviewRoleLabels", "memberRoleText", "applyOverviewFocus", "restoreSelectionFocus", "selectItem", "visualUnits", "wrapVisualText", "textWidth", "labelBlockMetrics"].map(actualFunction).join("\n");
function context(DATA) {
  const scope = {
    DATA,
    byNode: new Map(DATA.nodes.map(node => [String(node.id), node])),
    byAssertion: new Map(DATA.assertions.map(assertion => [String(assertion.id), assertion])),
    membersByAssertion: new Map(DATA.assertions.map(assertion => [String(assertion.id), DATA.members.filter(member => String(member.assertion_id) === String(assertion.id))])),
    structuralMetricCache: null,
    readerText: zh => zh,
    t: key => key,
    selection: null,
    focusAssertionIds: null,
    activeAssertions: () => { throw new Error("Overview must use the whole graph, not selected assertions"); },
    activeMembers: () => { throw new Error("Overview must use the whole graph, not selected memberships"); },
    activeNodes: () => { throw new Error("Overview must use the whole graph, not selected nodes"); },
  };
  vm.createContext(scope);
  vm.runInContext(helpers, scope);
  return scope;
}
function fixture(definitions, isolates = []) {
  const assertions = definitions.map(({ id, topology = "hyperedge", theme = "" }) => ({ id, topology, predicate: id, properties: { theme } }));
  const members = definitions.flatMap(({ id, ids }) => ids.map((node_id, ordinal) => ({ assertion_id: id, node_id, ordinal, role: `role-${ordinal}` })));
  return { assertions, members, nodes: [...new Set([...members.map(member => member.node_id), ...isolates])].map(id => ({ id, label: id })) };
}
function readTable(name) {
  return fs.readFileSync(path.join(root, "examples/sushi-local-preview/bundle", `${name}.jsonl`), "utf8").trim().split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
}
const canonical = { nodes: readTable("nodes"), assertions: readTable("assertions"), members: readTable("members") };
function plain(value) { return JSON.parse(JSON.stringify(value)); }
function close(actual, expected, message) { assert.ok(Math.abs(actual - expected) < 1e-8, `${message}: ${actual} != ${expected}`); }
function assertIdentities(scope, layout) {
  const expectedNodes = scope.DATA.nodes.map(node => String(node.id)).sort();
  const expectedEdges = scope.DATA.assertions.filter(scope.isHyperedge).map(edge => String(edge.id)).sort();
  const expectedLinks = [...new Set(scope.DATA.members.filter(member => expectedEdges.includes(String(member.assertion_id)) && scope.byNode.has(String(member.node_id))).map(member => `${member.assertion_id}|${member.node_id}`))].sort();
  assert.deepEqual(Array.from(layout.nodes, node => node.id).sort(), expectedNodes, "Every canonical entity appears exactly once");
  assert.deepEqual(Array.from(layout.edges, edge => edge.id).sort(), expectedEdges, "Every actual hyperedge appears exactly once");
  assert.deepEqual(Array.from(layout.links, link => `${link.assertionId}|${link.nodeId}`).sort(), expectedLinks, "Only actual incidence links are drawn");
  assert.equal(new Set(layout.nodes.map(node => node.id)).size, layout.nodes.length);
  assert.equal(new Set(layout.edges.map(edge => edge.id)).size, layout.edges.length);
  for (const link of layout.links) {
    assert.ok(layout.nodes.some(node => node.id === link.nodeId));
    assert.ok(layout.edges.some(edge => edge.id === link.assertionId));
  }
}
function assertFinite(layout) {
  for (const key of ["width", "height", "cx", "cy", "rx", "ry"]) assert.ok(Number.isFinite(layout[key]), `Finite ${key}`);
  assert.ok(layout.width > 0 && layout.height > 0 && layout.rx > 0 && layout.ry > 0);
  for (const item of [...layout.nodes, ...layout.edges]) {
    assert.ok(Number.isFinite(item.x) && Number.isFinite(item.y));
    assert.ok(item.x >= 0 && item.x <= layout.width && item.y >= 0 && item.y <= layout.height);
  }
}
function assertSameLayout(a, b) {
  assert.equal(a.hubId, b.hubId);
  for (const kind of ["nodes", "edges"]) {
    assert.deepEqual(Array.from(a[kind], item => item.id), Array.from(b[kind], item => item.id));
    for (let i = 0; i < a[kind].length; i++) {
      close(a[kind][i].x, b[kind][i].x, `${kind} stable x`);
      close(a[kind][i].y, b[kind][i].y, `${kind} stable y`);
      if (kind === "edges") assert.equal(a[kind][i].code, b[kind][i].code, "Display codes are stable with canonical identity");
    }
  }
  assert.deepEqual(plain(a.links), plain(b.links));
}
function nodeCollisions(layout) {
  const issues = [];
  for (let i = 0; i < layout.nodes.length; i++) for (let j = i + 1; j < layout.nodes.length; j++) {
    const a = layout.nodes[i], b = layout.nodes[j], gap = Math.hypot(a.x - b.x, a.y - b.y) - a.r - b.r;
    if (gap < -1e-8) issues.push({ a: a.id, b: b.id, gap });
  }
  return issues;
}
function actualEdgeGlyphs(scope, layout) {
  const panelSource = actualFunction("hypergraphOverviewPanel");
  const start = panelSource.indexOf("for(const edge of layout.edges){"), end = panelSource.indexOf("for(const node of layout.nodes){", start);
  assert.ok(start >= 0 && end > start, "Use actual edge-glyph drawing, including actual label widths");
  const glyph = (tag, attrs = {}) => ({ tag, attrs, children: [], append(...items) { this.children.push(...items); } });
  Object.assign(scope, {
    layout,
    metrics: scope.structuralMetrics(),
    edgeLayer: glyph("g"),
    svgEl: glyph,
    hyperedgeStyle: () => "",
    readerText: zh => zh,
    activateMark: () => {},
    tooltipHandlers: () => {},
    panel: { canvas: {} },
  });
  vm.runInContext(panelSource.slice(start, end), scope);
  return scope.edgeLayer.children;
}
function rectangle(x, y, width, height) { return [{ x, y }, { x: x + width, y }, { x: x + width, y: y + height }, { x, y: y + height }]; }
function edgeGeometry(scope, layout) {
  return actualEdgeGlyphs(scope, layout).map(mark => {
    const edge = layout.edges.find(item => item.id === mark.attrs["data-assertion"]), capsule = mark.children.find(item => item.tag === "rect" && item.attrs.class === "overview-edge-label");
    assert.ok(capsule, "Each hyperedge uses one real rounded capsule");
    assert.equal(mark.children.filter(item => item.tag === "rect").length, 1, "The capsule is the sole label background");
    assert.ok(!mark.children.some(item => item.tag === "path"), "The discarded diamond glyph must not return");
    const rect = capsule.attrs, points = rectangle(edge.x + rect.x, edge.y + rect.y, rect.width, rect.height);
    close(rect.rx, rect.height / 2, "Capsule has fully rounded ends");
    const code = mark.children.find(item => item.tag === "text" && item.attrs.class === "overview-edge-code");
    const name = mark.children.find(item => item.tag === "text" && item.attrs.class === "overview-edge-text");
    const divider = mark.children.find(item => item.tag === "line" && item.attrs.class === "overview-edge-divider");
    assert.ok(code && name && divider, "Each capsule contains a code compartment and an internal name");
    return { id: edge.id, edge, mark, name, code, divider, capsule, points, parts: [points] };
  });
}
function polygonsOverlap(a, b) {
  for (const polygon of [a, b]) for (let i = 0; i < polygon.length; i++) {
    const start = polygon[i], end = polygon[(i + 1) % polygon.length], axis = { x: -(end.y - start.y), y: end.x - start.x };
    const pa = a.map(point => point.x * axis.x + point.y * axis.y), pb = b.map(point => point.x * axis.x + point.y * axis.y);
    if (Math.max(...pa) <= Math.min(...pb) + 1e-8 || Math.max(...pb) <= Math.min(...pa) + 1e-8) return false;
  }
  return true;
}
function circlePolygonGap(circle, polygon) {
  let minimum = Infinity, sign = null, inside = true;
  for (let i = 0; i < polygon.length; i++) {
    const a = polygon[i], b = polygon[(i + 1) % polygon.length], dx = b.x - a.x, dy = b.y - a.y;
    const cross = dx * (circle.y - a.y) - dy * (circle.x - a.x), current = Math.sign(cross);
    if (current && sign !== null && current !== sign) inside = false;
    if (current) sign = current;
    const t = Math.max(0, Math.min(1, ((circle.x - a.x) * dx + (circle.y - a.y) * dy) / (dx * dx + dy * dy)));
    minimum = Math.min(minimum, Math.hypot(circle.x - a.x - t * dx, circle.y - a.y - t * dy));
  }
  return (inside ? -minimum : minimum) - circle.r;
}
function labelCollisions(scope, layout) {
  const glyphs = edgeGeometry(scope, layout), issues = [];
  for (let i = 0; i < glyphs.length; i++) {
    const a = glyphs[i];
    for (let j = i + 1; j < glyphs.length; j++) {
      const b = glyphs[j];
      for (const pa of a.parts) for (const pb of b.parts) if (polygonsOverlap(pa, pb)) issues.push({ kind: "capsule-bounds", a: a.id, b: b.id });
    }
    for (const node of layout.nodes) for (const part of a.parts) {
      const gap = circlePolygonGap(node, part);
      if (gap < -1e-8) issues.push({ kind: "label-node", a: a.id, b: node.id, gap });
    }
  }
  return issues;
}
function roleCollisions(scope, layout, labels) {
  const issues = [], overlap = (a, b) => Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  for (let i = 0; i < labels.length; i++) {
    const label = labels[i], box = { x: label.x - label.width / 2, y: label.y - label.height / 2, width: label.width, height: label.height };
    if (box.x < 12 || box.y < 12 || box.x + box.width > layout.width - 12 || box.y + box.height > layout.height - 12) issues.push({ kind: "viewport", role: label.value });
    for (const edge of layout.edges) {
      const glyph = scope.overviewEdgeMetrics(scope.byAssertion.get(edge.id).predicate);
      const area = overlap(box, { x: edge.x - glyph.width / 2 - 8, y: edge.y - glyph.height / 2 - 8, width: glyph.width + 16, height: glyph.height + 16 });
      if (area > 1e-8) issues.push({ kind: "role-edge", role: label.value, edge: edge.id, area });
    }
    for (let j = 0; j < i; j++) {
      const other = labels[j], area = overlap(box, { x: other.x - other.width / 2 - 6, y: other.y - other.height / 2 - 5, width: other.width + 12, height: other.height + 10 });
      if (area > 1e-8) issues.push({ kind: "role-role", role: label.value, other: other.value, area });
    }
    for (const node of layout.nodes) {
      const dx = node.x - Math.max(box.x, Math.min(node.x, box.x + box.width)), dy = node.y - Math.max(box.y, Math.min(node.y, box.y + box.height)), gap = node.r + 12 - Math.hypot(dx, dy);
      if (gap > 1e-8) issues.push({ kind: "role-node-halo", role: label.value, node: node.id, gap });
    }
  }
  return issues;
}
function focusPanel(layout) {
  const mark = (className, dataset) => {
    const classes = new Set([className]);
    return { dataset, classes, classList: { contains: name => classes.has(name), toggle(name, enabled) { if (enabled) classes.add(name); else classes.delete(name); } } };
  };
  const marks = [
    ...layout.nodes.map(node => mark("overview-node", { node: node.id })),
    ...layout.edges.map(edge => mark("overview-edge", { assertion: edge.id })),
    ...layout.links.map(link => mark("overview-link", { node: link.nodeId, assertion: link.assertionId })),
  ];
  return { marks, title: { textContent: "" }, roleCalls: [], __showOverviewRoles(focus) { this.roleCalls.push(focus); }, querySelectorAll: () => marks, querySelector() { return this.title; } };
}
const passed = [];
function test(name, callback) { callback(); passed.push(name); }

test("complete renderer syntax remains valid with overview implementation", () => {
  const start = source.indexOf("<script>") + "<script>".length, end = source.indexOf("</script>", start);
  assert.ok(start >= "<script>".length && end > start);
  new vm.Script(source.slice(start, end), { filename: "hypergraph-overview-renderer.js" });
});

test("current source-grounded example has 39 unique entities, 18 hyperedges and 65 incidences", () => {
  const s = context(canonical), before = JSON.stringify(s.DATA), layout = s.overviewLayout();
  assertIdentities(s, layout);
  assert.equal(layout.nodes.length, 39);
  assert.equal(layout.edges.length, 18);
  assert.equal(layout.links.length, 65);
  assert.equal(layout.hubId, "person:su-shi");
  assert.equal(s.structuralMetrics().nodes.get(layout.hubId).degree, 18);
  assert.equal(JSON.stringify(s.DATA), before);
});

test("duplicate member roles keep all source roles but create only one incidence mark", () => {
  const s = context(fixture([{ id: "H1", ids: ["A", "A", "B"] }, { id: "H2", ids: ["A", "C"] }]));
  const layout = s.overviewLayout();
  assertIdentities(s, layout);
  assert.equal(layout.nodes.length, 3);
  assert.equal(layout.links.length, 4);
  assert.equal(s.assertionMembers("H1").length, 3);
  assert.equal(s.structuralMetrics().nodes.get("A").degree, 2);
});

test("two-member hyperedges remain one explicit hyperedge and two memberships", () => {
  const s = context(fixture([{ id: "H", ids: ["A", "B"] }])), layout = s.overviewLayout();
  assertIdentities(s, layout);
  assert.equal(layout.edges.length, 1);
  assert.equal(layout.links.length, 2);
  assert.ok(layout.links.every(link => Object.keys(link).sort().join() === "assertionId,nodeId"));
});

test("same member set with distinct assertion IDs is never coalesced", () => {
  const s = context(fixture([{ id: "H1", ids: ["A", "B"] }, { id: "H2", ids: ["A", "B"] }])), layout = s.overviewLayout();
  assertIdentities(s, layout);
  assert.equal(layout.nodes.length, 2);
  assert.equal(layout.edges.length, 2);
  assert.equal(layout.links.length, 4);
});

test("disconnected components are not falsely connected through the chosen central node", () => {
  const s = context(fixture([{ id: "left", ids: ["A", "B", "C"] }, { id: "right", ids: ["D", "E"] }], ["isolated"]));
  const layout = s.overviewLayout();
  assertIdentities(s, layout);
  assert.equal(layout.hubId, "A");
  assert.ok(!layout.links.some(link => link.assertionId === "right" && link.nodeId === layout.hubId));
  assert.ok(!layout.links.some(link => link.nodeId === "isolated"));
  assert.equal(layout.nodes.find(node => node.id === "isolated").ring, "isolated");
});

test("empty graphs and graphs containing only isolated nodes remain finite and truthful", () => {
  for (const isolates of [[], ["alone"], ["A", "B", "C"]]) {
    const s = context(fixture([], isolates)), layout = s.overviewLayout();
    assertFinite(layout);
    assertIdentities(s, layout);
    assert.equal(layout.hubId, null);
    assert.equal(layout.links.length, 0);
    assert.ok(layout.nodes.every(node => node.ring === "isolated"));
  }
});

test("highest-degree hub ties resolve by canonical ID, never source order", () => {
  const data = fixture([{ id: "H1", ids: ["C", "B"] }, { id: "H2", ids: ["A", "C"] }, { id: "H3", ids: ["B", "A"] }]);
  const s = context(data), layout = s.overviewLayout();
  assert.equal(layout.hubId, "A");
  const hub = layout.nodes.find(node => node.id === "A");
  close(hub.x, layout.cx, "hub x");
  close(hub.y, layout.cy, "hub y");
  const reversed = context({ nodes: [...data.nodes].reverse(), assertions: [...data.assertions].reverse(), members: [...data.members].reverse() });
  assertSameLayout(layout, reversed.overviewLayout());
});

test("reversing all current data tables preserves deterministic geometry and membership", () => {
  const normal = context(canonical), reversed = context({ nodes: [...canonical.nodes].reverse(), assertions: [...canonical.assertions].reverse(), members: [...canonical.members].reverse() });
  assertSameLayout(normal.overviewLayout(), reversed.overviewLayout());
});

test("selection and filtering never shrink or reposition the whole-graph overview", () => {
  const s = context(canonical), layout = s.overviewLayout(), metrics = s.structuralMetrics();
  for (const kind of ["node", "assertion"]) for (const id of kind === "node" ? canonical.nodes.map(node => node.id) : canonical.assertions.map(edge => edge.id)) {
    s.selection = { kind, id };
    s.focusAssertionIds = new Set(kind === "assertion" ? [id] : metrics.nodes.get(id).edges);
    assertSameLayout(layout, s.overviewLayout());
    assert.equal(s.structuralMetrics(), metrics);
  }
});

test("actual relation focus dims unrelated marks without hiding nodes or leaving unrelated shared-endpoint lines active", () => {
  const s = context(fixture([{ id: "H1", ids: ["A", "B"] }, { id: "H2", ids: ["A", "C"] }, { id: "H3", ids: ["D", "E"] }], ["isolated"]));
  const layout = s.overviewLayout(), panel = focusPanel(layout), originalCount = panel.marks.length;
  s.selection = { kind: "assertion", id: "H1" };
  s.applyOverviewFocus(panel, s.selection);
  for (const mark of panel.marks) {
    const node = mark.classes.has("overview-node"), related = node ? ["A", "B"].includes(mark.dataset.node) : mark.dataset.assertion === "H1";
    assert.equal(mark.classes.has("is-overview-related"), related);
    assert.equal(mark.classes.has("is-overview-muted"), !related);
    assert.ok(!mark.classes.has("is-hidden"));
  }
  const otherSharedEndpoint = panel.marks.find(mark => mark.classes.has("overview-link") && mark.dataset.node === "A" && mark.dataset.assertion === "H2");
  assert.ok(otherSharedEndpoint.classes.has("is-overview-muted"));
  assert.equal(panel.marks.length, originalCount);
  assert.ok(panel.title.textContent.includes("H1"));
  assert.deepEqual(plain(panel.roleCalls), [{ kind: "assertion", id: "H1" }], "Relation selection also requests the actual focused role labels");
});

test("actual node and hover focus preserve pinned selection and restore the unfiltered scene", () => {
  const s = context(fixture([{ id: "H1", ids: ["A", "B"] }, { id: "H2", ids: ["A", "C"] }, { id: "H3", ids: ["D", "E"] }], ["isolated"]));
  const layout = s.overviewLayout(), panel = focusPanel(layout);
  s.selection = { kind: "node", id: "A" };
  s.applyOverviewFocus(panel, s.selection);
  assert.equal(panel.marks.filter(mark => mark.classes.has("overview-node") && mark.classes.has("is-overview-related")).length, 3);
  assert.equal(panel.marks.filter(mark => mark.classes.has("overview-edge") && mark.classes.has("is-overview-related")).length, 2);
  s.applyOverviewFocus(panel, { kind: "assertion", id: "H3" });
  assert.deepEqual(plain(s.selection), { kind: "node", id: "A" }, "Hovering never overwrites the pinned selection");
  assert.ok(panel.marks.find(mark => mark.classes.has("overview-node") && mark.dataset.node === "A").classes.has("is-selected"));
  s.applyOverviewFocus(panel, s.selection);
  assert.ok(panel.marks.find(mark => mark.classes.has("overview-edge") && mark.dataset.assertion === "H3").classes.has("is-overview-muted"));
  s.selection = null;
  s.applyOverviewFocus(panel, null);
  assert.ok(panel.marks.every(mark => !mark.classes.has("is-overview-related") && !mark.classes.has("is-overview-muted") && !mark.classes.has("is-hidden") && !mark.classes.has("is-selected")));
  s.selection = { kind: "node", id: "isolated" };
  s.applyOverviewFocus(panel, s.selection);
  assert.equal(panel.marks.filter(mark => mark.classes.has("is-overview-related")).length, 1);
  assert.deepEqual(plain(panel.roleCalls), [{ kind: "node", id: "A" }, { kind: "assertion", id: "H3" }, { kind: "node", id: "A" }, null, { kind: "node", id: "isolated" }], "Hover, leave, clear and isolate states update role visibility with the same focus");
  assertSameLayout(layout, s.overviewLayout());
});

test("keyboard navigation restores focus to overview capsules, entity glyphs and existing incidence assertion marks", () => {
  const s = context(fixture([{ id: "H1", ids: ["A", "B"] }]));
  const mark = (classNames, dataset) => {
    const classes = new Set(classNames.split(" "));
    return { dataset, focused: false, classList: { contains: name => classes.has(name) }, focus(options) { this.focused = true; this.focusOptions = options; } };
  };
  for (const [kind, id, targetClass] of [["assertion", "H1", "overview-edge"], ["node", "A", "entity-mark"], ["assertion", "H1", "assertion-mark"]]) {
    const key = kind === "node" ? "node" : "assertion", unrelated = mark(targetClass, { [key]: "unrelated" }), path = mark(`link ${targetClass}`, { [key]: id }), target = mark(targetClass, { [key]: id });
    s.document = { querySelectorAll: () => [unrelated, path, target] };
    s.restoreSelectionFocus(kind, id);
    assert.equal(target.focused, true, `${targetClass} regains focus after a drawer navigation replaces its button`);
    assert.deepEqual(plain(target.focusOptions), { preventScroll: true }, "Restoring keyboard focus must not unexpectedly pan the graph");
    assert.equal(unrelated.focused, false);
    assert.equal(path.focused, false, "Long incidence paths are never focus restoration targets");
  }
});

test("actual selection recovers a removed drawer focus even when Chromium activeElement has already reverted to connected body", () => {
  for (const mode of ["overview", "matrix"]) for (const kind of ["assertion", "node"]) for (const scenario of ["removed", "retained", "no-restore-request"]) {
    const s = context(fixture([{ id: "H1", ids: ["A", "B"] }])), id = kind === "node" ? "A" : "H1";
    s.DATA.manifest = { presentation: {} };
    s.currentView = "hypergraph";
    s.hyperMode = mode;
    const previousFocus = { tagName: "BUTTON", isConnected: true }, body = { tagName: "BODY", isConnected: true };
    const targetClass = kind === "node" ? mode === "overview" ? "entity-mark" : "matrix-row-label" : mode === "overview" ? "overview-edge" : "matrix-column-header";
    const target = { isConnected: true, dataset: { [kind === "node" ? "node" : "assertion"]: id }, classList: { contains: name => name === targetClass }, focusCount: 0, focus(options) { this.focusCount++; this.focusOptions = options; s.document.activeElement = this; } };
    s.document = { activeElement: previousFocus, querySelectorAll: () => [target] };
    let drawerCalls = 0, selectionCalls = 0;
    s.showDrawer = () => {
      drawerCalls++;
      if (scenario !== "retained") { previousFocus.isConnected = false; s.document.activeElement = body; }
    };
    s.applySelection = () => { selectionCalls++; };
    s.focusAssertionIds = new Set(["stale-selection"]);
    s.selectItem(kind, (kind === "node" ? s.byNode : s.byAssertion).get(id), { restoreFocus: scenario !== "no-restore-request" });
    assert.equal(drawerCalls, 1);
    assert.equal(selectionCalls, 1);
    assert.equal(s.selection.kind, kind);
    assert.equal(s.selection.id, id);
    assert.equal(s.focusAssertionIds, null, "Stable overview and matrix remain whole-graph views");
    if (scenario === "removed") {
      assert.equal(body.isConnected, true, "This reproduction covers browsers that move activeElement to connected BODY");
      assert.equal(s.document.activeElement, target, `${mode}/${kind}: restore based on the disconnected previous element, not current BODY`);
      assert.equal(target.focusCount, 1);
      assert.deepEqual(plain(target.focusOptions), { preventScroll: true });
    } else {
      assert.equal(target.focusCount, 0, `${mode}/${kind}: do not steal an existing focus or override a pointer-only action`);
      assert.equal(s.document.activeElement, scenario === "retained" ? previousFocus : body);
    }
  }
});

test("canonical nodes and real hyperedges occupy centered concentric ellipse bands", () => {
  const s = context(canonical);
  for (const [width, height] of [[390, 700], [1440, 900], [1920, 1080], [2600, 1500]]) {
    const layout = s.overviewLayout(width, height);
    assertFinite(layout);
    assertIdentities(s, layout);
    for (const node of layout.nodes) {
      if (node.ring === "isolated") continue;
      const factor = { hub: 0, shared: 0.32, outer: 1 }[node.ring];
      assert.ok(factor !== undefined, `Known ring ${node.ring}`);
      close(Math.hypot((node.x - layout.cx) / layout.rx, (node.y - layout.cy) / layout.ry), factor, "canonical entity ellipse radius");
    }
    for (const edge of layout.edges) close(Math.hypot((edge.x - layout.cx) / layout.rx, (edge.y - layout.cy) / layout.ry), 0.69, "hyperedge ellipse radius");
    close(layout.edges.reduce((sum, edge) => sum + edge.span, 0), Math.PI * 2, "edge sectors cover the orbit once");
  }
});

test("node visual radius uses global participation rather than name length or focus", () => {
  const data = fixture([{ id: "E1", ids: ["A", "B"] }, { id: "E2", ids: ["A", "C"] }, { id: "E3", ids: ["A", "B", "D"] }], ["isolated"]), s = context(data);
  const layout = s.overviewLayout(), radius = id => layout.nodes.find(node => node.id === id).r;
  assert.ok(radius("A") > radius("B") && radius("B") > radius("C") && radius("C") > radius("isolated"));
  data.nodes.forEach(node => { node.label = `${node.id}这是一个非常长的完整源节点名称`; });
  assertSameLayout(layout, s.overviewLayout());
  assert.deepEqual(Array.from(s.overviewLayout().nodes, node => node.r), Array.from(layout.nodes, node => node.r));
});

test("actual capsule bounds never overlap each other or canonical node circles", () => {
  const s = context(canonical);
  for (const [width, height] of [[390, 700], [1600, 1160], [1920, 1080]]) {
    const collisions = labelCollisions(s, s.overviewLayout(width, height));
    assert.deepEqual(collisions, [], JSON.stringify(collisions));
  }
});

test("display codes are contiguous, canonical, and never renumbered by source order or focus", () => {
  const s = context(canonical), before = JSON.stringify(s.DATA), layout = s.overviewLayout(), codes = Array.from(layout.edges, edge => [edge.id, edge.code]);
  assert.deepEqual(codes.map(([, code]) => code), Array.from({ length: 18 }, (_, i) => `E${i + 1}`));
  for (const node of canonical.nodes) {
    s.selection = { kind: "node", id: node.id };
    s.focusAssertionIds = new Set(s.structuralMetrics().nodes.get(node.id).edges);
    assert.deepEqual(Array.from(s.overviewLayout().edges, edge => [edge.id, edge.code]), codes);
  }
  const reverse = context({ nodes: [...canonical.nodes].reverse(), assertions: [...canonical.assertions].reverse(), members: [...canonical.members].reverse() });
  assert.deepEqual(Array.from(reverse.overviewLayout().edges, edge => [edge.id, edge.code]), codes);
  for (const glyph of edgeGeometry(s, layout)) {
    assert.equal(glyph.code.textContent, glyph.edge.code);
    assert.equal(glyph.mark.attrs["data-edge-code"], glyph.edge.code);
    assert.ok(glyph.code.attrs.x < glyph.divider.attrs.x1 && glyph.divider.attrs.x1 < glyph.name.attrs.x, "Stable code occupies the left compartment and the name occupies the right");
  }
  assert.equal(JSON.stringify(s.DATA), before, "Display E-codes never enter source records");
});

test("full source names and stable codes fit inside the actual rounded capsules", () => {
  const s = context(canonical), layout = s.overviewLayout();
  for (const glyph of edgeGeometry(s, layout)) {
    const lines = glyph.name.children.map(span => span.textContent);
    assert.equal(lines.join(""), s.byAssertion.get(glyph.id).predicate, "Current source names must not be truncated");
    assert.equal(lines.length, 1, "Current short source names fit on one clean line");
    const metrics = s.overviewEdgeMetrics(s.byAssertion.get(glyph.id).predicate), halfWidth = glyph.capsule.attrs.width / 2, halfHeight = glyph.capsule.attrs.height / 2;
    assert.equal(metrics.fontSize, 16);
    assert.equal(metrics.codeWidth, 44);
    close(halfWidth * 2, metrics.width, "Actual drawn width matches obstacle geometry");
    close(halfHeight * 2, metrics.height, "Actual drawn height matches obstacle geometry");
    assert.ok(halfWidth >= 70 && halfHeight >= 22);
    const assertInside = point => assert.ok(Math.hypot(Math.max(0, Math.abs(point.x) - (halfWidth - halfHeight)), point.y) <= halfHeight + 1e-8, `${glyph.id}: text remains inside rounded capsule ends`);
    const codeWidth = [...glyph.code.textContent].length * 9;
    for (const point of rectangle(glyph.code.attrs.x - codeWidth / 2, glyph.code.attrs.y - 13, codeWidth, 16)) { assertInside(point); assert.ok(point.x < glyph.divider.attrs.x1); }
    let baseline = glyph.name.attrs.y;
    for (const span of glyph.name.children) {
      baseline += Number(span.attrs.dy || 0);
      const width = [...span.textContent].reduce((sum, char) => sum + (char.charCodeAt(0) > 255 ? 16 : 9), 0);
      for (const point of rectangle(glyph.name.attrs.x - width / 2, baseline - 13, width, 16)) { assertInside(point); assert.ok(point.x > glyph.divider.attrs.x1); }
    }
  }
});

test("every edge or node focus shows exactly its true incidence-role labels, never the whole neighborhood", () => {
  const s = context(canonical), layout = s.overviewLayout(), before = JSON.stringify(s.DATA);
  for (const focus of [...canonical.nodes.map(node => ({ kind: "node", id: node.id })), ...canonical.assertions.map(edge => ({ kind: "assertion", id: edge.id }))]) {
    const labels = s.overviewRoleLabels(layout, focus), expected = layout.links.filter(link => focus.kind === "node" ? link.nodeId === focus.id : link.assertionId === focus.id);
    assert.deepEqual(Array.from(labels, label => `${label.assertionId}|${label.nodeId}`).sort(), Array.from(expected, link => `${link.assertionId}|${link.nodeId}`).sort());
    for (const label of labels) {
      const roles = [...new Set(canonical.members.filter(member => member.assertion_id === label.assertionId && member.node_id === label.nodeId).map(member => member.role))];
      assert.equal(label.value, roles.join(" / "));
      assert.equal(label.lines.join("").replace(/\s/g, ""), label.value.replace(/\s/g, ""), "Current role names remain fully visible");
      assert.ok(Number.isFinite(label.x) && Number.isFinite(label.y) && Number.isFinite(label.width) && Number.isFinite(label.height));
    }
  }
  assert.equal(s.overviewRoleLabels(layout, { kind: "node", id: "person:su-shi" }).length, 18, "Hub focus labels its 18 incidences, not all 65 memberships");
  assert.equal(JSON.stringify(s.DATA), before);
});

test("duplicate roles are collapsed as text, distinct roles retained, and no focus shows no roles", () => {
  const data = fixture([{ id: "H1", ids: ["A", "A", "A", "B"] }, { id: "H2", ids: ["A", "C"] }], ["isolated"]);
  data.members[0].role = "作者";
  data.members[1].role = "作者";
  data.members[2].role = "编者";
  const s = context(data), layout = s.overviewLayout(), labels = s.overviewRoleLabels(layout, { kind: "assertion", id: "H1" });
  assert.equal(labels.length, 2);
  assert.equal(labels.find(label => label.nodeId === "A").value, "作者 / 编者");
  for (const focus of [null, { kind: "node", id: "isolated" }, { kind: "node", id: "missing" }, { kind: "assertion", id: "missing" }]) assert.equal(s.overviewRoleLabels(layout, focus).length, 0);
  assert.equal(data.members.length, 6);
});

test("role anchors lie on actual incidence paths and repeat deterministically without mutating geometry", () => {
  const s = context(canonical), layout = s.overviewLayout(), before = JSON.stringify(layout), focus = { kind: "node", id: "person:su-shi" };
  const first = s.overviewRoleLabels(layout, focus), second = s.overviewRoleLabels(layout, focus);
  assert.deepEqual(plain(first), plain(second));
  for (const label of first) {
    const node = layout.nodes.find(item => item.id === label.nodeId), edge = layout.edges.find(item => item.id === label.assertionId);
    const candidates = [.56, .44, .68, .32, .78, .22, .88, .12].map(t => s.overviewLinkPoint(node, edge, t));
    assert.ok(candidates.some(point => Math.hypot(point.x - label.anchor.x, point.y - label.anchor.y) < 1e-8));
    close(Math.hypot(label.x - label.anchor.x, label.y - label.anchor.y), Math.abs(label.offset), "Any role displaced off its line has an explicit leader offset");
  }
  assert.equal(JSON.stringify(layout), before);
});

test("actual link paths stop one pixel outside rounded capsules and preserve the original quadratic curve", () => {
  const s = context(canonical);
  assert.ok(actualFunction("hypergraphOverviewPanel").includes("d:overviewLinkPath(source,target)"), "Actual incidence drawing must use the checked clipping helper");
  for (const [width, height] of [[2000, 1080], [2600, 1080], [3200, 1500]]) {
    const layout = s.overviewLayout(width, height), nodes = new Map(layout.nodes.map(node => [node.id, node])), edges = new Map(layout.edges.map(edge => [edge.id, edge]));
    for (const link of layout.links) {
      const node = nodes.get(link.nodeId), edge = edges.get(link.assertionId), glyph = s.overviewEdgeMetrics(s.byAssertion.get(edge.id).predicate), d = s.overviewLinkPath(node, edge);
      assert.ok(/^M .+ Q .+$/.test(d));
      const coords = d.match(/[-+]?\d*\.?\d+(?:e[-+]?\d+)?/gi).map(Number);
      assert.equal(coords.length, 6, "Each membership is one quadratic segment, not a new pairwise path");
      const start = { x: coords[0], y: coords[1] }, control = { x: coords[2], y: coords[3] }, end = { x: coords[4], y: coords[5] };
      close(start.x, node.x, "Path begins at its true canonical node x");
      close(start.y, node.y, "Path begins at its true canonical node y");
      const gap = Math.hypot(Math.max(0, Math.abs(end.x - edge.x) - (glyph.width - glyph.height) / 2), end.y - edge.y) - glyph.height / 2;
      assert.ok(gap >= 1 - 1e-8 && gap < 1.001, `${link.assertionId}|${link.nodeId}: endpoint stays one pixel outside actual capsule, got ${gap}`);
      const dx = edge.x - node.x, dy = edge.y - node.y, bend = node.ring === "outer" ? 0.12 : 0.07, originalControl = { x: (node.x + edge.x) / 2 - dy * bend, y: (node.y + edge.y) / 2 + dx * bend };
      const cx = originalControl.x - node.x, cy = originalControl.y - node.y, cut = ((control.x - node.x) * cx + (control.y - node.y) * cy) / (cx * cx + cy * cy);
      assert.ok(cut > 0 && cut < 1);
      for (const u of [0.2, 0.5, 0.8, 1]) {
        const complement = 1 - u, point = { x: complement ** 2 * start.x + 2 * complement * u * control.x + u ** 2 * end.x, y: complement ** 2 * start.y + 2 * complement * u * control.y + u ** 2 * end.y }, original = s.overviewLinkPoint(node, edge, u * cut);
        close(point.x, original.x, "Clipped x follows the original membership curve");
        close(point.y, original.y, "Clipped y follows the original membership curve");
      }
    }
  }
});

test("all current focus-role labels avoid edge glyphs, other labels and node safety halos", () => {
  const s = context(canonical), focuses = [...canonical.nodes.map(node => ({ kind: "node", id: node.id })), ...canonical.assertions.map(edge => ({ kind: "assertion", id: edge.id }))];
  for (const [width, height] of [[2000, 1080], [2600, 1080], [3200, 1500]]) {
    const layout = s.overviewLayout(width, height);
    for (const focus of focuses) {
      const issues = roleCollisions(s, layout, s.overviewRoleLabels(layout, focus));
      assert.deepEqual(issues, [], `${width}x${height} ${focus.kind}:${focus.id} ${JSON.stringify(issues)}`);
    }
  }
});

test("no canonical entity circles overlap in the current example", () => {
  const s = context(canonical);
  for (const [width, height] of [[390, 700], [1600, 1160], [1920, 1080]]) {
    const collisions = nodeCollisions(s.overviewLayout(width, height));
    assert.deepEqual(collisions, [], JSON.stringify(collisions));
  }
});

console.log(JSON.stringify({ passed, roleFocusCases: 171, clippedLinkCases: 195, currentNodes: canonical.nodes.length, currentHyperedges: canonical.assertions.length, currentIncidences: canonical.members.length }));
