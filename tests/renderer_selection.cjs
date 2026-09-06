/* Run actual selection functions with a deliberately small DOM test double. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(path.join(__dirname, "../hyperknowledge/visualization/html.py"), "utf8");
const functions = source.slice(source.indexOf("function svgEl("), source.indexOf("function createPanel("));
class Element {
  constructor(tagName = "div") {
    this.tagName = tagName; this.children = []; this.dataset = {}; this.style = {}; this.attrs = {}; this.events = {}; this.classes = new Set(); this.textContent = "";
    this.classList = { add: (...names) => names.forEach(name => this.classes.add(name)), remove: (...names) => names.forEach(name => this.classes.delete(name)), contains: name => this.classes.has(name) };
  }
  set className(value) { this.classes = new Set(String(value).split(/\s+/).filter(Boolean)); }
  setAttribute(name, value) { this.attrs[name] = String(value); if (name === "class") this.className = value; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  addEventListener(name, callback) { (this.events[name] ||= []).push(callback); }
  dispatchEvent(event) { for (const callback of this.events[event.type] || []) callback(event); }
  focus() { this.focused = true; }
}
function setup({ hyperOnly = false } = {}) {
  const DATA = { manifest: { bundle_id: "test", sources: [] }, evidence: [],
    nodes: ["a", "b", "c", "d", "isolated"].map(id => ({ id, label: id, type: "person" })),
    assertions: [{ id: "h", predicate: "event", topology: "hyperedge", epistemic_status: "editorial_candidate" }, ...(!hyperOnly ? [{ id: "p", predicate: "pair", topology: "pairwise" }, { id: "q", predicate: "other", topology: "pairwise" }] : [])],
    members: [{ assertion_id: "h", node_id: "a", role: "actor", ordinal: 0 }, { assertion_id: "h", node_id: "a", role: "author", ordinal: 1 }, { assertion_id: "h", node_id: "b", role: "place", ordinal: 2 }, { assertion_id: "h", node_id: "c", role: "time", ordinal: 3 }, ...(!hyperOnly ? [{ assertion_id: "p", node_id: "a", role: "member", ordinal: 0 }, { assertion_id: "p", node_id: "d", role: "member", ordinal: 1 }, { assertion_id: "q", node_id: "a", role: "member", ordinal: 0 }, { assertion_id: "q", node_id: "b", role: "member", ordinal: 1 }] : [])] };
  const elements = new Map(); const get = id => { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); };
  const scope = { DATA, SVG_NS: "svg", I18N: { en: {}, zh: {} }, currentLanguage: "en", currentView: "hypergraph", hyperMode: "contour", selection: null, focusAssertionIds: null, autoFitRequested: false, dragPositionOverrides: new Map(), roleIndex: new Map(), roles: [], marks: [], byNode: new Map(DATA.nodes.map(row => [row.id, row])), byAssertion: new Map(DATA.assertions.map(row => [row.id, row])), byEvidence: new Map(), membersByAssertion: new Map(DATA.assertions.map(row => [row.id, DATA.members.filter(member => member.assertion_id === row.id)])), document: { createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag), createTextNode: text => ({ textContent: text }), getElementById: get, querySelector: get, querySelectorAll: () => scope.marks, activeElement: null }, MouseEvent: class { constructor(type) { this.type = type; } stopPropagation() {} }, render: () => scope.renders++, renders: 0 };
  vm.createContext(scope); vm.runInContext(functions, scope); return scope;
}
function all(element) { return [element, ...element.children.flatMap(all)]; }
function mark(dataset, classes) { const element = new Element(); element.dataset = dataset; element.className = classes; return element; }
const passed = [];
function test(name, callback) { callback(); passed.push(name); }
test("hyperedge focus cannot leak into native pairwise representation", () => {
  const s = setup(); s.selectItem("assertion", s.byAssertion.get("h")); s.switchRepresentation("pairwise");
  assert.equal(s.selection, null); assert.equal(s.focusAssertionIds, null);
  assert.deepEqual(Array.from(s.activeAssertions(), row => row.id), ["p", "q"]);
  assert.deepEqual(Array.from(s.activeNodes(), row => row.id), ["a", "b", "d"]);
});
test("native node focus uses native relations, not its hyperedges", () => {
  const s = setup(); s.switchRepresentation("pairwise"); s.selectItem("node", s.byNode.get("a"));
  assert.deepEqual(Array.from(s.focusAssertionIds), ["p", "q"]);
  s.selectItem("assertion", s.byAssertion.get("p"));
  assert.deepEqual(Array.from(s.activeNodes(), row => row.id), ["a", "d"]);
});
test("drawer hyperedge navigation exits an incompatible native view", () => {
  const s = setup(); s.switchRepresentation("pairwise"); s.selectItem("assertion", s.byAssertion.get("h"));
  assert.equal(s.currentView, "hypergraph"); assert.equal(s.hyperMode, "incidence"); assert.deepEqual(Array.from(s.focusAssertionIds), ["h"]);
});
test("hypergraph-only bundles reject native-view entry", () => {
  const s = setup({ hyperOnly: true }); s.switchRepresentation("pairwise"); assert.equal(s.currentView, "hypergraph");
  s.currentView = "graph"; s.reconcileRepresentationSelection(); assert.equal(s.currentView, "hypergraph");
});
test("matrix clicks remain stable while retaining all member roles", () => {
  const s = setup(); s.switchRepresentation("matrix"); s.selectItem("member", s.DATA.members[0]);
  assert.equal(s.hyperMode, "matrix"); assert.equal(s.focusAssertionIds, null);
  const texts = all(s.document.getElementById("drawer-body")).map(row => row.textContent);
  assert.ok(texts.includes("actor / author"));
  const buttons = all(s.document.getElementById("drawer-body")).filter(row => row.tagName === "button");
  assert.equal(buttons.length, 3); assert.ok(buttons.every(row => !row.events.keydown));
});
test("member drawer buttons navigate and aggregate relation roles", () => {
  const s = setup(); s.showDrawer("node", s.byNode.get("a"));
  const buttons = all(s.document.getElementById("drawer-body")).filter(row => row.tagName === "button");
  assert.equal(buttons.length, 3); assert.equal(buttons[0].dataset.assertion, "h");
  buttons[0].dispatchEvent(new s.MouseEvent("click")); assert.equal(s.selection.id, "h");
  const nodeButtons = all(s.document.getElementById("drawer-body")).filter(row => row.tagName === "button");
  nodeButtons[1].dispatchEvent(new s.MouseEvent("click")); assert.equal(s.selection.id, "b");
});
test("unrelated links sharing a selected endpoint never stay emphasized", () => {
  const s = setup(); s.selection = { kind: "assertion", id: "h" };
  s.marks = [mark({ node: "a", nodeSecondary: "d", assertion: "p" }, "link pairwise"), mark({ node: "a", ownerAssertion: "h" }, "mark entity-mark"), mark({ node: "a", ownerAssertion: "p" }, "mark entity-mark")];
  s.applySelection(); assert.ok(s.marks[0].classList.contains("is-hidden")); assert.ok(s.marks[1].classList.contains("is-related")); assert.ok(s.marks[2].classList.contains("is-hidden"));
});
test("isolated node stays visible when explicitly focused", () => {
  const s = setup(); s.selectItem("node", s.byNode.get("isolated"));
  assert.deepEqual(Array.from(s.activeNodes(), row => row.id), ["isolated"]); assert.equal(s.activeAssertions().length, 0);
});
test("editorial provenance is never called automated extraction", () => {
  const s = setup(); assert.equal(s.localizedStatus("editorial_candidate"), "Editorial candidate");
  s.currentLanguage = "zh"; assert.equal(s.localizedStatus("editorial_candidate"), "编排候选"); assert.ok(s.statusExplanation("editorial_candidate").includes("不是自动抽取结果"));
});
test("focus restores to a relation name or glyph rather than its long edge path", () => {
  const s = setup(); s.marks = [mark({ assertion: "h" }, "link incidence"), mark({ assertion: "h" }, "mark assertion-mark")];
  s.restoreSelectionFocus("assertion", "h"); assert.equal(s.marks[0].focused, undefined); assert.equal(s.marks[1].focused, true);
});
test("tooltip is initially anchored inside its canvas instead of extending scroll height", () => {
  const s = setup(), target = new Element(), tip = new Element(), container = { querySelector: () => tip };
  s.tooltipHandlers(target, container, "source node");
  assert.equal(tip.style.left, "0px"); assert.equal(tip.style.top, "0px"); assert.equal(tip.style.transform, "none"); assert.equal(tip.style.overflowAnchor, "none");
});
test("tooltip position includes scrolling and remains inside the visible viewport", () => {
  const s = setup(), tip = new Element(); tip.offsetWidth = 100; tip.offsetHeight = 30;
  const container = { clientWidth: 300, clientHeight: 200, scrollLeft: 400, scrollTop: 258, getBoundingClientRect: () => ({left:10,top:20,width:300,height:200}) };
  s.positionTooltip({clientX:305,clientY:210}, container, tip);
  assert.equal(tip.style.left, "585px"); assert.equal(tip.style.top, "408px");
  assert.ok(parseFloat(tip.style.left) >= container.scrollLeft); assert.ok(parseFloat(tip.style.top) >= container.scrollTop);
  assert.ok(parseFloat(tip.style.left) + tip.offsetWidth <= container.scrollLeft + container.clientWidth);
  assert.ok(parseFloat(tip.style.top) + tip.offsetHeight <= container.scrollTop + container.clientHeight);
  assert.equal(container.scrollLeft, 400); assert.equal(container.scrollTop, 258);
});
console.log(JSON.stringify({ passed }));
