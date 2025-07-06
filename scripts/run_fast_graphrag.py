#!/usr/bin/env python3
"""Fast GraphRAG implementation for OBBB research"""

from fast_graphrag import GraphRAG, DefaultLLMService, DefaultEmbeddingService
import os
from pathlib import Path
import asyncio
import yaml
import pickle

class OBBBKnowledgeGraph:
    def __init__(self):
        # Create persistent workspace
        self.workspace_dir = Path("./graphrag_workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        self.db_path = self.workspace_dir / "obbb_graph.pkl"
        
        # Initialize GraphRAG with proper parameters
        self.domain = "Investment opportunities and tax benefits from HR119 (One Big Beautiful Bill)"
        self.example_queries = """
        - What opportunities can be stacked with Opportunity Zones?
        - How can I maximize returns with $400K investment?
        - What are the time-sensitive opportunities before 2026?
        - How do I structure QSBS with other tax benefits?
        """
        self.entity_types = [
            "OPPORTUNITY", "TAX_BENEFIT", "PROGRAM", "FUNDING_SOURCE",
            "LOCATION", "SECTOR", "REQUIREMENT", "DEADLINE", "AGENCY"
        ]
        
        # Configure LLM and Embedding services
        llm_service = DefaultLLMService(
            model="o4-mini",  # Using o4-mini as requested
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        embedding_service = DefaultEmbeddingService(
            model="text-embedding-3-small",
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize GraphRAG with custom config
        config = GraphRAG.Config(
            llm_service=llm_service,
            embedding_service=embedding_service
        )
        
        self.grag = GraphRAG(
            working_dir=str(self.workspace_dir),
            domain=self.domain,
            example_queries=self.example_queries,
            entity_types=self.entity_types,
            n_checkpoints=5,  # Save checkpoints during processing
            config=config
        )
    
    async def load_or_build_graph(self):
        """Load existing graph or build new one"""
        if self.db_path.exists():
            print(f"Loading existing graph from {self.db_path}")
            with open(self.db_path, 'rb') as f:
                self.grag = pickle.load(f)
            print("Graph loaded successfully!")
            return False  # Did not rebuild
        else:
            print("No existing graph found. Building new one...")
            await self.load_documents()
            await self.save_graph()
            return True  # Did rebuild
    
    async def save_graph(self):
        """Save the graph database"""
        print(f"Saving graph to {self.db_path}")
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.grag, f)
        print("Graph saved successfully!")
        
    async def load_documents(self):
        """Load all research documents into GraphRAG"""
        print("Loading research documents...")
        
        research_dir = Path('research')
        documents = []
        
        # Load all markdown files
        for md_file in research_dir.rglob('*.md'):
            # Skip small index files
            if md_file.stat().st_size < 500:
                continue
                
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Extract title from frontmatter or filename
            title = md_file.stem.replace('-', ' ').title()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        metadata = yaml.safe_load(parts[1])
                        title = metadata.get('title', title)
                        content = parts[2]  # Use content after frontmatter
                    except Exception:
                        pass
            
            documents.append({
                'content': content,
                'title': title,
                'path': str(md_file.relative_to(research_dir))
            })
        
        print(f"Found {len(documents)} documents to process")
        
        # Insert documents into GraphRAG
        for i, doc in enumerate(documents):
            print(f"Processing {i+1}/{len(documents)}: {doc['title'][:50]}...")
            await self.grag.async_insert(doc['content'])
        
        print("Document loading complete!")
    
    async def load_bill_sections(self):
        """Load the original bill in sections"""
        bill_path = Path('BILLS-119hr1eas.html')
        if not bill_path.exists():
            print("Bill file not found. Skipping bill processing.")
            return
        
        print("\nProcessing original bill...")
        
        # Read the bill
        with open(bill_path, 'r', encoding='utf-8') as f:
            bill_content = f.read()
        
        # Simple section splitter (you might want to improve this)
        # Split by major section headers
        import re
        
        # Find all section headers
        section_pattern = r'<h\d[^>]*>SEC\. (\d+)\. ([^<]+)</h\d>'
        sections = re.split(section_pattern, bill_content)
        
        # Process sections in chunks
        chunk_size = 50000  # ~50KB chunks to avoid token limits
        current_chunk = ""
        chunk_num = 0
        
        for i in range(0, len(sections), 3):  # Pattern gives us groups of 3
            if i + 2 < len(sections):
                section_num = sections[i + 1]
                section_title = sections[i + 2]
                section_content = sections[i] if i < len(sections) else ""
                
                # Add to current chunk
                section_text = f"\n\nSECTION {section_num}: {section_title}\n{section_content[:10000]}"
                
                if len(current_chunk) + len(section_text) > chunk_size:
                    # Process current chunk
                    chunk_num += 1
                    print(f"Processing bill chunk {chunk_num} ({len(current_chunk)} chars)")
                    await self.grag.async_insert(current_chunk)
                    current_chunk = section_text
                else:
                    current_chunk += section_text
        
        # Process final chunk
        if current_chunk:
            chunk_num += 1
            print(f"Processing final bill chunk {chunk_num}")
            await self.grag.async_insert(current_chunk)
        
        print(f"Bill processing complete! Processed {chunk_num} chunks.")
        
    async def query(self, question, mode='hybrid'):
        """Query the knowledge graph"""
        print(f"\nQuery: {question}")
        print(f"Mode: {mode}\n")
        
        result = await self.grag.async_query(question, mode=mode)
        
        return result
    
    async def focused_queries(self):
        """Run focused, high-value queries only"""
        queries = [
            # Stack maximization
            "What specific programs can be stacked with Opportunity Zones? Include dollar amounts and requirements.",
            
            # Time-sensitive
            "What opportunities require action before July 2026? List specific deadlines.",
            
            # NYC-specific
            "For a NYC investor with $400K, what are the exact steps to capture agricultural base acres?",
            
            # High-ROI combos
            "How do I combine QSBS $75M exemption with Opportunity Zone investments? Specific structure required.",
            
            # Defense + Minerals
            "What are the exact requirements to get DoD critical minerals contracts? Include contact information.",
        ]
        
        results = []
        for query in queries:
            result = await self.query(query, mode='hybrid')
            results.append({
                'query': query,
                'answer': result
            })
        
        # Save results
        output_path = self.workspace_dir / "query_results.yaml"
        with open(output_path, 'w') as f:
            yaml.dump(results, f, default_flow_style=False)
        
        print(f"\nResults saved to {output_path}")
        return results

async def main():
    """Main execution"""
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        return
    
    # Initialize knowledge graph
    kg = OBBBKnowledgeGraph()
    
    # Load or build graph
    rebuilt = await kg.load_or_build_graph()
    
    # If we rebuilt, also process the bill
    if rebuilt:
        # Uncomment to process the bill itself
        # await kg.load_bill_sections()
        # await kg.save_graph()
        pass
    
    # Run focused queries
    print("\n" + "="*80)
    print("FAST GRAPHRAG ANALYSIS - HIGH SIGNAL ONLY")
    print("="*80)
    
    await kg.focused_queries()
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE - Type 'quit' to exit")
    print("="*80)
    
    while True:
        query = input("\nEnter query (or 'quit'): ").strip()
        if query.lower() == 'quit':
            break
        
        if query:
            result = await kg.query(query, mode='hybrid')
            print(f"\nAnswer: {result}")
            
            # Save this query result too
            with open(kg.workspace_dir / "interactive_queries.log", 'a') as f:
                f.write(f"\nQ: {query}\nA: {result}\n" + "-"*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())