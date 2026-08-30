#!/usr/bin/env node
"use strict";

// Browser QA for the exact fourteen P-18R6 anchors.  The script uses an
// existing local Chrome/Playwright runtime and never downloads a browser or a
// network resource.  It is retained even when the controlling environment
// cannot navigate file://, so an independent reviewer can reproduce the run.

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

let playwright;
try {
  playwright = require("playwright-core");
} catch (error) {
  const bundledModules = process.env.P18R6_NODE_MODULES;
  if (!bundledModules) throw error;
  playwright = require(path.join(bundledModules, "playwright-core"));
}

const { chromium } = playwright;
const r6Dir = path.resolve(__dirname, "..");
const inventory = JSON.parse(fs.readFileSync(path.join(r6Dir, "P-18R6-INVENTORY.json"), "utf8"));
const reviewDir = path.join(r6Dir, "review");
const reportPath = path.join(reviewDir, "browser-verification.json");
const chromePath = process.env.P18R6_CHROME_EXECUTABLE || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

async function main() {
  fs.mkdirSync(reviewDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: chromePath, args: ["--disable-gpu"] });
  const page = await browser.newPage();
  const consoleErrors = [];
  const externalRequests = [];
  page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => consoleErrors.push(String(error)));
  page.on("request", (request) => { if (!request.url().startsWith("file:")) externalRequests.push(request.url()); });

  const viewports = [
    { id: "canonical", width: 2200, height: 1600 },
    { id: "desktop", width: 1440, height: 1100 },
    { id: "mobile", width: 390, height: 844 },
  ];
  const results = [];

  for (const item of inventory.engines) {
    const htmlPath = path.join(r6Dir, item.html);
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
      await page.evaluate(() => document.fonts.ready);
      const metrics = await page.evaluate(() => {
        const failures = [];
        const svg = document.querySelector(".artifact-frame svg");
        if (!svg) return { failures: ["missing-svg"] };
        const svgRect = svg.getBoundingClientRect();
        const contains = (outer, inner, tolerance = 1.5) => (
          inner.left >= outer.left - tolerance && inner.right <= outer.right + tolerance
          && inner.top >= outer.top - tolerance && inner.bottom <= outer.bottom + tolerance
        );
        const textItems = [...svg.querySelectorAll("text")].filter((node) => node.textContent.trim());
        for (const text of textItems) {
          if (!contains(svgRect, text.getBoundingClientRect(), 1)) failures.push(`svg-text-clipped:${text.textContent.trim()}`);
        }
        for (const card of svg.querySelectorAll(".node-card")) {
          const boundary = card.querySelector(".node-boundary");
          if (!boundary) continue;
          const boundaryRect = boundary.getBoundingClientRect();
          for (const text of card.querySelectorAll("text")) {
            if (!contains(boundaryRect, text.getBoundingClientRect())) failures.push(`node-text-outside:${text.textContent.trim()}`);
          }
        }
        const title = svg.querySelector("title");
        const desc = svg.querySelector("desc");
        if (!title || !desc || !title.textContent.trim() || !desc.textContent.trim()) failures.push("missing-title-desc");
        if (svg.getAttribute("role") !== "img") failures.push("missing-img-role");
        if (svg.querySelectorAll("script,foreignObject,image").length) failures.push("external-or-executable-element");
        const titleSample = svg.querySelector(".node-title");
        if (titleSample && parseFloat(getComputedStyle(titleSample).fontSize) < 20) failures.push("node-title-size");
        const materialSample = svg.querySelector(".material,.node-transition,.legend-text");
        if (materialSample && parseFloat(getComputedStyle(materialSample).fontSize) < 16) failures.push("material-size");
        const monoSample = svg.querySelector(".mono,.tag-text,.edge-label");
        if (monoSample && parseFloat(getComputedStyle(monoSample).fontSize) < 14) failures.push("mono-size");
        return {
          failures: [...new Set(failures)],
          documentOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
          svgWidth: svgRect.width,
          svgHeight: svgRect.height,
          textCount: textItems.length,
          engine: svg.dataset.layoutEngine,
          resolvedHumanFont: svg.dataset.resolvedHumanFont || null,
          resolvedMonoFont: svg.dataset.resolvedMonoFont || null,
        };
      });
      if (metrics.documentOverflow) metrics.failures.push("document-overflow");
      const status = metrics.failures.length === 0 ? "PASS" : "FAIL";
      results.push({ engine: item.engine, viewport: viewport.id, width: viewport.width, height: viewport.height, status, metrics });
      if (viewport.id === "canonical") {
        await page.locator(".artifact-frame").screenshot({ path: path.join(reviewDir, `browser-${item.engine}.png`) });
      }
    }
  }

  await browser.close();
  const failed = results.filter((item) => item.status !== "PASS");
  const report = {
    schema_version: "1.0",
    candidate_id: inventory.candidate_id,
    status: failed.length === 0 && consoleErrors.length === 0 && externalRequests.length === 0 ? "PASS" : "FAIL",
    case_count: results.length,
    pass_count: results.length - failed.length,
    fail_count: failed.length,
    console_errors: consoleErrors,
    external_requests: [...new Set(externalRequests)],
    results,
  };
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  process.stdout.write(`${JSON.stringify({ status: report.status, case_count: report.case_count, fail_count: report.fail_count })}\n`);
  if (report.status !== "PASS") process.exitCode = 1;
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
