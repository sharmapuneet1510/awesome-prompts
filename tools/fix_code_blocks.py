#!/usr/bin/env python3
"""
Fix unmarked code blocks in skill files by adding language tags.
Scans for ``` without a language tag and infers the appropriate tag based on context.
"""
import re
from pathlib import Path

def fix_skill_file(filepath: str) -> dict:
    """
    Fix unmarked code blocks in a skill file.
    Returns dict with filename, changes_made, lines_changed.
    """
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    lines = content.split('\n')

    # Detect the primary language(s) from filename and frontmatter
    filename = Path(filepath).name

    language_map = {
        'java': 'java',
        'python': 'python',
        'react': 'jsx',
        'mssql': 'sql',
        'camel': 'java',  # Apache Camel uses Java DSL
        'pulsar': 'java',  # Pulsar primary examples are Java
        'spring': 'java',  # Spring is Java framework
        'code_health': 'plaintext',  # Mixed examples
    }

    # Infer primary language
    primary_lang = 'plaintext'
    for key, lang in language_map.items():
        if key in filename:
            primary_lang = lang
            break

    # Process line by line to find unmarked code fences
    i = 0
    changes_made = 0
    changed_lines = []

    while i < len(lines):
        line = lines[i]

        # Match opening fence without language tag: ``` followed by newline or whitespace (no word chars)
        if re.match(r'^```\s*$', line):
            # Look ahead to determine what language this block contains
            inferred_lang = primary_lang

            # Peek at next few lines for hints
            if i + 1 < len(lines):
                next_line = lines[i + 1]

                # Check for language indicators
                if any(keyword in next_line for keyword in ['public ', 'private ', 'class ', 'interface ', 'package ', 'import ', '@Override', '@']):
                    inferred_lang = 'java'
                elif any(keyword in next_line for keyword in ['def ', 'import ', 'from ', 'async ', 'await ', 'class ', '@pytest', 'pytest']):
                    inferred_lang = 'python'
                elif any(keyword in next_line for keyword in ['const ', 'function ', 'interface ', 'export ', 'import ', 'useState', '<']):
                    inferred_lang = 'jsx'
                elif any(keyword in next_line for keyword in ['CREATE TABLE', 'SELECT ', 'INSERT ', 'UPDATE ', 'DELETE ', 'DECLARE ', 'EXEC ', 'BEGIN', 'END']):
                    inferred_lang = 'sql'
                elif any(keyword in next_line for keyword in ['bash', '$', 'pip ', 'mvn ', 'npm ', 'java -version', 'python']):
                    inferred_lang = 'bash'
                elif any(keyword in next_line for keyword in ['json', '{', '[', '"', ':']):
                    inferred_lang = 'json'
                elif any(keyword in next_line for keyword in ['yaml', 'yml', '---', 'version:', 'name:']):
                    inferred_lang = 'yaml'

            # Replace the line with language tag
            lines[i] = f'```{inferred_lang}'
            changes_made += 1
            changed_lines.append(i + 1)  # 1-indexed for reporting

        i += 1

    # Write back if changes were made
    if changes_made > 0:
        new_content = '\n'.join(lines)
        with open(filepath, 'w') as f:
            f.write(new_content)

    return {
        'file': Path(filepath).name,
        'changes': changes_made,
        'lines': changed_lines,
    }

def main():
    skills_dir = Path('skills')

    if not skills_dir.exists():
        print("Error: skills/ directory not found. Run from repo root.")
        return

    skill_files = sorted(skills_dir.glob('*_skill.md'))

    if not skill_files:
        print("No skill files found.")
        return

    print("=" * 70)
    print("FIXING UNMARKED CODE BLOCKS")
    print("=" * 70)

    total_changes = 0

    for filepath in skill_files:
        result = fix_skill_file(str(filepath))
        if result['changes'] > 0:
            print(f"\n✓ {result['file']}")
            print(f"  Fixed {result['changes']} code block(s) at lines: {', '.join(map(str, result['lines']))}")
            total_changes += result['changes']
        else:
            print(f"\n✓ {result['file']} — already clean")

    print("\n" + "=" * 70)
    print(f"SUMMARY: Fixed {total_changes} unmarked code block(s) across {len(skill_files)} skill(s)")
    print("=" * 70)

if __name__ == '__main__':
    main()
