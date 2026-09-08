/** DOM-level regression tests; these do not substitute for visual browser QA. */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { runInNewContext } from "node:vm";

const source = readFileSync(new URL("../docs/javascripts/gallery.js", import.meta.url), "utf8");

function setup({ lang = "zh-CN", modal = true } = {}) {
  const elements = [];
  const delayed = [];
  class Element {
    constructor(tag) {
      this.tag = tag;
      this.handlers = new Map();
      this.attributes = {};
      this.style = {};
      this.dataset = {};
      this.children = [];
      this.isConnected = true;
      this.open = false;
      elements.push(this);
    }
    addEventListener(name, callback) {
      this.handlers.set(name, [...(this.handlers.get(name) || []), callback]);
    }
    dispatch(name, values = {}) {
      const event = { target: this, button: 0, defaultPrevented: false,
        preventDefault() { this.defaultPrevented = true; }, ...values };
      for (const callback of this.handlers.get(name) || []) callback(event);
      return event;
    }
    append(...children) { this.children.push(...children); }
    setAttribute(name, value) { this.attributes[name] = value; }
    hasAttribute(name) { return name in this.attributes; }
    removeAttribute(name) { delete this.attributes[name]; delete this[name]; }
    closest(selector) { return selector === ".hk-gallery a" ? this.link : null; }
    querySelector(selector) { return selector === "img" ? this.image : null; }
    focus(options) { document.activeElement = this; this.focusOptions = options; }
    showModal() { this.open = true; }
    close() { this.open = false; delayed.push(() => this.dispatch("close")); }
  }
  if (!modal) Element.prototype.showModal = undefined;
  const document = new Element("document");
  document.documentElement = new Element("html");
  document.documentElement.lang = lang;
  document.documentElement.style.overflow = "auto";
  document.body = new Element("body");
  document.createElement = tag => new Element(tag);
  const window = { scrollX: 12, scrollY: 680,
    scrollTo({ left, top }) { this.scrollX = left; this.scrollY = top; } };
  const context = { document, window, Element };
  runInNewContext(source, context);
  const link = new Element("a");
  link.href = "http://127.0.0.1:8876/assets/showcase-v3/overview-matrix-zh.png";
  const thumbnail = new Element("img");
  thumbnail.alt = "完整关联矩阵";
  thumbnail.link = link;
  link.link = link;
  link.image = thumbnail;
  return { document, window, link, thumbnail, context,
    find: tag => elements.find(el => el.tag === tag),
    findClass: name => elements.find(el => el.className === name),
    click: (target = thumbnail, options = {}) => document.dispatch("click", { target, ...options }),
    flush: () => { while (delayed.length) delayed.shift()(); },
  };
}

test("gallery clicks load the original inside a labelled modal", () => {
  const env = setup();
  assert.equal(env.click().defaultPrevented, true);
  const viewer = env.find("dialog");
  const picture = env.findClass("hk-image-stage").children[0];
  assert.equal(viewer.open, true);
  assert.equal(picture.src, env.link.href);
  assert.equal(picture.alt, env.thumbnail.alt);
  assert.equal(viewer.attributes["aria-labelledby"], "hk-image-title");
  assert.equal(env.document.documentElement.style.overflow, "hidden");
  assert.equal(env.document.activeElement, env.find("button"));
  assert.equal(env.find("button").textContent, "关闭 ×");
  picture.dispatch("load");
  assert.equal(env.findClass("hk-image-status").hidden, true);
});

for (const method of ["image", "background", "stage", "button", "escape"]) {
  test(`${method} closes and restores focus, scroll and overflow`, () => {
    const env = setup();
    env.click();
    const viewer = env.find("dialog");
    const stage = env.findClass("hk-image-stage");
    const picture = stage.children[0];
    env.window.scrollY = 0;
    if (method === "button") env.find("button").dispatch("click");
    else if (method === "escape") assert.equal(viewer.dispatch("cancel").defaultPrevented, true);
    else viewer.dispatch("click", { target: method === "image" ? picture : method === "stage" ? stage : viewer });
    env.flush();
    assert.equal(viewer.open, false);
    assert.equal(env.document.documentElement.style.overflow, "auto");
    assert.equal(env.window.scrollX, 12);
    assert.equal(env.window.scrollY, 680);
    assert.equal(env.document.activeElement, env.link);
    assert.equal(env.link.focusOptions.preventScroll, true);
    assert.equal(picture.src, undefined);
  });
}

test("English labels and image-load failure stay inside the viewer", () => {
  const env = setup({ lang: "en" });
  env.click(env.link); // Keyboard activation targets the anchor, not the image.
  assert.equal(env.find("button").textContent, "Close ×");
  env.findClass("hk-image-stage").children[0].dispatch("error");
  assert.match(env.findClass("hk-image-status").textContent, /could not load/);
  assert.equal(env.findClass("hk-image-status").hidden, false);
  assert.equal(env.find("dialog").open, true);
});

test("regular links, modified clicks, downloads and unsupported browsers keep their defaults", () => {
  const env = setup();
  for (const options of [{ ctrlKey: true }, { metaKey: true }, { shiftKey: true },
    { altKey: true }, { button: 1 }, { defaultPrevented: true }]) {
    assert.equal(env.click(env.thumbnail, options).defaultPrevented, !!options.defaultPrevented);
  }
  assert.equal(env.click(env.document.body).defaultPrevented, false);
  env.link.setAttribute("download", "");
  assert.equal(env.click().defaultPrevented, false);
  assert.equal(env.find("dialog"), undefined);
  const legacy = setup({ modal: false });
  assert.equal(legacy.click().defaultPrevented, false);
  assert.equal(legacy.document.documentElement.style.overflow, "auto");
});

test("repeated initialization and a delayed close cannot reset a newly opened image", () => {
  const env = setup();
  runInNewContext(source, env.context);
  assert.equal(env.document.handlers.get("click").length, 1);
  env.click();
  env.find("button").dispatch("click");
  env.click();
  env.flush();
  assert.equal(env.find("dialog").open, true);
  assert.equal(env.document.documentElement.style.overflow, "hidden");
  env.find("button").dispatch("click");
  env.flush();
  assert.equal(env.document.documentElement.style.overflow, "auto");
});
