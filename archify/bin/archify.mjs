#!/usr/bin/env node

/**
 * Archify CLI — Diagram validation and delivery
 * Commands: validate, preview, deliver
 */

import fs from 'fs';
import crypto from 'crypto';
import { readFileSync } from 'fs';

// Simple validator (without Zod for standalone)
class SimpleValidator {
  validate(data) {
    const errors = [];
    const warnings = [];

    // Check required fields
    if (!data.type) errors.push('Missing required field: type');
    if (!data.version) errors.push('Missing required field: version');
    if (!data.title) errors.push('Missing required field: title');

    const validTypes = ['architecture', 'workflow', 'sequence', 'dataflow', 'lifecycle'];
    if (data.type && !validTypes.includes(data.type)) {
      errors.push(`Invalid type: ${data.type}. Must be one of: ${validTypes.join(', ')}`);
    }

    // Check nodes — sequence diagrams use participants, lifecycle diagrams use stages
    const usesNodes = !['sequence', 'lifecycle'].includes(data.type);
    if (!usesNodes) {
      // checked in the type-specific section below
    } else if (!data.nodes || !Array.isArray(data.nodes)) {
      errors.push('Missing or invalid nodes array');
    } else if (data.nodes.length === 0) {
      errors.push('Nodes array must not be empty');
    } else {
      const nodeIds = new Set();
      for (const node of data.nodes) {
        if (!node.id) errors.push('Node missing id');
        if (!node.label) errors.push(`Node ${node.id} missing label`);
        if (!node.color) errors.push(`Node ${node.id} missing color`);
        nodeIds.add(node.id);
      }

      // Check edge references
      if (data.edges && Array.isArray(data.edges)) {
        for (const edge of data.edges) {
          if (!nodeIds.has(edge.from)) {
            errors.push(`Edge references unknown node: ${edge.from}`);
          }
          if (!nodeIds.has(edge.to)) {
            errors.push(`Edge references unknown node: ${edge.to}`);
          }
        }
      }
    }

    // Type-specific validation
    if (data.type === 'workflow') {
      const hasStart = data.nodes?.some(n => n.type === 'start');
      const hasEnd = data.nodes?.some(n => n.type === 'end');
      if (!hasStart) errors.push('Workflow must have a node with type: "start"');
      if (!hasEnd) errors.push('Workflow must have a node with type: "end"');
    }

    if (data.type === 'sequence') {
      if (!data.participants || data.participants.length < 2) {
        errors.push('Sequence diagram must have at least 2 participants');
      }
      if (data.messages) {
        for (let i = 1; i < data.messages.length; i++) {
          if (data.messages[i].order <= data.messages[i - 1].order) {
            errors.push(`Message order not monotonic: ${data.messages[i].order} <= ${data.messages[i - 1].order}`);
          }
        }
      }
    }

    if (data.type === 'lifecycle') {
      if (!Array.isArray(data.stages) || data.stages.length === 0) {
        errors.push('Lifecycle diagram must have at least 1 stage');
      } else {
        const stageIds = new Set(data.stages.map(s => s.id));
        for (const t of data.transitions || []) {
          if (!stageIds.has(t.from)) errors.push(`Transition references unknown stage: ${t.from}`);
          if (!stageIds.has(t.to)) errors.push(`Transition references unknown stage: ${t.to}`);
        }
      }
    }

    // Check for evidence on high-value nodes
    if (data.nodes) {
      const highValue = data.nodes.filter(n =>
        ['security', 'database', 'external', 'cloud'].includes(n.color)
      );
      for (const node of highValue) {
        if (!node.evidence) {
          warnings.push(`Node ${node.id} (${node.label}) lacks evidence tie`);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      nodeCount: data.nodes?.length || 0,
      edgeCount: data.edges?.length || 0,
    };
  }
}

// CLI Commands
async function readStdin() {
  let data = '';
  for await (const chunk of process.stdin) {
    data += chunk;
  }
  return data;
}

async function cmdValidate() {
  try {
    const input = await readStdin();
    const data = JSON.parse(input);
    const validator = new SimpleValidator();
    const result = validator.validate(data);

    if (result.valid) {
      console.log('✓ Validation passed');
      console.log(`  Nodes: ${result.nodeCount}`);
      console.log(`  Edges: ${result.edgeCount}`);
      if (result.warnings.length > 0) {
        console.log(`  Warnings: ${result.warnings.length}`);
        result.warnings.forEach(w => console.log(`    ⚠ ${w}`));
      }
      process.exit(0);
    } else {
      console.log('✗ Validation failed');
      result.errors.forEach(e => console.log(`  ✗ ${e}`));
      if (result.warnings.length > 0) {
        result.warnings.forEach(w => console.log(`  ⚠ ${w}`));
      }
      process.exit(1);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdDeliver() {
  try {
    const input = await readStdin();
    const data = JSON.parse(input);
    const validator = new SimpleValidator();
    const result = validator.validate(data);

    if (!result.valid) {
      console.log('✗ Cannot deliver: validation failed');
      result.errors.forEach(e => console.log(`  ✗ ${e}`));
      process.exit(1);
    }

    // Calculate checksum
    const digest = crypto.createHash('sha256');
    digest.update(input);
    const sha = digest.digest('hex');
    const size = Buffer.byteLength(input);

    console.log('✓ Delivered successfully');
    console.log(`  SHA-256: ${sha}`);
    console.log(`  Size: ${size} bytes`);
    console.log(`  Type: ${data.type}`);
    console.log(`  Title: ${data.title}`);

    // Output JSON result
    console.log(JSON.stringify({
      delivered: true,
      sha256: sha,
      size: size,
      type: data.type,
      title: data.title,
      version: data.version,
      nodeCount: result.nodeCount,
      edgeCount: result.edgeCount,
    }, null, 2));

    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

async function cmdPreview() {
  try {
    const input = await readStdin();
    const data = JSON.parse(input);
    const validator = new SimpleValidator();
    const result = validator.validate(data);

    if (!result.valid) {
      console.log('✗ Preview failed: validation errors');
      result.errors.forEach(e => console.log(`  ✗ ${e}`));
      process.exit(1);
    }

    // Generate simple SVG preview
    const svg = generateBasicSVG(data);
    const html = wrapHTML(svg, data.title);

    const previewPath = '/tmp/archify-preview.html';
    fs.writeFileSync(previewPath, html);

    console.log('✓ Preview generated');
    console.log(`  File: ${previewPath}`);
    console.log(`  Open in browser to view (or copy path to terminal)`);

    process.exit(0);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

// Simple SVG generator
function generateBasicSVG(data) {
  const nodeCount = data.nodes?.length || 0;
  const coloring = {
    frontend: '#0066cc',
    backend: '#00aa44',
    database: '#ff8800',
    security: '#dd0000',
    cloud: '#6600cc',
    messaging: '#00aaaa',
    external: '#666666',
  };

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="#ffffff"/>`;

  // Simple grid layout
  const cols = Math.ceil(Math.sqrt(nodeCount));
  const rows = Math.ceil(nodeCount / cols);
  const w = 800 / cols - 20;
  const h = 600 / rows - 20;

  (data.nodes || []).forEach((node, idx) => {
    const col = idx % cols;
    const row = Math.floor(idx / cols);
    const x = 10 + col * (w + 20);
    const y = 10 + row * (h + 20);
    const color = coloring[node.color] || '#999999';

    svg += `
    <g id="node-${node.id}">
      <rect x="${x}" y="${y}" width="${w}" height="${h}"
            fill="${color}" opacity="0.2" stroke="${color}" stroke-width="2" rx="4"/>
      <text x="${x + 8}" y="${y + h / 2 + 4}"
            font-family="monospace" font-size="12" fill="${color}">
        ${node.label}
      </text>
    </g>`;
  });

  svg += '</svg>';
  return svg;
}

function wrapHTML(svg, title) {
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    body { font-family: sans-serif; margin: 20px; }
    h1 { color: #333; }
    .viewer { border: 1px solid #ddd; border-radius: 8px; padding: 20px; }
    svg { width: 100%; height: auto; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <div class="viewer">
    ${svg}
  </div>
  <p style="color: #999; font-size: 12px;">Generated by Archify</p>
</body>
</html>`;
}

// Main
async function main() {
  const cmd = process.argv[2] || 'validate';

  if (cmd === 'validate') {
    await cmdValidate();
  } else if (cmd === 'deliver') {
    await cmdDeliver();
  } else if (cmd === 'preview') {
    await cmdPreview();
  } else {
    console.log(`Archify CLI

Usage:
  cat diagram.json | node archify.mjs validate
  cat diagram.json | node archify.mjs deliver
  cat diagram.json | node archify.mjs preview

Commands:
  validate  - Validate JSON against schema and rules
  deliver   - Validate and output SHA-256 checksum
  preview   - Generate HTML preview
`);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
