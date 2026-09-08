/* An in-page viewer for linked screenshots; image links still work without JS. */
(() => {
  if (document.documentElement.dataset.hkGalleryReady) return;
  document.documentElement.dataset.hkGalleryReady = "true";

  let viewer;
  let picture;
  let heading;
  let hint;
  let status;
  let closeButton;
  let session;

  function restorePage() {
    if (!session) return;
    const previous = session;
    session = null;
    document.documentElement.style.overflow = previous.overflow;
    if (previous.link.isConnected) previous.link.focus({ preventScroll: true });
    window.scrollTo({ left: previous.x, top: previous.y, behavior: "instant" });
    picture.removeAttribute("src");
  }

  function closeViewer() {
    if (viewer.open) viewer.close();
    restorePage();
  }

  function createViewer() {
    viewer = document.createElement("dialog");
    if (typeof viewer.showModal !== "function") return false;
    viewer.className = "hk-image-viewer";
    viewer.setAttribute("aria-labelledby", "hk-image-title");
    viewer.setAttribute("aria-describedby", "hk-image-hint");

    const toolbar = document.createElement("div");
    toolbar.className = "hk-image-toolbar";
    heading = document.createElement("p");
    heading.id = "hk-image-title";
    closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "hk-image-close";
    closeButton.addEventListener("click", closeViewer);
    toolbar.append(heading, closeButton);

    const stage = document.createElement("div");
    stage.className = "hk-image-stage";
    picture = document.createElement("img");
    picture.draggable = false;
    status = document.createElement("p");
    status.className = "hk-image-status";
    status.setAttribute("role", "status");
    stage.append(picture, status);
    hint = document.createElement("p");
    hint.id = "hk-image-hint";
    hint.className = "hk-image-hint";
    viewer.append(toolbar, stage, hint);

    picture.addEventListener("load", () => { status.hidden = true; });
    picture.addEventListener("error", () => {
      if (!session) return;
      status.hidden = false;
      status.textContent = session.zh
        ? "图片未能加载，请关闭后重试。"
        : "The image could not load. Close the viewer and try again.";
    });
    viewer.addEventListener("click", (event) => {
      if ([viewer, stage, picture].includes(event.target)) closeViewer();
    });
    viewer.addEventListener("cancel", (event) => {
      event.preventDefault();
      closeViewer();
    });
    viewer.addEventListener("close", () => {
      if (!viewer.open) restorePage();
    });
    document.body.append(viewer);
    return true;
  }

  // Delegation also covers images revealed inside expandable galleries.
  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey
        || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (!(event.target instanceof Element)) return;
    const link = event.target.closest(".hk-gallery a");
    const thumbnail = link?.querySelector("img");
    if (!thumbnail || !link.href || link.hasAttribute("download")) return;
    if (!viewer && !createViewer()) { viewer = null; return; }
    if (viewer.open) return;

    const zh = document.documentElement.lang.toLowerCase().startsWith("zh");
    session = {
      link, zh, x: window.scrollX, y: window.scrollY,
      overflow: document.documentElement.style.overflow,
    };
    heading.textContent = thumbnail.alt || (zh ? "图谱截图" : "Graph screenshot");
    picture.alt = thumbnail.alt;
    closeButton.textContent = zh ? "关闭 ×" : "Close ×";
    closeButton.setAttribute("aria-label", zh ? "关闭图片，返回原位置" : "Close image and return");
    hint.textContent = zh
      ? "点击图片或空白处返回 · Esc 关闭"
      : "Click the image or background to return · Esc to close";
    status.textContent = zh ? "正在加载图片…" : "Loading image…";
    status.hidden = false;
    picture.src = link.href;
    viewer.showModal();
    document.documentElement.style.overflow = "hidden";
    closeButton.focus({ preventScroll: true });
    event.preventDefault();
  });
})();
