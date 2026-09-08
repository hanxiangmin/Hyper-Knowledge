/** Capture the Su Zhe selection via real clicks in a fresh local browser. */
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";

const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  assert(process.argv[i].startsWith("--") && process.argv[i + 1], "Expected --option value");
  options[process.argv[i].slice(2)] = process.argv[i + 1];
}
for (const key of ["source", "bundle", "assets", "report", "playwright", "browser"]) assert(options[key], `Missing --${key}`);
const source = resolve(options.source);
const assets = resolve(options.assets);
const reportDir = resolve(options.report);
const digest = async path => createHash("sha256").update(await readFile(path)).digest("hex");
const nodeId = "person:su-zhe";
const members = (await readFile(join(resolve(options.bundle), "members.jsonl"), "utf8"))
  .trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const expected = [...new Set(members.filter(row => row.node_id === nodeId).map(row => row.assertion_id))].sort();
assert.equal(expected.length, 4, "The Su Zhe showcase expects four incident hyperedges");
const require = createRequire(import.meta.url);
const { chromium } = require(resolve(options.playwright));
const report = { source, sourceSha256: await digest(source), selectedNode: nodeId,
  expectedHyperedges: expected, createdAt: new Date().toISOString(),
  isolation: "Fresh browser context, no user profile, external requests blocked",
  screenshots: [], errors: [], blockedRequests: [], passed: false };
await mkdir(assets, { recursive: true });
await mkdir(reportDir, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: resolve(options.browser) });
try {
  report.browserVersion = browser.version();
  for (const locale of ["zh", "en"]) {
    const context = await browser.newContext({ viewport: { width: 1920, height: 1200 },
      deviceScaleFactor: 1, colorScheme: "light", reducedMotion: "reduce",
      locale: locale === "zh" ? "zh-CN" : "en-US" });
    const page = await context.newPage();
    page.on("pageerror", error => report.errors.push(String(error)));
    await page.route(/^https?:/, route => {
      report.blockedRequests.push(route.request().url());
      return route.abort();
    });
    await page.goto(pathToFileURL(source).href);
    await page.locator(`[data-language="${locale}"]`).click();
    await page.locator('[data-representation="overview"]').click();
    const node = page.locator(`.overview-node[data-node="${nodeId}"]`);
    await node.locator(".node-halo").click();
    await page.mouse.move(1, 1);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(id => document.querySelector(`.overview-node[data-node="${id}"]`)?.classList.contains("is-selected"), nodeId);
    await page.waitForTimeout(500);
    const state = await page.evaluate(() => {
      const box = el => { const b = el.getBoundingClientRect(); return { x: b.x, y: b.y, width: b.width, height: b.height }; };
      return {
        language: document.documentElement.lang,
        representation: document.querySelector('.representation-button[aria-pressed="true"]').dataset.representation,
        selectedNodes: [...document.querySelectorAll(".overview-node.is-selected")].map(el => el.dataset.node),
        edges: [...document.querySelectorAll(".overview-edge.is-overview-related")].map(el => el.dataset.assertion).sort(),
        roles: [...document.querySelectorAll(".overview-role-label")].map(el => ({ node: el.dataset.node, edge: el.dataset.assertion, role: el.dataset.role, box: box(el) })),
        drawerTitle: document.querySelector(".drawer-title")?.textContent,
        muted: document.querySelectorAll(".is-overview-muted").length,
        canvas: box(document.querySelector(".canvas-wrap")),
        edgeLabels: [...document.querySelectorAll(".overview-edge.is-overview-related .overview-edge-label")].map(box),
        nodes: [...document.querySelectorAll(".overview-node.is-overview-related .node-halo")].map(box),
      };
    });
    assert.equal(state.representation, "overview");
    assert.deepEqual(state.selectedNodes, [nodeId]);
    assert.deepEqual(state.edges, expected);
    assert.equal(state.roles.length, expected.length);
    assert(state.roles.every(role => role.node === nodeId));
    assert(state.muted > 0);
    assert.equal(state.drawerTitle, "苏辙");
    assert(state.canvas.y + state.canvas.height <= 1201, "Graph exceeds the viewport");
    const overlaps = (a, b) => Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x) > 1
      && Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y) > 1;
    const collisions = [];
    for (const label of [...state.edgeLabels, ...state.roles.map(role => role.box)]) {
      for (const shape of state.nodes) if (overlaps(label, shape)) collisions.push({ label, shape });
    }
    assert.equal(collisions.length, 0, "A highlighted label covers a highlighted node");
    const path = join(assets, `node-su-zhe-overview-${locale}.png`);
    await page.screenshot({ path, fullPage: true });
    report.screenshots.push({ locale, path, sha256: await digest(path), state, collisions });
    await context.close();
    console.log(`PASS ${locale}: Su Zhe selected, four related hyperedges, no node-label collisions`);
  }
  assert.equal(report.errors.length, 0);
  assert.equal(await digest(source), report.sourceSha256, "Source workbench changed");
  report.passed = true;
} finally {
  await browser.close();
  await writeFile(join(reportDir, "suzhe-capture.json"), `${JSON.stringify(report, null, 2)}\n`);
}
