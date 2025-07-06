#!/usr/bin/env python3
"""Generate a simple static HTML site from the research markdown files"""

import os
import json
import markdown
from pathlib import Path
from datetime import datetime

def load_template():
    """Load or create basic HTML template"""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - OBBB Research</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin-left: 0;
            padding-left: 20px;
            color: #666;
        }}
        .nav {{
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
            margin: -20px -20px 20px -20px;
            border-radius: 10px 10px 0 0;
        }}
        .nav a {{
            color: white;
            margin-right: 20px;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }}
        .tag {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #f4f4f4;
            font-weight: bold;
        }}
        .opportunity-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            background: #f9f9f9;
        }}
        .opportunity-card h3 {{
            margin-top: 0;
            color: #2980b9;
        }}
        .returns {{
            color: #27ae60;
            font-weight: bold;
        }}
        .action-required {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">Home</a>
        <a href="master-index.html">All Research</a>
        <a href="nyc-investor-quick-start.html">Quick Start</a>
        <a href="opportunities.html">Search</a>
    </div>
    <div class="container">
        {content}
    </div>
    <script>
        // Add copy button to code blocks
        document.querySelectorAll('pre').forEach(pre => {{
            const button = document.createElement('button');
            button.textContent = 'Copy';
            button.style.position = 'absolute';
            button.style.right = '10px';
            button.style.top = '10px';
            button.style.fontSize = '12px';
            button.onclick = () => {{
                navigator.clipboard.writeText(pre.textContent);
                button.textContent = 'Copied!';
                setTimeout(() => button.textContent = 'Copy', 2000);
            }};
            pre.style.position = 'relative';
            pre.appendChild(button);
        }});
    </script>
</body>
</html>"""
    return template

def convert_markdown_to_html(md_path, template):
    """Convert a markdown file to HTML"""
    with open(md_path, 'r') as f:
        content = f.read()
    
    # Extract frontmatter
    metadata = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            import yaml
            metadata = yaml.safe_load(parts[1])
            content = parts[2]
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    html_content = md.convert(content)
    
    # Add metadata section if available
    if metadata:
        meta_html = '<div class="metadata">'
        if metadata.get('sector'):
            meta_html += f'<strong>Sector:</strong> {metadata["sector"]} | '
        if metadata.get('capital_level'):
            meta_html += f'<strong>Capital Required:</strong> {metadata["capital_level"]} | '
        if metadata.get('tags'):
            meta_html += '<strong>Tags:</strong> '
            for tag in metadata['tags']:
                meta_html += f'<span class="tag">{tag}</span>'
        meta_html += '</div>'
        html_content = meta_html + html_content
    
    # Fill template
    title = metadata.get('title', md_path.stem.replace('-', ' ').title())
    return template.format(title=title, content=html_content)

def create_search_page(opportunities, template):
    """Create a searchable opportunities page"""
    content = """
    <h1>Search Opportunities</h1>
    <input type="text" id="search" placeholder="Search opportunities..." style="width: 100%; padding: 10px; margin: 20px 0; border: 1px solid #ddd; border-radius: 5px;">
    
    <div id="filters" style="margin-bottom: 20px;">
        <label><input type="checkbox" class="tag-filter" value="Tax Benefits"> Tax Benefits</label>
        <label><input type="checkbox" class="tag-filter" value="Funding"> Funding</label>
        <label><input type="checkbox" class="tag-filter" value="Agriculture"> Agriculture</label>
        <label><input type="checkbox" class="tag-filter" value="Defense"> Defense</label>
        <label><input type="checkbox" class="tag-filter" value="Opportunity Zones"> Opportunity Zones</label>
        <label><input type="checkbox" class="tag-filter" value="QSBS"> QSBS</label>
    </div>
    
    <div id="results"></div>
    
    <script>
    const opportunities = """ + json.dumps(opportunities) + """;
    
    function renderOpportunities(filtered) {
        const results = document.getElementById('results');
        results.innerHTML = '';
        
        filtered.forEach(opp => {
            const card = document.createElement('div');
            card.className = 'opportunity-card';
            card.innerHTML = `
                <h3><a href="${opp.file_path.replace('.md', '.html')}">${opp.title}</a></h3>
                <p>${opp.summary || 'No summary available'}</p>
                <div>
                    <strong>Sector:</strong> ${opp.sector} | 
                    <strong>Category:</strong> ${opp.category}
                    ${opp.tags ? ' | <strong>Tags:</strong> ' + opp.tags.map(t => `<span class="tag">${t}</span>`).join('') : ''}
                </div>
            `;
            results.appendChild(card);
        });
        
        if (filtered.length === 0) {
            results.innerHTML = '<p>No opportunities match your search.</p>';
        }
    }
    
    function filterOpportunities() {
        const searchTerm = document.getElementById('search').value.toLowerCase();
        const selectedTags = Array.from(document.querySelectorAll('.tag-filter:checked')).map(cb => cb.value);
        
        const filtered = opportunities.filter(opp => {
            const matchesSearch = !searchTerm || 
                opp.title.toLowerCase().includes(searchTerm) ||
                (opp.summary && opp.summary.toLowerCase().includes(searchTerm)) ||
                opp.sector.toLowerCase().includes(searchTerm);
            
            const matchesTags = selectedTags.length === 0 || 
                selectedTags.some(tag => opp.tags && opp.tags.includes(tag));
            
            return matchesSearch && matchesTags;
        });
        
        renderOpportunities(filtered);
    }
    
    document.getElementById('search').addEventListener('input', filterOpportunities);
    document.querySelectorAll('.tag-filter').forEach(cb => {
        cb.addEventListener('change', filterOpportunities);
    });
    
    // Initial render
    renderOpportunities(opportunities);
    </script>
    """
    
    return template.format(title="Search Opportunities", content=content)

def generate_site():
    """Generate the complete static site"""
    # Create output directory
    output_dir = Path('site')
    output_dir.mkdir(exist_ok=True)
    
    # Load template
    template = load_template()
    
    # Load opportunities index
    with open('research/opportunities.json', 'r') as f:
        opportunities = json.load(f)
    
    # Convert all markdown files
    research_dir = Path('research')
    for md_file in research_dir.rglob('*.md'):
        # Calculate relative path for output
        rel_path = md_file.relative_to(research_dir)
        html_path = output_dir / rel_path.with_suffix('.html')
        
        # Create subdirectories if needed
        html_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert and save
        html_content = convert_markdown_to_html(md_file, template)
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        print(f"Generated: {html_path}")
    
    # Create search page
    search_html = create_search_page(opportunities, template)
    with open(output_dir / 'opportunities.html', 'w') as f:
        f.write(search_html)
    
    # Copy JSON files
    import shutil
    shutil.copy('research/opportunities.json', output_dir / 'opportunities.json')
    shutil.copy('research/index-stats.json', output_dir / 'index-stats.json')
    
    print(f"\nSite generated in {output_dir}/")
    print("\nTo view locally, run:")
    print("  cd site && python -m http.server 8000")
    print("Then open http://localhost:8000")

if __name__ == '__main__':
    generate_site()