from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import json
from pathlib import Path


class RequirementParser:
    """Parse requirements from multiple sources (free text, JIRA, file) into structured format."""

    def __init__(self, requirement_text: str, source: str = "free_text"):
        self.raw_text = requirement_text
        self.source = source  # free_text | jira | file
        self.parsed_data: Dict[str, Any] = {}
        self.requirement_object: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """Extract structured data from raw text."""
        self.parsed_data = {
            'project_name': self._extract_project_name(),
            'vision': self._extract_vision(),
            'tech_stack': self._extract_tech_stack(),
            'features': self._extract_features(),
            'success_criteria': self._extract_success_criteria(),
            'timeline': self._extract_timeline(),
            'constraints': self._extract_constraints(),
        }
        return self.parsed_data

    def get_requirement_object(self) -> Dict[str, Any]:
        """Return structured requirement object for developer_agent consumption."""
        if not self.parsed_data:
            self.parse()

        self.requirement_object = {
            "source": self.source,
            "title": self.parsed_data['project_name'],
            "description": self.parsed_data['vision'],
            "features": self.parsed_data['features'],
            "constraints": self.parsed_data['constraints'],
            "acceptance_criteria": self.parsed_data['success_criteria'],
            "priority": "high",  # Default priority
            "parsed_at": datetime.now().isoformat(),
            "raw_text": self.raw_text[:500] + "..." if len(self.raw_text) > 500 else self.raw_text,
        }
        return self.requirement_object

    @classmethod
    def from_free_text(cls, requirement_text: str) -> 'RequirementParser':
        """Parse from free text description."""
        parser = cls(requirement_text, source="free_text")
        return parser

    @classmethod
    def from_file(cls, file_path: str) -> 'RequirementParser':
        """Parse from requirement file (txt, md, yaml)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Requirement file not found: {file_path}")

        content = path.read_text(encoding='utf-8')
        parser = cls(content, source="file")
        parser.source_file = str(file_path)
        return parser

    @classmethod
    def from_jira(cls, jira_data: Dict[str, Any]) -> 'RequirementParser':
        """Parse from JIRA ticket data (obtained via MCP)."""
        # Build text representation from JIRA fields
        text_parts = [
            f"Project: {jira_data.get('project', 'Unknown')}",
            f"Summary: {jira_data.get('summary', '')}",
            f"Description: {jira_data.get('description', '')}",
        ]

        # Add acceptance criteria if present
        if 'acceptance_criteria' in jira_data:
            text_parts.append(f"Acceptance Criteria: {' '.join(jira_data['acceptance_criteria'])}")

        requirement_text = "\n".join(text_parts)
        parser = cls(requirement_text, source="jira")
        parser.jira_key = jira_data.get('key', '')
        parser.jira_status = jira_data.get('status', '')
        parser.jira_assignee = jira_data.get('assignee', '')
        return parser

    @classmethod
    def from_project_file(cls, project_root: str) -> Optional['RequirementParser']:
        """Auto-detect and parse requirement file from project root."""
        project_path = Path(project_root)
        candidate_files = [
            project_path / 'requirements.md',
            project_path / 'requirements.txt',
            project_path / 'REQUIREMENTS.md',
            project_path / 'spec.md',
            project_path / '.requirements',
        ]

        for candidate in candidate_files:
            if candidate.exists():
                return cls.from_file(str(candidate))

        return None

    def _extract_project_name(self) -> str:
        """Extract or infer project name."""
        # Look for explicit project name mention
        match = re.search(r'(?:project|system|app|application|platform)\s+(?:called|named|is|:\s*)(\w+(?:\s+\w+)*)',
                         self.raw_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Default: extract first meaningful words
        words = self.raw_text.split()[:3]
        return ' '.join(words).rstrip('.,;:')

    def _extract_vision(self) -> str:
        """Extract 2-3 sentence vision from raw text."""
        sentences = re.split(r'(?<=[.!?])\s+', self.raw_text)
        vision = '. '.join(sentences[:2]) + '.'
        return vision.replace('..', '.')

    def _extract_tech_stack(self) -> Dict[str, str]:
        """Extract frontend, backend, database technology choices."""
        tech_map = {
            'frontend': ['react', 'vue', 'angular', 'next', 'svelte'],
            'backend': ['fastapi', 'flask', 'django', 'spring', 'java', 'python', 'node', 'express', 'golang'],
            'database': ['postgresql', 'mysql', 'mongodb', 'redis', 'sql server', 'dynamodb'],
            'auth': ['jwt', 'oauth', 'session', 'saml'],
        }

        text_lower = self.raw_text.lower()
        stack = {'frontend': '', 'backend': '', 'database': ''}

        for key, technologies in tech_map.items():
            for tech in technologies:
                if tech in text_lower:
                    if key == 'auth':
                        stack['auth'] = tech.upper()
                    else:
                        stack[key] = tech.title() if key != 'frontend' else 'React'
                    break

        # Provide defaults if not found
        if not stack['frontend']:
            stack['frontend'] = 'React 18+'
        if not stack['backend']:
            stack['backend'] = 'Python/FastAPI'
        if not stack['database']:
            stack['database'] = 'PostgreSQL'

        return stack

    def _extract_features(self) -> List[str]:
        """Extract key features."""
        # Simple: split on keywords like "feature", "support", "include", "add"
        features = []
        feature_keywords = r'(?:feature|support|include|add|implement|create|build|with)\s+([^.!?]+)'
        matches = re.findall(feature_keywords, self.raw_text, re.IGNORECASE)
        return [m.strip() for m in matches[:5]]  # Top 5 features

    def _extract_success_criteria(self) -> List[str]:
        """Extract success/acceptance criteria."""
        # Look for "must", "should", "require" keywords
        criteria = []
        criterion_keywords = r'(?:must|should|require|need)\s+([^.!?]+)'
        matches = re.findall(criterion_keywords, self.raw_text, re.IGNORECASE)
        return [f"[ ] {m.strip()}" for m in matches[:4]]

    def _extract_timeline(self) -> str:
        """Extract timeline if mentioned."""
        match = re.search(r'(?:timeline|ready in|within|in|by):\s+([^.!?,]+?)(?:\.|,|$)',
                         self.raw_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Try without colon
        match = re.search(r'timeline\s+([^.!?,]+?)(?:\.|,|$)',
                         self.raw_text, re.IGNORECASE)
        return match.group(1).strip() if match else "Not specified"

    def _extract_constraints(self) -> List[str]:
        """Extract constraints (budget, team size, etc.)."""
        constraints = []
        if 'team' in self.raw_text.lower():
            match = re.search(r'team[^.!?]*?(\d+)', self.raw_text)
            if match:
                constraints.append(f"Team: {match.group(1)} people")
        return constraints

    def to_markdown(self) -> str:
        """Generate requirement.md content."""
        if not self.parsed_data:
            self.parse()

        tech = self.parsed_data['tech_stack']
        features = self.parsed_data['features']
        timeline = self.parsed_data['timeline']

        md = f"""---
name: {self.parsed_data['project_name'].lower().replace(' ', '_')}
version: 1.0
generated_at: {datetime.now().isoformat()}
---

# Project: {self.parsed_data['project_name']}

## Vision
{self.parsed_data['vision']}

## Tech Stack
- **Frontend:** {tech['frontend']}
- **Backend:** {tech['backend']}
- **Database:** {tech['database']}

## Features (User Stories)
"""
        for i, feature in enumerate(features, 1):
            md += f"{i}. {feature.capitalize()}\n"

        md += """
## Success Criteria
"""
        for criterion in self.parsed_data['success_criteria']:
            md += f"- {criterion}\n"

        md += f"""
## Constraints
- Timeline: {timeline}
"""

        if self.parsed_data['constraints']:
            for constraint in self.parsed_data['constraints']:
                md += f"- {constraint}\n"

        md += "\n## Architecture Overview\n[Auto-generated after codebase scan]\n"

        return md


# CLI and helper functions
def parse_requirement_interactive() -> Dict[str, Any]:
    """Interactive CLI for requirement input."""
    print("\n" + "=" * 60)
    print("REQUIREMENT PARSER")
    print("=" * 60)
    print("\nHow would you like to provide requirements?\n")
    print("  a) Free text description (describe what you want to build)")
    print("  b) JIRA ticket/story (link or ticket key)")
    print("  c) Requirement file (path to requirements.txt, .md, etc.)")
    print("  d) Auto-detect from project (searches project root)")
    print("\nChoice [a/b/c/d]: ", end='')

    choice = input().strip().lower()

    if choice == 'a':
        print("\nDescribe what you want to build (press Enter twice to finish):\n")
        lines = []
        empty_lines = 0
        while empty_lines < 1:
            line = input()
            if line:
                lines.append(line)
                empty_lines = 0
            else:
                empty_lines += 1
        requirement_text = '\n'.join(lines)
        parser = RequirementParser.from_free_text(requirement_text)

    elif choice == 'b':
        print("\nEnter JIRA ticket (key like PROJ-123 or full link): ", end='')
        jira_key = input().strip()
        print("\nNote: JIRA parsing requires MCP integration.")
        print("For now, paste JIRA details as free text or use a requirement file.")
        requirement_text = f"JIRA Ticket: {jira_key}\n(Note: Install MCP for automatic JIRA parsing)"
        parser = RequirementParser.from_free_text(requirement_text)
        parser.source = "jira_manual"

    elif choice == 'c':
        print("\nEnter path to requirement file: ", end='')
        file_path = input().strip()
        try:
            parser = RequirementParser.from_file(file_path)
        except FileNotFoundError as e:
            print(f"\nError: {e}")
            return {}

    elif choice == 'd':
        print("\nSearching for requirement file in project root...")
        parser = RequirementParser.from_project_file('.')
        if parser:
            print(f"Found: {parser.source_file if hasattr(parser, 'source_file') else 'requirement file'}")
        else:
            print("No requirement file found. Using free text instead.")
            print("\nDescribe your project: ", end='')
            requirement_text = input().strip()
            parser = RequirementParser.from_free_text(requirement_text)

    else:
        print("Invalid choice. Defaulting to free text input.")
        requirement_text = input("\nDescribe your project: ").strip()
        parser = RequirementParser.from_free_text(requirement_text)

    # Parse and return requirement object
    parser.parse()
    requirement_obj = parser.get_requirement_object()

    print("\n" + "-" * 60)
    print("PARSED REQUIREMENT")
    print("-" * 60)
    print(f"Title: {requirement_obj['title']}")
    print(f"Source: {requirement_obj['source']}")
    print(f"Features: {', '.join(requirement_obj['features']) if requirement_obj['features'] else 'None detected'}")
    print("-" * 60 + "\n")

    return requirement_obj


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Command-line usage: python requirement_parser.py <file_path_or_text>
        arg = sys.argv[1]
        if Path(arg).exists():
            parser = RequirementParser.from_file(arg)
        else:
            parser = RequirementParser.from_free_text(arg)

        parser.parse()
        print(json.dumps(parser.get_requirement_object(), indent=2))
    else:
        # Interactive mode
        requirement = parse_requirement_interactive()
        print("\nRequirement object:")
        print(json.dumps(requirement, indent=2))
