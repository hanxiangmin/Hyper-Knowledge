/* Execute the renderer's real functions in a VM, without a browser or network. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../hyperknowledge/visualization/html.py"), "utf8");
const functions = source.slice(source.indexOf("function svgEl("), source.indexOf("function hypergraphPanel("));

function context(relations, extraNodes = []) {
  const nodeIds = [...new Set([...relations.flatMap(row => row.nodes), ...extraNodes])];
  const DATA = {
    nodes: nodeIds.map(id => ({ id, label: id, type: "entity" })),
    assertions: relations.map(row => ({ id: row.id, predicate: row.id, topology: row.topology || "hyperedge" })),
    members: relations.flatMap(row => row.nodes.map((id, i) => ({ assertion_id: row.id, node_id: id, ordinal: i, role: "member" }))),
  };
  const scope = {
    DATA, byNode: new Map(DATA.nodes.map(row => [row.id, row])),
    byAssertion: new Map(DATA.assertions.map(row => [row.id, row])),
    membersByAssertion: new Map(DATA.assertions.map(row => [row.id, DATA.members.filter(member => member.assertion_id === row.id)])),
    viewFrame: { width: 1200, height: 700, cx: 600, cy: 350, xStretch: 1060 / 860, yStretch: 584 / 534 },
    BASE_VIEW_WIDTH: 1000, BASE_VIEW_HEIGHT: 650,
  };
  vm.createContext(scope);
  vm.runInContext(functions, scope);
  return scope;
}

const mixed = context([{ id: "H1", nodes: ["A", "B", "C"] }, { id: "P1", nodes: ["D", "E"], topology: "pairwise" }], ["ISOLATED"]);
const mixedLayout = mixed.contourMembershipLayout(mixed.DATA.nodes, mixed.DATA.assertions);
const partial = context([
  { id: "H1", nodes: ["HUB", "A", "B"] }, { id: "H2", nodes: ["HUB", "C", "D"] },
  { id: "H3", nodes: ["HUB", "E", "F"] }, { id: "H4", nodes: ["G", "H", "I"] },
  { id: "H5", nodes: ["J", "K", "L"] },
]);
const partialLayout = partial.contourMembershipLayout(partial.DATA.nodes, partial.DATA.assertions);
const connected = context([
  { id: "H1", nodes: ["HUB", "A", "B"] }, { id: "H2", nodes: ["HUB", "C", "D"] },
  { id: "H3", nodes: ["HUB", "E", "F"] }, { id: "H4", nodes: ["A", "G", "H"] },
  { id: "H5", nodes: ["C", "I", "J"] },
]);
const connectedLayout = connected.contourMembershipLayout(connected.DATA.nodes, connected.DATA.assertions);
const single = context([{ id: "H1", nodes: ["A", "B", "C", "D"] }]);
const singleLayout = single.contourMembershipLayout(single.DATA.nodes, single.DATA.assertions);
const spec = singleLayout.enclosureSpecs.get("H1");
const before = JSON.stringify(spec);
const rejected = single.refitCenteredEnclosure(spec, { x: spec.center.x, y: spec.center.y - 3 }, -Math.PI / 2);
const after = JSON.stringify(spec);
const target = { x: spec.center.x + 30, y: spec.center.y - spec.semiMajor * 1.1 };
const validRefit = single.refitCenteredEnclosure(spec, target, -Math.PI / 2);
const label = single.nodeCircleMetrics("TP53R175HLongUnbrokenIdentifier");
const items = [
  { id: "A", center: { x: 500, y: 300 }, width: 130, height: 40 },
  { id: "B", center: { x: 500, y: 300 }, width: 130, height: 40 },
];
const obstacles = [{ point: { x: 500, y: 300 }, radius: 32 }];
const labels = single.placeContourLabels(items, obstacles);
const boxes = items.map(item => { const p = labels.get(item.id); return { left: p.x - 65, right: p.x + 65, top: p.y - 5, bottom: p.y + 35 }; });
const anchored = [...partialLayout.enclosureSpecs].filter(([, value]) => value.hubNodeId);
const allPositions = layout => [...layout.positions].every(([, point]) => Number.isFinite(point.x) && Number.isFinite(point.y));
console.log(JSON.stringify({
  mixed: { missing: mixed.DATA.nodes.filter(row => !mixedLayout.positions.has(row.id)).map(row => row.id), links: mixed.graphLinks(mixed.DATA.assertions).map(row => [mixedLayout.positions.has(row.source), mixedLayout.positions.has(row.target)]), finite: allPositions(mixedLayout) },
  partial: { missing: partial.DATA.nodes.filter(row => !partialLayout.positions.has(row.id)).map(row => row.id), falseAnchors: anchored.filter(([id, value]) => !partial.assertionMembers(id).some(member => member.node_id === value.hubNodeId)).map(([id]) => id), unrelatedFree: ["H4", "H5"].every(id => partialLayout.enclosureSpecs.get(id)?.freeCenter), finite: allPositions(partialLayout) },
  connected: { hub: connectedLayout.dominantNodeId, finite: allPositions(connectedLayout) },
  drag: { rejected, unchanged: before === after, validRefit, boundaryRadius: single.orbitalNormalizedRadius(target, spec) },
  text: { lines: label.lines, widths: label.lines.map(line => single.textWidth(line, label.fontSize)), diameter: label.radius * 2 },
  labels: { nodeCollisions: boxes.filter(box => single.boxCircleOverlap(box, obstacles[0].point, 39)).length, labelCollision: single.boxesOverlap(boxes[0], boxes[1], 8) },
}));
