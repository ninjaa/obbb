#!/usr/bin/env python3
"""Build JSON index from markdown files with frontmatter"""

import os
import re
import json
import yaml
from pathlib import Path

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    if not content.strip().startswith('---'):
        return None, content
    
    # Find the closing ---
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    
    try:
        metadata = yaml.safe_load(parts[1])
        remaining_content = parts[2]
        return metadata, remaining_content
    except:
        return None, content

def build_index():
    """Build opportunities.json from all markdown files"""
    research_dir = Path('research')
    opportunities = []
    
    # Find all markdown files
    md_files = list(research_dir.rglob('*.md'))
    
    for filepath in md_files:
        with open(filepath, 'r') as f:
            content = f.read()
        
        metadata, remaining_content = extract_frontmatter(content)
        
        if metadata:
            # Add file path relative to research dir
            metadata['file_path'] = str(filepath.relative_to(research_dir))
            
            # Extract key insights if not in summary
            if len(metadata.get('summary', '')) < 50:
                # Try to extract first meaningful paragraph
                paragraphs = remaining_content.strip().split('\n\n')
                for para in paragraphs:
                    if len(para) > 50 and not para.startswith('#'):
                        metadata['summary'] = para[:200] + '...'
                        break
            
            # Add category based on path
            if 'deep-dives' in str(filepath):
                metadata['category'] = 'deep-dive'
            elif 'enrichments' in str(filepath):
                metadata['category'] = 'enrichment'
            elif 'sectors' in str(filepath):
                metadata['category'] = 'sector-analysis'
            else:
                metadata['category'] = 'general'
            
            opportunities.append(metadata)
    
    # Sort by category and title
    opportunities.sort(key=lambda x: (x.get('category', ''), x.get('title', '')))
    
    # Write JSON index
    with open('research/opportunities.json', 'w') as f:
        json.dump(opportunities, f, indent=2)
    
    print(f"Built index with {len(opportunities)} opportunities")
    
    # Also create a quick stats summary
    stats = {
        'total_opportunities': len(opportunities),
        'by_category': {},
        'by_sector': {},
        'by_capital_level': {},
        'by_tags': {}
    }
    
    for opp in opportunities:
        # Category stats
        cat = opp.get('category', 'unknown')
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
        
        # Sector stats
        sector = opp.get('sector', 'unknown')
        stats['by_sector'][sector] = stats['by_sector'].get(sector, 0) + 1
        
        # Capital level stats
        capital = opp.get('capital_level', 'unknown')
        stats['by_capital_level'][capital] = stats['by_capital_level'].get(capital, 0) + 1
        
        # Tag stats
        for tag in opp.get('tags', []):
            stats['by_tags'][tag] = stats['by_tags'].get(tag, 0) + 1
    
    with open('research/index-stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\nStats summary:")
    print(json.dumps(stats, indent=2))

if __name__ == '__main__':
    build_index()