import { z } from 'zod';

// Semantic colors - fixed meaning across all themes
export const SemanticColor = z.enum([
  'frontend',      // User-facing interfaces
  'backend',       // Server-side logic
  'database',      // Data storage
  'security',      // Auth, encryption, guards
  'cloud',         // Cloud services, infrastructure
  'messaging',     // Queues, pub/sub, event systems
  'external',      // Third-party services
]);
export type SemanticColor = z.infer<typeof SemanticColor>;

// Node metadata - evidence grounding
const EvidenceSchema = z.object({
  file: z.string().optional().describe('File path (relative to repo root)'),
  lines: z.string().optional().describe('Line range, e.g., "42-88" or "42"'),
  commit: z.string().optional().describe('Git commit SHA (first 7+ chars)'),
  url: z.string().url().optional().describe('External URL (GitHub, docs, etc.)'),
}).refine(e => e.file !== undefined || e.url !== undefined, {
  message: 'Evidence needs a file (code in this repo) or a url (external source)',
}).describe('Evidence ties node/edge to authored source');

// Base node - shared across all diagram types
const BaseNodeSchema = z.object({
  id: z.string().min(1).max(64).describe('Stable ID (alphanumeric + hyphens, immutable)'),
  label: z.string().min(1).max(128).describe('Display name'),
  color: SemanticColor.describe('Semantic color (meaning, not aesthetic)'),
  icon: z.string().optional().describe('Icon ID from simple-icons'),
  evidence: EvidenceSchema.optional(),
  description: z.string().max(256).optional().describe('Brief explanation'),
  metadata: z.record(z.unknown()).optional().describe('Domain-specific properties'),
}).describe('Core node properties');

// Edge - represents relationship or flow
const EdgeSchema = z.object({
  id: z.string().min(1).max(64).describe('Stable ID'),
  from: z.string().describe('Source node ID'),
  to: z.string().describe('Target node ID'),
  label: z.string().max(64).optional().describe('Relationship type'),
  evidence: EvidenceSchema.optional(),
  metadata: z.record(z.unknown()).optional(),
}).describe('Edge connecting two nodes');

// Diagram type: Architecture
const ArchitectureNodeSchema = BaseNodeSchema.extend({
  zone: z.string().optional().describe('Zone/domain (e.g., "payment", "auth")'),
  tier: z.enum(['frontend', 'backend', 'database', 'external']).optional(),
});

const ArchitectureSchema = z.object({
  type: z.literal('architecture'),
  version: z.string().describe('Spec version (semver)'),
  title: z.string().min(1).max(200).describe('Diagram title'),
  description: z.string().max(1000).optional(),
  nodes: z.array(ArchitectureNodeSchema).min(1).describe('System components'),
  edges: z.array(EdgeSchema).describe('Dependencies and flows'),
  zones: z.array(z.object({
    id: z.string(),
    label: z.string(),
    color: z.string().optional(),
  })).optional().describe('Logical groupings'),
  metadata: z.object({
    author: z.string().optional(),
    created: z.string().datetime().optional(),
    updated: z.string().datetime().optional(),
    version: z.string().optional().describe('Project version'),
  }).optional(),
}).describe('Architecture diagram IR');

// Diagram type: Workflow
const WorkflowNodeSchema = BaseNodeSchema.extend({
  type: z.enum(['start', 'process', 'decision', 'end']).optional().describe('Node type'),
  action: z.string().optional().describe('Action or transformation'),
});

const WorkflowEdgeSchema = EdgeSchema.extend({
  condition: z.string().optional().describe('Condition or trigger'),
  order: z.number().optional().describe('Execution order'),
});

const WorkflowSchema = z.object({
  type: z.literal('workflow'),
  version: z.string(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  nodes: z.array(WorkflowNodeSchema).min(1),
  edges: z.array(WorkflowEdgeSchema),
  swimlanes: z.array(z.object({
    id: z.string(),
    label: z.string(),
    actor: z.string().optional().describe('Actor/role responsible'),
  })).optional(),
  metadata: z.object({
    author: z.string().optional(),
    created: z.string().datetime().optional(),
    updated: z.string().datetime().optional(),
  }).optional(),
}).describe('Workflow diagram IR');

// Diagram type: Sequence
const SequenceNodeSchema = BaseNodeSchema.extend({
  role: z.enum(['actor', 'participant', 'system']).optional(),
});

const SequenceMessageSchema = z.object({
  id: z.string(),
  from: z.string().describe('Source participant'),
  to: z.string().describe('Target participant'),
  label: z.string().describe('Message text'),
  type: z.enum(['sync', 'async', 'return']).optional(),
  order: z.number().describe('Message sequence order'),
  evidence: EvidenceSchema.optional(),
});

const SequenceSchema = z.object({
  type: z.literal('sequence'),
  version: z.string(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  participants: z.array(SequenceNodeSchema).min(2),
  messages: z.array(SequenceMessageSchema).min(1),
  metadata: z.object({
    author: z.string().optional(),
    created: z.string().datetime().optional(),
    scenario: z.string().optional().describe('Use case or scenario name'),
  }).optional(),
}).describe('Sequence diagram IR');

// Diagram type: Data Flow
const DataFlowNodeSchema = BaseNodeSchema.extend({
  dataType: z.string().optional().describe('Data structure type'),
  transformation: z.string().optional().describe('Transformation applied'),
});

const DataFlowEdgeSchema = EdgeSchema.extend({
  dataSchema: z.string().optional().describe('Data schema reference'),
  format: z.enum(['json', 'xml', 'csv', 'protobuf', 'avro', 'parquet']).optional(),
});

const DataFlowSchema = z.object({
  type: z.literal('dataflow'),
  version: z.string(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  nodes: z.array(DataFlowNodeSchema).min(1),
  edges: z.array(DataFlowEdgeSchema),
  flows: z.array(z.object({
    id: z.string(),
    path: z.array(z.string()).describe('Ordered list of node IDs'),
    dataType: z.string().optional(),
    description: z.string().optional(),
  })).optional().describe('Named data flow paths'),
  metadata: z.object({
    author: z.string().optional(),
    created: z.string().datetime().optional(),
  }).optional(),
}).describe('Data flow diagram IR');

// Diagram type: Lifecycle
const LifecycleStageSchema = z.object({
  id: z.string(),
  label: z.string(),
  duration: z.string().optional().describe('Typical duration (e.g., "2-4 weeks")'),
  description: z.string().optional(),
  activities: z.array(z.string()).optional(),
});

const LifecycleSchema = z.object({
  type: z.literal('lifecycle'),
  version: z.string(),
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  stages: z.array(LifecycleStageSchema).min(1).describe('Ordered lifecycle stages'),
  transitions: z.array(z.object({
    from: z.string().describe('From stage ID'),
    to: z.string().describe('To stage ID'),
    trigger: z.string().optional().describe('Transition trigger'),
    condition: z.string().optional().describe('Optional condition'),
  })).optional(),
  metadata: z.object({
    author: z.string().optional(),
    created: z.string().datetime().optional(),
    subject: z.string().optional().describe('What lifecycle is this for'),
  }).optional(),
}).describe('Lifecycle diagram IR');

// Union of all diagram types, keyed on `type` so errors point at the failing field
export const DiagramSchema = z.discriminatedUnion('type', [
  ArchitectureSchema,
  WorkflowSchema,
  SequenceSchema,
  DataFlowSchema,
  LifecycleSchema,
]).describe('Typed JSON intermediate representation for diagrams');

export type Diagram = z.infer<typeof DiagramSchema>;
export type ArchitectureDiagram = z.infer<typeof ArchitectureSchema>;
export type WorkflowDiagram = z.infer<typeof WorkflowSchema>;
export type SequenceDiagram = z.infer<typeof SequenceSchema>;
export type DataFlowDiagram = z.infer<typeof DataFlowSchema>;
export type LifecycleDiagram = z.infer<typeof LifecycleSchema>;

// Validation result
export const ValidationResultSchema = z.object({
  valid: z.boolean(),
  errors: z.array(z.object({
    path: z.array(z.union([z.string(), z.number()])),
    message: z.string(),
    code: z.string(),
  })),
  warnings: z.array(z.object({
    subject: z.string(),
    message: z.string(),
    suggestion: z.string().optional(),
  })),
  diagnostics: z.object({
    nodeCount: z.number(),
    edgeCount: z.number(),
    missingEvidence: z.array(z.string()).optional().describe('Node IDs without evidence'),
    unreachableNodes: z.array(z.string()).optional().describe('Orphaned nodes'),
    cycles: z.array(z.array(z.string())).optional().describe('Circular dependencies'),
  }),
});

export type ValidationResult = z.infer<typeof ValidationResultSchema>;
