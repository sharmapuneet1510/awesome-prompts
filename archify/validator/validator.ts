/**
 * Validation Pipeline — Schema validation + custom rules
 */

import { DiagramSchema, ValidationResultSchema, Diagram } from '../schema/schema.js';
import { ZodError } from 'zod';

export interface ValidationError {
  subject: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  info: ValidationError[];
  diagnostics: {
    nodeCount: number;
    edgeCount: number;
    missingEvidence: string[];
    unreachableNodes: string[];
    cycles: string[][];
  };
}

export class DiagramValidator {
  validate(data: unknown): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];
    const info: ValidationError[] = [];
    let diagram: Diagram | null = null;

    // Step 1: Schema validation
    try {
      diagram = DiagramSchema.parse(data);
    } catch (err) {
      if (err instanceof ZodError) {
        for (const issue of err.issues) {
          errors.push({
            subject: issue.path.join('.') || 'root',
            message: issue.message,
            severity: 'error',
          });
        }
      }
      return this.buildResult(false, errors, warnings, info, diagram || (data as Diagram));
    }

    // Step 2: Type-specific validation
    if (diagram.type === 'architecture') {
      this.validateArchitecture(diagram, errors, warnings, info);
    } else if (diagram.type === 'workflow') {
      this.validateWorkflow(diagram, errors, warnings, info);
    } else if (diagram.type === 'sequence') {
      this.validateSequence(diagram, errors, warnings, info);
    } else if (diagram.type === 'dataflow') {
      this.validateDataFlow(diagram, errors, warnings, info);
    } else if (diagram.type === 'lifecycle') {
      this.validateLifecycle(diagram, errors, warnings, info);
    }

    // Step 3: Common validations
    this.validateConnectivity(diagram, errors, warnings);
    this.validateEvidence(diagram, warnings);
    this.validateColors(diagram, warnings);

    const valid = errors.length === 0;
    return this.buildResult(valid, errors, warnings, info, diagram);
  }

  private validateArchitecture(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[], info: ValidationError[]) {
    const d = diagram as any;
    const nodeIds = new Set(d.nodes?.map((n: any) => n.id) || []);

    // Check zones are not empty
    if (d.zones && d.zones.length > 0) {
      for (const zone of d.zones) {
        const nodesInZone = d.nodes?.filter((n: any) => n.zone === zone.id) || [];
        if (nodesInZone.length === 0) {
          warnings.push({
            subject: `zone "${zone.id}"`,
            message: `Zone '${zone.label}' has no nodes`,
            severity: 'warning',
            suggestion: `Remove zone or add nodes to it`,
          });
        }
      }
    }

    // Check tier consistency
    const tiers = new Set(d.nodes?.map((n: any) => n.tier).filter(Boolean) || []);
    if (tiers.size > 0 && d.nodes) {
      const tierOrder = ['frontend', 'backend', 'database', 'external'];
      const tierIndices = new Map<string, number>();
      d.nodes.forEach((n: any) => {
        if (n.tier) tierIndices.set(n.id, tierOrder.indexOf(n.tier));
      });

      // Check if edges go backward in tier hierarchy
      for (const edge of d.edges || []) {
        const fromTier = tierIndices.get(edge.from);
        const toTier = tierIndices.get(edge.to);
        if (fromTier !== undefined && toTier !== undefined && fromTier > toTier) {
          info.push({
            subject: `edge "${edge.id}"`,
            message: `Edge goes from lower to higher tier (may indicate unusual flow)`,
            severity: 'info',
          });
        }
      }
    }
  }

  private validateWorkflow(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[], info: ValidationError[]) {
    const d = diagram as any;
    const nodeIds = new Set(d.nodes?.map((n: any) => n.id) || []);

    // Must have start node
    const startNodes = d.nodes?.filter((n: any) => n.type === 'start') || [];
    if (startNodes.length === 0) {
      errors.push({
        subject: 'workflow',
        message: `Workflow missing 'start' node (type: 'start')`,
        severity: 'error',
        suggestion: `Add a node with type: 'start' at the beginning`,
      });
    }

    // Must have end node
    const endNodes = d.nodes?.filter((n: any) => n.type === 'end') || [];
    if (endNodes.length === 0) {
      errors.push({
        subject: 'workflow',
        message: `Workflow missing 'end' node (type: 'end')`,
        severity: 'error',
        suggestion: `Add a node with type: 'end'`,
      });
    }

    // Check decision nodes have 2+ outgoing edges
    for (const node of d.nodes || []) {
      if (node.type === 'decision') {
        const outgoing = (d.edges || []).filter((e: any) => e.from === node.id).length;
        if (outgoing < 2) {
          warnings.push({
            subject: `node "${node.id}"`,
            message: `Decision node '${node.label}' has only ${outgoing} outgoing edge (need 2+)`,
            severity: 'warning',
            suggestion: `Add more branches to the decision`,
          });
        }
      }
    }

    // Check swimlane usage
    if (d.swimlanes && d.swimlanes.length > 0) {
      // Optional: check if swimlanes are properly used
    }
  }

  private validateSequence(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[], info: ValidationError[]) {
    const d = diagram as any;
    const participantIds = new Set(d.participants?.map((p: any) => p.id) || []);

    // Check participants referenced
    for (const msg of d.messages || []) {
      if (!participantIds.has(msg.from)) {
        errors.push({
          subject: `message "${msg.id}"`,
          message: `Message references unknown participant '${msg.from}'`,
          severity: 'error',
          suggestion: `Use one of: ${Array.from(participantIds).join(', ')}`,
        });
      }
      if (!participantIds.has(msg.to)) {
        errors.push({
          subject: `message "${msg.id}"`,
          message: `Message references unknown participant '${msg.to}'`,
          severity: 'error',
          suggestion: `Use one of: ${Array.from(participantIds).join(', ')}`,
        });
      }
    }

    // Check message order is monotonic
    const messages = d.messages || [];
    for (let i = 1; i < messages.length; i++) {
      if (messages[i].order <= messages[i - 1].order) {
        errors.push({
          subject: `message "${messages[i].id}"`,
          message: `Message order is not monotonic (${messages[i].order} <= ${messages[i - 1].order})`,
          severity: 'error',
          suggestion: `Ensure order field increases: 1, 2, 3, ...`,
        });
      }
    }
  }

  private validateDataFlow(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[], info: ValidationError[]) {
    const d = diagram as any;
    const nodeIds = new Set(d.nodes?.map((n: any) => n.id) || []);

    // Check flows reference valid nodes
    for (const flow of d.flows || []) {
      for (const nodeId of flow.path || []) {
        if (!nodeIds.has(nodeId)) {
          errors.push({
            subject: `flow "${flow.id}"`,
            message: `Flow path references unknown node '${nodeId}'`,
            severity: 'error',
          });
        }
      }
    }

    // Check data type consistency
    const edgeDataTypes = new Map<string, string>();
    for (const edge of d.edges || []) {
      if (edge.format) edgeDataTypes.set(edge.id, edge.format);
    }
  }

  private validateLifecycle(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[], info: ValidationError[]) {
    const d = diagram as any;
    const stageIds = new Set(d.stages?.map((s: any) => s.id) || []);

    // Check transitions reference valid stages
    for (const trans of d.transitions || []) {
      if (!stageIds.has(trans.from)) {
        errors.push({
          subject: `transition`,
          message: `Transition references unknown stage '${trans.from}'`,
          severity: 'error',
        });
      }
      if (!stageIds.has(trans.to)) {
        errors.push({
          subject: `transition`,
          message: `Transition references unknown stage '${trans.to}'`,
          severity: 'error',
        });
      }
    }
  }

  private validateConnectivity(diagram: Diagram, errors: ValidationError[], warnings: ValidationError[]) {
    const d = diagram as any;
    const nodeIds = new Set(d.nodes?.map((n: any) => n.id) || []);

    // Check all edges reference valid nodes
    for (const edge of d.edges || []) {
      if (!nodeIds.has(edge.from)) {
        errors.push({
          subject: `edge "${edge.id}"`,
          message: `Edge references unknown node '${edge.from}'`,
          severity: 'error',
        });
      }
      if (!nodeIds.has(edge.to)) {
        errors.push({
          subject: `edge "${edge.id}"`,
          message: `Edge references unknown node '${edge.to}'`,
          severity: 'error',
        });
      }
    }

    // Check for orphaned nodes
    const edgeNodes = new Set<string>();
    for (const edge of d.edges || []) {
      edgeNodes.add(edge.from);
      edgeNodes.add(edge.to);
    }

    for (const node of d.nodes || []) {
      if (!edgeNodes.has(node.id)) {
        warnings.push({
          subject: `node "${node.id}"`,
          message: `Node '${node.label}' is not connected to any edge (orphaned)`,
          severity: 'warning',
          suggestion: `Connect the node or remove it`,
        });
      }
    }
  }

  private validateEvidence(diagram: Diagram, warnings: ValidationError[]) {
    const d = diagram as any;
    const highValueNodes = d.nodes?.filter((n: any) =>
      ['security', 'database', 'external', 'cloud'].includes(n.color)
    ) || [];

    for (const node of highValueNodes) {
      if (!node.evidence) {
        warnings.push({
          subject: `node "${node.id}"`,
          message: `High-value node '${node.label}' lacks evidence tie`,
          severity: 'warning',
          suggestion: `Add evidence: { file, lines, commit, or url }`,
        });
      }
    }
  }

  private validateColors(diagram: Diagram, warnings: ValidationError[]) {
    const d = diagram as any;
    const validColors = ['frontend', 'backend', 'database', 'security', 'cloud', 'messaging', 'external'];

    for (const node of d.nodes || []) {
      if (!validColors.includes(node.color)) {
        warnings.push({
          subject: `node "${node.id}"`,
          message: `Node uses invalid color '${node.color}'`,
          severity: 'warning',
          suggestion: `Use: ${validColors.join(', ')}`,
        });
      }
    }
  }

  private buildResult(
    valid: boolean,
    errors: ValidationError[],
    warnings: ValidationError[],
    info: ValidationError[],
    diagram: Diagram
  ): ValidationResult {
    const d = diagram as any;
    return {
      valid,
      errors,
      warnings,
      info,
      diagnostics: {
        nodeCount: d.nodes?.length || 0,
        edgeCount: d.edges?.length || 0,
        missingEvidence: d.nodes?.filter((n: any) => !n.evidence).map((n: any) => n.id) || [],
        unreachableNodes: [],
        cycles: [],
      },
    };
  }
}
