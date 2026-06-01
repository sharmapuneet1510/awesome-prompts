#!/usr/bin/env python3
"""
feedback_processor.py — Apply feedback to improve the system

Reads feedback.yaml and:
1. Identifies patterns and pain points
2. Generates improvement tasks
3. Updates documentation based on common questions
4. Suggests code changes for bugs

Usage:
    python3 tools/feedback_processor.py --analyze
    python3 tools/feedback_processor.py --generate-tasks
    python3 tools/feedback_processor.py --suggest-fixes
"""

import yaml
from pathlib import Path
from collections import Counter
from typing import Dict, List
import argparse


class FeedbackProcessor:
    """Process feedback to drive system improvements."""

    def __init__(self, feedback_file: Path = None):
        if feedback_file is None:
            repo_root = Path(__file__).parent.parent
            feedback_file = repo_root / ".feedback" / "feedback.yaml"

        self.feedback_file = feedback_file
        self.feedback = self._load_feedback()
        self.repo_root = feedback_file.parent.parent

    def _load_feedback(self) -> list:
        """Load feedback from YAML file."""
        if not self.feedback_file.exists():
            return []

        try:
            with open(self.feedback_file, 'r') as f:
                data = yaml.safe_load(f)
                return data if data else []
        except Exception as e:
            print(f"Error loading feedback: {e}")
            return []

    def get_critical_issues(self) -> list:
        """Get all critical and high-severity issues."""
        return [
            f for f in self.feedback
            if f.get('status') == 'open'
            and f.get('severity') in ['critical', 'high']
        ]

    def get_feature_requests(self) -> list:
        """Get all feature requests."""
        return [
            f for f in self.feedback
            if f.get('type') == 'feature-request'
            and f.get('status') == 'open'
        ]

    def get_most_requested_features(self, limit: int = 5) -> list:
        """Get most requested features (by label frequency)."""
        feature_requests = self.get_feature_requests()

        if not feature_requests:
            return []

        # Count label frequency
        all_labels = []
        for req in feature_requests:
            all_labels.extend(req.get('labels', []))

        label_counts = Counter(all_labels)

        # Get top N labels and find features with those labels
        top_labels = [label for label, _ in label_counts.most_common(limit)]

        relevant_features = []
        for req in feature_requests:
            if any(label in req.get('labels', []) for label in top_labels):
                relevant_features.append(req)

        return relevant_features[:limit]

    def analyze_feedback_patterns(self) -> Dict:
        """Identify patterns in feedback."""
        patterns = {
            'critical_issues': len(self.get_critical_issues()),
            'feature_requests': len(self.get_feature_requests()),
            'documentation_gaps': len([
                f for f in self.feedback
                if f.get('category') == 'documentation'
                and f.get('status') == 'open'
            ]),
            'performance_issues': len([
                f for f in self.feedback
                if f.get('category') == 'performance'
                and f.get('status') == 'open'
            ]),
            'total_unresolved': len([
                f for f in self.feedback
                if f.get('status') == 'open'
            ]),
        }

        return patterns

    def generate_improvement_tasks(self) -> List[str]:
        """Generate tasks based on feedback."""
        tasks = []

        patterns = self.analyze_feedback_patterns()

        if patterns['critical_issues'] > 0:
            tasks.append(
                f"🚨 Fix {patterns['critical_issues']} critical issues"
            )

        if patterns['feature_requests'] > 2:
            tasks.append(
                f"⭐ Implement top {min(3, patterns['feature_requests'])} feature requests"
            )

        if patterns['documentation_gaps'] > 2:
            tasks.append(
                f"📚 Fill {patterns['documentation_gaps']} documentation gaps"
            )

        if patterns['performance_issues'] > 0:
            tasks.append(
                f"🚀 Optimize {patterns['performance_issues']} performance issues"
            )

        # Add specific tasks for top issues
        critical = self.get_critical_issues()
        if critical:
            for issue in critical[:2]:
                tasks.append(f"🔧 {issue.get('title', 'Fix issue')}")

        return tasks

    def suggest_documentation_updates(self) -> List[str]:
        """Suggest which documentation should be updated."""
        suggestions = []

        # Find documentation feedback
        doc_feedback = [
            f for f in self.feedback
            if f.get('category') == 'documentation'
            and f.get('status') == 'open'
        ]

        for item in doc_feedback:
            title = item.get('title', '')
            suggestions.append(f"📖 {title}")

        # Find common questions (implied documentation gaps)
        common_issues = [
            f for f in self.feedback
            if f.get('type') == 'improvement'
            and f.get('status') == 'open'
        ]

        for item in common_issues[:3]:
            title = item.get('title', '')
            suggestions.append(f"💡 {title}")

        return suggestions

    def get_action_items(self) -> Dict:
        """Get actionable items from feedback."""
        return {
            'critical_fixes': self.get_critical_issues()[:3],
            'top_features': self.get_most_requested_features(3),
            'doc_updates': self.suggest_documentation_updates()[:3],
            'improvement_tasks': self.generate_improvement_tasks(),
        }

    def print_analysis(self):
        """Print detailed analysis of feedback."""
        patterns = self.analyze_feedback_patterns()

        print("\n" + "=" * 70)
        print("📊 FEEDBACK ANALYSIS REPORT")
        print("=" * 70)

        print("\n📈 STATISTICS:")
        print(f"  Critical Issues:    {patterns['critical_issues']}")
        print(f"  Feature Requests:   {patterns['feature_requests']}")
        print(f"  Documentation Gaps: {patterns['documentation_gaps']}")
        print(f"  Performance Issues: {patterns['performance_issues']}")
        print(f"  Total Unresolved:   {patterns['total_unresolved']}")

        action_items = self.get_action_items()

        if action_items['critical_fixes']:
            print("\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in action_items['critical_fixes']:
                print(f"  • {issue.get('title', 'Unknown')}")

        if action_items['top_features']:
            print("\n⭐ TOP FEATURE REQUESTS:")
            for feature in action_items['top_features']:
                print(f"  • {feature.get('title', 'Unknown')}")

        if action_items['doc_updates']:
            print("\n📚 DOCUMENTATION NEEDS:")
            for doc in action_items['doc_updates']:
                print(f"  • {doc}")

        print("\n" + "=" * 70)

    def print_tasks(self):
        """Print generated improvement tasks."""
        tasks = self.generate_improvement_tasks()

        print("\n" + "=" * 70)
        print("📋 IMPROVEMENT TASKS (Generated from Feedback)")
        print("=" * 70)

        if not tasks:
            print("\n✅ No tasks needed! All feedback resolved.")
            return

        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

        print("\n" + "=" * 70)

    def print_summary(self):
        """Print quick summary for CI/CD."""
        patterns = self.analyze_feedback_patterns()

        print(f"Feedback: {patterns['total_unresolved']} open items | "
              f"{patterns['critical_issues']} critical | "
              f"{patterns['feature_requests']} features | "
              f"{patterns['documentation_gaps']} doc gaps")


def main():
    parser = argparse.ArgumentParser(
        description="Process feedback to drive improvements"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Show detailed feedback analysis"
    )
    parser.add_argument(
        "--generate-tasks",
        action="store_true",
        help="Generate improvement tasks from feedback"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Quick summary (for CI/CD logs)"
    )
    parser.add_argument(
        "--feedback-file",
        type=Path,
        help="Path to feedback.yaml"
    )

    args = parser.parse_args()

    processor = FeedbackProcessor(args.feedback_file)

    if not processor.feedback:
        print("No feedback found. Add feedback to .feedback/feedback.yaml")
        return

    if args.analyze:
        processor.print_analysis()
    elif args.generate_tasks:
        processor.print_tasks()
    elif args.summary:
        processor.print_summary()
    else:
        # Default: show analysis
        processor.print_analysis()


if __name__ == "__main__":
    main()
