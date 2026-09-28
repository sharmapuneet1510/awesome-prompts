/**
 * SVG Builder — Generate self-contained SVG from layout
 */

import { NodeLayout, EdgePath, LayoutResult, Point } from './layout-engine';

export interface SemanticColorScheme {
  frontend: string;
  backend: string;
  database: string;
  security: string;
  cloud: string;
  messaging: string;
  external: string;
}

export const lightTheme: SemanticColorScheme = {
  frontend: '#0066cc',
  backend: '#00aa44',
  database: '#ff8800',
  security: '#dd0000',
  cloud: '#6600cc',
  messaging: '#00aaaa',
  external: '#666666',
};

export const darkTheme: SemanticColorScheme = {
  frontend: '#3399ff',
  backend: '#00dd66',
  database: '#ffaa33',
  security: '#ff3333',
  cloud: '#9933ff',
  messaging: '#33dddd',
  external: '#999999',
};

export interface SVGNode {
  id: string;
  label: string;
  color: string;
  layout: NodeLayout;
}

export interface SVGEdge {
  id: string;
  label?: string;
  path: EdgePath;
}

export class SVGBuilder {
  private theme: SemanticColorScheme = lightTheme;
  private width = 1000;
  private height = 800;

  setTheme(theme: SemanticColorScheme) {
    this.theme = theme;
  }

  build(nodes: SVGNode[], edges: SVGEdge[]): string {
    const defs = this.buildDefs();
    const edgeElements = edges.map(e => this.buildEdge(e)).join('\n');
    const nodeElements = nodes.map(n => this.buildNode(n)).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${this.width} ${this.height}" width="${this.width}" height="${this.height}">
  <defs>
    ${defs}
  </defs>
  <rect width="${this.width}" height="${this.height}" fill="#ffffff"/>
  <g class="edges">
    ${edgeElements}
  </g>
  <g class="nodes">
    ${nodeElements}
  </g>
</svg>`;
  }

  private buildDefs(): string {
    return `
    <style>
      .node-box { stroke-width: 2; }
      .node-label { font-family: 'Monaco', 'Courier New', monospace; font-size: 12px; }
      .edge-line { stroke-width: 2; fill: none; }
      .edge-label { font-family: 'Monaco', monospace; font-size: 10px; fill: #333; }
      .node-box:hover { stroke-width: 3; }
      @media (prefers-color-scheme: dark) {
        rect[class="background"] { fill: #1a1a1a; }
        .node-label { fill: #ffffff; }
        .edge-label { fill: #cccccc; }
      }
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#333"/>
    </marker>
    `;
  }

  private buildNode(node: SVGNode): string {
    const x = node.layout.position.x;
    const y = node.layout.position.y;
    const w = node.layout.width;
    const h = node.layout.height;
    const color = this.theme[node.color as keyof SemanticColorScheme] || '#999999';

    return `
    <g class="node" id="node-${node.id}" data-node-id="${node.id}">
      <rect class="node-box" x="${x}" y="${y}" width="${w}" height="${h}"
            fill="${color}" stroke="${color}" rx="4" opacity="0.1"/>
      <rect class="node-box" x="${x}" y="${y}" width="${w}" height="${h}"
            fill="none" stroke="${color}" rx="4"/>
      <text class="node-label" x="${x + 8}" y="${y + h / 2 + 4}" fill="${color}">
        ${this.escape(node.label)}
      </text>
    </g>`;
  }

  private buildEdge(edge: SVGEdge): string {
    const points = edge.path.points;
    const pathData = this.buildPath(points);
    const midPoint = this.getMidpoint(points);

    return `
    <g class="edge" id="edge-${edge.id}" data-edge-id="${edge.id}">
      <path class="edge-line" d="${pathData}" stroke="#999" marker-end="url(#arrowhead)"/>
      ${edge.label ? `
      <text class="edge-label" x="${midPoint.x + 4}" y="${midPoint.y - 4}">
        ${this.escape(edge.label)}
      </text>` : ''}
    </g>`;
  }

  private buildPath(points: Point[]): string {
    if (points.length < 2) return '';
    let path = `M ${points[0].x} ${points[0].y}`;
    for (let i = 1; i < points.length; i++) {
      path += ` L ${points[i].x} ${points[i].y}`;
    }
    return path;
  }

  private getMidpoint(points: Point[]): Point {
    if (points.length === 0) return { x: 0, y: 0 };
    const mid = Math.floor(points.length / 2);
    return points[mid];
  }

  private escape(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
}

// Generate self-contained HTML with embedded SVG
export function buildHTML(svg: string, title: string, isDark = false): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      background: ${isDark ? '#1a1a1a' : '#ffffff'};
      color: ${isDark ? '#ffffff' : '#333333'};
      padding: 20px;
    }
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    h1 {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 20px;
    }
    .viewer {
      border: 1px solid ${isDark ? '#444444' : '#cccccc'};
      border-radius: 8px;
      background: ${isDark ? '#222222' : '#fafafa'};
      overflow: auto;
      height: 600px;
    }
    svg {
      display: block;
      margin: 20px auto;
    }
    .controls {
      display: flex;
      gap: 12px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid ${isDark ? '#444444' : '#eeeeee'};
    }
    button {
      padding: 8px 16px;
      border: 1px solid ${isDark ? '#555555' : '#dddddd'};
      border-radius: 4px;
      background: ${isDark ? '#333333' : '#f5f5f5'};
      color: ${isDark ? '#ffffff' : '#333333'};
      cursor: pointer;
      font-size: 14px;
    }
    button:hover {
      background: ${isDark ? '#444444' : '#eeeeee'};
    }
    .legend {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 20px;
      padding: 16px;
      background: ${isDark ? '#222222' : '#f9f9f9'};
      border-radius: 8px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 2px;
      border: 1px solid currentColor;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>${title}</h1>
    <div class="viewer">
      ${svg}
    </div>
    <div class="controls">
      <button onclick="this.parentElement.parentElement.style.filter='invert(1)'">
        Toggle Theme
      </button>
      <button onclick="downloadSVG()">
        Download SVG
      </button>
      <button onclick="downloadPNG()">
        Download PNG
      </button>
    </div>
    <div class="legend">
      <div class="legend-item">
        <div class="legend-color" style="background: #0066cc;"></div>
        <span>Frontend</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #00aa44;"></div>
        <span>Backend</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #ff8800;"></div>
        <span>Database</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #dd0000;"></div>
        <span>Security</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #6600cc;"></div>
        <span>Cloud</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #00aaaa;"></div>
        <span>Messaging</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #666666;"></div>
        <span>External</span>
      </div>
    </div>
  </div>
  <script>
    function downloadSVG() {
      const svg = document.querySelector('svg');
      const data = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([data], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'diagram.svg';
      link.click();
    }
    function downloadPNG() {
      alert('PNG export requires canvas rendering (not implemented in this preview)');
    }
  </script>
</body>
</html>`;
}
