#!/usr/bin/env node
"use strict";

// Optional executable QA helper. It reuses an installed Playwright/Chrome;
// it never downloads a browser or mutates gallery source.

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
let playwright;
try {
  playwright = require("playwright-core");
} catch (error) {
  const bundledModules = process.env.P18_NODE_MODULES;
  if (!bundledModules) throw error;
  playwright = require(path.join(bundledModules, "playwright-core"));
}
const { chromium } = playwright;

function argument(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] !== undefined ? process.argv[index + 1] : fallback;
}

async function main() {
  const sourceDir = __dirname;
  const galleryDir = path.resolve(sourceDir, "../gallery");
  const outputDir = path.resolve(argument("--output-dir", "/private/tmp/p18-visual-review"));
  const start = Number(argument("--start", "0"));
  const count = Number(argument("--count", "6"));
  const screenshots = process.argv.includes("--screenshots");
  const chromePath = process.env.P18_CHROME_EXECUTABLE || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  const allFiles = fs.readdirSync(galleryDir).filter((name) => name.endsWith(".html")).sort();
  const files = allFiles.slice(start, start + count);
  const viewports = [
    { id: "desktop", width: 1440, height: 1100 },
    { id: "tablet", width: 1024, height: 900 },
    { id: "mobile", width: 390, height: 844 },
  ];
  fs.mkdirSync(outputDir, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: chromePath, args: ["--disable-gpu"] });
  const page = await browser.newPage();
  const results = [];
  for (const file of files) {
    const errors = [];
    const external = [];
    page.removeAllListeners();
    page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
    page.on("pageerror", (error) => errors.push(String(error)));
    page.on("request", (request) => { if (!request.url().startsWith("file:")) external.push(request.url()); });
    await page.goto(pathToFileURL(path.join(galleryDir, file)).href, { waitUntil: "load" });
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      const metrics = await page.evaluate(() => {
        const svg = document.querySelector("svg");
        const svgRect = svg.getBoundingClientRect();
        const visibleSvgText = [...svg.querySelectorAll("text")].map((element) => element.textContent.trim()).filter(Boolean);
        const titleText = document.querySelector("h1")?.textContent.trim() || "";
        const field = svg.querySelector('[data-semantic-field="true"]');
        const legend = svg.querySelector('[data-type-legend="true"]');
        const fieldTop = Number(field?.getAttribute("y") || 0);
        const fieldBottom = fieldTop + Number(field?.getAttribute("height") || 0);
        const legendTop = Number(legend?.getAttribute("data-legend-top") || 0);
        const legendBottom = Number(legend?.getAttribute("data-legend-bottom") || 0);
        const occupancy = ((fieldBottom - fieldTop) + (legendBottom - legendTop)) / 900;

        const textRects = [...svg.querySelectorAll("text")].map((element) => ({
          element,
          rect: element.getBoundingClientRect(),
          value: element.textContent.trim(),
        })).filter((item) => item.value && item.rect.width > 0 && item.rect.height > 0);
        const clippedText = textRects.filter(({ rect }) => rect.left < svgRect.left - 1 || rect.right > svgRect.right + 1 || rect.top < svgRect.top - 1 || rect.bottom > svgRect.bottom + 1).map((item) => item.value);
        const textOverlaps = [];
        for (let leftIndex = 0; leftIndex < textRects.length; leftIndex += 1) {
          for (let rightIndex = leftIndex + 1; rightIndex < textRects.length; rightIndex += 1) {
            const left = textRects[leftIndex];
            const right = textRects[rightIndex];
            if (left.element.closest(".type-legend") && right.element.closest(".type-legend")) continue;
            const overlapX = Math.min(left.rect.right, right.rect.right) - Math.max(left.rect.left, right.rect.left);
            const overlapY = Math.min(left.rect.bottom, right.rect.bottom) - Math.max(left.rect.top, right.rect.top);
            if (overlapX > 2 && overlapY > 2) textOverlaps.push([left.value, right.value]);
          }
        }

        const nodeRects = new Map([...svg.querySelectorAll("[data-node-id]")].map((element) => [element.getAttribute("data-node-id"), element.getBoundingClientRect()]));
        const routeFailures = [];
        const endpointFailures = [];
        const outsideDistance = (point, rect) => Math.hypot(
          Math.max(rect.left - point.x, 0, point.x - rect.right),
          Math.max(rect.top - point.y, 0, point.y - rect.bottom),
        );
        const inside = (point, rect, padding = 4) => outsideDistance(point, rect) <= padding;
        for (const route of svg.querySelectorAll("[data-edge-id]")) {
          if (typeof route.getTotalLength !== "function") continue;
          const matrix = route.getScreenCTM();
          const length = route.getTotalLength();
          const screenPoint = (at) => {
            const point = route.getPointAtLength(at);
            return new DOMPoint(point.x, point.y).matrixTransform(matrix);
          };
          const source = route.getAttribute("data-source");
          const target = route.getAttribute("data-target");
          const sourceRect = nodeRects.get(source);
          const targetRect = nodeRects.get(target);
          // Marker refX and transformed boundary strokes add a stable browser
          // bbox offset at arrow targets. Keep the acceptance in canonical
          // artboard units so responsive scaling cannot change the result.
          const endpointTolerance = 18 * (svgRect.width / 1440);
          if (sourceRect && !inside(screenPoint(0), sourceRect, endpointTolerance)) endpointFailures.push(`${route.getAttribute("data-edge-id")}:source:${outsideDistance(screenPoint(0), sourceRect).toFixed(2)}px`);
          if (targetRect && !inside(screenPoint(length), targetRect, endpointTolerance)) endpointFailures.push(`${route.getAttribute("data-edge-id")}:target:${outsideDistance(screenPoint(length), targetRect).toFixed(2)}px`);
          for (let at = Math.min(10, length / 4); at < length - Math.min(10, length / 4); at += Math.max(4, length / 80)) {
            const point = screenPoint(at);
            for (const [nodeId, rect] of nodeRects) {
              if (nodeId === source || nodeId === target) continue;
              if (inside(point, rect, 1)) routeFailures.push(`${route.getAttribute("data-edge-id")}:${nodeId}`);
            }
          }
        }
        const visualFailures = [];
        if (document.querySelectorAll("h1").length !== 1) visualFailures.push("visible-title-count");
        if (visibleSvgText.includes(titleText)) visualFailures.push("duplicate-visible-title");
        if (visibleSvgText.some((value) => value.toUpperCase().includes("EVIDENCE RAIL"))) visualFailures.push("evidence-rail");
        if (occupancy < 0.75) visualFailures.push("artboard-occupancy");
        const titleSize = Number.parseFloat(getComputedStyle(document.querySelector("h1")).fontSize);
        if (titleSize < 40 || titleSize > 48) visualFailures.push("display-title-size");
        if (clippedText.length) visualFailures.push("text-clipping");
        if (textOverlaps.length) visualFailures.push("text-overlap");
        if (routeFailures.length) visualFailures.push("connector-through-node");
        if (endpointFailures.length) visualFailures.push("wrong-endpoint");
        return {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          svgCount: document.querySelectorAll("svg").length,
          tableCount: document.querySelectorAll("table").length,
          title: document.title,
          localLinksValid: [...document.querySelectorAll("a")].every((element) => Boolean(element.getAttribute("href"))),
          visual: { occupancy, titleSize, clippedText, textOverlaps, routeFailures: [...new Set(routeFailures)], endpointFailures: [...new Set(endpointFailures)], failures: visualFailures },
        };
      });
      const status = metrics.scrollWidth <= metrics.clientWidth && metrics.svgCount === 1 && metrics.tableCount >= 1 && metrics.localLinksValid && metrics.visual.failures.length === 0 && errors.length === 0 && external.length === 0 ? "PASS" : "FAIL";
      results.push({ file, viewport: viewport.id, width: viewport.width, height: viewport.height, metrics, consoleErrors: [...errors], externalRequests: [...external], status });
      if (screenshots && viewport.id === "desktop") {
        await page.locator(".artifact-frame").screenshot({ path: path.join(outputDir, file.replace(".html", ".png")) });
      }
    }
  }
  await browser.close();
  const report = {
    schema_version: "1.0",
    browser: "Google Chrome",
    engine: "chromium",
    start,
    requested_count: count,
    file_count: files.length,
    viewport_count: viewports.length,
    run_count: results.length,
    pass_count: results.filter((item) => item.status === "PASS").length,
    fail_count: results.filter((item) => item.status === "FAIL").length,
    screenshot_count: screenshots ? files.length : 0,
    results,
  };
  const reportPath = path.join(outputDir, `browser-batch-${String(start).padStart(2, "0")}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  process.stdout.write(JSON.stringify({ reportPath, fileCount: report.file_count, runCount: report.run_count, passCount: report.pass_count, failCount: report.fail_count, screenshotCount: report.screenshot_count }) + "\n");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
