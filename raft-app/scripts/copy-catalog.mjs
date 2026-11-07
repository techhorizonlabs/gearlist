// Copies the two catalog files the actions read from the built site (site/dist) into
// raft-app/catalog, which wrangler serves to the Worker through the ASSETS binding.
// Wrangler runs this before `wrangler dev` and `wrangler deploy` (build.command in
// wrangler.jsonc). Build the site first: python3 build.py && python3 site/build_site.py

import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.resolve(APP, "..", "site", "dist");
const OUT = path.join(APP, "catalog");
const FILES = ["resources.json", ".well-known/agent-skills/index.json"];

await rm(OUT, { recursive: true, force: true });
for (const file of FILES) {
  let text;
  try {
    text = await readFile(path.join(DIST, file), "utf8");
    JSON.parse(text);
  } catch {
    console.error(`Missing or invalid site/dist/${file}. Run python3 build.py && python3 site/build_site.py first.`);
    process.exit(1);
  }
  await mkdir(path.dirname(path.join(OUT, file)), { recursive: true });
  await writeFile(path.join(OUT, file), text);
}
console.log(`Copied ${FILES.length} catalog files from site/dist to raft-app/catalog.`);
