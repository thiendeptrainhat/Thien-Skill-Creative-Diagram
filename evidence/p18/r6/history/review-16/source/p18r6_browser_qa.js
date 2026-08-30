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
        const bandEngines = new Set(["dependency-dag", "work-experience", "hierarchy"]);
        if (bandEngines.has(svg.dataset.layoutEngine)) {
          const contract = svg.querySelector('[data-band-layout-contract="D-073"]');
          if (!contract) {
            failures.push("band-contract-missing");
          } else {
            const boundaries = contract.dataset.bandBoundaries.split(/\s+/).filter(Boolean).map(Number);
            const expectedBandCount = Number(contract.dataset.bandCount);
            const tolerance = 0.75;
            const requiredClearance = Number(contract.dataset.minimumSeparatorClearance);
            const separators = [...contract.querySelectorAll("[data-band-separator-index]")];
            const members = [...svg.querySelectorAll("[data-band-member]")];
            if (boundaries.length !== expectedBandCount + 1 || separators.length !== boundaries.length || !members.length) {
              failures.push(`band-anatomy:${svg.dataset.layoutEngine}`);
            }
            separators.forEach((separator, index) => {
              const y1 = Number(separator.getAttribute("y1"));
              const y2 = Number(separator.getAttribute("y2"));
              if (Math.abs(y1 - boundaries[index]) > 0.01 || Math.abs(y2 - boundaries[index]) > 0.01) {
                failures.push(`band-separator-position:${svg.dataset.layoutEngine}:${index}`);
              }
            });
            for (const member of members) {
              const index = Number(member.dataset.bandIndex);
              const box = member.getBBox();
              if (!Number.isInteger(index) || index < 0 || index >= boundaries.length - 1) {
                failures.push(`band-member-index:${svg.dataset.layoutEngine}`);
                continue;
              }
              const top = boundaries[index];
              const bottom = boundaries[index + 1];
              const expectedCenter = (top + bottom) / 2;
              const actualCenter = box.y + box.height / 2;
              const declaredCenter = Number(member.dataset.bandCenterY);
              if (Math.abs(actualCenter - expectedCenter) > tolerance || Math.abs(declaredCenter - expectedCenter) > 0.01) {
                failures.push(`band-member-center:${svg.dataset.layoutEngine}:${member.dataset.bandMember}`);
              }
              const clearance = Math.min(box.y - top, bottom - (box.y + box.height));
              if (clearance < requiredClearance - tolerance) {
                failures.push(`band-separator-clearance:${svg.dataset.layoutEngine}:${member.dataset.bandMember}:${clearance.toFixed(2)}`);
              }
              if (boundaries.some((separatorY) => separatorY >= box.y - tolerance && separatorY <= box.y + box.height + tolerance)) {
                failures.push(`band-separator-member-intersection:${svg.dataset.layoutEngine}:${member.dataset.bandMember}`);
              }
            }
          }
        }
        if (svg.dataset.layoutEngine === "quantitative") {
          const axes = [...svg.querySelectorAll('[data-origin-arrowhead="none"][data-remediation="D-074"]')];
          if (axes.length !== 2) failures.push(`quantitative-axis-contract-count:${axes.length}`);
          for (const axis of axes) {
            const style = getComputedStyle(axis);
            if (axis.hasAttribute("marker-start") || axis.hasAttribute("marker-mid") || axis.hasAttribute("marker-end")) {
              failures.push(`quantitative-axis-marker-attribute:${axis.dataset.axisId}`);
            }
            if (style.markerStart !== "none" || style.markerMid !== "none" || style.markerEnd !== "none") {
              failures.push(`quantitative-axis-marker-computed:${axis.dataset.axisId}`);
            }
          }
        }
        if (svg.dataset.layoutEngine === "compartment-model") {
          const cardinalities = [...svg.querySelectorAll("[data-relationship-cardinality]")];
          const knockouts = [...svg.querySelectorAll("[data-cardinality-knockout]")];
          if (cardinalities.length !== 6 || knockouts.length !== 6) failures.push("inline-cardinality-count");
          for (const label of cardinalities) {
            const binding = label.dataset.relationshipCardinality;
            const relationshipId = label.dataset.relationshipId;
            const knockout = knockouts.find((item) => item.dataset.cardinalityKnockout === binding);
            const line = svg.querySelector(`[data-schema-relationship="${relationshipId}"]`);
            if (!knockout || !line) {
              failures.push(`inline-cardinality-binding:${binding}`);
              continue;
            }
            const labelBox = label.getBBox();
            const knockoutBox = knockout.getBBox();
            const axis = line.dataset.axis;
            const lineAxis = axis === "horizontal" ? Number(line.getAttribute("y1")) : Number(line.getAttribute("x1"));
            const labelAxis = axis === "horizontal"
              ? labelBox.y + labelBox.height / 2
              : labelBox.x + labelBox.width / 2;
            if (Math.abs(labelAxis - lineAxis) > 0.75) failures.push(`inline-cardinality-axis:${binding}`);
            const containsLabel = (
              labelBox.x >= knockoutBox.x - 0.25
              && labelBox.y >= knockoutBox.y - 0.25
              && labelBox.x + labelBox.width <= knockoutBox.x + knockoutBox.width + 0.25
              && labelBox.y + labelBox.height <= knockoutBox.y + knockoutBox.height + 0.25
            );
            if (!containsLabel) failures.push(`inline-cardinality-knockout-containment:${binding}`);
            const knockoutStyle = getComputedStyle(knockout);
            if (knockoutStyle.fill !== "rgb(247, 246, 242)" || knockoutStyle.stroke !== "none") {
              failures.push(`inline-cardinality-knockout-paint:${binding}`);
            }
            const siblings = [...label.parentElement.children];
            if (!(siblings.indexOf(line) < siblings.indexOf(knockout) && siblings.indexOf(knockout) < siblings.indexOf(label))) {
              failures.push(`inline-cardinality-paint-order:${binding}`);
            }
          }
        }
        if (svg.dataset.layoutEngine === "special-geometry") {
          const contract = svg.querySelector('[data-sankey-contract="D-072"]');
          const nodes = [...svg.querySelectorAll("[data-sankey-node]")];
          const ribbons = [...svg.querySelectorAll("[data-sankey-ribbon]")];
          if (!contract || nodes.length !== 7 || ribbons.length !== 9) failures.push("sankey-contract-count");
          const scale = 0.025;
          const tilesInterface = (node, side) => {
            const nodeBox = node.querySelector("[data-sankey-node-bar]").getBBox();
            const relevant = ribbons.filter((ribbon) => (
              side === "right"
                ? ribbon.dataset.sourceNode === node.dataset.sankeyNode
                : ribbon.dataset.targetNode === node.dataset.sankeyNode
            ));
            const intervals = relevant.map((ribbon) => (
              side === "right"
                ? [Number(ribbon.dataset.sourceY0), Number(ribbon.dataset.sourceY1)]
                : [Number(ribbon.dataset.targetY0), Number(ribbon.dataset.targetY1)]
            )).sort((a, b) => a[0] - b[0]);
            if (!intervals.length) return false;
            if (Math.abs(intervals[0][0] - nodeBox.y) > 0.01) return false;
            if (Math.abs(intervals.at(-1)[1] - (nodeBox.y + nodeBox.height)) > 0.01) return false;
            return intervals.slice(1).every((interval, index) => Math.abs(intervals[index][1] - interval[0]) <= 0.01);
          };
          for (const node of nodes) {
            const nodeId = node.dataset.sankeyNode;
            const bar = node.querySelector(`[data-sankey-node-bar="${nodeId}"]`);
            const labels = [...node.querySelectorAll(`[data-node-label="${nodeId}"]`)];
            if (!bar || labels.length !== 2) {
              failures.push(`sankey-node-anatomy:${nodeId}`);
              continue;
            }
            const barBox = bar.getBBox();
            const expectedHeight = Number(node.dataset.value) * scale;
            if (Math.abs(barBox.height - expectedHeight) > 0.01) failures.push(`sankey-node-scale:${nodeId}`);
            if (bar.rx.baseVal.value !== 0 || node.dataset.nodeCornerStyle !== "square") failures.push(`sankey-square-bar:${nodeId}`);
            for (const label of labels) {
              const labelBox = label.getBBox();
              if (labelBox.y + labelBox.height > barBox.y - 12) failures.push(`sankey-label-not-above:${nodeId}`);
              if (Math.abs(labelBox.x + labelBox.width / 2 - (barBox.x + barBox.width / 2)) > 0.75) {
                failures.push(`sankey-label-not-centered:${nodeId}`);
              }
            }
            const column = node.dataset.column;
            if (column === "source" && !tilesInterface(node, "right")) failures.push(`sankey-right-occupancy:${nodeId}`);
            if (column === "stage" && (!tilesInterface(node, "left") || !tilesInterface(node, "right"))) {
              failures.push(`sankey-both-occupancy:${nodeId}`);
            }
            if (column === "outcome" && !tilesInterface(node, "left")) failures.push(`sankey-left-occupancy:${nodeId}`);
          }
          const topRowIds = ["budget", "unit", "passed"];
          const topRowY = topRowIds.map((nodeId) => {
            const bar = svg.querySelector(`[data-sankey-node="${nodeId}"] [data-sankey-node-bar="${nodeId}"]`);
            return bar ? bar.getBBox().y : Number.NaN;
          });
          const topRowSpread = Math.max(...topRowY) - Math.min(...topRowY);
          if (
            contract?.dataset.inheritedContract !== "D-071"
            || contract?.dataset.topRowAlignment !== "top"
            || topRowY.some((value) => !Number.isFinite(value) || Math.abs(value - 210) > 0.01)
            || topRowSpread > 0.01
          ) failures.push(`sankey-top-row-not-aligned:${topRowY.join(",")}`);
        }
        const geometryBox = (element) => ({
          x: Number(element.dataset.boxX),
          y: Number(element.dataset.boxY),
          width: Number(element.dataset.boxWidth),
          height: Number(element.dataset.boxHeight),
        });
        const geometryItems = [...svg.querySelectorAll("[data-box-x][data-box-y][data-box-width][data-box-height]")];
        const zones = [...svg.querySelectorAll("[data-zone-id]")];
        for (const zone of zones) {
          const parent = geometryBox(zone);
          const children = geometryItems.filter((item) => item.dataset.parentId === zone.dataset.zoneId);
          if (!children.length) {
            failures.push(`containment-no-child:${zone.dataset.zoneId}`);
            continue;
          }
          const minimumPadding = Number(zone.dataset.minimumChildPadding || 0);
          const left = Math.min(...children.map((item) => geometryBox(item).x));
          const top = Math.min(...children.map((item) => geometryBox(item).y));
          const right = Math.max(...children.map((item) => {
            const child = geometryBox(item);
            return child.x + child.width;
          }));
          const bottom = Math.max(...children.map((item) => {
            const child = geometryBox(item);
            return child.y + child.height;
          }));
          if (
            left < parent.x + minimumPadding - 0.01
            || top < parent.y + minimumPadding - 0.01
            || right > parent.x + parent.width - minimumPadding + 0.01
            || bottom > parent.y + parent.height - minimumPadding + 0.01
          ) failures.push(`containment-padding:${zone.dataset.zoneId}`);
          const parentCenterX = parent.x + parent.width / 2;
          const parentCenterY = parent.y + parent.height / 2;
          if (Math.abs((left + right) / 2 - parentCenterX) > 0.01 || Math.abs((top + bottom) / 2 - parentCenterY) > 0.01) {
            failures.push(`containment-group-centering:${zone.dataset.zoneId}`);
          }
          const centersX = children.map((item) => {
            const child = geometryBox(item);
            return child.x + child.width / 2;
          });
          const centersY = children.map((item) => {
            const child = geometryBox(item);
            return child.y + child.height / 2;
          });
          if (zone.dataset.childLayout === "row" && Math.max(...centersY) - Math.min(...centersY) > 0.01) {
            failures.push(`containment-row-center-y:${zone.dataset.zoneId}`);
          }
          if (zone.dataset.childLayout === "column" && Math.max(...centersX) - Math.min(...centersX) > 0.01) {
            failures.push(`containment-column-center-x:${zone.dataset.zoneId}`);
          }
          if (
            zone.dataset.childLayout === "single"
            && (Math.abs(centersX[0] - parentCenterX) > 0.01 || Math.abs(centersY[0] - parentCenterY) > 0.01)
          ) failures.push(`containment-single-center:${zone.dataset.zoneId}`);
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
