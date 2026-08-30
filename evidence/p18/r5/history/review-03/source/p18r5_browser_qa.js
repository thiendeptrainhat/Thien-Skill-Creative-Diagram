#!/usr/bin/env node
"use strict";

// Browser QA for the one authorized P-18R5 anchor. It uses an existing local
// Chrome/Playwright runtime and never downloads a browser or network resource.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { pathToFileURL } = require("url");

let playwright;
try {
  playwright = require("playwright-core");
} catch (error) {
  const bundledModules = process.env.P18R5_NODE_MODULES;
  if (!bundledModules) throw error;
  playwright = require(path.join(bundledModules, "playwright-core"));
}

const { chromium } = playwright;
const sourceDir = __dirname;
const r5Dir = path.resolve(sourceDir, "..");
const htmlPath = path.join(r5Dir, "anchor", "swimlane--neutral-light.html");
const reviewDir = path.join(r5Dir, "review");
const reportPath = path.join(reviewDir, "browser-verification.json");
const screenshotPath = path.join(reviewDir, "swimlane--neutral-light.png");
const chromePath = process.env.P18R5_CHROME_EXECUTABLE || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

function overlaps(left, right, tolerance = 1) {
  const overlapX = Math.min(left.right, right.right) - Math.max(left.left, right.left);
  const overlapY = Math.min(left.bottom, right.bottom) - Math.max(left.top, right.top);
  return overlapX > tolerance && overlapY > tolerance;
}

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
    { id: "canonical", width: 3700, height: 1900 },
    { id: "desktop", width: 1440, height: 1100 },
    { id: "mobile", width: 390, height: 844 },
  ];
  const results = [];

  for (const viewport of viewports) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    const metrics = await page.evaluate(() => {
      const svg = document.querySelector(".artifact-frame svg");
      const svgRect = svg.getBoundingClientRect();
      const scale = svgRect.width / Number(svg.viewBox.baseVal.width);
      const failures = [];
      const contains = (outer, inner, tolerance = 1) => (
        inner.left >= outer.left - tolerance
        && inner.right <= outer.right + tolerance
        && inner.top >= outer.top - tolerance
        && inner.bottom <= outer.bottom + tolerance
      );
      const pointDistanceToRect = (point, rect) => Math.hypot(
        Math.max(rect.left - point.x, 0, point.x - rect.right),
        Math.max(rect.top - point.y, 0, point.y - rect.bottom),
      );
      const overlapsRect = (left, right, tolerance = 1) => {
        const overlapX = Math.min(left.right, right.right) - Math.max(left.left, right.left);
        const overlapY = Math.min(left.bottom, right.bottom) - Math.max(left.top, right.top);
        return overlapX > tolerance && overlapY > tolerance;
      };

      const titleStyle = getComputedStyle(svg.querySelector(".node-title"));
      const materialStyle = getComputedStyle(svg.querySelector(".node-transition"));
      const tagStyle = getComputedStyle(svg.querySelector(".tag-text"));
      const humanFont = svg.dataset.resolvedHumanFont;
      const monoFont = svg.dataset.resolvedMonoFont;
      if (!titleStyle.fontFamily.includes(humanFont)) failures.push("resolved-human-font");
      if (!getComputedStyle(svg.querySelector(".edge-label")).fontFamily.includes(monoFont)) failures.push("resolved-mono-font");
      if (parseFloat(titleStyle.fontSize) < 20) failures.push("node-title-size");
      if (parseFloat(materialStyle.fontSize) < 16) failures.push("material-size");
      if (parseFloat(tagStyle.fontSize) < 14) failures.push("mono-size");

      const nodeRects = new Map();
      for (const group of svg.querySelectorAll("[data-node-id]")) {
        const boundary = group.querySelector(".node-boundary").getBoundingClientRect();
        nodeRects.set(group.dataset.nodeId, boundary);
        for (const text of group.querySelectorAll("[data-material-text='true']")) {
          const rect = text.getBoundingClientRect();
          if (!contains(boundary, rect, 1.5)) failures.push(`text-outside:${group.dataset.nodeId}:${text.textContent.trim()}`);
        }
      }

      const nodeEntries = [...nodeRects.entries()];
      for (let leftIndex = 0; leftIndex < nodeEntries.length; leftIndex += 1) {
        for (let rightIndex = leftIndex + 1; rightIndex < nodeEntries.length; rightIndex += 1) {
          if (overlapsRect(nodeEntries[leftIndex][1], nodeEntries[rightIndex][1], 1)) {
            failures.push(`node-overlap:${nodeEntries[leftIndex][0]}:${nodeEntries[rightIndex][0]}`);
          }
        }
      }

      const routeData = [];
      for (const route of svg.querySelectorAll("[data-edge-id]")) {
        const length = route.getTotalLength();
        const matrix = route.getScreenCTM();
        const screenPoint = (distance) => {
          const point = route.getPointAtLength(distance);
          return new DOMPoint(point.x, point.y).matrixTransform(matrix);
        };
        const sourceRect = nodeRects.get(route.dataset.source);
        const targetRect = nodeRects.get(route.dataset.target);
        if (pointDistanceToRect(screenPoint(0), sourceRect) > Math.max(2, 3 * scale)) failures.push(`endpoint-source:${route.dataset.edgeId}`);
        if (pointDistanceToRect(screenPoint(length), targetRect) > Math.max(2, 3 * scale)) failures.push(`endpoint-target:${route.dataset.edgeId}`);
        const samples = [];
        const margin = Math.min(16 * scale, length / 5);
        for (let distance = margin; distance < length - margin; distance += Math.max(3, length / 120)) {
          const point = screenPoint(distance);
          samples.push(point);
          for (const [nodeId, rect] of nodeRects) {
            if (nodeId === route.dataset.source || nodeId === route.dataset.target) continue;
            if (pointDistanceToRect(point, rect) <= 0.5) failures.push(`route-through-node:${route.dataset.edgeId}:${nodeId}`);
          }
        }
        routeData.push({ id: route.dataset.edgeId, samples });
      }

      for (const mask of svg.querySelectorAll("[data-edge-label-for]")) {
        const rect = mask.getBoundingClientRect();
        for (const route of routeData) {
          if (route.id === mask.dataset.edgeLabelFor) continue;
          const minimum = Math.min(...route.samples.map((point) => pointDistanceToRect(point, rect)));
          if (minimum < 8 * scale - 0.75) failures.push(`label-clearance:${mask.dataset.edgeLabelFor}:${route.id}:${minimum.toFixed(2)}`);
        }
      }

      const bridgeGroups = [...svg.querySelectorAll(".bridge-mark")];
      const bridgeGaps = [...svg.querySelectorAll("[data-bridge-role='gap']")];
      const bridgeUnderlays = [...svg.querySelectorAll("[data-bridge-role='underlay']")];
      const bridgeHops = [...svg.querySelectorAll("[data-bridge-role='hop']")];
      if (!bridgeGroups.length) failures.push("bridge-missing");
      if (
        bridgeGaps.length !== 0
        || bridgeUnderlays.length !== bridgeGroups.length
        || bridgeHops.length !== bridgeGroups.length
      ) failures.push("bridge-pass-count");
      if (svg.querySelectorAll(".port-dot").length) failures.push("junction-like-port-dot");
      const routes = [...svg.querySelectorAll("[data-edge-id]")];
      const integratedRoutes = routes.filter((route) => route.dataset.pathBridgesIntegrated === "true");
      if (integratedRoutes.length !== routes.length) failures.push("bridge-path-integration-marker");
      const bridgesByRouteSegment = new Map();
      for (const group of bridgeGroups) {
        if (group.dataset.bridgeOrientation !== "horizontal") failures.push("bridge-orientation");
        const key = `${group.dataset.bridgeEdge}:${group.dataset.bridgeSegment}`;
        if (!bridgesByRouteSegment.has(key)) bridgesByRouteSegment.set(key, []);
        bridgesByRouteSegment.get(key).push({
          x: Number(group.dataset.bridgeX),
          radius: Number(group.dataset.bridgeRadius),
        });
      }
      for (const hop of bridgeHops) {
        if (getComputedStyle(hop).fill !== "none") failures.push("bridge-hop-fill");
      }
      let bridgePitchMin = null;
      for (const [key, marks] of bridgesByRouteSegment) {
        marks.sort((left, right) => left.x - right.x);
        for (let index = 0; index < marks.length - 1; index += 1) {
          const actual = marks[index + 1].x - marks[index].x;
          const required = marks[index].radius + marks[index + 1].radius + 12;
          bridgePitchMin = bridgePitchMin === null ? actual : Math.min(bridgePitchMin, actual);
          if (actual + 0.001 < required) failures.push(`compound-hop:${key}:${actual.toFixed(2)}<${required.toFixed(2)}`);
        }
      }
      for (const route of routes) {
        const routeBridgeCount = bridgeGroups.filter((group) => group.dataset.bridgeEdge === route.dataset.edgeId).length;
        if (!routeBridgeCount) continue;
        const cubicCount = (route.getAttribute("d").match(/\bC\b/g) || []).length;
        if (cubicCount < routeBridgeCount * 2) failures.push(`hop-not-integrated:${route.dataset.edgeId}`);
      }

      const adaptiveTitleLines = {};
      for (const nodeId of ["card-cash", "card-ledger-post"]) {
        const group = svg.querySelector(`[data-node-id='${nodeId}']`);
        const lines = [...group.querySelectorAll(".node-title")].map((line) => line.textContent.trim());
        adaptiveTitleLines[nodeId] = lines;
        if (lines.length !== 1) failures.push(`avoidable-title-wrap:${nodeId}`);
      }

      const allText = [...svg.querySelectorAll("text")].filter((item) => item.textContent.trim());
      for (const text of allText) {
        if (!contains(svgRect, text.getBoundingClientRect(), 1)) failures.push(`svg-text-clipped:${text.textContent.trim()}`);
      }
      if (allText.some((item) => item.textContent.trim() === "Luồng chứng từ thu tiền")) failures.push("duplicate-visible-title");
      if (allText.some((item) => item.textContent.toUpperCase().includes("EVIDENCE RAIL"))) failures.push("evidence-rail");

      const semanticNodes = new Set();
      svg.querySelectorAll("[data-semantic-node-ids]").forEach((node) => node.dataset.semanticNodeIds.split(",").forEach((id) => semanticNodes.add(id)));
      const semanticEdges = new Set();
      svg.querySelectorAll("[data-semantic-edge-ids]").forEach((edge) => edge.dataset.semanticEdgeIds.split(",").forEach((id) => semanticEdges.add(id)));
      if (semanticNodes.size !== 12) failures.push("semantic-node-count");
      if (semanticEdges.size !== 10) failures.push("semantic-edge-count");

      return {
        failures: [...new Set(failures)],
        documentOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        svgWidth: svgRect.width,
        svgHeight: svgRect.height,
        scale,
        humanFont,
        monoFont,
        titleSize: parseFloat(titleStyle.fontSize),
        materialSize: parseFloat(materialStyle.fontSize),
        monoSize: parseFloat(tagStyle.fontSize),
        nodeCount: nodeRects.size,
        edgeCount: routeData.length,
        labelCount: svg.querySelectorAll("[data-edge-label-for]").length,
        bridgeCount: bridgeGroups.length,
        bridgeGapCount: bridgeGaps.length,
        bridgeUnderlayCount: bridgeUnderlays.length,
        bridgeHopCount: bridgeHops.length,
        integratedRouteCount: integratedRoutes.length,
        bridgePitchMin,
        portDotCount: svg.querySelectorAll(".port-dot").length,
        adaptiveTitleLines,
        externalResourceElements: svg.querySelectorAll("image, foreignObject, script").length,
      };
    });
    if (metrics.documentOverflow) metrics.failures.push("document-overflow");
    if (metrics.externalResourceElements) metrics.failures.push("external-resource-element");
    const status = metrics.failures.length === 0 && consoleErrors.length === 0 && externalRequests.length === 0 ? "PASS" : "FAIL";
    results.push({ viewport: viewport.id, width: viewport.width, height: viewport.height, status, metrics });
    if (viewport.id === "canonical") {
      await page.locator(".artifact-frame").screenshot({ path: screenshotPath });
    }
  }

  await browser.close();
  const failCount = results.filter((result) => result.status === "FAIL").length;
  const report = {
    schema_version: "1.0",
    phase: "P-18R5",
    anchor_id: "P18R5-SWIMLANE-NEUTRAL-LIGHT",
    browser: "Google Chrome",
    engine: "Chromium via existing Playwright runtime",
    status: failCount === 0 && consoleErrors.length === 0 && externalRequests.length === 0 ? "PASS" : "FAIL",
    run_count: results.length,
    pass_count: results.length - failCount,
    fail_count: failCount,
    console_errors: consoleErrors,
    external_requests: externalRequests,
    screenshot: path.relative(r5Dir, screenshotPath),
    artifact_sha256: crypto.createHash("sha256").update(fs.readFileSync(htmlPath)).digest("hex"),
    results,
  };
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  process.stdout.write(JSON.stringify({ status: report.status, runs: report.run_count, failures: report.fail_count, report: reportPath, screenshot: screenshotPath }) + "\n");
  if (report.status !== "PASS") process.exitCode = 1;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
