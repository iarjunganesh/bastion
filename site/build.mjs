import { cp, mkdir, readFile, rm } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(siteRoot, "..");
const outputRoot = resolve(siteRoot, "dist");
const manifestPath = resolve(siteRoot, "asset-manifest.json");

const sourceFiles = [
  "404.html",
  "app.js",
  "data/site-content.json",
  "favicon.svg",
  "index.html",
  "robots.txt",
  "sitemap.xml",
  "styles.css",
];

if (!outputRoot.startsWith(`${siteRoot}\\`) && !outputRoot.startsWith(`${siteRoot}/`)) {
  throw new Error("Refusing to build outside the static site directory.");
}

await rm(outputRoot, { recursive: true, force: true });
await mkdir(outputRoot, { recursive: true });

for (const source of sourceFiles) {
  const target = resolve(outputRoot, source);
  await mkdir(dirname(target), { recursive: true });
  await cp(resolve(siteRoot, source), target);
}

const manifest = JSON.parse(await readFile(manifestPath, "utf8"));
for (const asset of manifest.assets) {
  const source = resolve(siteRoot, asset.source);
  const target = resolve(outputRoot, asset.output);
  if (!source.startsWith(`${repositoryRoot}\\`) && !source.startsWith(`${repositoryRoot}/`)) {
    throw new Error(`Asset source escapes the repository: ${asset.source}`);
  }
  if (!target.startsWith(`${outputRoot}\\`) && !target.startsWith(`${outputRoot}/`)) {
    throw new Error(`Asset output escapes the static build: ${asset.output}`);
  }
  await mkdir(dirname(target), { recursive: true });
  await cp(source, target);
}

console.log(`Built static evidence console with ${manifest.assets.length} reviewed assets.`);
