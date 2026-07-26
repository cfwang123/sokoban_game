/**
 * Minimal GBA header fixer (title, checksum). Enough for mGBA / VBA.
 */
const fs = require("fs");

const path = process.argv[2];
const title = (process.argv[3] || "SOKOBAN").substring(0, 12);
if (!path) {
  console.error("Usage: node gbafix.js file.bin [TITLE]");
  process.exit(1);
}

const buf = fs.readFileSync(path);
if (buf.length < 0xc0) {
  console.error("ROM too small");
  process.exit(1);
}

for (let i = 0; i < 12; i++)
  buf[0xa0 + i] = i < title.length ? title.charCodeAt(i) : 0;
buf[0xac] = "C".charCodeAt(0);
buf[0xad] = "S".charCodeAt(0);
buf[0xae] = "K".charCodeAt(0);
buf[0xaf] = "J".charCodeAt(0);
buf[0xb0] = "0".charCodeAt(0);
buf[0xb1] = "1".charCodeAt(0);
buf[0xb2] = 0x96;
buf[0xb3] = 0;
buf[0xb4] = 0;
for (let i = 0xb5; i <= 0xbc; i++) buf[i] = 0;
buf[0xbd] = 0;

let sum = 0;
for (let i = 0xa0; i <= 0xbc; i++) sum += buf[i];
buf[0xbe] = (-(sum + 0x19)) & 0xff;
buf[0xbf] = 0;

let out = buf;
const pad = (4 - (out.length % 4)) % 4;
if (pad) out = Buffer.concat([out, Buffer.alloc(pad)]);

fs.writeFileSync(path, out);
console.log("Fixed header:", path, "size", out.length);
