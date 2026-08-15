import fs from "node:fs";
import path from "node:path";

const metadataDir = "/home/ubuntu/cookie-chain-edition-444-original-stickers/metadata";
const catalogOutput = "/home/ubuntu/sweetardio-cookie-chain-edition/catalog/edition_444_release/visual_preview_tokens_50.json";
const managedOutput = "/home/ubuntu/cookie-chain-edition-mint/client/src/data/previewTokens.ts";

// Chosen from the complete release contact-sheet review for visual contrast,
// distinctive silhouettes, varied backgrounds, and broad sticker representation.
const selection = [152, 2, 4, 8, 11, 15, 18, 21, 25, 26, 34, 39, 44, 45, 51, 53, 57, 59, 64, 68, 71, 72, 75, 77, 87, 88, 98, 100, 104, 105, 108, 109, 115, 120, 121, 127, 129, 136, 145, 148, 149, 155, 161, 162, 163, 170, 172, 174, 176, 179];

const assetUrls = {
  2: "/manus-storage/token-002_7c6be5c4.png", 4: "/manus-storage/token-004_4c37bca9.png",
  8: "/manus-storage/token-008_a533c0ef.png", 11: "/manus-storage/token-011_ee413dad.png",
  15: "/manus-storage/token-015_d1f84cd5.png", 18: "/manus-storage/token-018_5a03cac4.png",
  21: "/manus-storage/token-021_b7cda261.png", 25: "/manus-storage/token-025_dbe308ae.png",
  26: "/manus-storage/token-026_5e3e30fc.png", 34: "/manus-storage/token-034_d0d549f4.png",
  39: "/manus-storage/token-039_0be72d34.png", 44: "/manus-storage/token-044_0fc59a53.png",
  45: "/manus-storage/token-045_47bfd225.png", 51: "/manus-storage/token-051_f75be28b.png",
  53: "/manus-storage/token-053_9c81fe12.png", 57: "/manus-storage/token-057_6eaf355e.png",
  59: "/manus-storage/token-059_e7d8991a.png", 64: "/manus-storage/token-064_02cb1374.png",
  68: "/manus-storage/token-068_d6b60f53.png", 71: "/manus-storage/token-071_d4e2c5d7.png",
  72: "/manus-storage/token-072_fb5ed57d.png", 75: "/manus-storage/token-075_7e34270b.png",
  77: "/manus-storage/token-077_af6f90f3.png", 87: "/manus-storage/token-087_ef4dc6d2.png",
  88: "/manus-storage/token-088_03fc9198.png", 98: "/manus-storage/token-098_f52e4199.png",
  100: "/manus-storage/token-100_69457e4b.png", 104: "/manus-storage/token-104_af1d00a2.png",
  105: "/manus-storage/token-105_617e1b13.png", 108: "/manus-storage/token-108_086de2fb.png",
  109: "/manus-storage/token-109_8995400e.png", 115: "/manus-storage/token-115_1380934b.png",
  120: "/manus-storage/token-120_6e948802.png", 121: "/manus-storage/token-121_48a9c2f0.png",
  127: "/manus-storage/token-127_9a900ed6.png", 129: "/manus-storage/token-129_b15b5256.png",
  136: "/manus-storage/token-136_1a9a8017.png", 145: "/manus-storage/token-145_477cb59f.png",
  148: "/manus-storage/token-148_a88ba07b.png", 149: "/manus-storage/token-149_c8062ccf.png",
  152: "/manus-storage/token-152_8d5b076d.png", 155: "/manus-storage/token-155_d3e047d8.png",
  161: "/manus-storage/token-161_a1c8b047.png", 162: "/manus-storage/token-162_ad224f96.png",
  163: "/manus-storage/token-163_d3551851.png", 170: "/manus-storage/token-170_c9a6d1a3.png",
  172: "/manus-storage/token-172_61e0d57d.png", 174: "/manus-storage/token-174_8e4e24fc.png",
  176: "/manus-storage/token-176_e029363c.png", 179: "/manus-storage/token-179_60f5a714.png",
};

const attr = (metadata, traitType) => metadata.attributes.find((attribute) => attribute.trait_type === traitType)?.value ?? "";
const tokens = selection.map((id) => {
  const metadata = JSON.parse(fs.readFileSync(path.join(metadataDir, `${String(id).padStart(3, "0")}.json`), "utf8"));
  const background = attr(metadata, "Background");
  return {
    id: String(id).padStart(3, "0"),
    name: attr(metadata, "Character"),
    image: assetUrls[id],
    rarity: attr(metadata, "Rarity"),
    sticker: `${attr(metadata, "Sticker")} sticker`,
    note: background === "Nightly Legendary" ? "Nightly Legendary" : "Curated draw",
    background,
  };
});

if (tokens.length !== 50 || tokens[0].id !== "152" || tokens.some((token) => !token.image)) {
  throw new Error("Expected 50 complete token records with Nightly Legendary #152 first");
}

fs.writeFileSync(catalogOutput, JSON.stringify({ count: tokens.length, selection: tokens }, null, 2) + "\n");
fs.mkdirSync(path.dirname(managedOutput), { recursive: true });
const managedTokens = tokens.map(({ background, ...token }) => token);
fs.writeFileSync(
  managedOutput,
  `// Generated from the visually curated, validated Cookie Chain Edition release; do not hand-edit.\nexport type PreviewToken = { id: string; name: string; image: string; rarity: string; sticker: string; note: string };\n\nexport const previewTokens: PreviewToken[] = ${JSON.stringify(managedTokens, null, 2)};\n`,
);
console.log(`wrote ${tokens.length} visually curated previews; Nightly Legendary #${tokens[0].id} remains first`);
