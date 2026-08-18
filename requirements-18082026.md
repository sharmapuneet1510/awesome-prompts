# AI Spec-Driven Development Platform

## Vision

Build an AI-first engineering platform where the **Specification is the
Single Source of Truth** and every engineering decision is captured as
structured knowledge. The platform is composed of role-based AI
companions that collaborate through a centralized Project Context and
immutable ADRs.

# 1. Core Principles

-   Specification-first development
-   Human approves, AI accelerates
-   Every meaningful decision becomes an ADR
-   Current state and historical reasoning are separated
-   Complete traceability from business requirement to production
-   Shared project memory across all companions

# 2. High-Level Workflow

``` text
Business Discussion
    │
    ▼
BA Companion
    │
    ▼
Jira + Requirements
    │
    ▼
Developer Companion
    │
    ▼
Technical Analysis
    │
    ▼
ADR Creation (continuous)
    │
    ▼
Current Technical Specification
    │
    ▼
Implementation Plan
    │
    ▼
Coding Companion
    │
    ▼
Pull Request
    │
    ▼
Review Companion
    │
    ▼
QA Companion
    │
    ▼
Deployment
    │
    ▼
Project Context Updated
```

# 3. AI Companions

## BA Companion

-   Discover requirements
-   Clarify ambiguity
-   Build business context
-   Generate Epics/Stories/Tasks
-   Define acceptance criteria
-   Maintain traceability

Outputs: - BRD - Business Rules - User Flows - Jira - Acceptance
Criteria

## Developer Companion

-   Read Jira
-   Understand codebase
-   Explain current flow
-   Discuss implementation
-   Generate technical analysis
-   Record every engineering decision
-   Maintain ADRs
-   Produce current technical specification

## Coding Companion

-   Read approved specification
-   Implement only approved work
-   Generate unit/integration tests
-   Generate documentation

## Review Companion

Compares: - Requirement ↔ Code - ADR ↔ Code - Technical Spec ↔ Code -
Tests ↔ Acceptance Criteria

Produces observations only.

## QA Companion

Maintains: - Sanity - Regression - Integration - Performance -
Security - UAT

# 4. Central Project Context

``` text
Project Context
├── Project Overview
├── Business Context
├── Technical Context
├── Architecture Context
├── Known Behaviours
├── Technical Debt
├── MVP / Scope
├── Quality Context
│   ├── Sanity
│   ├── Regression
│   ├── Integration
│   ├── Performance
│   └── Security
├── Dependencies
├── Risks
├── Release History
├── Open Questions
└── AI Memory
```

## Business Context

-   Goals
-   Stakeholders
-   Business flows
-   Business rules
-   Domain glossary
-   Regulatory constraints
-   Assumptions

## Technical Context

-   Architecture
-   Services
-   APIs
-   Database
-   Messaging
-   External systems
-   Deployment
-   Observability

## Known Behaviour

Expected behaviour, intentional limitations, known quirks.

## Technical Debt

Issue, impact, workaround, recommendation, priority.

## Quality Context

Maintain reusable scenarios: - Sanity - Regression - Integration -
Performance - Security

# 5. Engineering Decision Records (ADR)

Every significant engineering decision creates a lightweight ADR.

Template:

-   ID
-   Parent Jira
-   Status
-   Context
-   Problem
-   Options
-   Decision
-   Rationale
-   Consequences
-   Affected Components
-   Affected Tests
-   Related ADRs
-   Supersedes
-   Superseded By

Lifecycle: Draft → Proposed → Accepted → Implemented → Verified →
Superseded → Archived

Decision Types: - Architecture - API - Database - Performance -
Security - Testing - Deployment - Refactoring - Business Logic -
Monitoring

# 6. Relationship Model

``` text
Requirement
   │
   ▼
Jira
   │
   ▼
Technical Analysis
   │
   ▼
ADRs (many)
   │
   ▼
Current Technical Specification
   │
   ▼
Implementation Plan
   │
   ▼
Code
   │
   ▼
Tests
   │
   ▼
Pull Request
   │
   ▼
Review
   │
   ▼
Deployment
```

# 7. Current Technical Specification

Represents the latest approved design only.

Includes: - Architecture - Flow - Components - APIs - Data Model - Error
Handling - Performance - Security - Testing - Rollback

# 8. Final Implementation Record

Stores: - Jira - Final Spec Version - ADRs Applied - PR - Code
Components - Tests - Tech Debt - Release

# 9. Traceability

Requirement → Jira → ADR → Technical Specification → Implementation →
Tests → PR → Release

# 10. Guiding Rule

The platform always distinguishes:

-   FACT
-   INFERENCE
-   PROPOSAL
-   DECISION

Only DECISION updates the Technical Specification after approval.

