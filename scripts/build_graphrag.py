#!/usr/bin/env python3
"""
Build GraphRAG knowledge graph from One Big Beautiful Bill
"""
import os
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from fast_graphrag import GraphRAG
from dotenv import load_dotenv

load_dotenv()

class OBBBGraphRAG:
    def __init__(self, working_dir: str = "./data/graphrag"):
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Define entity types specific to bill analysis
        self.entity_types = [
            "Company",           # Contractors, corporations
            "Agency",            # Government agencies
            "Program",           # Government programs
            "Amount",            # Funding amounts
            "Location",          # Geographic regions
            "Timeframe",         # Implementation dates
            "Requirement",       # Eligibility criteria
            "Opportunity",       # Profit vectors
            "Sector",            # Industry sectors
            "Role"               # Economic roles
        ]
        
        self.grag = GraphRAG(
            working_dir=str(self.working_dir),
            domain="Analyze profit opportunities in federal legislation",
            entity_types=self.entity_types,
            # Add custom prompts for better entity extraction
            extraction_prompt_template="""
            You are analyzing federal legislation to identify profit opportunities.
            Focus on extracting entities that represent:
            - Companies and contractors mentioned
            - Government agencies and programs
            - Funding amounts and budgets
            - Geographic regions and locations
            - Implementation timeframes
            - Business opportunities and profit vectors
            - Requirements and eligibility criteria
            
            Extract entities from this text: {text}
            """
        )
    
    def preprocess_bill(self, bill_path: str) -> str:
        """Convert HTML bill to clean text"""
        with open(bill_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 10000) -> list[str]:
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    async def build_knowledge_graph(self, bill_path: str):
        """Build knowledge graph from bill text"""
        print("Preprocessing bill text...")
        text = self.preprocess_bill(bill_path)
        
        print("Chunking text...")
        chunks = self.chunk_text(text)
        
        print(f"Processing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            await self.grag.ainsert(chunk)
        
        print("Knowledge graph built successfully!")
    
    async def query_opportunities(self, query: str) -> str:
        """Query the knowledge graph for profit opportunities"""
        return await self.grag.aquery(query)
    
    def get_graph_stats(self) -> dict:
        """Get statistics about the knowledge graph"""
        # This would need to be implemented based on fast-graphrag's API
        return {
            "entities": "TBD",
            "relationships": "TBD",
            "chunks_processed": "TBD"
        }

async def main():
    """Main function to build the knowledge graph"""
    bill_path = "./BILLS-119hr1eas.html"
    
    if not os.path.exists(bill_path):
        print(f"Bill file not found at {bill_path}")
        return
    
    print("Building OBBB Knowledge Graph...")
    obbb = OBBBGraphRAG()
    
    await obbb.build_knowledge_graph(bill_path)
    
    # Test with a sample query
    print("\nTesting with sample query...")
    result = await obbb.query_opportunities(
        "What are the major defense spending opportunities for contractors?"
    )
    print("Sample query result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())