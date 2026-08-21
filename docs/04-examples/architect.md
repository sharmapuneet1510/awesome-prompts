---
title: Architect Agent — SDLC Examples
description: Complete software development lifecycle examples showing architect functions in real-world scenarios
version: 1.0
---

# Architect Agent — SDLC Examples

**Role:** Architecture & Design | **Functions:** design, refactor, schema, api, frontend, a11y

Complete lifecycle examples showing how architect functions work together in design phases.

---

## 📋 SDLC Lifecycle Overview

```
Phase 0: Greenfield Design        → architect:design
Phase 1: API Contract Design      → architect:api
Phase 2: Database Schema Design   → architect:schema
Phase 3: Frontend Architecture    → architect:frontend
Phase 4: Accessibility Audit      → architect:a11y
Phase 5: Brownfield Refactoring   → architect:refactor
```

---

## 🎯 Scenario 1: Real-Time Chat System (Greenfield)

### Phase 0: System Design

**Situation:** Team needs to build real-time chat system for 100K concurrent users. No existing code.

**Command:**
```bash
architect:design requirements="Real-time chat system supporting:
- 100K concurrent users worldwide
- Private 1:1 chats + group chats (up to 500 members)
- Rich media support (images, files, voice messages)
- Message history (searchable, 2-year retention)
- Push notifications (mobile + web)
- Typing indicators + read receipts
- Low latency (<200ms message delivery)"
```

**Architect Output: System Topology**

```
┌─────────────────────────────────────────────────────┐
│                   CDN + CloudFlare                   │
│           (Static assets, DDoS protection)           │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              API Gateway + Load Balancer             │
│          (Rate limiting, routing, compression)       │
└─────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┬──────────────────┐
        ↓                 ↓                  ↓
   ┌─────────┐       ┌─────────┐      ┌──────────┐
   │  Chat   │       │  User   │      │Notification
   │ Service │       │ Service │      │ Service
   │ (C++)   │       │(FastAPI)│      │(Python)
   └─────────┘       └─────────┘      └──────────┘
        ↓                 ↓                  ↓
   ┌──────────────────────────────────────────────┐
   │         Message Queue (Apache Pulsar)         │
   │    (Message ordering, replay, retention)      │
   └──────────────────────────────────────────────┘
        ↓                 ↓                  ↓
   ┌─────────┐       ┌─────────┐      ┌──────────┐
   │ Redis   │       │PostgreSQL      │ Cassandra│
   │(Cache)  │       │(Messages)      │(Analytics
   └─────────┘       └─────────┘      └──────────┘
```

**Architecture Output Document:**

```
REAL-TIME CHAT SYSTEM ARCHITECTURE

1. Frontend Layer
   ├─ React Web App (TypeScript)
   │  ├─ Chat view (message list, input, typing indicators)
   │  ├─ User list + search
   │  └─ Notification center
   │
   └─ React Native Mobile (iOS/Android)
      ├─ Chat interface
      ├─ Push notifications
      └─ Offline message queue

2. WebSocket Layer (Low-Latency Communication)
   ├─ Socket.io server (handles real-time events)
   ├─ Message routing (1:1 vs group differentiation)
   ├─ Presence management (online/offline status)
   └─ Typing indicator broadcasting

3. Chat Service (Core Logic)
   ├─ Message processing (validation, sanitization)
   ├─ Message storage (PostgreSQL for history)
   ├─ Message indexing (Elasticsearch for search)
   └─ Rich media handling (images, files, transcription)

4. User Service
   ├─ Authentication (OAuth2 + JWT)
   ├─ User profiles
   ├─ Contact lists + blocking
   └─ User preferences

5. Notification Service
   ├─ Push notifications (Firebase Cloud Messaging)
   ├─ Email notifications (SendGrid)
   ├─ Notification preferences
   └─ Delivery tracking

6. Data Layer
   ├─ PostgreSQL (user data, messages, relationships)
   ├─ Redis (cache, sessions, presence)
   ├─ Elasticsearch (full-text search)
   └─ Cassandra (analytics, event log)

7. Message Queue (Apache Pulsar)
   ├─ Topic: user.messages (all messages)
   ├─ Topic: user.typing (typing indicators)
   ├─ Topic: user.presence (online/offline)
   └─ Topic: notifications (notification events)

8. Infrastructure
   ├─ Kubernetes (container orchestration)
   ├─ Auto-scaling (based on concurrent connections)
   ├─ Multi-region deployment
   └─ Disaster recovery (RTO: 1 hour, RPO: 5 min)
```

**Caching Strategy:**

```
┌──────────────────────────────────────┐
│   Data Access Pattern Optimization    │
├──────────────────────────────────────┤
│ User profile        │ 1h TTL, Redis   │
│ Contact list        │ 24h TTL, Redis  │
│ Chat list           │ 5m TTL, Redis   │
│ Message (recent 100)│ 7d TTL, Redis   │
│ Typing status       │ 3s TTL, Redis   │
│ User presence       │ 30s TTL, Redis  │
└──────────────────────────────────────┘

Cache Invalidation:
├─ Write-through for presence (real-time accuracy)
├─ Write-behind for profiles (eventual consistency OK)
└─ Event-driven invalidation via Pulsar
```

**Deployment Topology:**

```
Primary Region (US-East)
├─ 3x Chat Service replicas
├─ 3x User Service replicas
├─ 3x Notification Service replicas
├─ PostgreSQL primary + 2 replicas
└─ Redis cluster (6 nodes)

Secondary Region (EU-West) - Hot standby
├─ Full replica of primary
└─ Ready for failover (<5 min)

Edge Locations (Global)
├─ CDN caches (CloudFront)
├─ Regional Redis read replicas
└─ DNS geo-routing
```

**Timeline:** 1-2 hours | **Output Size:** 20-30 pages

---

### Phase 1: API Contract Design

**Command:**
```bash
architect:api requirements="
- List chats (paginated, sorted by last message)
- Get chat with history (with pagination)
- Send message (text, image, file)
- Get message search results
- Mark messages as read
- Get typing indicator status
- Get user presence status
- Create/leave group chat"
```

**Architect Output: OpenAPI 3.0 Specification**

```yaml
openapi: 3.0.0
info:
  title: Chat API
  version: 1.0.0

servers:
  - url: https://api.chat.example.com/v1

paths:
  /chats:
    get:
      summary: List user's chats
      parameters:
        - name: skip
          in: query
          schema: { type: integer, default: 0 }
        - name: limit
          in: query
          schema: { type: integer, default: 20 }
        - name: sort_by
          in: query
          schema: { type: string, enum: [last_message_at, created_at] }
      responses:
        '200':
          description: List of chats
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/Chat' }

  /chats/{chat_id}:
    get:
      summary: Get chat with message history
      parameters:
        - name: chat_id
          in: path
          required: true
          schema: { type: string }
        - name: limit
          in: query
          schema: { type: integer, default: 50 }
      responses:
        '200':
          description: Chat with messages
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ChatWithMessages' }

  /chats/{chat_id}/messages:
    post:
      summary: Send message
      parameters:
        - name: chat_id
          in: path
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                content: { type: string }
                media: { type: array, items: { type: string } }
                reply_to: { type: string }
      responses:
        '201':
          description: Message created
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Message' }

  /chats/{chat_id}/messages/search:
    get:
      summary: Search messages
      parameters:
        - name: chat_id
          in: path
          required: true
          schema: { type: string }
        - name: q
          in: query
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items: { $ref: '#/components/schemas/Message' }

components:
  schemas:
    Chat:
      type: object
      properties:
        id: { type: string }
        type: { type: string, enum: [direct, group] }
        name: { type: string }
        avatar: { type: string }
        last_message: { $ref: '#/components/schemas/Message' }
        unread_count: { type: integer }
        last_message_at: { type: string, format: date-time }

    Message:
      type: object
      properties:
        id: { type: string }
        chat_id: { type: string }
        sender_id: { type: string }
        content: { type: string }
        media: { type: array, items: { type: string } }
        created_at: { type: string, format: date-time }
        read_by: { type: array, items: { type: string } }
        reply_to: { type: string }
```

**Timeline:** 30-45 minutes | **Output:** Swagger UI + client SDK generation

---

### Phase 2: Database Schema Design

**Command:**
```bash
architect:schema requirements="
Users (id, email, name, avatar, status, created_at, updated_at)
Chats (id, type, name, created_at, updated_at)
Chat Members (chat_id, user_id, joined_at, role)
Messages (id, chat_id, sender_id, content, media_urls, created_at, updated_at)
Message Reads (message_id, user_id, read_at)
Blocked Users (user_id, blocked_user_id, created_at)" db=postgresql
```

**Architect Output: Database Schema**

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    status VARCHAR(50) CHECK (status IN ('online', 'away', 'offline', 'dnd')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

-- Chats table (supports 1:1 and group chats)
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) CHECK (type IN ('direct', 'group')),
    name VARCHAR(255),
    avatar_url TEXT,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chats_type ON chats(type);
CREATE INDEX idx_chats_created_by ON chats(created_by);

-- Chat members (join table with roles)
CREATE TABLE chat_members (
    id SERIAL PRIMARY KEY,
    chat_id UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) CHECK (role IN ('member', 'admin', 'owner')),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chat_id, user_id)
);

CREATE INDEX idx_chat_members_user ON chat_members(user_id);
CREATE INDEX idx_chat_members_chat ON chat_members(chat_id);

-- Messages table (high-volume, optimized for querying)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(id),
    sender_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    media_urls TEXT[] DEFAULT ARRAY[]::TEXT[],
    reply_to_id UUID REFERENCES messages(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_chat_created ON messages(chat_id, created_at DESC);
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_reply_to ON messages(reply_to_id);

-- Partition messages by chat for performance
CREATE TABLE messages_1 PARTITION OF messages
    FOR VALUES IN ('chat-id-1');

-- Message reads (tracks who read what)
CREATE TABLE message_reads (
    id SERIAL PRIMARY KEY,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, user_id)
);

CREATE INDEX idx_message_reads_message ON message_reads(message_id);

-- Blocked users
CREATE TABLE blocked_users (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    blocked_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, blocked_user_id),
    CHECK (user_id != blocked_user_id)
);

CREATE INDEX idx_blocked_users_user ON blocked_users(user_id);
CREATE INDEX idx_blocked_users_blocked ON blocked_users(blocked_user_id);

-- Create migrations
-- Migration 001_init_schema.sql (above)
-- Migration 002_add_indexes.sql
-- Migration 003_partition_messages.sql
```

**Optimization Notes:**

```
High-Volume Optimizations:
├─ Messages table partitioned by chat_id (reduces scan time)
├─ Composite index on (chat_id, created_at) for chronological queries
├─ Message reads table separate (not denormalized) for scalability
└─ Connection pooling recommended (PgBouncer)

Capacity Planning:
├─ 100K users = ~10GB initial data
├─ Messages grow ~100K/day = ~2TB/year
├─ Strategy: Archive messages >2 years to Cassandra
└─ Read replicas for analytics queries
```

**Timeline:** 30-45 minutes | **Output:** DDL + migrations + optimization guide

---

### Phase 3: Frontend Architecture

**Command:**
```bash
architect:frontend requirements="
Chat list component (showing recent chats with unread indicator)
Chat header (chat name, member count, settings)
Message list (scrollable, virtual rendering for 1000+ messages)
Message input (text, rich formatting, file upload, emoji picker)
Typing indicator (showing who's typing)
Read receipt indicator (showing who read when)"
```

**Architect Output: Component Architecture**

```typescript
// Component Hierarchy
ChatApp
├─ Sidebar (Chat list)
│  ├─ SearchChats
│  ├─ ChatListItem (repeated)
│  │  ├─ Avatar
│  │  ├─ ChatName
│  │  ├─ LastMessage
│  │  └─ UnreadBadge
│  └─ CreateChatButton
│
├─ ChatView
│  ├─ ChatHeader
│  │  ├─ ChatInfo
│  │  ├─ MemberCount
│  │  └─ SettingsButton
│  │
│  ├─ MessageList (virtualized)
│  │  ├─ MessageBubble (repeated)
│  │  │  ├─ Avatar
│  │  │  ├─ SenderName
│  │  │  ├─ MessageContent (with media)
│  │  │  ├─ Timestamp
│  │  │  └─ ReadReceipts
│  │  │
│  │  └─ TypingIndicator
│  │
│  └─ MessageInput
│     ├─ Textarea (with @mentions)
│     ├─ FormatToolbar
│     ├─ FileUpload
│     ├─ EmojiPicker
│     └─ SendButton

// State Management (Redux/Zustand)
{
  chats: Chat[],
  activeChat: Chat,
  messages: Message[],
  loading: boolean,
  error: string | null,
  user: User,
  typingUsers: User[],
  presence: { [userId]: 'online' | 'away' | 'offline' }
}

// Performance Optimizations
├─ Virtual scrolling for message list (1000+ messages)
├─ Message memoization (prevent re-renders)
├─ Lazy loading of chat history
├─ Debounced typing indicator (avoid spam)
└─ Web Worker for message processing

// Real-time Updates (WebSocket)
├─ New message → append to list
├─ Typing indicator → update state
├─ Read receipt → update message
├─ User presence → update sidebar
└─ Chat member joined/left → update header
```

**Component Examples:**

```typescript
interface ChatListItemProps {
  chat: Chat;
  isActive: boolean;
  unreadCount: number;
  onClick: (chatId: string) => void;
}

export const ChatListItem: React.FC<ChatListItemProps> = ({
  chat,
  isActive,
  unreadCount,
  onClick,
}) => {
  return (
    <div
      className={`chat-item ${isActive ? 'active' : ''}`}
      onClick={() => onClick(chat.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick(chat.id)}
    >
      <img src={chat.avatar} alt={chat.name} className="avatar" />
      <div className="chat-info">
        <h4>{chat.name}</h4>
        <p>{chat.lastMessage?.content.substring(0, 50)}...</p>
      </div>
      {unreadCount > 0 && (
        <span className="unread-badge">{unreadCount}</span>
      )}
    </div>
  );
};
```

**Timeline:** 1-2 hours | **Output:** Component tree + props interface + state model

---

### Phase 4: Accessibility Audit

**Command:**
```bash
architect:a11y path=./src/components/ChatApp.tsx
```

**Architect Output: Accessibility Report**

```
ACCESSIBILITY AUDIT — CHAT APPLICATION

✓ PASS: Color Contrast
  All text meets WCAG AA standard (4.5:1 minimum)

✓ PASS: Keyboard Navigation
  Tab order: Chat list → Message list → Input
  Enter to send, Escape to close popups

❌ FAIL: Missing alt text
  - Chat avatars missing alt text
  - Fix: <img alt="Chat: {name}" />

❌ FAIL: Form labels not associated
  - Message input has no label
  - Fix: <label htmlFor="message-input">Message</label>

❌ FAIL: Heading hierarchy
  - H2 appears before H1
  - Fix: Use semantic HTML structure

⚠️  WARNING: Focus indicators not visible
  - Add CSS: input:focus { outline: 2px solid #0066cc; }

⚠️  WARNING: ARIA labels missing
  - Send button needs aria-label="Send message"
  - Unread badge needs aria-live="polite"

WCAG 2.1 AA Compliance: 65% → Target: 100%

Remediation Steps:
1. Add alt text to all images (1 hour)
2. Associate form labels (30 minutes)
3. Fix heading hierarchy (15 minutes)
4. Add visible focus indicators (30 minutes)
5. Add ARIA labels + live regions (2 hours)

Timeline to compliance: 4 hours
```

**Timeline:** 15-30 minutes | **Output:** Audit report + remediation roadmap

---

## 🎯 Scenario 2: Monolith to Microservices Refactoring

### Phase 0: Current State Assessment

**Command:**
```bash
architect:refactor path=./legacy-monolith goal="
Split 5-year monolith into 4 independent microservices (User, Product, Order, Payment).
Reduce deployment time from 4 hours to 15 minutes. Enable independent team scaling."
```

**Architect Output: Refactoring Assessment**

```
BROWNFIELD REFACTORING ANALYSIS

Current State (Monolith)
├─ Technology: Java 11 + Spring Boot 2.7
├─ Database: Single PostgreSQL instance
├─ Deployment: 1 GitHub Actions pipeline (4 hours)
├─ Team size: 8 engineers (all touching same codebase)
├─ Coupling: User → Order → Payment → Inventory (tight)
├─ Testing: 3 hours for full test suite
├─ Scalability: 50K concurrent users (hitting limits)
└─ Tech debt: HIGH (210 violations, 8 deprecated dependencies)

Problem Analysis
├─ Tight coupling between domains
├─ Shared database prevents independent scaling
├─ All features blocked on one release cycle
├─ Hard to test (dependencies everywhere)
└─ New team members take 3 weeks to understand

Target State (Microservices)
├─ 4 independent services
│  ├─ User Service (authentication, profiles)
│  ├─ Product Service (catalog, inventory)
│  ├─ Order Service (order management)
│  └─ Payment Service (payments, refunds)
├─ Separate databases per service
├─ Independent deployment pipelines
├─ Event-driven communication (Kafka/Pulsar)
├─ Scalability: 500K concurrent users
└─ Team structure: 1-2 engineers per service

Migration Path (Strangler Pattern)
├─ Phase 1: Set up infrastructure (Week 1)
│  ├─ Kubernetes cluster
│  ├─ Message queue (Pulsar)
│  ├─ Service registry (Consul)
│  └─ CI/CD pipelines
│
├─ Phase 2: Extract User Service (Week 2-3)
│  ├─ Create User Service with separate database
│  ├─ Add API gateway to route /auth/* and /users/*
│  ├─ Monolith still handles most requests
│  └─ Gradual traffic migration to new service
│
├─ Phase 3: Extract Product Service (Week 4-5)
│  ├─ Move product catalog logic
│  ├─ Create ProductService with separate DB
│  └─ Monolith still handles orders
│
├─ Phase 4: Extract Order Service (Week 6-8)
│  ├─ Move order logic
│  ├─ Set up event-driven communication
│  ├─ Handle distributed transactions
│  └─ Critical: Coordination with Payment Service
│
├─ Phase 5: Extract Payment Service (Week 9-10)
│  └─ Last service extraction
│
└─ Phase 6: Remove Monolith (Week 11-12)
   └─ Safely decommission old codebase

Zero-Downtime Deployment Strategy
├─ Blue-Green deployment for each phase
├─ Canary releases (5% → 25% → 100% traffic)
├─ Instant rollback capability
├─ Database migration verification before cutover
└─ Customer-facing change: ZERO downtime

Database Migration Strategy
├─ Phase 1: User Service DB
│  ├─ Create new PostgreSQL instance
│  ├─ Sync data from monolith (one-way replication)
│  ├─ Validate consistency (24 hours)
│  └─ Switch writes to User Service DB
│
├─ Phase 2-4: Repeat for Product, Order, Payment
│
└─ Final: Archive monolith DB (2-year retention)

Event-Driven Communication
├─ When User created → User Service publishes user.created event
├─ When Order created → Order Service consumes, publishes order.created
├─ When Payment processed → Payment Service publishes payment.completed
└─ No direct service-to-service calls (eventual consistency)

Risk Mitigation
├─ 🔴 Distributed transactions → Use Saga pattern with Pulsar
├─ 🔴 Data consistency → Event sourcing + CQRS
├─ 🟡 Debugging complexity → Distributed tracing (Jaeger)
├─ 🟡 Testing → Contract testing (Pact)
└─ 🟡 Operational complexity → Kubernetes + monitoring

Rollback Strategy
├─ Phase 1 rollback: Stop User Service, use monolith (5 min)
├─ Phase 2 rollback: Stop Product Service, use monolith (5 min)
├─ Phase 3 rollback: Most complex (event replay required)
└─ Phase 4 rollback: Same as Phase 3

Post-Migration Benefits
├─ Deployment time: 4h → 15 min (16x faster)
├─ Team scaling: 8 engineers on 1 repo → 2 engineers per service
├─ Feature velocity: +50% (parallel development)
├─ Scalability: 50K → 500K concurrent users
├─ Tech debt: Can upgrade services independently
└─ Testing: 3h → 30 min per service

Timeline: 12 weeks | Team size: 3 infrastructure engineers + existing teams
```

**Timeline:** 2-3 hours | **Output:** Detailed refactoring roadmap + risk matrix

---

## 📊 SDLC Chaining Examples

### Complete Design Lifecycle (2-3 days)

```
Day 1 Morning:
  architect:design → System topology

Day 1 Afternoon:
  architect:api → API contract
  architect:schema → Database schema

Day 2 Morning:
  architect:frontend → Component architecture
  architect:a11y → Accessibility audit

Day 2 Afternoon:
  [Review + refinement]

Day 3 Morning:
  architect:refactor (if needed)
  [Final documentation]

Day 3 Afternoon:
  [Ready for implementation]
```

### Parallel Design Workflow

```
architect:design (1-2 hours)
  ├─ architect:api (parallel, 30-45 min)
  ├─ architect:schema (parallel, 30-45 min)
  └─ architect:frontend (parallel, 1-2 hours)
     └─ architect:a11y (sequential, 15-30 min)
```

---

## ✨ Pro Tips for Architect Functions

1. **Design before coding** — Prevents costly rewrites
2. **API contract first** — Frontend and backend can work in parallel
3. **Schema optimization upfront** — Much cheaper than migration
4. **A11y from day 1** — Retrofitting is 3x more expensive
5. **Document assumptions** — Design artifacts become requirements
6. **Get stakeholder buy-in early** — Save weeks of rework
7. **Consider operations** — Design for debugging and monitoring
8. **Plan for growth** — 10x user growth should be achievable without redesign

