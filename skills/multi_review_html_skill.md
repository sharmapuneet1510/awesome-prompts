---
name: Multi-Review HTML Skill
version: 1.0
description: >
  Generate self-contained HTML reports for batch PR reviews with fixed left sidebar tabs,
  summary dashboard, and per-PR detailed review panels. All CSS/JS inline, zero external dependencies.
  Supports tabbed navigation, filtering, and PDF/JSON export.
---

# Multi-Review HTML Skill — v1.0

## Purpose

Generate a single self-contained HTML file that displays batch code reviews with:
- Fixed left sidebar with tab navigation (Summary + per-PR tabs)
- Verdict badges and score indicators per tab
- Summary dashboard with aggregate stats, priority matrix, score comparison
- Per-PR review panels with full context, AC coverage, issues, before/after code
- Export options (JSON, Print/PDF)

## Technical Spec

### Technology Stack
- **Language:** HTML5 + CSS3 + Vanilla JavaScript (ES6)
- **Dependencies:** ZERO (no CDN, no external libraries)
- **File size:** Self-contained in single HTML file
- **Compatibility:** All modern browsers (Chrome, Firefox, Safari, Edge 2022+)

### Page Structure

```html
<!DOCTYPE html>
<html>
  <head>
    <style>/* ALL CSS INLINE */</style>
  </head>
  <body>
    <header><!-- Header section --></header>
    <main>
      <aside><!-- Sidebar with tabs --></aside>
      <section><!-- Content panels --></section>
    </main>
    <script>/* ALL JS INLINE */</script>
  </body>
</html>
```

## Layout Design

### Header Section

```html
<header class="header">
  <div class="header-content">
    <h1>Quality Review — Batch PR Assessment</h1>
    <div class="header-meta">
      <span>Generated: 2026-06-04 14:32:45 UTC</span>
      <span>Reviews: 3 PRs</span>
    </div>
  </div>
</header>
```

**Styling:**
- Background: Linear gradient `#667eea → #764ba2`
- Text color: White
- Padding: 1.5rem
- Font size: 1.5rem for title, 0.875rem for meta

### Sidebar Navigation (Fixed Left Panel)

```html
<aside class="sidebar">
  <div class="sidebar-header">
    <h2>Reviews</h2>
  </div>
  
  <div class="tabs">
    <!-- Summary tab -->
    <button class="sidebar-tab active" id="tab-summary" onclick="showTab('summary')">
      <div class="tab-icon">📊</div>
      <div class="tab-label">Summary</div>
    </button>
    
    <!-- Per-PR tabs -->
    <button class="sidebar-tab" id="tab-pr-456" onclick="showTab('pr-456')">
      <div class="tab-verdict">🔴</div>
      <div class="tab-details">
        <div class="tab-pr">PR#456</div>
        <div class="tab-ticket">PROJ-123</div>
        <div class="tab-score">74% · C+</div>
        <div class="tab-blockers">3 blockers</div>
      </div>
    </button>
    
    <!-- More PR tabs... -->
  </div>
  
  <div class="sidebar-footer">
    <button class="export-btn" onclick="exportJSON()">📥 Export JSON</button>
    <button class="print-btn" onclick="window.print()">🖨️ Print/PDF</button>
  </div>
</aside>
```

**Styling:**
- Width: 280px
- Position: fixed
- Height: 100vh (full viewport)
- Overflow-y: auto
- Background: #f8f9fa
- Border-right: 1px solid #e0e0e0

**Tab styling:**
- Padding: 1rem
- Border-left: 4px solid transparent
- Background: white
- Cursor: pointer
- Border-left changes to #667eea on hover/active

### Content Panel (Main Area)

```html
<section class="content">
  <!-- Summary panel -->
  <div class="tab-panel active" id="panel-summary">
    <h2>Summary Dashboard</h2>
    <!-- Aggregate stats, priority matrix, etc. -->
  </div>
  
  <!-- Per-PR panels -->
  <div class="tab-panel" id="panel-pr-456">
    <h2>PR#456 (PROJ-123) Review</h2>
    <!-- Full review content -->
  </div>
  
  <!-- More panels... -->
</section>
```

**Styling:**
- Flex: 1
- Overflow-y: auto
- Padding: 2rem
- Max-width: 1200px

### Flexbox Layout

```css
body {
  display: flex;
  flex-direction: column;
  height: 100vh;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

header {
  flex: 0 0 auto;
}

main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  flex: 0 0 280px;
}

.content {
  flex: 1;
}
```

## Summary Tab Content

### Stats Cards (4-column grid)

```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-label">Total Reviews</div>
    <div class="stat-value">3</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Blockers Found</div>
    <div class="stat-value">5</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Avg Score</div>
    <div class="stat-value">78%</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total Fix Time</div>
    <div class="stat-value">6 hrs</div>
  </div>
</div>
```

**Styling:**
- CSS Grid: `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`
- Background: #f5f5f5
- Border-radius: 8px
- Padding: 1.5rem
- Box-shadow: 0 1px 3px rgba(0,0,0,0.1)

### Merged Verdict Banner

```html
<div class="verdict-banner verdict-stop">
  <div class="verdict-icon">🔴</div>
  <div class="verdict-text">
    <strong>STOP — 1 of 3 PRs has blockers</strong>
    <p>PR#456 (PROJ-123) must be resolved first</p>
  </div>
</div>
```

**Verdict levels:**
- `verdict-stop` (🔴): Red background, any PR has blockers
- `verdict-caution` (⚠️): Yellow background, warnings but no blockers
- `verdict-proceed` (✅): Green background, all clean

### Priority Matrix Table

```html
<table class="priority-matrix">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Affected PRs</th>
    </tr>
  </thead>
  <tbody>
    <tr class="severity-p0">
      <td>🔴 P0</td>
      <td>2</td>
      <td>PR#456, PR#789</td>
    </tr>
    <tr class="severity-p1">
      <td>🟠 P1</td>
      <td>3</td>
      <td>PR#456 (x2), PR#789</td>
    </tr>
    <!-- More rows... -->
  </tbody>
</table>
```

### Score Comparison Table

```html
<table class="score-table sortable">
  <thead>
    <tr>
      <th onclick="sortTable(this)">PR</th>
      <th onclick="sortTable(this)">Ticket</th>
      <th onclick="sortTable(this)">Requirements</th>
      <th onclick="sortTable(this)">Quality</th>
      <th onclick="sortTable(this)">Security</th>
      <th onclick="sortTable(this)">Tests</th>
      <th onclick="sortTable(this)">Overall</th>
      <th onclick="sortTable(this)">Verdict</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>PR#910</td>
      <td>PROJ-125</td>
      <td>95%</td>
      <td>88%</td>
      <td>90%</td>
      <td>85%</td>
      <td><strong>90%</strong> <span class="grade">B+</span></td>
      <td><span class="verdict-approve">✅ APPROVE</span></td>
    </tr>
    <!-- More rows... -->
  </tbody>
</table>
```

**Sorting:**
- Click any column header to sort ascending/descending
- Arrow indicator shows sort direction (↑/↓)

### Top 5 Worst Issues

```html
<div class="worst-issues">
  <h3>Top 5 Worst Issues Across All PRs</h3>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>PR</th>
        <th>Severity</th>
        <th>Title</th>
        <th>Fix Time</th>
      </tr>
    </thead>
    <tbody>
      <tr class="severity-p0">
        <td>1</td>
        <td>PR#456</td>
        <td>🔴 P0</td>
        <td>Hardcoded OAuth2 secret</td>
        <td>30 min</td>
      </tr>
      <!-- More rows... -->
    </tbody>
  </table>
</div>
```

## Per-PR Tab Content

### Review Context Header

```html
<div class="review-context">
  <h3>Review Context</h3>
  <dl>
    <dt>Ticket</dt>
    <dd>PROJ-123 (auto-detected)</dd>
    <dt>Context</dt>
    <dd>OAuth2 security hardening for enterprise customers</dd>
    <dt>Business Justification</dt>
    <dd>SOC 2 compliance required by Q3</dd>
    <dt>Review Scope</dt>
    <dd>Authentication layer only (skip frontend)</dd>
    <dt>Success Criteria</dt>
    <dd>No unvalidated redirects, all inputs sanitized</dd>
  </dl>
</div>
```

### What Was Implemented Section

```html
<section class="phase-section">
  <h3>✅ What Was Implemented (Coverage: 85%)</h3>
  <table class="ac-table">
    <thead>
      <tr>
        <th>AC#</th>
        <th>Description</th>
        <th>Status</th>
        <th>Coverage</th>
        <th>Implementation</th>
        <th>File:Line</th>
      </tr>
    </thead>
    <tbody>
      <tr class="status-pass">
        <td>AC#1</td>
        <td>OAuth2 login flow</td>
        <td>✅ PASS</td>
        <td>100%</td>
        <td>OAuthController.login()</td>
        <td>src/auth/oauth.py:45</td>
      </tr>
      <!-- More rows... -->
    </tbody>
  </table>
</section>
```

### Issues Found Section

```html
<section class="issues-section">
  <h3>🐛 Issues Found (3 Critical)</h3>
  
  <div class="issue" id="issue-1" class="severity-p0">
    <div class="issue-header">
      <span class="issue-number">Issue #1</span>
      <span class="issue-title">Hardcoded OAuth2 secret in config</span>
      <span class="severity-badge severity-p0">🔴 P0-CRITICAL</span>
      <span class="blocker-badge">🚨 Blocks Merge</span>
    </div>
    
    <div class="issue-details">
      <p><strong>File:</strong> src/auth/oauth.py (line 95)</p>
      <p><strong>Problem:</strong> OAuth2 client secret hardcoded as string literal. Exposed in version control and all production deployments.</p>
      <p><strong>Why it matters:</strong> Anyone with repo access can impersonate the OAuth2 client, hijack user sessions, and gain full account access.</p>
      <p><strong>Fix time:</strong> 30 minutes</p>
    </div>
    
    <div class="code-diff">
      <div class="code-before">
        <h4>Before (Broken)</h4>
        <pre><code class="language-python">def get_oauth_secret():
    return "super-secret-key-12345"  # HARDCODED!</code></pre>
      </div>
      
      <div class="code-after">
        <h4>After (Fixed)</h4>
        <pre><code class="language-python">def get_oauth_secret():
    return os.environ.get("OAUTH_SECRET")
    # Load from secure vault at runtime</code></pre>
      </div>
    </div>
  </div>
  
  <!-- More issues... -->
</section>
```

**Issue styling:**
- `.severity-p0` → red border-left
- `.severity-p1` → orange border-left
- `.severity-p2` → yellow border-left
- `.severity-p3` → blue border-left

### Scorecard + Verdict

```html
<section class="scorecard-section">
  <h3>📊 Scorecard</h3>
  
  <table class="scorecard">
    <tbody>
      <tr class="category">
        <td>Requirements</td>
        <td class="score">85%</td>
        <td class="grade grade-b">B</td>
        <td class="notes">1 AC missing (rate limiting)</td>
      </tr>
      <tr class="category">
        <td>Code Quality</td>
        <td class="score">72%</td>
        <td class="grade grade-c-plus">C+</td>
        <td class="notes">3 P1 issues (1 hardcoded secret)</td>
      </tr>
      <tr class="category">
        <td>Security</td>
        <td class="score">60%</td>
        <td class="grade grade-d">D</td>
        <td class="notes">2 critical vulnerabilities</td>
      </tr>
      <tr class="category">
        <td>Test Coverage</td>
        <td class="score">88%</td>
        <td class="grade grade-b-plus">B+</td>
        <td class="notes">Missing error path tests</td>
      </tr>
      <tr class="category">
        <td>Documentation</td>
        <td class="score">95%</td>
        <td class="grade grade-a">A</td>
        <td class="notes">Excellent inline docs</td>
      </tr>
      <tr class="overall">
        <td><strong>OVERALL</strong></td>
        <td class="score"><strong>74%</strong></td>
        <td class="grade grade-c-plus"><strong>C+</strong></td>
        <td></td>
      </tr>
    </tbody>
  </table>
  
  <div class="verdict-box verdict-request-changes">
    <div class="verdict-icon">🔴</div>
    <div class="verdict-content">
      <h4>Verdict: REQUEST CHANGES</h4>
      <p><strong>Blockers:</strong> 3 issues must be fixed before merge (2–3 hours total)</p>
      <p><strong>Non-blocking:</strong> 2 improvements recommended (nice-to-have)</p>
    </div>
  </div>
</section>
```

### Blockers + Non-Blocking Lists

```html
<section class="blockers-section">
  <div class="blockers-list">
    <h3>🚨 Blockers (Must Fix)</h3>
    <ol>
      <li><strong>Hardcoded OAuth2 secret</strong> — src/auth/oauth.py:95 — 30 min</li>
      <li><strong>MD5 token generation</strong> — src/auth/token.py:120 — 15 min</li>
      <li><strong>Missing rate limiting on login</strong> — src/api/handlers.py:45 — 2 hrs</li>
    </ol>
  </div>
  
  <div class="non-blockers-list">
    <h3>💡 Non-Blocking (Nice-to-Have)</h3>
    <ol>
      <li><strong>Add docstring to OAuthController</strong> — P3</li>
      <li><strong>Extract magic string into constant</strong> — P3</li>
    </ol>
  </div>
</section>
```

## JavaScript Functions

### Tab Switching

```javascript
function showTab(tabId) {
  // Hide all panels
  document.querySelectorAll('.tab-panel').forEach(p => {
    p.classList.remove('active');
  });
  
  // Deactivate all sidebar tabs
  document.querySelectorAll('.sidebar-tab').forEach(t => {
    t.classList.remove('active');
  });
  
  // Show active panel
  document.getElementById('panel-' + tabId).classList.add('active');
  document.getElementById('tab-' + tabId).classList.add('active');
  
  // Scroll to top
  window.scrollTo(0, 0);
}
```

### Table Sorting

```javascript
function sortTable(headerCell) {
  const table = headerCell.closest('table');
  const colIndex = Array.from(headerCell.parentNode.children).indexOf(headerCell);
  const rows = Array.from(table.querySelectorAll('tbody tr'));
  
  const isAscending = headerCell.classList.toggle('sort-asc');
  headerCell.classList.toggle('sort-desc');
  
  rows.sort((a, b) => {
    const aVal = a.cells[colIndex].textContent.trim();
    const bVal = b.cells[colIndex].textContent.trim();
    
    // Try numeric sort if both are numbers
    const aNum = parseFloat(aVal);
    const bNum = parseFloat(bVal);
    
    if (!isNaN(aNum) && !isNaN(bNum)) {
      return isAscending ? aNum - bNum : bNum - aNum;
    }
    
    // Fall back to string sort
    return isAscending 
      ? aVal.localeCompare(bVal)
      : bVal.localeCompare(aVal);
  });
  
  rows.forEach(row => table.querySelector('tbody').appendChild(row));
}
```

### Export JSON

```javascript
function exportJSON() {
  const data = {
    generated_at: new Date().toISOString(),
    reviews: reviewData,  // Injected from server
    summary: summaryData  // Injected from server
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `quality-batch-review-${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  URL.revokeObjectURL(url);
}
```

## CSS Classes Reference

### Colors & Severity

```css
.severity-p0 { border-left-color: #dc3545; }  /* Red */
.severity-p1 { border-left-color: #fd7e14; }  /* Orange */
.severity-p2 { border-left-color: #ffc107; }  /* Yellow */
.severity-p3 { border-left-color: #0d6efd; }  /* Blue */

.verdict-approve { color: #198754; }        /* Green */
.verdict-caution { color: #ffc107; }        /* Yellow */
.verdict-stop { color: #dc3545; }           /* Red */

.code-before { background-color: #fff0f0; } /* Light red */
.code-after { background-color: #f0fff0; }  /* Light green */
```

### Grade Letters

```css
.grade-a { background: #198754; color: white; }        /* A */
.grade-b-plus { background: #20c997; color: white; }   /* B+ */
.grade-b { background: #0d6efd; color: white; }        /* B */
.grade-c-plus { background: #ffc107; color: #000; }    /* C+ */
.grade-d { background: #dc3545; color: white; }        /* D */
.grade-f { background: #6f42c1; color: white; }        /* F */
```

## Print Media Query

```css
@media print {
  .sidebar {
    display: none;  /* Hide sidebar when printing */
  }
  
  .content {
    flex: 1;
    max-width: 100%;
  }
  
  .export-btn, .print-btn {
    display: none;
  }
  
  body {
    background: white;
  }
  
  .page-break {
    page-break-before: always;
  }
}
```

## Data Injection Format

The HTML expects two JavaScript objects injected before the main script:

```html
<script>
  const reviewData = [
    {
      pr: 456,
      ticket: "PROJ-123",
      verdict: "REQUEST_CHANGES",
      score: 74,
      grade: "C+",
      blockers_count: 3,
      non_blockers_count: 2,
      context: {...},
      ac_coverage: [...],
      issues: [...]
    },
    // ... more reviews
  ];
  
  const summaryData = {
    total_reviews: 3,
    total_blockers: 5,
    avg_score: 78,
    total_fix_hours: 6,
    merged_verdict: "STOP",
    priority_matrix: {...},
    score_comparison: [...],
    worst_issues: [...]
  };
</script>
```

## Acceptance Criteria

✓ HTML is single self-contained file (no external CDN or asset references)  
✓ Sidebar is fixed (280px width) and sticky while scrolling content  
✓ Summary tab shows aggregate stats, priority matrix, score comparison, worst issues  
✓ Per-PR tabs show full review context, AC coverage, issues with before/after code, scorecard  
✓ Verdict icons (🔴/⚠️/✅) displayed on each PR tab  
✓ Tab switching via JavaScript (no page reload)  
✓ Score comparison table is sortable (click column headers)  
✓ Code before/after blocks have distinct styling (red/green background)  
✓ Export JSON button downloads current batch review as JSON file  
✓ Print (Cmd+P) renders correctly with sidebar hidden, full-width content  
✓ Renders correctly in all modern browsers (Chrome, Firefox, Safari, Edge)  
✓ All CSS and JavaScript are inline (no external files)  
✓ No console errors or broken references

---

**Last Updated:** June 4, 2026 | **Version:** 1.0.0 | **Compatibility:** HTML5 + ES6
