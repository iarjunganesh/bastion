"use strict";

const gallery = document.querySelector("#evidence-gallery");
const nav = document.querySelector("#site-nav");
const navToggle = document.querySelector(".nav-toggle");
const header = document.querySelector("[data-header]");
const themeToggle = document.querySelector("[data-theme-toggle]");
const themeLabel = document.querySelector("[data-theme-label]");
const colorScheme = window.matchMedia("(prefers-color-scheme: dark)");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const allowedEvidenceOrigin = "https://github.com";
const allowedVideoOrigins = new Set([
  "https://www.youtube-nocookie.com",
  "https://player.vimeo.com",
]);

function savedTheme() {
  try {
    const value = window.localStorage.getItem("bastion-theme");
    return value === "light" || value === "dark" ? value : "system";
  } catch {
    return "system";
  }
}

function effectiveTheme(mode) {
  return mode === "system" ? (colorScheme.matches ? "dark" : "light") : mode;
}

function updateThemeAssets(theme) {
  const motion = reducedMotion.matches ? "static" : "gif";
  for (const asset of document.querySelectorAll("[data-theme-asset]")) {
    const source = asset.dataset[`${theme}${motion === "gif" ? "Gif" : "Static"}`];
    if (source && asset.getAttribute("src") !== source) asset.setAttribute("src", source);
  }
}

function applyTheme(mode) {
  const theme = effectiveTheme(mode);
  if (mode === "system") {
    delete document.documentElement.dataset.theme;
  } else {
    document.documentElement.dataset.theme = mode;
  }
  if (themeLabel) themeLabel.textContent = mode;
  if (themeToggle) {
    const next = mode === "system" ? "light" : mode === "light" ? "dark" : "system";
    themeToggle.setAttribute("aria-label", `Use ${next} theme`);
  }
  updateThemeAssets(theme);
}

function storeTheme(mode) {
  try {
    if (mode === "system") window.localStorage.removeItem("bastion-theme");
    else window.localStorage.setItem("bastion-theme", mode);
  } catch {
    // Theme persistence is optional; the control still works for this page view.
  }
}

function safeUrl(value, allowedOrigins) {
  try {
    const url = new URL(value);
    return allowedOrigins.has(url.origin) ? url.toString() : "";
  } catch {
    return "";
  }
}

function createEvidenceCard(item, index) {
  const card = document.createElement("article");
  card.className = "evidence-card";
  card.style.setProperty("--card-accent", item.accent || "#5b8cff");

  const kicker = document.createElement("div");
  kicker.className = "evidence-kicker";
  const number = document.createElement("span");
  number.textContent = String(index + 1).padStart(2, "0");
  const state = document.createElement("span");
  state.className = "evidence-state";
  state.textContent = item.state || "RECORD VERIFIED";
  kicker.append(number, state);

  const title = document.createElement("h3");
  title.textContent = item.title;
  const summary = document.createElement("p");
  summary.textContent = item.summary;
  card.append(kicker, title, summary);

  const href = safeUrl(item.recordUrl, new Set([allowedEvidenceOrigin]));
  if (href) {
    const link = document.createElement("a");
    link.className = "evidence-link";
    link.href = href;
    link.textContent = "Inspect proof boundary ↗";
    link.setAttribute("aria-label", `Inspect proof boundary for ${item.title}`);
    card.append(link);
  }
  return card;
}

function renderEvidence(items) {
  if (!gallery) return;
  gallery.replaceChildren();
  gallery.setAttribute("aria-busy", "false");

  if (!Array.isArray(items) || items.length === 0) {
    const empty = document.createElement("article");
    empty.className = "evidence-card evidence-empty";
    const title = document.createElement("h3");
    title.textContent = "Final gallery captures are still being prepared.";
    const message = document.createElement("p");
    message.textContent = "The repository remains the source of truth for verified proof records.";
    empty.append(title, message);
    gallery.append(empty);
    return;
  }

  for (const [index, item] of items.entries()) {
    gallery.append(createEvidenceCard(item, index));
  }
}

function renderEvidenceError() {
  if (!gallery) return;
  gallery.replaceChildren();
  gallery.setAttribute("aria-busy", "false");
  const error = document.createElement("article");
  error.className = "evidence-card evidence-error";
  const title = document.createElement("h3");
  title.textContent = "Evidence index unavailable.";
  const message = document.createElement("p");
  message.textContent = "No production endpoint was contacted. Open the public repository to inspect retained proof.";
  const link = document.createElement("a");
  link.className = "button button-secondary";
  link.href = "https://github.com/iarjunganesh/bastion/tree/main/assets/evidence";
  link.textContent = "Open evidence ledger";
  error.append(title, message, link);
  gallery.append(error);
}

function renderVideo(video) {
  if (!video || video.status !== "published") return;
  const container = document.querySelector("[data-video-container]");
  const embedUrl = safeUrl(video.embedUrl, allowedVideoOrigins);
  if (!container || !embedUrl) return;

  const frame = document.createElement("iframe");
  frame.className = "video-embed";
  frame.src = embedUrl;
  frame.title = video.title || "Bastion demo video";
  frame.loading = "lazy";
  frame.allow = "accelerometer; encrypted-media; gyroscope; picture-in-picture";
  frame.allowFullscreen = true;
  container.replaceWith(frame);
}

/** Render how old the committed snapshot is, from the stamp already in the markup.
 *
 * The absolute UTC time stays authoritative and visible; this only says how far away it is, so a
 * reader sees staleness instead of having to compute it. It reads the `datetime` attribute that
 * `check_site.py` already pins to the selected count-only snapshot's `captured_utc` — there is no second source
 * and no network call, because a page that fetched its own freshness would be claiming liveness
 * this console deliberately does not have. */
function renderVerifiedAge() {
  const stamp = document.querySelector("[data-verified-at]");
  const target = document.querySelector("[data-verified-age]");
  if (!stamp || !target) return;

  const captured = Date.parse(stamp.getAttribute("datetime") || "");
  if (Number.isNaN(captured)) return;

  const seconds = Math.round((captured - Date.now()) / 1000);
  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
  ];

  let label = "just now";
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size) {
      const relative = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
      label = relative.format(Math.round(seconds / size), unit);
      break;
    }
  }

  target.textContent = `snapshot ${label}`;
  target.hidden = false;
}

async function loadPublicContent() {
  if (!gallery) return;
  try {
    const response = await fetch("/data/site-content.json", {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("public content unavailable");
    const content = await response.json();
    renderEvidence(content.evidence);
    renderVideo(content.video);
  } catch {
    renderEvidenceError();
  }
}

if (nav && navToggle) {
  navToggle.addEventListener("click", () => {
    const isOpen = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!isOpen));
    nav.classList.toggle("is-open", !isOpen);
  });

  nav.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      navToggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    }
  });
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const current = savedTheme();
    const next = current === "system" ? "light" : current === "light" ? "dark" : "system";
    storeTheme(next);
    applyTheme(next);
  });
}

colorScheme.addEventListener("change", () => {
  if (savedTheme() === "system") applyTheme("system");
});
reducedMotion.addEventListener("change", () => applyTheme(savedTheme()));

if (header) {
  const updateHeader = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
}

applyTheme(savedTheme());
renderVerifiedAge();
loadPublicContent();
