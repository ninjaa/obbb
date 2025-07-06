#!/usr/bin/env python3
"""
Fixed parser that actually extracts section content, not just TOC
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

class FixedOBBBParser:
    def __init__(self):
        self.sections = {}
        
    def extract_real_section_content(self, html_content: str, section_id: str, lines_to_read: int = 200) -> str:
        """Extract actual section content by finding the section anchor and reading following content"""
        lines = html_content.split('\n')
        
        # Find the line with the actual section anchor (not TOC)
        section_start = None
        for i, line in enumerate(lines):
            if f'<a id="{section_id}">' in line:
                section_start = i
                break
        
        if section_start is None:
            return ""
        
        # Read content from that line forward
        section_lines = lines[section_start:section_start + lines_to_read]
        section_text = '\n'.join(section_lines)
        
        # Parse with BeautifulSoup to extract clean text
        soup = BeautifulSoup(section_text, 'html.parser')
        return soup.get_text().strip()
    
    def extract_dollar_amounts(self, text: str) -> list:
        """Extract specific dollar amounts from text"""
        # Pattern for dollar amounts like $1,000,000,000 or $250,000,000
        dollar_pattern = r'\$[\d,]+,\d{3}'
        amounts = re.findall(dollar_pattern, text)
        return amounts
    
    def parse_defense_sections(self, html_content: str) -> dict:
        """Parse specific defense sections with real content"""
        defense_sections = {
            "HF68BCB652FA44E10B98CF72B11D49961": "Sec. 20001. Enhancement of Department of Defense resources for improving the quality of life for military personnel",
            "HBCAA2FA1DBA0421B80E96E87F73E7FD0": "Sec. 20002. Enhancement of Department of Defense resources for shipbuilding",
            "H8B8A3B4A01C8423F8607496E64FEAA51": "Sec. 20003. Enhancement of Department of Defense resources for integrated air and missile defense",
            "HF394A39A4652435A9BB575302C66263A": "Sec. 20004. Enhancement of Department of Defense resources for munitions and defense supply chain resiliency",
            "H7184360F03264307AD5B99EF90CBF2F7": "Sec. 20005. Enhancement of Department of Defense resources for scaling low-cost weapons into production"
        }
        
        parsed_sections = {}
        
        for section_id, section_title in defense_sections.items():
            content = self.extract_real_section_content(html_content, section_id)
            
            if content:
                dollar_amounts = self.extract_dollar_amounts(content)
                
                parsed_sections[section_title] = {
                    'content': content[:2000],  # First 2000 chars
                    'dollar_amounts': dollar_amounts,
                    'total_funding': len(dollar_amounts),
                    'word_count': len(content.split())
                }
        
        return parsed_sections
    
    def find_major_funding_lines(self, text: str) -> list:
        """Extract lines that contain major funding allocations"""
        lines = text.split('\n')
        funding_lines = []
        
        for line in lines:
            if '$' in line and any(keyword in line.lower() for keyword in ['million', 'billion', 'for']):
                # Clean up the line
                clean_line = re.sub(r'<[^>]+>', '', line).strip()
                if clean_line and len(clean_line) > 20:  # Filter out short/empty lines
                    funding_lines.append(clean_line)
        
        return funding_lines[:10]  # Top 10 funding lines

def main():
    parser = FixedOBBBParser()
    
    with open('./BILLS-119hr1eas.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse defense sections with real content
    defense_data = parser.parse_defense_sections(html_content)
    
    # Save real parsed data
    with open('./data/real_defense_data.json', 'w') as f:
        json.dump(defense_data, f, indent=2)
    
    print("Fixed parsing complete!")
    print(f"Parsed {len(defense_data)} defense sections with real content")
    
    # Show actual findings
    for title, data in defense_data.items():
        print(f"\n{title}:")
        print(f"  - Dollar amounts found: {data['total_funding']}")
        print(f"  - Word count: {data['word_count']}")
        if data['dollar_amounts']:
            print(f"  - Sample amounts: {data['dollar_amounts'][:3]}")
        
        # Show major funding lines
        funding_lines = parser.find_major_funding_lines(data['content'])
        if funding_lines:
            print(f"  - Major funding lines:")
            for line in funding_lines[:3]:
                print(f"    * {line}")

if __name__ == "__main__":
    main()