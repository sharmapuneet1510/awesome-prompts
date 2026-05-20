from datetime import datetime
from typing import Dict, List, Any
import re


class RequirementParser:
    """Parse plain-text requirements into structured format."""

    def __init__(self, requirement_text: str):
        self.raw_text = requirement_text
        self.parsed_data: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """Extract structured data from plain text."""
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
