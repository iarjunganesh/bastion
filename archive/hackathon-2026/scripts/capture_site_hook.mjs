/**
 * Record the opening beat from the live public evidence console.
 *
 * The hook is the one beat whose subject is a web page rather than a console session, and the
 * page genuinely moves: the hero route diagram carries 24 `animateMotion` and 20 `animate`
 * elements, so a full-page screenshot panned by the assembler would throw away the thing that
 * makes it worth showing. This drives a real browser against the real deployed URL and records
 * what it renders.
 *
 * Deliberate choices:
 *
 * - **Dark.** The site follows `prefers-color-scheme`, and every other asset in the cut is dark;
 *   `archive/hackathon-2026/assets/screenshots/README.md` asks for that on purpose, so the sequence reads as one project.
 * - **A fresh browser profile**, which is why no account photo, bookmark bar or open tab can leak
 *   into frame the way they did in the promoted `.takes/` captures. Playwright records the page
 *   viewport only — there is no browser chrome in the output at all.
 * - **The live URL, not `site/dist`.** Serving the local build would produce the same pixels while
 *   proving strictly less: that the public console is genuinely reachable is part of the claim.
 *
 * Requires Playwright and the installed Edge, neither of which is a repository dependency — this
 * is one-time media tooling, not a CI gate:
 *
 *     npm install playwright@1.62.1 --prefix "$env:TEMP/bastion-media"
 *     $env:BASTION_PLAYWRIGHT = "file:///$env:TEMP/bastion-media/node_modules/playwright/index.mjs"
 *     node archive/hackathon-2026/scripts/capture_site_hook.mjs
 *
 * The result is written to `assets/demo-video/beats/00-hook.mp4`, which is gitignored like every
 * other raw take. Declare it in `VIDEO_REDACTIONS` and run `python scripts/redact_evidence.py
 * --check` before it reaches anything judge-facing.
 */

import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Resolved dynamically so the capture needs no repository dependency: this is one-time media
// tooling, and a root package.json plus node_modules would enter the clean-clone
// reproducibility surface for the sake of one beat. Point BASTION_PLAYWRIGHT at an install
// outside the tree, or install playwright anywhere on the default resolution path.
const { chromium } = await import(process.env.BASTION_PLAYWRIGHT ?? "playwright");

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(ROOT, "assets", "demo-video", "beats", "00-hook.mp4");
const SCRATCH = join(ROOT, "assets", "demo-video", "build", "site-capture");

const URL = "https://bastion.arjunganesh.dev/";
const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 30;

// The pan stops to be read rather than scrolling continuously. A single 27s glide was tried first
// and nothing landed: text moved past faster than a viewer could take it in, which made a page
// full of substance feel like a page being skimmed. Each stop instead rests on one section long
// enough to read it, and the offsets are the section positions measured on the live page rather
// than estimated. They also track the narration — the pillars stop arrives under "deployed on
// Google's managed agent stack", and the governed-flow stop under the read-only boundary.
//
// One stop carries an optional `driftTo`, and it is the exception that proves the rule: the
// governed-flow section is 1547px tall and its figure alone is 739px, so no single 1080px frame
// holds both the heading and the whole diagram — parking at the section top cut the bottom row
// (Access Auditor, Escalation Agent, the live IAM policy) out of frame, and parking low enough to
// keep it sheared the heading against the sticky nav. The drift crosses 315px over the whole hold
// — roughly 48px a second, slower than the eye tracks as movement — so the shot opens on "Raw IAM
// stops here. Context continues." and settles on the complete flow with the boundary cards below
// it. It costs no extra time, which matters: the recording only carries ~0.9s of slack over the
// 34.1s hook narration that `render_take` trims it to.
const STOPS = [
  { y: 0, holdMs: 7500 }, // hero: "The access review that reviews itself", route animation running
  { y: 1150, holdMs: 5500 }, // the fleet counters, then "Institutional ownership is the architecture"
  { y: 2185, driftTo: 2500, holdMs: 6500 }, // "Raw IAM stops here." onto the whole governed flow
  { y: 3732, holdMs: 4500 }, // "A human decision outlives the process that received it."
  { y: 4718, holdMs: 5500 }, // "Controls outside the prompt." — the seven managed pillars
];
// Where a stop leaves the page, which is where the next transition has to start from.
const restsAt = (stop) => stop.driftTo ?? stop.y;
const MOVE_MS = 1000;
const TAIL_MS = 1500;

async function main() {
  rmSync(SCRATCH, { recursive: true, force: true });
  mkdirSync(SCRATCH, { recursive: true });
  mkdirSync(dirname(OUT), { recursive: true });

  const browser = await chromium.launch({ channel: "msedge" });
  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 1,
    colorScheme: "dark",
    recordVideo: { dir: SCRATCH, size: { width: WIDTH, height: HEIGHT } },
  });
  const page = await context.newPage();

  await page.goto(URL, { waitUntil: "networkidle" });

  // `styles.css` sets `scroll-behavior: smooth` on html, so every per-frame scrollTo below would
  // start a fresh smooth animation and interrupt the previous one — the pan crawls a few hundred
  // pixels instead of travelling. Override only that property, through the CSSOM: the site ships
  // a strict `style-src 'self'` policy that rejects an injected style tag, and that policy is a
  // deliberate part of the submission rather than something to work around. Playwright's
  // `reducedMotion` would also clear the smooth scroll and must not be used either — the site
  // serves a static SVG under reduced motion, which would switch off the route animation this
  // recording exists to capture in the first place.
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = "auto";
  });
  // Ease each move in and out rather than stepping it, so a transition reads as a camera move and
  // not as a mouse wheel. Driving it inside the page keeps it independent of the recorder's cadence.
  // A drift is the same glide held linearly instead: easing a move that spans a whole 6.5s hold
  // would accelerate and brake visibly, and a camera creeping across a diagram should not do either.
  const glide = (from, to, duration, eased) =>
    page.evaluate(
      ([from, to, duration, eased]) =>
        new Promise((resolve) => {
          const start = performance.now();
          const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2);
          const step = (now) => {
            const t = Math.min((now - start) / duration, 1);
            const p = eased ? ease(t) : t;
            window.scrollTo({ top: from + (to - from) * p, behavior: "instant" });
            if (t < 1) requestAnimationFrame(step);
            else resolve();
          };
          requestAnimationFrame(step);
        }),
      [from, to, duration, eased],
    );

  for (const [index, stop] of STOPS.entries()) {
    if (index > 0) {
      await glide(restsAt(STOPS[index - 1]), stop.y, MOVE_MS, true);
    }
    if (stop.driftTo === undefined) {
      await page.waitForTimeout(stop.holdMs);
    } else {
      await glide(stop.y, stop.driftTo, stop.holdMs, false);
    }
  }

  await page.waitForTimeout(TAIL_MS);
  await context.close();
  await browser.close();

  const recorded = readdirSync(SCRATCH).find((name) => name.endsWith(".webm"));
  if (!recorded) throw new Error("Playwright wrote no video");

  // Playwright emits VP8 webm at its own cadence; conform it to the cut's 30fps H.264 so the
  // assembler concatenates it without re-encoding surprises.
  const ffmpeg = spawnSync(
    "ffmpeg",
    // prettier-ignore
    [
      "-y", "-i", join(SCRATCH, recorded),
      "-vf", `scale=${WIDTH}:${HEIGHT},setsar=1,format=yuv420p`,
      "-r", String(FPS), "-an",
      "-c:v", "libx264", "-preset", "medium", "-crf", "18",
      OUT,
    ],
    { stdio: "inherit" },
  );
  if (ffmpeg.status !== 0) throw new Error("ffmpeg failed to conform the recording");

  rmSync(SCRATCH, { recursive: true, force: true });
  console.log(`Wrote ${OUT}`);
}

await main();
