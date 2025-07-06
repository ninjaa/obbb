#!/usr/bin/env python3
"""
Verify claims made in research documents against source material.
Prevents reward hacking and overestimation.
"""

import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

class ClaimVerifier:
    def __init__(self, bill_path: str):
        self.bill_path = Path(bill_path)
        self.bill_content = self.bill_path.read_text()
        self.bill_lines = self.bill_content.split('\n')
        
    def verify_dollar_amounts(self, research_dir: Path) -> Dict[str, List[Dict]]:
        """Verify all dollar amounts claimed in research files."""
        results = defaultdict(list)
        
        # Pattern to find dollar amounts in research files
        dollar_pattern = r'\$[\d,]+(?:\.\d+)?(?:[BMK]|\s*(?:billion|million|thousand))?'
        
        for md_file in research_dir.rglob('*.md'):
            content = md_file.read_text()
            
            # Find all dollar claims
            for match in re.finditer(dollar_pattern, content):
                amount = match.group()
                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content[start:end].replace('\n', ' ')
                
                # Convert shorthand to full numbers for searching
                search_amounts = [amount]
                
                # Convert $7.5B to 7,500,000,000 etc
                if 'B' in amount or 'billion' in amount.lower():
                    num = re.search(r'[\d.]+', amount)
                    if num:
                        val = float(num.group()) * 1_000_000_000
                        search_amounts.append(f"{int(val):,}")
                elif 'M' in amount or 'million' in amount.lower():
                    num = re.search(r'[\d.]+', amount)
                    if num:
                        val = float(num.group()) * 1_000_000
                        search_amounts.append(f"{int(val):,}")
                elif 'K' in amount or 'thousand' in amount.lower():
                    num = re.search(r'[\d.]+', amount)
                    if num:
                        val = float(num.group()) * 1_000
                        search_amounts.append(f"{int(val):,}")
                
                # Check if this amount appears in the bill
                bill_matches = []
                for search_amt in search_amounts:
                    for i, line in enumerate(self.bill_lines):
                        if search_amt.replace('$', '').replace(',', '') in line.replace(',', ''):
                            bill_matches.append({
                                'line_number': i + 1,
                                'line_content': line.strip()
                            })
                            if len(bill_matches) >= 3:
                                break
                
                results[str(md_file)].append({
                    'amount': amount,
                    'context': context,
                    'verified': len(bill_matches) > 0,
                    'bill_matches': bill_matches[:3]  # First 3 matches
                })
        
        return results
    
    def verify_section_references(self, research_dir: Path) -> Dict[str, List[Dict]]:
        """Verify all section references exist in the bill."""
        results = defaultdict(list)
        
        # Pattern to find section references
        section_pattern = r'Section\s+(\d+(?:\.\d+)?(?:\([a-z]\))?)'
        
        for md_file in research_dir.rglob('*.md'):
            content = md_file.read_text()
            
            for match in re.finditer(section_pattern, content, re.IGNORECASE):
                section = match.group(1)
                
                # Check if section exists in bill
                section_exists = False
                section_id_pattern = f'id="[^"]*{section}[^"]*"'
                if re.search(section_id_pattern, self.bill_content, re.IGNORECASE):
                    section_exists = True
                
                results[str(md_file)].append({
                    'section': section,
                    'verified': section_exists,
                    'context': content[max(0, match.start()-30):match.end()+30]
                })
        
        return results
    
    def calculate_metrics(self, research_dir: Path) -> Dict:
        """Calculate accuracy metrics for our research."""
        metrics = {
            'total_files': 0,
            'total_claims': 0,
            'verified_claims': 0,
            'unverified_claims': 0,
            'files_with_issues': []
        }
        
        # Check dollar amounts
        dollar_results = self.verify_dollar_amounts(research_dir)
        for file, claims in dollar_results.items():
            metrics['total_files'] += 1
            for claim in claims:
                metrics['total_claims'] += 1
                if claim['verified']:
                    metrics['verified_claims'] += 1
                else:
                    metrics['unverified_claims'] += 1
                    if file not in metrics['files_with_issues']:
                        metrics['files_with_issues'].append(file)
        
        metrics['accuracy_rate'] = (
            metrics['verified_claims'] / metrics['total_claims'] * 100 
            if metrics['total_claims'] > 0 else 0
        )
        
        return metrics

def main():
    verifier = ClaimVerifier('BILLS-119hr1eas.html')
    research_dir = Path('research')
    
    print("=== Claim Verification Report ===\n")
    
    # Verify dollar amounts
    print("1. Dollar Amount Verification:")
    dollar_results = verifier.verify_dollar_amounts(research_dir)
    
    unverified_count = 0
    for file, claims in dollar_results.items():
        unverified = [c for c in claims if not c['verified']]
        if unverified:
            print(f"\n{Path(file).name}:")
            for claim in unverified[:5]:  # Show first 5
                print(f"  ❌ {claim['amount']} - NOT FOUND IN BILL")
                print(f"     Context: ...{claim['context']}...")
            unverified_count += len(unverified)
    
    if unverified_count == 0:
        print("  ✅ All dollar amounts verified!")
    
    # Calculate metrics
    print("\n2. Overall Metrics:")
    metrics = verifier.calculate_metrics(research_dir)
    print(f"  Total claims checked: {metrics['total_claims']}")
    print(f"  Verified claims: {metrics['verified_claims']}")
    print(f"  Unverified claims: {metrics['unverified_claims']}")
    print(f"  Accuracy rate: {metrics['accuracy_rate']:.1f}%")
    
    if metrics['files_with_issues']:
        print("\n3. Files needing review:")
        for file in metrics['files_with_issues']:
            print(f"  - {Path(file).name}")

if __name__ == "__main__":
    main()