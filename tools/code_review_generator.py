#!/usr/bin/env python3
"""
code_review_generator.py — Interactive HTML report generator for code reviews.

Generates self-contained HTML reports from Code Review Agent output with:
- Visual scorecard (4 metrics + final grade)
- Requirement analysis (feature description + acceptance criteria)
- Issues grouped by severity (P0, P1, P2, P3)
- File-by-file breakdown with heatmap
- Top 5 actionable suggestions ranked by impact
- Responsive design, collapsible sections, embedded CSS/JS

No external dependencies. All JS/CSS inlined. Works offline.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReviewReportGenerator:
    """Generates interactive HTML code review reports."""

    # Severity level display configuration
    SEVERITY_COLORS = {
        "P0": "#dc2626",  # red-600
        "P1": "#ea580c",  # orange-600
        "P2": "#eab308",  # yellow-500
        "P3": "#60a5fa",  # blue-400
    }

    SEVERITY_LABELS = {
        "P0": "Critical",
        "P1": "High",
        "P2": "Medium",
        "P3": "Low",
    }

    def __init__(self, output_dir: str = "docs/reviews"):
        """Initialize the report generator.

        Args:
            output_dir: Directory where HTML reports will be saved.
                       Created if doesn't exist.

        Raises:
            OSError: If directory cannot be created.
        """
        self.output_dir = Path(output_dir)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create output directory {output_dir}: {e}")

    def generate(self, review_data: Dict[str, Any], jira_key: str) -> str:
        """Generate HTML report from review data.

        Args:
            review_data: Complete review result dict with structure:
                {
                    "requirement_analysis": {...},
                    "scorecard": {...},
                    "issues": [...],
                    "file_breakdown": {...},
                    "suggestions": [...]
                }
            jira_key: JIRA ticket number (e.g., "PROJ-123")

        Returns:
            str: Full path to generated HTML file

        Raises:
            ValueError: If required fields missing in review_data
            IOError: If file cannot be written
        """
        # Validate required fields
        required_fields = ["scorecard", "issues"]
        missing = [f for f in required_fields if f not in review_data]
        if missing:
            raise ValueError(f"Missing required fields in review_data: {missing}")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"review-{jira_key}-{timestamp}.html"
        filepath = self.output_dir / filename

        # Build HTML content
        html_content = self._build_html(review_data, jira_key)

        # Write to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
        except IOError as e:
            raise IOError(f"Failed to write report to {filepath}: {e}")

        return str(filepath.absolute())

    def _build_html(self, review_data: Dict[str, Any], jira_key: str) -> str:
        """Build complete self-contained HTML document.

        Args:
            review_data: Review result dictionary
            jira_key: JIRA ticket key

        Returns:
            str: Complete HTML document as string
        """
        scorecard = review_data.get("scorecard", {})
        issues = review_data.get("issues", [])
        file_breakdown = review_data.get("file_breakdown", {})
        suggestions = review_data.get("suggestions", [])
        requirement_analysis = review_data.get("requirement_analysis", {})

        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "  <meta charset='UTF-8'>",
            "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"  <title>Code Review - {jira_key}</title>",
            "  <style>",
            self._get_css(),
            "  </style>",
            "</head>",
            "<body>",
            self._build_header(jira_key),
            self._build_scorecard_section(scorecard),
            self._build_requirement_section(requirement_analysis),
            self._build_issues_section(issues),
            self._build_files_section(file_breakdown),
            self._build_severity_heatmap_section(file_breakdown, issues),
            self._build_suggestions_section(suggestions, issues),
            self._build_footer(),
            "  <script>",
            self._get_javascript(),
            "  </script>",
            "</body>",
            "</html>",
        ]

        return "\n".join(html_parts)

    def _build_header(self, jira_key: str) -> str:
        """Build report header section.

        Args:
            jira_key: JIRA ticket key

        Returns:
            str: HTML header markup
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
  <header class="header">
    <div class="header-content">
      <h1>Code Review Report</h1>
      <div class="header-meta">
        <span class="jira-key">{jira_key}</span>
        <span class="timestamp">Generated: {timestamp}</span>
      </div>
    </div>
  </header>
"""

    def _build_scorecard_section(self, scorecard: Dict[str, Any]) -> str:
        """Build visual scorecard with 4 metrics and final grade.

        Args:
            scorecard: Dict with keys: requirement, code_quality, testing, documentation, final_grade

        Returns:
            str: HTML scorecard markup with progress bars and grade badge
        """
        requirement = scorecard.get("requirement", 0)
        code_quality = scorecard.get("code_quality", 0)
        testing = scorecard.get("testing", 0)
        documentation = scorecard.get("documentation", 0)
        final_grade = scorecard.get("final_grade", "N/A")

        # Grade color mapping
        grade_colors = {
            "A": "#16a34a",  # green
            "B": "#2563eb",  # blue
            "C": "#ea580c",  # orange
            "D": "#dc2626",  # red
            "F": "#7c2d12",  # dark red
        }
        grade_color = grade_colors.get(final_grade, "#6b7280")

        return f"""
  <section class="section scorecard-section">
    <h2>📊 Scorecard</h2>
    <div class="scorecard">
      <div class="metrics-grid">
        <div class="metric">
          <label>Requirement Match</label>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {requirement}%; background-color: #3b82f6;"></div>
          </div>
          <span class="metric-value">{requirement}%</span>
        </div>
        <div class="metric">
          <label>Code Quality</label>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {code_quality}%; background-color: #8b5cf6;"></div>
          </div>
          <span class="metric-value">{code_quality}%</span>
        </div>
        <div class="metric">
          <label>Testing</label>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {testing}%; background-color: #06b6d4;"></div>
          </div>
          <span class="metric-value">{testing}%</span>
        </div>
        <div class="metric">
          <label>Documentation</label>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {documentation}%; background-color: #f59e0b;"></div>
          </div>
          <span class="metric-value">{documentation}%</span>
        </div>
      </div>
      <div class="grade-badge" style="background-color: {grade_color};">
        <span class="grade-letter">{final_grade}</span>
        <span class="grade-label">Final Grade</span>
      </div>
    </div>
  </section>
"""

    def _build_requirement_section(self, analysis: Dict[str, Any]) -> str:
        """Build requirement analysis section.

        Args:
            analysis: Dict with keys: feature_description, acceptance_criteria

        Returns:
            str: HTML requirement markup
        """
        feature_desc = analysis.get("feature_description", "No description provided.")
        acceptance_criteria = analysis.get("acceptance_criteria", [])

        criteria_html = ""
        if acceptance_criteria:
            criteria_html = "<ul class='criteria-list'>"
            for criterion in acceptance_criteria:
                criteria_html += f"<li>{criterion}</li>"
            criteria_html += "</ul>"

        return f"""
  <section class="section requirement-section">
    <h2>✅ Requirement Analysis</h2>
    <div class="card">
      <h3>Feature Description</h3>
      <p>{feature_desc}</p>
      <h3>Acceptance Criteria</h3>
      {criteria_html if criteria_html else "<p><em>No acceptance criteria defined.</em></p>"}
    </div>
  </section>
"""

    def _build_issues_section(self, issues: List[Dict[str, Any]]) -> str:
        """Build issues section grouped by severity.

        Args:
            issues: List of issue dicts with keys:
                   category, severity, file, line, description, impact, suggested_fix

        Returns:
            str: HTML issues markup with collapsible per-issue details
        """
        # Group issues by severity
        by_severity = {"P0": [], "P1": [], "P2": [], "P3": []}
        for issue in issues:
            severity = issue.get("severity", "P3")
            if severity in by_severity:
                by_severity[severity].append(issue)

        issues_html = ""
        for severity in ["P0", "P1", "P2", "P3"]:
            severity_issues = by_severity[severity]
            if not severity_issues:
                continue

            color = self.SEVERITY_COLORS[severity]
            label = self.SEVERITY_LABELS[severity]
            count = len(severity_issues)

            issues_html += f"""
    <div class="severity-group">
      <h3 class="severity-header" style="border-left: 4px solid {color};">
        <span class="severity-badge" style="background-color: {color};">{severity}</span>
        {label} ({count})
      </h3>
      <div class="issues-list">
"""
            for idx, issue in enumerate(severity_issues):
                issue_id = f"{severity}-issue-{idx}"
                category = issue.get("category", "General")
                file_path = issue.get("file", "unknown")
                line = issue.get("line", "")
                description = issue.get("description", "No description")
                impact = issue.get("impact", "")
                fix = issue.get("suggested_fix", "")

                line_info = f" (line {line})" if line else ""

                issues_html += f"""
        <div class="issue-card">
          <div class="issue-header" onclick="toggleIssue('{issue_id}')">
            <span class="issue-category">{category}</span>
            <span class="issue-file">{file_path}{line_info}</span>
            <span class="toggle-icon">►</span>
          </div>
          <div class="issue-details" id="{issue_id}" style="display: none;">
            <p><strong>Issue:</strong> {description}</p>
"""
                if impact:
                    issues_html += f"<p><strong>Why it matters:</strong> {impact}</p>"
                if fix:
                    issues_html += f"<p><strong>Suggested fix:</strong></p><pre>{self._escape_html(fix)}</pre>"

                issues_html += "          </div>\n        </div>\n"

            issues_html += "      </div>\n    </div>\n"

        if not issues_html:
            issues_html = "<p><em>No issues found.</em></p>"

        return f"""
  <section class="section issues-section">
    <h2>🐛 Issues by Severity</h2>
    <div class="issues-container">
{issues_html}
    </div>
  </section>
"""

    def _build_files_section(self, file_breakdown: Dict[str, Any]) -> str:
        """Build file-by-file breakdown section.

        Args:
            file_breakdown: Dict with file paths as keys, each containing:
                          lines_added, issues_count, coverage_percent

        Returns:
            str: HTML files markup with sortable table
        """
        if not file_breakdown:
            return """
  <section class="section files-section">
    <h2>📁 File-by-File Breakdown</h2>
    <p><em>No file data available.</em></p>
  </section>
"""

        files_rows = ""
        for file_path, data in sorted(file_breakdown.items()):
            lines = data.get("lines_added", 0)
            issues = data.get("issues_count", 0)
            coverage = data.get("coverage_percent", 0)

            # Color code coverage
            if coverage >= 80:
                coverage_color = "#16a34a"  # green
            elif coverage >= 60:
                coverage_color = "#f59e0b"  # amber
            else:
                coverage_color = "#dc2626"  # red

            files_rows += f"""
      <tr>
        <td class="file-name">{file_path}</td>
        <td class="numeric">{lines}</td>
        <td class="numeric">{issues}</td>
        <td>
          <div class="coverage-bar">
            <div class="coverage-fill" style="width: {coverage}%; background-color: {coverage_color};"></div>
          </div>
          <span class="coverage-percent">{coverage}%</span>
        </td>
      </tr>
"""

        return f"""
  <section class="section files-section">
    <h2>📁 File-by-File Breakdown</h2>
    <table class="files-table">
      <thead>
        <tr>
          <th>File</th>
          <th>Lines Added</th>
          <th>Issues</th>
          <th>Coverage</th>
        </tr>
      </thead>
      <tbody>
{files_rows}
      </tbody>
    </table>
  </section>
"""

    def _build_severity_heatmap_section(
        self, file_breakdown: Dict[str, Any], issues: List[Dict[str, Any]]
    ) -> str:
        """Build severity heatmap visualization.

        Args:
            file_breakdown: File breakdown data
            issues: List of issues

        Returns:
            str: HTML heatmap markup
        """
        # Count issues per file by severity
        severity_per_file = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            severity = issue.get("severity", "P3")
            if file_path not in severity_per_file:
                severity_per_file[file_path] = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
            severity_per_file[file_path][severity] += 1

        if not severity_per_file:
            return """
  <section class="section heatmap-section">
    <h2>🔥 Severity Heatmap</h2>
    <p><em>No issues to display in heatmap.</em></p>
  </section>
"""

        heatmap_rows = ""
        for file_path in sorted(severity_per_file.keys()):
            counts = severity_per_file[file_path]
            heatmap_rows += f"""
      <tr>
        <td class="file-name">{file_path}</td>
        <td><span class="severity-count p0">{counts['P0']}</span></td>
        <td><span class="severity-count p1">{counts['P1']}</span></td>
        <td><span class="severity-count p2">{counts['P2']}</span></td>
        <td><span class="severity-count p3">{counts['P3']}</span></td>
      </tr>
"""

        return f"""
  <section class="section heatmap-section">
    <h2>🔥 Severity Heatmap</h2>
    <table class="heatmap-table">
      <thead>
        <tr>
          <th>File</th>
          <th style="background-color: {self.SEVERITY_COLORS['P0']};">P0</th>
          <th style="background-color: {self.SEVERITY_COLORS['P1']};">P1</th>
          <th style="background-color: {self.SEVERITY_COLORS['P2']};">P2</th>
          <th style="background-color: {self.SEVERITY_COLORS['P3']};">P3</th>
        </tr>
      </thead>
      <tbody>
{heatmap_rows}
      </tbody>
    </table>
  </section>
"""

    def _build_suggestions_section(
        self, suggestions: List[Dict[str, Any]], issues: List[Dict[str, Any]]
    ) -> str:
        """Build top suggestions section ranked by impact.

        Args:
            suggestions: List of suggestion dicts with keys:
                        title, impact, code_example
            issues: List of issues for fallback suggestion generation

        Returns:
            str: HTML suggestions markup with code examples
        """
        # Use provided suggestions, or generate from top issues
        display_suggestions = suggestions if suggestions else self._generate_suggestions_from_issues(issues)

        # Limit to top 5
        display_suggestions = display_suggestions[:5]

        suggestions_html = ""
        for idx, sugg in enumerate(display_suggestions, 1):
            title = sugg.get("title", "Improvement")
            impact = sugg.get("impact", "")
            code_example = sugg.get("code_example", "")

            impact_html = f"<p><strong>Impact:</strong> {impact}</p>" if impact else ""
            code_html = f"<pre class='suggestion-code'>{self._escape_html(code_example)}</pre>" if code_example else ""

            suggestions_html += f"""
      <div class="suggestion-card">
        <div class="suggestion-rank">#{idx}</div>
        <div class="suggestion-content">
          <h4>{title}</h4>
          {impact_html}
          {code_html}
        </div>
      </div>
"""

        return f"""
  <section class="section suggestions-section">
    <h2>💡 Top Suggestions</h2>
    <div class="suggestions-container">
{suggestions_html}
    </div>
  </section>
"""

    def _generate_suggestions_from_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate suggestions from issues if not provided.

        Args:
            issues: List of issues

        Returns:
            List of suggestion dicts
        """
        suggestions = []
        for issue in issues[:5]:
            suggestions.append({
                "title": issue.get("category", "Improvement"),
                "impact": issue.get("impact", ""),
                "code_example": issue.get("suggested_fix", ""),
            })
        return suggestions

    def _build_footer(self) -> str:
        """Build report footer.

        Returns:
            str: HTML footer markup
        """
        return """
  <footer class="footer">
    <p>Generated by Code Review Agent v3 | Interactive HTML Report</p>
  </footer>
"""

    def _get_css(self) -> str:
        """Return embedded CSS styles.

        Returns:
            str: Complete CSS stylesheet
        """
        return """
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
          'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #1f2937;
        line-height: 1.6;
        min-height: 100vh;
        padding: 20px;
      }

      header.header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        margin-bottom: 30px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      }

      .header-content {
        max-width: 1200px;
        margin: 0 auto;
      }

      header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
      }

      .header-meta {
        display: flex;
        gap: 20px;
        font-size: 0.95em;
        opacity: 0.9;
      }

      .jira-key {
        font-weight: bold;
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 10px;
        border-radius: 4px;
      }

      .section {
        max-width: 1200px;
        margin: 30px auto;
        background: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      }

      .section h2 {
        font-size: 1.8em;
        margin-bottom: 20px;
        color: #1f2937;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
      }

      /* Scorecard Section */
      .scorecard-section .scorecard {
        display: flex;
        gap: 30px;
        align-items: center;
      }

      .metrics-grid {
        flex: 1;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
      }

      .metric {
        background: #f9fafb;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #667eea;
      }

      .metric label {
        display: block;
        font-weight: 600;
        margin-bottom: 8px;
        font-size: 0.9em;
        color: #4b5563;
      }

      .progress-bar {
        width: 100%;
        height: 8px;
        background: #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 8px;
      }

      .progress-fill {
        height: 100%;
        transition: width 0.3s ease;
      }

      .metric-value {
        font-weight: bold;
        font-size: 1.1em;
      }

      .grade-badge {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        color: white;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      }

      .grade-letter {
        font-size: 3em;
        font-weight: bold;
      }

      .grade-label {
        font-size: 0.8em;
        margin-top: 5px;
      }

      /* Requirement Section */
      .requirement-section .card {
        background: #f0f9ff;
        padding: 20px;
        border-radius: 6px;
        border-left: 4px solid #0ea5e9;
      }

      .requirement-section h3 {
        font-size: 1.1em;
        margin-top: 15px;
        margin-bottom: 10px;
        color: #1f2937;
      }

      .requirement-section h3:first-child {
        margin-top: 0;
      }

      .criteria-list {
        list-style: none;
        padding-left: 0;
      }

      .criteria-list li {
        padding: 8px 0;
        padding-left: 24px;
        position: relative;
      }

      .criteria-list li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #16a34a;
        font-weight: bold;
      }

      /* Issues Section */
      .issues-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
      }

      .severity-group {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        overflow: hidden;
      }

      .severity-header {
        background: #f3f4f6;
        padding: 12px 15px;
        margin: 0;
        font-size: 1em;
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
      }

      .severity-badge {
        display: inline-block;
        color: white;
        padding: 4px 8px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 0.9em;
        min-width: 50px;
        text-align: center;
      }

      .issues-list {
        padding: 15px;
        background: white;
      }

      .issue-card {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        margin-bottom: 10px;
        overflow: hidden;
      }

      .issue-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 15px;
        background: #fafafa;
        cursor: pointer;
        transition: background 0.2s;
      }

      .issue-header:hover {
        background: #f3f4f6;
      }

      .issue-category {
        background: #667eea;
        color: white;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 0.85em;
        font-weight: 600;
      }

      .issue-file {
        flex: 1;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
        color: #6b7280;
      }

      .toggle-icon {
        color: #9ca3af;
        transition: transform 0.2s;
      }

      .issue-header:hover .toggle-icon {
        transform: rotate(90deg);
      }

      .issue-details {
        padding: 15px;
        background: #fafafa;
        border-top: 1px solid #e5e7eb;
      }

      .issue-details p {
        margin-bottom: 10px;
      }

      .issue-details pre {
        background: #1f2937;
        color: #e5e7eb;
        padding: 12px;
        border-radius: 4px;
        overflow-x: auto;
        font-size: 0.85em;
      }

      /* Files Section */
      .files-table {
        width: 100%;
        border-collapse: collapse;
      }

      .files-table thead {
        background: #f3f4f6;
      }

      .files-table th,
      .files-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #e5e7eb;
      }

      .files-table th {
        font-weight: 600;
        color: #374151;
      }

      .files-table tbody tr:hover {
        background: #f9fafb;
      }

      .file-name {
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
      }

      .numeric {
        text-align: right;
        font-weight: 600;
      }

      .coverage-bar {
        width: 100%;
        height: 6px;
        background: #e5e7eb;
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 5px;
      }

      .coverage-fill {
        height: 100%;
        transition: width 0.3s ease;
      }

      .coverage-percent {
        font-size: 0.85em;
        font-weight: 600;
      }

      /* Heatmap Section */
      .heatmap-table {
        width: 100%;
        border-collapse: collapse;
      }

      .heatmap-table thead {
        background: #f3f4f6;
      }

      .heatmap-table th,
      .heatmap-table td {
        padding: 12px;
        text-align: center;
        border-bottom: 1px solid #e5e7eb;
      }

      .heatmap-table th {
        font-weight: 600;
        color: white;
      }

      .heatmap-table tbody tr:hover {
        background: #f9fafb;
      }

      .severity-count {
        display: inline-block;
        min-width: 30px;
        padding: 4px 8px;
        border-radius: 4px;
        color: white;
        font-weight: bold;
      }

      .severity-count.p0 {
        background-color: #dc2626;
      }

      .severity-count.p1 {
        background-color: #ea580c;
      }

      .severity-count.p2 {
        background-color: #eab308;
        color: #1f2937;
      }

      .severity-count.p3 {
        background-color: #60a5fa;
      }

      /* Suggestions Section */
      .suggestions-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
      }

      .suggestion-card {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 20px;
        border-radius: 6px;
        display: flex;
        gap: 15px;
      }

      .suggestion-rank {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: #16a34a;
        color: white;
        border-radius: 50%;
        font-weight: bold;
        flex-shrink: 0;
      }

      .suggestion-content {
        flex: 1;
      }

      .suggestion-content h4 {
        margin-bottom: 10px;
        color: #1f2937;
      }

      .suggestion-content p {
        margin-bottom: 10px;
        font-size: 0.95em;
      }

      .suggestion-code {
        background: #1f2937;
        color: #e5e7eb;
        padding: 10px;
        border-radius: 4px;
        overflow-x: auto;
        font-size: 0.8em;
      }

      /* Footer */
      footer.footer {
        max-width: 1200px;
        margin: 40px auto;
        text-align: center;
        color: #6b7280;
        font-size: 0.9em;
      }

      /* Responsive Design */
      @media (max-width: 768px) {
        body {
          padding: 10px;
        }

        .section {
          padding: 20px;
          margin: 20px auto;
        }

        header h1 {
          font-size: 1.8em;
        }

        .scorecard {
          flex-direction: column;
        }

        .metrics-grid {
          grid-template-columns: 1fr;
        }

        .header-meta {
          flex-direction: column;
          gap: 10px;
        }

        .suggestions-container {
          grid-template-columns: 1fr;
        }

        .files-table,
        .heatmap-table {
          font-size: 0.9em;
        }

        .files-table th,
        .files-table td,
        .heatmap-table th,
        .heatmap-table td {
          padding: 8px;
        }
      }
"""

    def _get_javascript(self) -> str:
        """Return embedded JavaScript for interactivity.

        Returns:
            str: Complete JavaScript code
        """
        return """
      function toggleIssue(issueId) {
        const element = document.getElementById(issueId);
        const isVisible = element.style.display !== 'none';
        element.style.display = isVisible ? 'none' : 'block';

        // Rotate toggle icon
        const icon = event.target.closest('.issue-header').querySelector('.toggle-icon');
        if (icon) {
          icon.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(90deg)';
        }
      }

      // Add keyboard navigation
      document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
          // Collapse all issues
          const allDetails = document.querySelectorAll('.issue-details');
          allDetails.forEach(detail => {
            detail.style.display = 'none';
            const icon = detail.closest('.issue-card').querySelector('.toggle-icon');
            if (icon) icon.style.transform = 'rotate(0deg)';
          });
        }
      });

      // Add print styling
      window.addEventListener('beforeprint', function() {
        // Expand all issues before printing
        document.querySelectorAll('.issue-details').forEach(detail => {
          detail.style.display = 'block';
        });
      });

      // Smooth scroll on page load
      document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
          anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
              target.scrollIntoView({ behavior: 'smooth' });
            }
          });
        });
      });
"""

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Text to escape

        Returns:
            str: HTML-escaped text
        """
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )
