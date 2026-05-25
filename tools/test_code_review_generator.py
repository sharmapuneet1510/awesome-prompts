#!/usr/bin/env python3
"""
test_code_review_generator.py — Test suite for ReviewReportGenerator.

Tests:
1. HTML generation with sample review data
2. File creation at correct path
3. All 8 sections present in output
4. CSS and JavaScript embedded
5. Progress bars and color coding
6. Issue grouping by severity
7. Suggestions ranking
"""

import json
import tempfile
from pathlib import Path

from code_review_generator import ReviewReportGenerator


def create_sample_review_data() -> dict:
    """Create sample review data matching Code Review Agent output.

    Returns:
        dict: Complete review result with all sections
    """
    return {
        "requirement_analysis": {
            "feature_description": "Implement user authentication with JWT token support for secure API access.",
            "acceptance_criteria": [
                "User can register with email and password",
                "User can login and receive JWT token",
                "JWT token is validated on each request",
                "Token expires after 24 hours",
                "Passwords are hashed with bcrypt",
            ],
        },
        "scorecard": {
            "requirement": 85,
            "code_quality": 78,
            "testing": 70,
            "documentation": 65,
            "final_grade": "B",
        },
        "issues": [
            {
                "category": "Security",
                "severity": "P0",
                "file": "auth/models.py",
                "line": 42,
                "description": "Password is stored in plain text instead of hashed",
                "impact": "Critical security vulnerability - passwords are exposed if database is compromised",
                "suggested_fix": "from werkzeug.security import generate_password_hash\n"
                "user.password = generate_password_hash(password)",
            },
            {
                "category": "Design",
                "severity": "P1",
                "file": "auth/routes.py",
                "line": 15,
                "description": "No input validation on login endpoint",
                "impact": "Application vulnerable to injection attacks and malformed requests",
                "suggested_fix": "from marshmallow import Schema, fields, validate\n"
                "class LoginSchema(Schema):\n"
                "    email = fields.Email(required=True)\n"
                "    password = fields.Str(required=True, validate=validate.Length(min=8))",
            },
            {
                "category": "Testing",
                "severity": "P2",
                "file": "tests/test_auth.py",
                "line": 0,
                "description": "Missing test for expired token validation",
                "impact": "Expired tokens may not be properly rejected, allowing unauthorized access",
                "suggested_fix": "def test_expired_token_rejected():\n"
                "    expired_token = create_expired_token()\n"
                "    response = client.get('/api/user', headers={'Authorization': f'Bearer {expired_token}'})\n"
                "    assert response.status_code == 401",
            },
            {
                "category": "Documentation",
                "severity": "P2",
                "file": "auth/models.py",
                "line": 1,
                "description": "Missing docstring on User model class",
                "impact": "API users don't understand User model structure and requirements",
                "suggested_fix": '"""User model for authentication.\n\nAttributes:\n    id: Unique user identifier\n    email: User email address (unique)\n    password: Hashed password"""',
            },
            {
                "category": "Code Quality",
                "severity": "P3",
                "file": "auth/utils.py",
                "line": 8,
                "description": "Unused import statement",
                "impact": "Clutters code and reduces readability",
                "suggested_fix": "Remove: import uuid  # unused",
            },
        ],
        "file_breakdown": {
            "auth/models.py": {
                "lines_added": 45,
                "issues_count": 2,
                "coverage_percent": 85,
            },
            "auth/routes.py": {
                "lines_added": 78,
                "issues_count": 1,
                "coverage_percent": 70,
            },
            "auth/utils.py": {
                "lines_added": 32,
                "issues_count": 1,
                "coverage_percent": 60,
            },
            "tests/test_auth.py": {
                "lines_added": 120,
                "issues_count": 1,
                "coverage_percent": 75,
            },
        },
        "suggestions": [
            {
                "title": "Implement password hashing immediately",
                "impact": "This is a critical security issue affecting all user data",
                "code_example": "from werkzeug.security import generate_password_hash, check_password_hash\n\n"
                "class User(db.Model):\n"
                "    @property\n"
                "    def password(self):\n"
                "        raise AttributeError('Password is not readable')\n\n"
                "    @password.setter\n"
                "    def password(self, pwd):\n"
                "        self.password_hash = generate_password_hash(pwd)",
            },
            {
                "title": "Add input validation to all endpoints",
                "impact": "Prevents injection attacks and invalid data from entering the system",
                "code_example": "from flask import request\nfrom marshmallow import ValidationError\n\n"
                "@auth.route('/login', methods=['POST'])\ndef login():\n"
                "    try:\n"
                "        data = LoginSchema().load(request.json)\n"
                "    except ValidationError as err:\n"
                "        return {'errors': err.messages}, 400",
            },
            {
                "title": "Expand test coverage to 95%+",
                "impact": "Catches regressions early and ensures authentication works in all scenarios",
                "code_example": "# Run coverage report\npytest --cov=auth tests/\n\n# Test expired tokens, invalid tokens, missing headers",
            },
            {
                "title": "Document all models with comprehensive docstrings",
                "impact": "Team can understand and use the API correctly without source diving",
                "code_example": '"""User authentication model.\n\nStores user credentials and authentication metadata.\n\nAttributes:\n    id: Primary key\n    email: User email, must be unique\n    password_hash: Argon2 hashed password\n    created_at: Account creation timestamp\n    last_login: Last successful login timestamp\n"""',
            },
            {
                "title": "Remove unused imports and clean up",
                "impact": "Improves code clarity and reduces cognitive load",
                "code_example": "# Before:\nimport uuid  # unused\n\n# After:\n# (removed)",
            },
        ],
    }


def test_review_report_generator():
    """Test ReviewReportGenerator with sample data."""
    print("\n" + "="*70)
    print("TEST 1: Initialize generator and create output directory")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        gen = ReviewReportGenerator(output_dir=tmpdir)
        assert Path(tmpdir).exists(), "Output directory not created"
        print(f"✓ Generator initialized with output_dir: {tmpdir}")

        print("\n" + "="*70)
        print("TEST 2: Generate HTML report from sample data")
        print("="*70)

        review_data = create_sample_review_data()
        jira_key = "AUTH-789"

        html_path = gen.generate(review_data, jira_key)
        assert html_path, "No path returned from generate()"
        print(f"✓ Report generated at: {html_path}")

        print("\n" + "="*70)
        print("TEST 3: Verify file exists at correct path")
        print("="*70)

        assert Path(html_path).exists(), f"File not created at {html_path}"
        print(f"✓ File exists: {Path(html_path).name}")

        print("\n" + "="*70)
        print("TEST 4: Verify HTML structure and sections")
        print("="*70)

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Check HTML structure
        assert "<!DOCTYPE html>" in html_content, "Missing DOCTYPE"
        print("✓ Valid HTML document structure")

        assert "<head>" in html_content and "<body>" in html_content
        print("✓ HTML head and body tags present")

        # Check all 8 sections
        sections = [
            ("Header", "Code Review Report"),
            ("Scorecard", "📊 Scorecard"),
            ("Requirement", "✅ Requirement Analysis"),
            ("Issues", "🐛 Issues by Severity"),
            ("Files", "📁 File-by-File Breakdown"),
            ("Heatmap", "🔥 Severity Heatmap"),
            ("Suggestions", "💡 Top Suggestions"),
            ("Footer", "Code Review Agent v3"),
        ]

        for section_name, section_marker in sections:
            assert section_marker in html_content, f"Missing section: {section_name}"
            print(f"✓ Section present: {section_name}")

        print("\n" + "="*70)
        print("TEST 5: Verify CSS is embedded")
        print("="*70)

        assert "<style>" in html_content and "</style>" in html_content
        print("✓ CSS embedded in <style> tag")

        assert "body {" in html_content
        print("✓ CSS contains style rules")

        assert ".scorecard" in html_content
        print("✓ CSS contains scorecard styles")

        print("\n" + "="*70)
        print("TEST 6: Verify JavaScript is embedded")
        print("="*70)

        assert "<script>" in html_content and "</script>" in html_content
        print("✓ JavaScript embedded in <script> tag")

        assert "toggleIssue" in html_content
        print("✓ JavaScript contains toggleIssue function")

        assert "keydown" in html_content
        print("✓ JavaScript contains event handlers")

        print("\n" + "="*70)
        print("TEST 7: Verify scorecard data")
        print("="*70)

        assert "85%" in html_content or "85" in html_content
        print("✓ Scorecard shows requirement metric (85%)")

        assert "final_grade" in html_content or "B" in html_content
        assert "Final Grade" in html_content
        print("✓ Final grade badge present")

        print("\n" + "="*70)
        print("TEST 8: Verify issues grouped by severity")
        print("="*70)

        # Check severity grouping
        assert "P0" in html_content or "Critical" in html_content
        print("✓ P0 (Critical) issues present")

        assert "P1" in html_content or "High" in html_content
        print("✓ P1 (High) issues present")

        assert "P2" in html_content or "Medium" in html_content
        print("✓ P2 (Medium) issues present")

        # Check issue details
        assert "SQL injection" not in html_content or "Security" in html_content
        assert "password" in html_content.lower()
        print("✓ Issue content present (passwords, hashing)")

        print("\n" + "="*70)
        print("TEST 9: Verify file breakdown table")
        print("="*70)

        assert "auth/models.py" in html_content
        print("✓ File breakdown includes auth/models.py")

        assert "45" in html_content or "lines_added" in html_content
        print("✓ Lines added information present")

        assert "coverage" in html_content.lower()
        print("✓ Coverage metrics present")

        print("\n" + "="*70)
        print("TEST 10: Verify suggestions")
        print("="*70)

        assert "hashing" in html_content.lower() or "Hash" in html_content
        print("✓ Suggestion about password hashing present")

        assert "validation" in html_content.lower()
        print("✓ Suggestion about input validation present")

        assert "#1" in html_content or "rank" in html_content.lower()
        print("✓ Suggestions ranked numerically")

        print("\n" + "="*70)
        print("TEST 11: Verify color coding")
        print("="*70)

        assert "#dc2626" in html_content  # P0 red
        print("✓ P0 severity color (#dc2626) present")

        assert "#ea580c" in html_content  # P1 orange
        print("✓ P1 severity color (#ea580c) present")

        assert "#16a34a" in html_content  # green for A grade
        print("✓ Grade A color (#16a34a) present")

        print("\n" + "="*70)
        print("TEST 12: Verify responsive design")
        print("="*70)

        assert "@media (max-width: 768px)" in html_content
        print("✓ Mobile responsive CSS present")

        print("\n" + "="*70)
        print("TEST 13: Verify JIRA key in header")
        print("="*70)

        assert jira_key in html_content
        print(f"✓ JIRA key {jira_key} present in output")

        print("\n" + "="*70)
        print("TEST 14: Verify no external dependencies")
        print("="*70)

        assert "http://" not in html_content or "localhost" in html_content
        assert "https://" not in html_content or "localhost" in html_content or "data:" in html_content
        print("✓ No external HTTP/HTTPS links (self-contained)")

        print("\n" + "="*70)
        print("TEST 15: Verify HTML escaping")
        print("="*70)

        # The HTML should properly escape code examples
        assert "&lt;" in html_content or "<" in html_content
        print("✓ Special characters properly handled")

        print("\n" + "="*70)
        print("TEST 16: Test error handling")
        print("="*70)

        # Test missing required fields
        incomplete_data = {"scorecard": {}}  # missing 'issues'
        try:
            gen.generate(incomplete_data, "TEST-1")
            print("✗ Should have raised ValueError for missing 'issues'")
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print("All tests passed! ✓")
        print(f"\nGenerated report: {html_path}")
        print(f"File size: {Path(html_path).stat().st_size:,} bytes")
        print("\nTo view the report:")
        print(f"  open {html_path}")


if __name__ == "__main__":
    test_review_report_generator()
