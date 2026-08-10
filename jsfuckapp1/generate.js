#!/usr/bin/env node
/**
 * Encode readable sources → pure JSFuck (only []()!+).
 *
 *   node generate.js
 *   node generate.js --check
 *
 * Writes:
 *   sokoban.jsfuck.js         (Node CLI game)
 *   sokoban.browser.jsfuck.js (browser game)
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { JSFuck } = require("./jsfuck_lib.js");

const DIR = __dirname;

function pureOnly(s) {
  return /^[\[\]()!+]+$/.test(s);
}

function encodeFile(srcName, outName, runInParentScope) {
  const src = fs.readFileSync(path.join(DIR, srcName), "utf8");
  // strip line comments for smaller / safer encode
  const cleaned = src
    .split("\n")
    .filter((ln) => !/^\s*\/\//.test(ln))
    .join("\n");
  const pure = JSFuck.encode(cleaned, true, runInParentScope);
  if (!pureOnly(pure)) {
    console.error("FAIL non-pure:", outName);
    process.exit(1);
  }
  fs.writeFileSync(path.join(DIR, outName), pure + "\n", "utf8");
  console.log("wrote", outName, pure.length, "chars");
  return pure;
}

function main() {
  const t0 = Date.now();
  // Node: need parent scope so `process` / `console` exist (eval)
  encodeFile("game_src.js", "sokoban.jsfuck.js", true);
  encodeFile("game_src_browser.js", "sokoban.browser.jsfuck.js", true);
  console.log("time_ms", Date.now() - t0);

  if (process.argv.includes("--check")) {
    // smoke without interactive hang: spawn child with input
    const { spawnSync } = require("child_process");
    const r = spawnSync(
      process.execPath,
      [path.join(DIR, "sokoban.jsfuck.js")],
      {
        input: "d\nq\n",
        encoding: "utf8",
        timeout: 15000,
        cwd: DIR,
      }
    );
    const out = (r.stdout || "") + (r.stderr || "");
    if (r.error) {
      console.error("FAIL spawn", r.error);
      process.exit(1);
    }
    if (!out.includes("#######")) {
      console.error("FAIL board missing:\n", out.slice(0, 400));
      process.exit(1);
    }
    if (!out.includes("moves=1")) {
      console.error("FAIL push:\n", out.slice(-500));
      process.exit(1);
    }
    console.log("check: interactive push ok");
  }
}

main();
