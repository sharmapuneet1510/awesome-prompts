---
name: JIRA HTML Report Skill
version: 1.0
description: >
  Parse JIRA JSON or CSV exports and generate a single-file, self-contained HTML
  backlog report with filtering, sorting, summary stats, and row expansion. No
  external dependencies—all CSS and JavaScript inline.
---

# JIRA HTML Report Skill — v1.0

## Purpose

Transform local JIRA exports (JSON or CSV format) into an interactive, browser-ready HTML report. Single-file output, no server required, no external CDN dependencies.

---

## Input Specification

### Format 1: JSON (JIRA Cloud / Server Export)

**File:** `jira-export.json`

**Structure:**
```json
{
  "expand": "...",
  "startAt": 0,
  "maxResults": 50,
  "total": 156,
  "issues": [
    {
      "key": "PROJ-1",
      "fields": {
        "summary": "Add login feature",
        "issuetype": { "name": "Story" },
        "priority": { "name": "High" },
        "status": { "name": "In Progress" },
        "assignee": { "displayName": "Alice" },
        "description": "Implement OAuth2 login...",
        "created": "2026-05-15T10:30:00.000+0000",
        "updated": "2026-06-02T14:22:00.000+0000",
        "customfield_10027": "Sprint-5",
        "customfield_10020": 8
      }
    },
    ...
  ]
}
```

### Format 2: CSV (JIRA Filter Export)

**File:** `jira-export.csv`

**Headers (comma-separated, optional columns shown with asterisk):**
```
"Issue Key","Summary","Issue Type","Priority","Status","Assignee","Sprint*","Story Points*","Description*","Created*","Updated*","Labels*"
"PROJ-1","Add login feature","Story","High","In Progress","Alice","Sprint-5","8","Implement OAuth2...","2026-05-15","2026-06-02","auth,oauth2"
"PROJ-2","Fix NPE in auth","Bug","Critical","Open","Bob","","","Null pointer when...","2026-05-20","2026-06-02","auth,critical"
...
```

---

## Output Specification

**File:** `jira-report.html`

**Format:** Single HTML file (DOCTYPE, inline CSS, inline JavaScript)

**Size:** Typically 50-200KB (depending on issue count)

**Browser Support:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

---

## Parsing Logic

### Step 1: Detect Format

```python
def detect_format(file_path):
    with open(file_path, 'r') as f:
        first_bytes = f.read(100)
    
    if first_bytes.strip().startswith('{') or first_bytes.strip().startswith('['):
        return 'json'
    elif first_bytes.startswith('"Issue Key"') or first_bytes.startswith('Issue Key'):
        return 'csv'
    else:
        raise ValueError("Unknown format. Expected JSON or CSV.")
```

### Step 2: Parse Issues

#### For JSON:

```python
import json

def parse_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    issues = []
    for issue in data.get('issues', []):
        fields = issue.get('fields', {})
        issues.append({
            'key': issue.get('key'),
            'summary': fields.get('summary', ''),
            'type': fields.get('issuetype', {}).get('name', 'Unknown'),
            'priority': fields.get('priority', {}).get('name', 'Medium'),
            'status': fields.get('status', {}).get('name', 'Open'),
            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned'),
            'sprint': extract_sprint(fields),
            'story_points': fields.get('customfield_10020', 0) or 0,
            'description': fields.get('description', ''),
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'labels': fields.get('labels', []),
        })
    return issues

def extract_sprint(fields):
    # Sprint data is typically in customfield_10027 (Cloud) or customfield_10000 (Server)
    # Format: "com.atlassian.greenhopper.service.sprint.Sprint@abc123[id=5,rapidViewId=1,name=Sprint-5,...]"
    sprint_field = fields.get('customfield_10027') or fields.get('customfield_10000')
    if not sprint_field:
        return 'Backlog'
    
    if isinstance(sprint_field, str):
        # Extract name from "...name=Sprint-5,..." pattern
        import re
        match = re.search(r'name=([^,\]]+)', sprint_field)
        return match.group(1) if match else 'Backlog'
    return 'Backlog'
```

#### For CSV:

```python
import csv

def parse_csv(file_path):
    issues = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issues.append({
                'key': row.get('Issue Key', '').strip(),
                'summary': row.get('Summary', '').strip(),
                'type': row.get('Issue Type', 'Unknown').strip(),
                'priority': row.get('Priority', 'Medium').strip(),
                'status': row.get('Status', 'Open').strip(),
                'assignee': row.get('Assignee', 'Unassigned').strip() or 'Unassigned',
                'sprint': row.get('Sprint', 'Backlog').strip() or 'Backlog',
                'story_points': float(row.get('Story Points', 0) or 0),
                'description': row.get('Description', '').strip(),
                'created': row.get('Created', '').strip(),
                'updated': row.get('Updated', '').strip(),
                'labels': row.get('Labels', '').split(','),
            })
    return issues
```

### Step 3: Normalize Data

```python
def normalize_issues(issues):
    for issue in issues:
        # Ensure required fields
        issue['key'] = issue.get('key') or 'UNKNOWN'
        issue['summary'] = issue.get('summary') or '(no summary)'
        issue['type'] = issue.get('type') or 'Unknown'
        issue['priority'] = issue.get('priority') or 'Medium'
        issue['status'] = issue.get('status') or 'Open'
        issue['assignee'] = issue.get('assignee') or 'Unassigned'
        issue['sprint'] = issue.get('sprint') or 'Backlog'
        
        # Convert story points to int
        try:
            issue['story_points'] = int(float(issue.get('story_points', 0)))
        except (ValueError, TypeError):
            issue['story_points'] = 0
        
        # Escape HTML in text fields
        issue['summary'] = escape_html(issue['summary'])
        issue['description'] = escape_html(issue['description'])
    
    return issues

def escape_html(text):
    if not text:
        return ''
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
```

### Step 4: Calculate Statistics

```python
def calculate_stats(issues):
    stats = {
        'total': len(issues),
        'by_status': {},
        'by_priority': {},
        'by_type': {},
        'by_assignee': {},
        'by_sprint': {},
        'total_story_points': 0,
        'completed_story_points': 0,
    }
    
    for issue in issues:
        # Count by status
        status = issue['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Count by priority
        priority = issue['priority']
        stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Count by type
        type_name = issue['type']
        stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1
        
        # Count by assignee
        assignee = issue['assignee']
        stats['by_assignee'][assignee] = stats['by_assignee'].get(assignee, 0) + 1
        
        # Count by sprint
        sprint = issue['sprint']
        stats['by_sprint'][sprint] = stats['by_sprint'].get(sprint, 0) + 1
        
        # Sum story points
        stats['total_story_points'] += issue['story_points']
        if status == 'Done':
            stats['completed_story_points'] += issue['story_points']
    
    return stats
```

---

## HTML Generation

### Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JIRA Backlog Report</title>
    <style>
        /* All CSS inline, no external stylesheets */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 6px;
            backdrop-filter: blur(10px);
        }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .filter-group select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        thead {
            background: #f8f9fa;
            border-bottom: 2px solid #e0e0e0;
        }
        th {
            padding: 12px;
            text-align: left;
            cursor: pointer;
            user-select: none;
            font-weight: 600;
        }
        th:hover { background: #e8e9eb; }
        td { padding: 12px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f8f9fa; }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-open { background: #e3f2fd; color: #1976d2; }
        .status-in-progress { background: #fff3e0; color: #f57c00; }
        .status-done { background: #e8f5e9; color: #388e3c; }
        .status-blocked { background: #ffebee; color: #d32f2f; }
        .priority-critical { color: #d32f2f; }
        .priority-high { color: #f57c00; }
        .priority-medium { color: #fbc02d; }
        .priority-low { color: #388e3c; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header with Stats -->
        <div class="header">
            <h1>📊 JIRA Backlog Report</h1>
            <p>Generated: <time>2026-06-03 14:32:45 UTC</time></p>
            <div class="stats">
                <!-- Stats cards injected here -->
            </div>
        </div>
        
        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label>Status</label>
                <select id="statusFilter">
                    <option value="">All Statuses</option>
                </select>
            </div>
            <!-- More filters -->
        </div>
        
        <!-- Issues Table -->
        <table id="issuesTable">
            <thead>
                <tr>
                    <th onclick="sortTable('key')">Key ⇅</th>
                    <th onclick="sortTable('summary')">Summary ⇅</th>
                    <th onclick="sortTable('type')">Type ⇅</th>
                    <th onclick="sortTable('priority')">Priority ⇅</th>
                    <th onclick="sortTable('status')">Status ⇅</th>
                    <th onclick="sortTable('assignee')">Assignee ⇅</th>
                    <th onclick="sortTable('sprint')">Sprint ⇅</th>
                    <th onclick="sortTable('story_points')">Points ⇅</th>
                </tr>
            </thead>
            <tbody id="issuesBody">
                <!-- Rows injected here -->
            </tbody>
        </table>
    </div>
    
    <script>
        // All JavaScript inline for self-contained single file
        const allIssues = [/* injected */];
        let filteredIssues = allIssues;
        
        function filterTable() {
            // Apply all active filters
        }
        
        function sortTable(field) {
            // Sort by field ascending/descending
        }
        
        function renderTable() {
            // Render filtered + sorted issues
        }
        
        // Initialize on page load
        window.addEventListener('DOMContentLoaded', () => {
            renderTable();
        });
    </script>
</body>
</html>
```

### Rendering

1. **Inject issues data** as JSON into `<script>const allIssues = [...];</script>`
2. **Generate table rows** from issues array
3. **Apply color coding** based on status, priority, type
4. **Attach event listeners** for filtering and sorting
5. **Generate stats header** with summary counts

---

## Color Scheme

| Status | Background | Text | Example |
|--------|-----------|------|---------|
| Open | `#e3f2fd` | `#1976d2` | <span style="background: #e3f2fd; color: #1976d2">● Open</span> |
| In Progress | `#fff3e0` | `#f57c00` | <span style="background: #fff3e0; color: #f57c00">● In Progress</span> |
| Done | `#e8f5e9` | `#388e3c` | <span style="background: #e8f5e9; color: #388e3c">● Done</span> |
| Blocked | `#ffebee` | `#d32f2f` | <span style="background: #ffebee; color: #d32f2f">● Blocked</span> |

| Priority | Icon | Color |
|----------|------|-------|
| Critical | 🔴 | `#d32f2f` (red) |
| High | 🟠 | `#f57c00` (orange) |
| Medium | 🟡 | `#fbc02d` (yellow) |
| Low | 🟢 | `#388e3c` (green) |

---

## Example Output

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JIRA Backlog Report</title>
    <style>
        /* ... CSS inline ... */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 JIRA Backlog Report</h1>
            <p>Generated: 2026-06-03 14:32:45 UTC</p>
            <div class="stats">
                <div class="stat-card">
                    <strong>156</strong> Total Issues
                </div>
                <div class="stat-card">
                    <strong>42</strong> Open / In Progress
                </div>
                <div class="stat-card">
                    <strong>114</strong> Done
                </div>
                <div class="stat-card">
                    <strong>1,240</strong> Total Story Points
                </div>
            </div>
        </div>
        
        <div class="filters">
            <!-- Filter inputs -->
        </div>
        
        <table>
            <!-- Issue rows -->
        </table>
    </div>
    
    <script>
        const allIssues = [
            { key: "PROJ-1", summary: "Add login feature", ... },
            { key: "PROJ-2", summary: "Fix NPE in auth", ... },
            ...
        ];
        // Filtering and sorting logic
    </script>
</body>
</html>
```

---

## Acceptance Criteria

✓ Auto-detect JSON vs CSV format  
✓ Parse all issue fields (key, summary, type, priority, status, assignee, sprint, story_points)  
✓ Generate single HTML file (no external dependencies)  
✓ Stats header shows correct counts and percentages  
✓ Filters work (status, priority, assignee, sprint, type)  
✓ Table is sortable by all columns  
✓ Color coding applied correctly  
✓ Renders in all modern browsers  
✓ No console errors  
✓ Handles edge cases (missing fields, empty descriptions, special characters)  
