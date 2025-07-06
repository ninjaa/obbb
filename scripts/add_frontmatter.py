#!/usr/bin/env python3
"""Add YAML frontmatter to research markdown files"""

import os
import re
from pathlib import Path

def extract_metadata(filepath, content):
    """Extract metadata from file path and content"""
    path_parts = filepath.parts
    
    # Default metadata
    metadata = {
        'title': '',
        'opportunity_id': '',
        'sector': 'General',
        'role': 'General',
        'capital_level': 'Variable',
        'region': 'National',
        'summary': '',
        'tags': []
    }
    
    # Extract from path
    if 'sectors' in path_parts:
        idx = path_parts.index('sectors')
        if idx + 1 < len(path_parts):
            metadata['sector'] = path_parts[idx + 1].replace('-', ' ').title()
    
    if 'economic-roles' in path_parts:
        idx = path_parts.index('economic-roles')
        if idx + 1 < len(path_parts):
            metadata['role'] = path_parts[idx + 1].replace('-', ' ').title()
    
    if 'regions' in path_parts:
        idx = path_parts.index('regions')
        if idx + 1 < len(path_parts):
            metadata['region'] = path_parts[idx + 1].replace('-', ' ').title()
    
    # Extract from filename
    filename = filepath.stem
    if 'low-capital' in filename:
        metadata['capital_level'] = 'Low'
    elif 'medium-capital' in filename:
        metadata['capital_level'] = 'Medium'
    elif 'high-capital' in filename:
        metadata['capital_level'] = 'High'
    
    # Extract title from first H1
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # Extract summary from first paragraph after title
    summary_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|$)', content, re.MULTILINE | re.DOTALL)
    if summary_match:
        metadata['summary'] = summary_match.group(1).strip().replace('\n', ' ')[:200] + '...'
    
    # Generate ID
    parts = []
    if 'deep-dives' in str(filepath):
        parts.append('DD')
    elif 'enrichments' in str(filepath):
        parts.append('ENR')
    else:
        parts.append('RES')
    
    parts.append(metadata['sector'][:3].upper())
    parts.append(str(len(metadata['title']))[:2])
    metadata['opportunity_id'] = '-'.join(parts)
    
    # Extract tags from content
    tags = set()
    if 'AI' in content or 'artificial intelligence' in content.lower():
        tags.add('AI')
    if 'blockchain' in content.lower():
        tags.add('Blockchain')
    if 'tax' in content.lower():
        tags.add('Tax Benefits')
    if '$' in content and ('billion' in content.lower() or 'million' in content.lower()):
        tags.add('Funding')
    if 'opportunity zone' in content.lower():
        tags.add('Opportunity Zones')
    if 'QSBS' in content:
        tags.add('QSBS')
    if 'agriculture' in content.lower() or 'farm' in content.lower():
        tags.add('Agriculture')
    if 'defense' in content.lower() or 'military' in content.lower():
        tags.add('Defense')
    
    metadata['tags'] = sorted(list(tags))
    
    return metadata

def add_frontmatter(filepath):
    """Add YAML frontmatter to a markdown file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Skip if already has frontmatter
    if content.strip().startswith('---'):
        print(f"Skipping {filepath} - already has frontmatter")
        return
    
    # Extract metadata
    metadata = extract_metadata(filepath, content)
    
    # Build frontmatter
    frontmatter = ['---']
    for key, value in metadata.items():
        if isinstance(value, list):
            if value:
                frontmatter.append(f'{key}:')
                for item in value:
                    frontmatter.append(f'  - "{item}"')
            else:
                frontmatter.append(f'{key}: []')
        else:
            # Escape quotes in strings
            if isinstance(value, str) and '"' in value:
                value = value.replace('"', '\\"')
            frontmatter.append(f'{key}: "{value}"')
    frontmatter.append('---')
    frontmatter.append('')
    
    # Write back with frontmatter
    new_content = '\n'.join(frontmatter) + content
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"Added frontmatter to {filepath}")

def main():
    research_dir = Path('research')
    
    # Find all markdown files
    md_files = list(research_dir.rglob('*.md'))
    
    print(f"Found {len(md_files)} markdown files")
    
    for filepath in md_files:
        add_frontmatter(filepath)
    
    print("\nFrontmatter addition complete!")

if __name__ == '__main__':
    main()