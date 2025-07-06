#!/usr/bin/env python3
"""
Smart parser that leverages the bill's structure for targeted analysis
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

class SmartOBBBParser:
    def __init__(self):
        self.bill_sections = {}
        self.profit_vectors = []
        
    def extract_toc(self, html_content: str) -> dict:
        """Extract table of contents with section links"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        toc = {}
        current_title = None
        
        # Find all TOC entries
        toc_links = soup.find_all('a', href=lambda x: x and x.startswith('#toc-'))
        
        for link in toc_links:
            text = link.get_text().strip()
            href = link.get('href')
            
            if 'TITLE' in text:
                current_title = text
                toc[current_title] = {'sections': [], 'href': href}
            elif current_title and 'Sec.' in text:
                toc[current_title]['sections'].append({
                    'text': text,
                    'href': href
                })
        
        return toc
    
    def extract_section_by_id(self, html_content: str, section_id: str) -> str:
        """Extract specific section content by ID"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the section anchor
        anchor_id = section_id.replace('#toc-', '')
        anchor = soup.find('a', id=anchor_id)
        if not anchor:
            return ""
        
        # Get the parent element that contains the section
        section_parent = anchor.find_parent(['div', 'section', 'p'])
        if not section_parent:
            section_parent = anchor.parent
        
        # Extract text from the section and following elements
        section_text = []
        current = section_parent
        
        # Get up to 5 following elements to capture section content
        for i in range(5):
            if current:
                text = current.get_text() if hasattr(current, 'get_text') else str(current)
                section_text.append(text)
                current = current.next_sibling
            else:
                break
        
        return ' '.join(section_text).strip()
    
    def identify_profit_keywords(self, text: str) -> list:
        """Identify profit-relevant keywords in text"""
        profit_keywords = [
            r'\$[\d,]+\s*(?:billion|million|thousand)',  # Dollar amounts
            r'appropriat\w+',  # Appropriations
            r'grant\w*',  # Grants
            r'contract\w*',  # Contracts
            r'fund\w*',  # Funding
            r'invest\w*',  # Investment
            r'credit\w*',  # Tax credits
            r'deduction\w*',  # Deductions
            r'exemption\w*',  # Exemptions
            r'incentive\w*',  # Incentives
            r'subsid\w*',  # Subsidies
            r'loan\w*',  # Loans
            r'benefit\w*',  # Benefits
        ]
        
        matches = []
        for keyword in profit_keywords:
            matches.extend(re.findall(keyword, text, re.IGNORECASE))
        
        return matches
    
    def smart_parse_bill(self, bill_path: str) -> dict:
        """Parse bill intelligently by sections"""
        with open(bill_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract table of contents
        toc = self.extract_toc(html_content)
        
        # Parse high-value sections first
        high_value_titles = [
            'TITLE II—COMMITTEE ON ARMED SERVICES',  # Defense spending
            'TITLE VII—FINANCE',  # Tax changes
            'TITLE III—COMMITTEE ON BANKING',  # Financial opportunities
            'TITLE V—COMMITTEE ON ENERGY',  # Energy opportunities
        ]
        
        parsed_sections = {}
        
        for title in high_value_titles:
            if title in toc:
                title_data = {'sections': {}}
                
                for section in toc[title]['sections'][:5]:  # Limit to first 5 sections
                    section_id = section['href']
                    section_text = self.extract_section_by_id(html_content, section_id)
                    
                    if section_text:
                        profit_keywords = self.identify_profit_keywords(section_text)
                        
                        title_data['sections'][section['text']] = {
                            'text': section_text[:1000],  # First 1000 chars
                            'profit_keywords': profit_keywords,
                            'word_count': len(section_text.split())
                        }
                
                parsed_sections[title] = title_data
        
        return parsed_sections

def main():
    parser = SmartOBBBParser()
    
    # Parse the bill intelligently
    sections = parser.smart_parse_bill('./BILLS-119hr1eas.html')
    
    # Save parsed sections
    with open('./data/parsed_sections.json', 'w') as f:
        json.dump(sections, f, indent=2)
    
    print("Smart parsing complete!")
    print(f"Parsed {len(sections)} high-value titles")
    
    # Show sample results
    for title, data in sections.items():
        print(f"\n{title}:")
        print(f"  - {len(data['sections'])} sections parsed")
        
        for section_name, section_data in data['sections'].items():
            if section_data['profit_keywords']:
                print(f"  - {section_name}: {len(section_data['profit_keywords'])} profit keywords")

if __name__ == "__main__":
    main()