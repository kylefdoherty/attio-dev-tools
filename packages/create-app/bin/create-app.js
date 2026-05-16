#!/usr/bin/env node

import { cpSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import { resolve, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

const projectName = process.argv[2];

if (!projectName) {
  console.error("Usage: npx create-attio-app <project-name>");
  process.exit(1);
}

const targetDir = resolve(process.cwd(), projectName);

if (existsSync(targetDir)) {
  console.error(`Error: Directory "${projectName}" already exists.`);
  process.exit(1);
}

const templateDir = join(__dirname, "..", "template");

console.log(`\n  Creating Attio app in ./${projectName}...\n`);

// Copy template
cpSync(templateDir, targetDir, { recursive: true });

// Update package.json name
const pkgPath = join(targetDir, "package.json");
const pkg = JSON.parse(readFileSync(pkgPath, "utf-8"));
pkg.name = projectName;
writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");

// Rename gitignore (npm strips .gitignore from published packages)
const gitignoreSrc = join(targetDir, "_gitignore");
const gitignoreDest = join(targetDir, ".gitignore");
if (existsSync(gitignoreSrc)) {
  cpSync(gitignoreSrc, gitignoreDest);
  execSync(`rm "${gitignoreSrc}"`);
}

console.log("  Installing dependencies...\n");

try {
  execSync("npm install", { cwd: targetDir, stdio: "inherit" });
} catch {
  console.log("\n  Could not auto-install. Run `npm install` manually.\n");
}

console.log(`
  Done! Your Attio app is ready.

  Next steps:
    cd ${projectName}
    cp .env.example .env.local    # Add your Attio OAuth credentials
    npm run dev                   # Start the dev server

  Get your OAuth credentials at:
    https://app.attio.com/settings/developers

  Read more: ./README.md
`);
