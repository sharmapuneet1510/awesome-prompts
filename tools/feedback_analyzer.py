#!/usr/bin/env python3
"""
feedback_analyzer.py — Parse and analyze feedback for continuous improvement

Reads feedback.yaml and provides insights on:
- Most common issues
- Severity distribution
- Category breakdown
- Resolution rate
- Improvement suggestions

Usage:
    python3 tools/feedback_analyzer.py --stats
    python3 tools/feedback_analyzer.py --category exporter
    python3 tools/feedback_analyzer.py --severity high
    python3 tools/feedback_analyzer.py --top-issues 10
    python3 tools/feedback_analyzer.py --summary
"""

import yaml
from pathlib import Path
from collections import Counter
from datetime import datetime
from typing import Optional
import argparse


class FeedbackAnalyzer:
    """Analyze feedback for patterns and insights."""

    def __init__(self, feedback_file: Path = None):
        if feedback_file is None:
            # Find feedback.yaml in .feedback/ directory
            repo_root = Path(__file__).parent.parent
            feedback_file = repo_root / ".feedback" / "feedback.yaml"

        self.feedback_file = feedback_file
        self.feedback = self._load_feedback()

    def _load_feedback(self) -> list:
        """Load and parse feedback.yaml"""
        if not self.feedback_file.exists():
            return []

        try:
            with open(self.feedback_file, 'r') as f:
                data = yaml.safe_load(f)
                return data if data else []
        except Exception as e:
            print(f"Error loading feedback: {e}")
            return []

    def filter_by_status(self, status: str) -> list:
        """Filter feedback by status."""
        return [f for f in self.feedback if f.get('status') == status]

    def filter_by_category(self, category: str) -> list:
        """Filter feedback by category."""
        return [f for f in self.feedback if f.get('category') == category]

    def filter_by_severity(self, severity: str) -> list:
        """Filter feedback by severity."""
        return [f for f in self.feedback if f.get('severity') == severity]

    def get_stats(self) -> dict:
        """Generate statistics about feedback."""
        total = len(self.feedback)
        open_items = len(self.filter_by_status('open'))
        resolved_items = len(self.filter_by_status('resolved'))

        # Count by category
        categories = Counter(f.get('category', 'unknown') for f in self.feedback)

        # Count by severity
        severities = Counter(f.get('severity', 'unknown') for f in self.feedback)

        # Count by type
        types = Counter(f.get('type', 'unknown') for f in self.feedback)

        # Count by status
        statuses = Counter(f.get('status', 'unknown') for f in self.feedback)

        return {
            'total': total,
            'open': open_items,
            'resolved': resolved_items,
            'resolution_rate': (resolved_items / total * 100) if total > 0 else 0,
            'categories': dict(categories),
            'severities': dict(severities),
            'types': dict(types),
            'statuses': dict(statuses),
        }

    def get_top_issues(self, limit: int = 10) -> list:
        """Get top issues by severity and status."""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        sorted_feedback = sorted(
            self.filter_by_status('open'),
            key=lambda f: severity_order.get(f.get('severity', 'low'), 999)
        )

        return sorted_feedback[:limit]

    def get_summary(self) -> str:
        """Generate human-readable summary."""
        stats = self.get_stats()

        lines = [
            "📊 FEEDBACK SUMMARY",
            "─" * 60,
            f"Total Items:        {stats['total']}",
            f"Open:               {stats['open']}",
            f"Resolved:           {stats['resolved']}",
            f"Resolution Rate:    {stats['resolution_rate']:.1f}%",
            "",
            "BY CATEGORY:",
        ]

        for category, count in sorted(
            stats['categories'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            lines.append(f"  • {category:<20} {count:3d} items")

        lines.extend([
            "",
            "BY SEVERITY:",
        ])

        severity_order = ['critical', 'high', 'medium', 'low']
        for severity in severity_order:
            count = stats['severities'].get(severity, 0)
            if count > 0:
                lines.append(f"  • {severity:<20} {count:3d} items")

        lines.extend([
            "",
            "BY TYPE:",
        ])

        for type_name, count in sorted(
            stats['types'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            lines.append(f"  • {type_name:<20} {count:3d} items")

        lines.extend([
            "",
            "─" * 60,
        ])

        return "\n".join(lines)

    def format_feedback_item(self, item: dict) -> str:
        """Format a single feedback item for display."""
        lines = [
            f"📌 [{item.get('severity', 'unknown').upper()}] {item.get('title', 'Untitled')}",
            f"   Category: {item.get('category', 'unknown')}",
            f"   Type: {item.get('type', 'unknown')}",
            f"   Status: {item.get('status', 'unknown')}",
            f"   Date: {item.get('date', 'unknown')}",
        ]

        if item.get('description'):
            lines.append(f"   Description:")
            for line in item['description'].strip().split('\n'):
                lines.append(f"      {line}")

        if item.get('labels'):
            labels_str = ", ".join(item['labels'])
            lines.append(f"   Labels: {labels_str}")

        return "\n".join(lines)

    def print_top_issues(self, limit: int = 10):
        """Print top issues by severity."""
        top = self.get_top_issues(limit)

        print(f"\n🔝 TOP {len(top)} ISSUES (by severity)\n")
        print("─" * 60)

        for i, item in enumerate(top, 1):
            print(f"\n{i}. {self.format_feedback_item(item)}")

        print("\n" + "─" * 60)

    def print_by_category(self, category: str):
        """Print all feedback for a category."""
        items = self.filter_by_category(category)

        print(f"\n📂 FEEDBACK FOR: {category.upper()}\n")
        print(f"Found {len(items)} item(s)\n")
        print("─" * 60)

        for i, item in enumerate(items, 1):
            print(f"\n{i}. {self.format_feedback_item(item)}")

        print("\n" + "─" * 60)

    def print_by_severity(self, severity: str):
        """Print all feedback with specific severity."""
        items = self.filter_by_severity(severity)

        print(f"\n⚠️  FEEDBACK WITH {severity.upper()} SEVERITY\n")
        print(f"Found {len(items)} item(s)\n")
        print("─" * 60)

        for i, item in enumerate(items, 1):
            print(f"\n{i}. {self.format_feedback_item(item)}")

        print("\n" + "─" * 60)

    def export_summary(self, output_file: Path = None):
        """Export summary to markdown file."""
        if output_file is None:
            output_file = self.feedback_file.parent / "FEEDBACK_SUMMARY.md"

        content = [
            "# 📊 Feedback Summary",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            self.get_summary().replace("─", ""), # Remove box chars for markdown
            "",
            "## 🔝 Top Issues",
            ""
        ]

        for i, item in enumerate(self.get_top_issues(5), 1):
            content.append(f"### {i}. {item.get('title', 'Untitled')}")
            content.append(f"- **Severity:** {item.get('severity')}")
            content.append(f"- **Category:** {item.get('category')}")
            content.append(f"- **Status:** {item.get('status')}")
            if item.get('description'):
                content.append(f"- **Description:** {item['description'].split(chr(10))[0]}")
            content.append("")

        output_file.write_text("\n".join(content))
        print(f"✓ Summary exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze feedback for improvement insights"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show overall statistics"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary and export to markdown"
    )
    parser.add_argument(
        "--category",
        help="Filter by category"
    )
    parser.add_argument(
        "--severity",
        help="Filter by severity (critical, high, medium, low)"
    )
    parser.add_argument(
        "--top-issues",
        type=int,
        default=10,
        help="Show top N issues (default: 10)"
    )
    parser.add_argument(
        "--feedback-file",
        type=Path,
        help="Path to feedback.yaml"
    )

    args = parser.parse_args()

    analyzer = FeedbackAnalyzer(args.feedback_file)

    if not analyzer.feedback:
        print("No feedback found. Add feedback to .feedback/feedback.yaml")
        return

    if args.stats:
        print(analyzer.get_summary())
    elif args.summary:
        print(analyzer.get_summary())
        analyzer.export_summary()
    elif args.category:
        analyzer.print_by_category(args.category)
    elif args.severity:
        analyzer.print_by_severity(args.severity)
    else:
        # Default: show top issues
        analyzer.print_top_issues(args.top_issues)


if __name__ == "__main__":
    main()
