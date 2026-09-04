#!/usr/bin/env node
/** Exercise the built handbook in a fresh, loopback-only browser context. */
import { createServer } from "node:http";
import { createReadStream } from "node:fs";
import { mkdir, stat, writeFile } from "node:fs/promises";
import { extname, join, resolve, sep } from "node:path";
import { pathToFileURL } from "node:url";

const defaults = {
  "base-path": "/Hyper-Knowledge/",
};
const options = { ...defaults };
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  if (key === "--help") {
    process.stdout.write("Usage: node check_docs_browser.mjs --site DIR --out DIR [--playwright PACKAGE_DIR] [--browser EXE] [--base-path /Hyper-Knowledge/]\n");
    process.exit(0);
  }
  if (!key?.startsWith("--") || !process.argv[i + 1]) throw new Error(`Invalid argument: ${key}`);
  options[key.slice(2)] = process.argv[i + 1];
}
if (!options.site || !options.out) throw new Error("--site and --out are required");
const site = resolve(options.site);
const out = resolve(options.out);
const basePath = `/${options["base-path"].split("/").filter(Boolean).join("/")}/`;
await stat(join(site, "index.html"));
await mkdir(out, { recursive: true });

const mime = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".gif": "image/gif", ".mp4": "video/mp4", ".webm": "video/webm", ".ico": "image/x-icon",
  ".woff": "font/woff", ".woff2": "font/woff2", ".txt": "text/plain; charset=utf-8",
};
const serverErrors = [];
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://127.0.0.1").pathname);
    if (pathname === "/" && basePath !== "/") {
      response.writeHead(302, { Location: basePath }); response.end(); return;
    }
    if (!pathname.startsWith(basePath)) {
      response.writeHead(404); response.end("Outside handbook base path"); return;
    }
    let file = resolve(site, `.${sep}${pathname.slice(basePath.length)}`);
    if (file !== site && !file.startsWith(`${site}${sep}`)) {
      response.writeHead(403); response.end("Forbidden"); return;
    }
    let info = await stat(file);
    if (info.isDirectory()) { file = join(file, "index.html"); info = await stat(file); }
    const headers = {
      "Content-Type": mime[extname(file).toLowerCase()] || "application/octet-stream",
      "Accept-Ranges": "bytes", "Cache-Control": "no-store",
    };
    let start = 0;
    let end = info.size - 1;
    let status = 200;
    if (request.headers.range) {
      const range = /^bytes=(\d*)-(\d*)$/.exec(request.headers.range);
      if (!range || (!range[1] && !range[2])) {
        response.writeHead(416, { "Content-Range": `bytes */${info.size}` }); response.end(); return;
      }
      if (range[1]) { start = Number(range[1]); end = range[2] ? Number(range[2]) : end; }
      else start = Math.max(0, info.size - Number(range[2]));
      end = Math.min(end, info.size - 1);
      if (start > end || start >= info.size) {
        response.writeHead(416, { "Content-Range": `bytes */${info.size}` }); response.end(); return;
      }
      status = 206;
      headers["Content-Range"] = `bytes ${start}-${end}/${info.size}`;
    }
    headers["Content-Length"] = end - start + 1;
    response.writeHead(status, headers);
    if (request.method === "HEAD") response.end();
    else createReadStream(file, { start, end }).on("error", () => response.destroy()).pipe(response);
  } catch (error) {
    if (error.code !== "ENOENT") serverErrors.push(String(error));
    response.writeHead(error.code === "ENOENT" ? 404 : 500); response.end("Not found");
  }
});
await new Promise((accept, reject) => {
  server.once("error", reject); server.listen(0, "127.0.0.1", accept);
});
const port = server.address().port;
const origin = `http://127.0.0.1:${port}`;
let playwright;
if (options.playwright) {
  let pwEntry = resolve(options.playwright);
  if ((await stat(pwEntry)).isDirectory()) pwEntry = join(pwEntry, "index.mjs");
  playwright = await import(pathToFileURL(pwEntry).href);
} else playwright = await import("playwright");
const { chromium } = playwright;
const report = {
  schema: "hyper-knowledge.docs-browser-qa/v2", created_at: new Date().toISOString(),
  site, browser: options.browser || "Playwright bundled Chromium", base_path: basePath,
  isolation: { fresh_context_per_viewport_and_locale: true, user_profile_used: false, allowed_origin: origin },
  pages: [], searches: [], gif_checks: [], blocked_external_requests: [], browser_errors: [], http_errors: [],
  server_errors: serverErrors, failures: [], screenshots: [],
};
const states = [
  "overview-matrix", "overview-incidence", "overview-enclosure", "edge-matrix", "edge-incidence",
  "edge-enclosure", "node-matrix", "node-incidence", "node-enclosure", "hover-enclosure",
];
const check = (condition, message) => { if (!condition) throw new Error(message); };
const screenshot = async (page, name, fullPage = true) => {
  const path = join(out, `${name}.png`);
  if (fullPage) {
    await page.evaluate(() => { scrollTo(0, 0); });
    await page.evaluate(() => new Promise(accept => requestAnimationFrame(() => requestAnimationFrame(accept))));
  }
  await page.screenshot({ path, fullPage, animations: "disabled" });
  report.screenshots.push(path);
  return path;
};
async function settle(page) {
  await page.locator(".md-content h1").waitFor({ state: "visible" });
  await page.evaluate(() => document.fonts.ready);
}
async function assertNoOverflow(page) {
  const result = await page.evaluate(() => ({
    width: innerWidth, document_width: document.documentElement.scrollWidth,
    body_width: document.body.scrollWidth,
    offenders: [...document.querySelectorAll("body *")].filter(el => {
      const r = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return r.width > 0 && style.visibility !== "hidden" && style.display !== "none"
        && (r.right > innerWidth + 2 || r.left < -2) && style.position !== "fixed";
    }).slice(0, 10).map(el => ({ tag: el.tagName, class: String(el.className), width: el.getBoundingClientRect().width })),
  }));
  check(result.document_width <= result.width + 1 && result.body_width <= result.width + 1,
    `Horizontal page overflow: ${JSON.stringify(result)}`);
  return result;
}
async function galleryChecks(page, locale, device) {
  const groups = page.locator("details.hk-gallery-group");
  check(await groups.count() === 4, "Expected four gallery groups");
  const toggles = [];
  for (let i = 0; i < 4; i++) {
    const group = groups.nth(i);
    const initial = await group.evaluate(el => el.open);
    await group.locator("summary").click();
    const toggled = await group.evaluate(el => el.open);
    check(toggled !== initial, `Gallery group ${i + 1} did not toggle from a real click`);
    await group.locator("summary").click();
    check(await group.evaluate(el => el.open) === initial, `Gallery group ${i + 1} did not restore`);
    if (!initial) await group.locator("summary").click();
    toggles.push({ group: i + 1, initially_open: initial, click_toggle_verified: true });
  }
  const images = page.locator(".hk-gallery-group .hk-gallery img");
  check(await images.count() === 10, "Expected exactly ten gallery state images");
  await page.waitForFunction(() => [...document.querySelectorAll(".hk-gallery-group .hk-gallery img")]
    .every(img => img.complete && img.naturalWidth > 0), undefined, { timeout: 20000 });
  const metadata = await images.evaluateAll(elements => elements.map(img => ({
    src: img.src, width: img.naturalWidth, height: img.naturalHeight,
    link: img.closest("a")?.href, alt: img.alt,
  })));
  for (const state of states) {
    const item = metadata.find(img => new URL(img.src).pathname.endsWith(`/${state}-${locale}.png`));
    check(item && item.width > 0 && item.link === item.src, `Missing loaded click-through state: ${state}-${locale}`);
  }
  const overflow = await assertNoOverflow(page);
  await screenshot(page, `gallery-open-${locale}-${device}`);
  const first = images.first();
  const target = await first.evaluate(img => img.closest("a").href);
  await first.click();
  await page.waitForURL(target);
  await page.waitForFunction(() => [...document.images].some(img => img.complete && img.naturalWidth > 0));
  const original = await page.locator("img").first().evaluate(img => ({ width: img.naturalWidth, height: img.naturalHeight }));
  check(original.width === metadata[0].width, "Click-through did not open the original resolution");
  await page.goBack({ waitUntil: "domcontentloaded" });
  await settle(page);
  return { toggles, images: metadata, open_all_overflow: overflow, original_image_click_verified: true };
}
async function gifCheck(page, locale, device, pageName) {
  check(await page.locator('.md-content video, .md-content a[href$=".mp4"]').count() === 0,
    "Public tour must use an embedded GIF rather than a video player or MP4 link");
  const image = page.locator(`.md-content img[src$="/tour-${locale}.gif"]`).first();
  await image.waitFor({ state: "visible" });
  const embedded = await image.evaluate(img => ({
    source: img.currentSrc, width: img.naturalWidth, height: img.naturalHeight,
    complete: img.complete, link: img.closest("a")?.href,
  }));
  check(embedded.complete && embedded.width > 0 && embedded.height > 0,
    `Embedded GIF did not load: ${JSON.stringify(embedded)}`);
  check(embedded.link === embedded.source, "Embedded GIF must link directly to its original GIF file");
  await image.click();
  await page.waitForURL(embedded.link);
  await page.waitForFunction(() => [...document.images]
    .some(img => img.complete && img.naturalWidth > 0), undefined, { timeout: 20000 });
  const original = await page.locator("img").first().evaluate(img => ({
    source: img.currentSrc, width: img.naturalWidth, height: img.naturalHeight, complete: img.complete,
  }));
  check(original.complete && original.source === embedded.source
    && original.width === embedded.width && original.height === embedded.height,
    `GIF click-through did not load the original image: ${JSON.stringify(original)}`);
  // A loaded browser image does not prove frame timing or looping. Those are
  // decoded and checked separately by tools/check_live_showcase.py.
  report.gif_checks.push({ locale, device, page: pageName, embedded, original,
    embedded_load_verified: true, original_gif_click_verified: true,
    playback_timing_verified: false, playback_check: "tools/check_live_showcase.py" });
  await page.goBack({ waitUntil: "domcontentloaded" });
  await settle(page);
}
async function searchCheck(page, locale, device) {
  const input = page.locator('[data-md-component="search-query"]');
  if (!await input.isVisible()) await page.locator('.md-header label[for="__search"]').click();
  const query = locale === "zh" ? "苏轼" : "hyperedge";
  await input.fill(query);
  const results = page.locator('[data-md-component="search-result"] a.md-search-result__link');
  await results.first().waitFor({ state: "visible", timeout: 20000 });
  const found = await results.evaluateAll(links => links.map(link => ({ href: link.href, text: link.innerText.trim() })));
  check(found.length > 0, `No search results for ${query}`);
  const target = found[0];
  check(new URL(target.href).origin === origin, "Search result points outside local server");
  const expectedPrefix = `${basePath}${locale === "zh" ? "zh/" : ""}`;
  check(new URL(target.href).pathname.startsWith(expectedPrefix), "Search result is outside active locale");
  if (locale === "en") check(!new URL(target.href).pathname.startsWith(`${basePath}zh/`), "English search returned Chinese route first");
  await screenshot(page, `search-${locale}-${device}`, false);
  await results.first().click();
  await page.waitForURL(url => url.pathname === new URL(target.href).pathname);
  await settle(page);
  report.searches.push({ locale, device, query, count: found.length, first: target, click_verified: true });
}

let browser;
try {
  browser = await chromium.launch({ headless: true, ...(options.browser ? { executablePath: options.browser } : {}) });
  for (const [device, viewport] of Object.entries({ desktop: { width: 1920, height: 1200 }, mobile: { width: 390, height: 844 } })) {
    for (const locale of ["en", "zh"]) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1, reducedMotion: "reduce", locale: locale === "zh" ? "zh-CN" : "en-US" });
      await context.route("**/*", route => {
        const url = new URL(route.request().url());
        if (["data:", "blob:", "about:"].includes(url.protocol) || url.origin === origin) return route.continue();
        report.blocked_external_requests.push({ url: url.href, resource: route.request().resourceType(), locale, device });
        return route.abort("blockedbyclient");
      });
      const page = await context.newPage();
      page.setDefaultTimeout(15000);
      page.on("pageerror", error => report.browser_errors.push({ locale, device, error: String(error) }));
      page.on("response", response => {
        if (response.status() >= 400) report.http_errors.push({ locale, device, status: response.status(), url: response.url() });
      });
      const localPrefix = `${origin}${basePath}${locale === "zh" ? "zh/" : ""}`;
      for (const [name, suffix] of [["home", ""], ["workbench", "guide/workbench/"]]) {
        const result = { locale, device, page: name, url: `${localPrefix}${suffix}` };
        try {
          const response = await page.goto(result.url, { waitUntil: "domcontentloaded" });
          check(response?.ok(), `Page returned ${response?.status()}`);
          await settle(page);
          await page.waitForFunction(() => [...document.querySelectorAll(".md-content img")].every(img => img.complete && img.naturalWidth > 0), undefined, { timeout: 20000 });
          result.heading = await page.locator(".md-content h1").innerText();
          result.overflow = await assertNoOverflow(page);
          result.screenshot = await screenshot(page, `${name}-${locale}-${device}`);
          await gifCheck(page, locale, device, name);
          if (name === "workbench") {
            result.gallery = await galleryChecks(page, locale, device);
            await searchCheck(page, locale, device);
          }
          result.passed = true;
        } catch (error) {
          result.passed = false;
          result.error = String(error);
          report.failures.push({ locale, device, page: name, error: String(error) });
          await screenshot(page, `failure-${name}-${locale}-${device}`, false).catch(() => {});
        }
        report.pages.push(result);
        process.stdout.write(`${result.passed ? "PASS" : "FAIL"} ${locale} ${device} ${name}${result.error ? `: ${result.error}` : ""}\n`);
      }
      await context.close();
    }
  }
} catch (error) {
  report.failures.push({ stage: "browser_setup", error: String(error) });
} finally {
  if (browser) await browser.close();
  await new Promise(accept => server.close(accept));
}
// Material gracefully probes these optional services. A bare `mkdocs build`
// has no mike versions.json, and its language switcher also probes per-page
// sitemap URLs before falling back to the explicit language links. Keep every
// request in the report; never substitute fake responses or hide asset errors.
report.optional_metadata_requests = [];
report.required_http_errors = report.http_errors.filter(item => {
  const path = new URL(item.url).pathname;
  let reason;
  if (item.status === 404 && path.endsWith("/versions.json")) reason = "mike version index is generated at deployment, not by a bare site build";
  else if (item.status === 404 && path.endsWith("/sitemap.xml") && path !== `${basePath}sitemap.xml`) reason = "Material alternate-language sitemap probe falls back to explicit page links";
  if (reason) report.optional_metadata_requests.push({ ...item, reason });
  return !reason;
});
report.unexpected_external_requests = report.blocked_external_requests.filter(item => {
  const optional = /^https:\/\/api\.github\.com\/repos\/[^/]+\/[^/]+(?:\/releases\/latest)?$/.test(item.url);
  if (optional) report.optional_metadata_requests.push({ ...item, reason: "optional GitHub repository facts blocked by the loopback-only test policy" });
  return !optional;
});
report.core_interactions_passed = report.failures.length === 0 && report.pages.length === 8
  && report.browser_errors.length === 0 && report.required_http_errors.length === 0 && report.server_errors.length === 0;
report.optional_metadata_verified = report.optional_metadata_requests.length === 0;
report.passed = report.core_interactions_passed && report.unexpected_external_requests.length === 0;
report.status = report.passed
  ? (report.optional_metadata_verified ? "passed" : "core_passed_optional_metadata_unverified") : "failed";
report.summary = {
  page_checks: report.pages.length, passed_pages: report.pages.filter(item => item.passed).length,
  original_image_click_checks: report.pages.filter(item => item.gallery?.original_image_click_verified).length,
  embedded_gif_checks: report.gif_checks.length,
  original_gif_click_checks: report.gif_checks.filter(item => item.original_gif_click_verified).length,
  search_click_checks: report.searches.length,
  screenshot_count: report.screenshots.length,
};
await writeFile(join(out, "browser-qa.json"), `${JSON.stringify(report, null, 2)}\n`);
process.stdout.write(`${JSON.stringify({ passed: report.passed, status: report.status, ...report.summary, report: join(out, "browser-qa.json") })}\n`);
if (!report.passed) process.exitCode = 1;
