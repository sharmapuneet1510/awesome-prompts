/**
 * Validator Tests — Comprehensive test suite
 */

import { DiagramValidator } from '../validator/validator';

const validator = new DiagramValidator();

describe('Validator', () => {
  describe('Schema Validation', () => {
    test('accepts valid architecture diagram', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test System',
        nodes: [
          { id: 'api', label: 'API', color: 'backend' },
          { id: 'db', label: 'Database', color: 'database' }
        ],
        edges: [
          { id: 'e1', from: 'api', to: 'db' }
        ]
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('rejects missing type', () => {
      const diagram = { version: '1.0.0', title: 'Test' };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.subject.includes('type'))).toBe(true);
    });

    test('rejects invalid type', () => {
      const diagram = {
        type: 'invalid-type',
        version: '1.0.0',
        title: 'Test',
        nodes: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
    });

    test('rejects empty nodes array', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
    });
  });

  describe('Connectivity Validation', () => {
    test('rejects edge referencing unknown node', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [{ id: 'api', label: 'API', color: 'backend' }],
        edges: [{ id: 'e1', from: 'api', to: 'unknown' }]
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.subject.includes('unknown'))).toBe(true);
    });

    test('warns on orphaned nodes', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          { id: 'api', label: 'API', color: 'backend' },
          { id: 'orphan', label: 'Unused', color: 'backend' }
        ],
        edges: [{ id: 'e1', from: 'api', to: 'api' }]
      };
      const result = validator.validate(diagram);
      expect(result.warnings.some(w => w.subject.includes('orphan'))).toBe(true);
    });
  });

  describe('Workflow-Specific Validation', () => {
    test('requires start node', () => {
      const diagram = {
        type: 'workflow',
        version: '1.0.0',
        title: 'Process',
        nodes: [
          { id: 'process', label: 'Step', type: 'process', color: 'backend' },
          { id: 'end', label: 'End', type: 'end', color: 'backend' }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.message.includes('start'))).toBe(true);
    });

    test('requires end node', () => {
      const diagram = {
        type: 'workflow',
        version: '1.0.0',
        title: 'Process',
        nodes: [
          { id: 'start', label: 'Start', type: 'start', color: 'backend' },
          { id: 'process', label: 'Step', type: 'process', color: 'backend' }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.message.includes('end'))).toBe(true);
    });

    test('warns on decision with < 2 branches', () => {
      const diagram = {
        type: 'workflow',
        version: '1.0.0',
        title: 'Process',
        nodes: [
          { id: 'start', label: 'Start', type: 'start', color: 'backend' },
          { id: 'decision', label: 'Decide', type: 'decision', color: 'backend' },
          { id: 'end', label: 'End', type: 'end', color: 'backend' }
        ],
        edges: [
          { id: 'e1', from: 'start', to: 'decision' },
          { id: 'e2', from: 'decision', to: 'end' }
        ]
      };
      const result = validator.validate(diagram);
      expect(result.warnings.some(w => w.message.includes('Decision'))).toBe(true);
    });
  });

  describe('Sequence-Specific Validation', () => {
    test('requires 2+ participants', () => {
      const diagram = {
        type: 'sequence',
        version: '1.0.0',
        title: 'Flow',
        participants: [{ id: 'a', label: 'Actor', role: 'actor', color: 'frontend' }],
        messages: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
    });

    test('validates message order is monotonic', () => {
      const diagram = {
        type: 'sequence',
        version: '1.0.0',
        title: 'Flow',
        participants: [
          { id: 'a', label: 'A', role: 'actor', color: 'frontend' },
          { id: 'b', label: 'B', role: 'participant', color: 'backend' }
        ],
        messages: [
          { id: 'm1', from: 'a', to: 'b', label: 'Msg 1', order: 1 },
          { id: 'm2', from: 'b', to: 'a', label: 'Msg 2', order: 1 }
        ]
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.message.includes('order'))).toBe(true);
    });

    test('rejects message referencing unknown participant', () => {
      const diagram = {
        type: 'sequence',
        version: '1.0.0',
        title: 'Flow',
        participants: [
          { id: 'a', label: 'A', role: 'actor', color: 'frontend' }
        ],
        messages: [
          { id: 'm1', from: 'a', to: 'unknown', label: 'Msg', order: 1 }
        ]
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(false);
    });
  });

  describe('Evidence Validation', () => {
    test('warns on missing evidence for high-value nodes', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          { id: 'auth', label: 'Auth', color: 'security' }, // High-value, no evidence
          { id: 'cache', label: 'Cache', color: 'database', evidence: { file: 'cache.ts' } }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.warnings.some(w => w.subject.includes('auth'))).toBe(true);
    });

    test('accepts evidence on nodes', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          {
            id: 'api',
            label: 'API',
            color: 'backend',
            evidence: {
              file: 'src/api/server.ts',
              lines: '1-50',
              commit: 'abc1234'
            }
          }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('Diagnostics', () => {
    test('reports node and edge counts', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          { id: 'a', label: 'A', color: 'backend' },
          { id: 'b', label: 'B', color: 'backend' }
        ],
        edges: [
          { id: 'e1', from: 'a', to: 'b' }
        ]
      };
      const result = validator.validate(diagram);
      expect(result.diagnostics.nodeCount).toBe(2);
      expect(result.diagnostics.edgeCount).toBe(1);
    });

    test('lists missing evidence nodes', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          { id: 'a', label: 'A', color: 'database' }, // High-value, missing evidence
          { id: 'b', label: 'B', color: 'backend', evidence: { file: 'b.ts' } }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.diagnostics.missingEvidence).toContain('a');
      expect(result.diagnostics.missingEvidence).not.toContain('b');
    });
  });

  describe('Color Validation', () => {
    test('warns on invalid color', () => {
      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes: [
          { id: 'a', label: 'A', color: 'invalid-color' }
        ],
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.warnings.some(w => w.message.includes('color'))).toBe(true);
    });

    test('accepts all 7 semantic colors', () => {
      const colors = ['frontend', 'backend', 'database', 'security', 'cloud', 'messaging', 'external'];
      const nodes = colors.map((color, i) => ({
        id: `node-${i}`,
        label: `Node ${i}`,
        color: color as any
      }));

      const diagram = {
        type: 'architecture',
        version: '1.0.0',
        title: 'Test',
        nodes,
        edges: []
      };
      const result = validator.validate(diagram);
      expect(result.valid).toBe(true);
    });
  });
});

// Test runner (simplified)
function test(name: string, fn: () => void) {
  try {
    fn();
    console.log(`✓ ${name}`);
  } catch (err) {
    console.error(`✗ ${name}`);
    console.error(`  ${(err as Error).message}`);
  }
}

function describe(suite: string, fn: () => void) {
  console.log(`\n${suite}`);
  fn();
}

function expect(value: any) {
  return {
    toBe: (expected: any) => {
      if (value !== expected) throw new Error(`Expected ${expected}, got ${value}`);
    },
    toHaveLength: (length: number) => {
      if (Array.isArray(value) && value.length !== length) {
        throw new Error(`Expected length ${length}, got ${value.length}`);
      }
    },
    toContain: (item: any) => {
      if (!Array.isArray(value) || !value.includes(item)) {
        throw new Error(`Expected array to contain ${item}`);
      }
    },
    toEqual: (expected: any) => {
      if (JSON.stringify(value) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(expected)}, got ${JSON.stringify(value)}`);
      }
    },
    toEqual: (expected: any) => {
      if (JSON.stringify(value) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(expected)}, got ${JSON.stringify(value)}`);
      }
    },
    not: {
      toContain: (item: any) => {
        if (Array.isArray(value) && value.includes(item)) {
          throw new Error(`Expected array to not contain ${item}`);
        }
      },
    },
  };
}
