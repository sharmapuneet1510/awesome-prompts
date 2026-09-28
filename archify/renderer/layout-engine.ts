/**
 * Layout Engine — Automatic node placement and edge routing
 * Supports hierarchical, force-directed, and circular layouts
 */

export interface Point {
  x: number;
  y: number;
}

export interface NodeLayout {
  id: string;
  position: Point;
  width: number;
  height: number;
}

export interface EdgePath {
  id: string;
  points: Point[];
  controlPoints?: Point[];
}

export interface LayoutResult {
  nodes: Map<string, NodeLayout>;
  edges: EdgePath[];
  bounds: { minX: number; minY: number; maxX: number; maxY: number };
}

interface GraphNode {
  id: string;
  width: number;
  height: number;
  layer?: number;
}

interface GraphEdge {
  id: string;
  from: string;
  to: string;
}

// Hierarchical layout (top-down, suitable for architecture/workflow)
export class HierarchicalLayout {
  private padding = 60;
  private nodeSpacingX = 120;
  private nodeSpacingY = 100;

  layout(nodes: GraphNode[], edges: GraphEdge[]): LayoutResult {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const adjList = this.buildAdjacencyList(nodes, edges);

    // Assign layers using topological sort
    const layers = this.assignLayers(nodeMap, adjList);

    // Position nodes by layer
    const nodePositions = new Map<string, NodeLayout>();
    const layerNodes = new Map<number, string[]>();

    for (const [nodeId, layer] of layers) {
      if (!layerNodes.has(layer)) layerNodes.set(layer, []);
      layerNodes.get(layer)!.push(nodeId);
    }

    for (const [layer, nodeIds] of layerNodes) {
      const nodesInLayer = nodeIds.map(id => nodeMap.get(id)!);
      const totalWidth = nodesInLayer.reduce((sum, n) => sum + n.width, 0) +
                        (nodeIds.length - 1) * this.nodeSpacingX;

      let x = this.padding + (800 - totalWidth) / 2;
      const y = this.padding + layer * this.nodeSpacingY;

      for (const nodeId of nodeIds) {
        const node = nodeMap.get(nodeId)!;
        nodePositions.set(nodeId, {
          id: nodeId,
          position: { x, y },
          width: node.width,
          height: node.height,
        });
        x += node.width + this.nodeSpacingX;
      }
    }

    // Route edges
    const edgePaths = this.routeEdges(nodePositions, edges);

    // Calculate bounds
    const bounds = this.calculateBounds(nodePositions);

    return {
      nodes: nodePositions,
      edges: edgePaths,
      bounds,
    };
  }

  private buildAdjacencyList(nodes: GraphNode[], edges: GraphEdge[]): Map<string, string[]> {
    const adj = new Map<string, string[]>();
    for (const node of nodes) adj.set(node.id, []);
    for (const edge of edges) {
      if (adj.has(edge.from)) adj.get(edge.from)!.push(edge.to);
    }
    return adj;
  }

  private assignLayers(nodeMap: Map<string, GraphNode>, adjList: Map<string, string[]>): Map<string, number> {
    const layers = new Map<string, number>();
    const visited = new Set<string>();

    const dfs = (nodeId: string, layer: number) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      layers.set(nodeId, layer);

      for (const child of adjList.get(nodeId) || []) {
        dfs(child, layer + 1);
      }
    };

    for (const nodeId of nodeMap.keys()) {
      if (!visited.has(nodeId)) dfs(nodeId, 0);
    }

    return layers;
  }

  private routeEdges(nodePositions: Map<string, NodeLayout>, edges: GraphEdge[]): EdgePath[] {
    return edges.map(edge => {
      const from = nodePositions.get(edge.from)!;
      const to = nodePositions.get(edge.to)!;

      const fromY = from.position.y + from.height / 2;
      const toY = to.position.y - to.height / 2;
      const midY = (fromY + toY) / 2;

      return {
        id: edge.id,
        points: [
          { x: from.position.x + from.width / 2, y: fromY },
          { x: from.position.x + from.width / 2, y: midY },
          { x: to.position.x + to.width / 2, y: midY },
          { x: to.position.x + to.width / 2, y: toY },
        ],
      };
    });
  }

  private calculateBounds(nodePositions: Map<string, NodeLayout>) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    for (const node of nodePositions.values()) {
      minX = Math.min(minX, node.position.x);
      minY = Math.min(minY, node.position.y);
      maxX = Math.max(maxX, node.position.x + node.width);
      maxY = Math.max(maxY, node.position.y + node.height);
    }

    return { minX, minY, maxX, maxY };
  }
}

// Circular layout (suitable for sequence, cyclic relationships)
export class CircularLayout {
  private padding = 60;
  private radius = 300;

  layout(nodes: GraphNode[], edges: GraphEdge[]): LayoutResult {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const nodeArray = Array.from(nodeMap.values());
    const nodeCount = nodeArray.length;

    const nodePositions = new Map<string, NodeLayout>();
    const angleStep = (2 * Math.PI) / nodeCount;

    for (let i = 0; i < nodeArray.length; i++) {
      const node = nodeArray[i];
      const angle = i * angleStep;
      const x = 400 + this.radius * Math.cos(angle) - node.width / 2;
      const y = 300 + this.radius * Math.sin(angle) - node.height / 2;

      nodePositions.set(node.id, {
        id: node.id,
        position: { x, y },
        width: node.width,
        height: node.height,
      });
    }

    const edgePaths = this.routeEdges(nodePositions, edges);
    const bounds = this.calculateBounds(nodePositions);

    return { nodes: nodePositions, edges: edgePaths, bounds };
  }

  private routeEdges(nodePositions: Map<string, NodeLayout>, edges: GraphEdge[]): EdgePath[] {
    return edges.map(edge => {
      const from = nodePositions.get(edge.from)!;
      const to = nodePositions.get(edge.to)!;

      const fromCenter = {
        x: from.position.x + from.width / 2,
        y: from.position.y + from.height / 2,
      };
      const toCenter = {
        x: to.position.x + to.width / 2,
        y: to.position.y + to.height / 2,
      };

      return {
        id: edge.id,
        points: [fromCenter, toCenter],
      };
    });
  }

  private calculateBounds(nodePositions: Map<string, NodeLayout>) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

    for (const node of nodePositions.values()) {
      minX = Math.min(minX, node.position.x);
      minY = Math.min(minY, node.position.y);
      maxX = Math.max(maxX, node.position.x + node.width);
      maxY = Math.max(maxY, node.position.y + node.height);
    }

    return { minX, minY, maxX, maxY };
  }
}

// Factory for choosing appropriate layout
export function getLayout(diagramType: string): HierarchicalLayout | CircularLayout {
  if (diagramType === 'sequence') {
    return new CircularLayout();
  }
  return new HierarchicalLayout();
}
