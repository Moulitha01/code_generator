// Takes screenshots of the frontend at phone / tablet / laptop widths.
// Run with: node responsive-screenshot.js
const { chromium } = require("playwright");
const fs = require("fs");

const URL = process.env.SCREENSHOT_URL || "http://localhost:5000";

const VIEWPORTS = [
  { name: "phone", width: 375, height: 812 },   // iPhone-ish
  { name: "tablet", width: 768, height: 1024 }, // iPad-ish
  { name: "laptop", width: 1440, height: 900 }, // common laptop
];

(async () => {
  fs.mkdirSync("screenshots", { recursive: true });

  const browser = await chromium.launch();

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage({
      viewport: { width: vp.width, height: vp.height },
    });

    await page.goto(URL, { waitUntil: "networkidle" });

    // Flag pages that overflow horizontally — the #1 responsive-design bug.
    const hasHorizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    );

    if (hasHorizontalOverflow) {
      console.log(`WARNING: horizontal overflow detected at ${vp.name} (${vp.width}px)`);
    }

    const path = `screenshots/${vp.name}-${vp.width}px.png`;
    await page.screenshot({ path, fullPage: true });
    console.log(`Saved ${path}`);

    await page.close();
  }

  await browser.close();
})();