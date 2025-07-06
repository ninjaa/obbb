#!/usr/bin/env python3
"""Setup Fast GraphRAG for OBBB research knowledge graph"""

import os
import json
from pathlib import Path

def create_graphrag_config():
    """Create configuration for Fast GraphRAG"""
    config = {
        "llm": {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "embedding": {
            "model": "text-embedding-3-small",
            "dimension": 1536
        },
        "graph": {
            "entity_types": [
                "OPPORTUNITY",
                "SECTOR", 
                "PROGRAM",
                "FUNDING_SOURCE",
                "TAX_BENEFIT",
                "LOCATION",
                "CAPITAL_REQUIREMENT",
                "GOVERNMENT_AGENCY"
            ],
            "relation_types": [
                "STACKS_WITH",
                "REQUIRES",
                "PROVIDES",
                "LOCATED_IN",
                "ADMINISTERED_BY",
                "QUALIFIES_FOR",
                "COMBINES_WITH"
            ]
        },
        "indexing": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "max_entities_per_chunk": 10
        }
    }
    
    with open('graphrag_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Created GraphRAG configuration")
    return config

def prepare_documents():
    """Prepare documents for GraphRAG ingestion"""
    documents = []
    
    # Load all markdown files
    research_dir = Path('research')
    for md_file in research_dir.rglob('*.md'):
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Skip if it's just an index
        if len(content) < 500:
            continue
            
        # Extract metadata from frontmatter
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                metadata = yaml.safe_load(parts[1])
                content = parts[2]
        
        doc = {
            "id": str(md_file.relative_to(research_dir)),
            "title": metadata.get('title', md_file.stem),
            "content": content,
            "metadata": {
                "sector": metadata.get('sector', 'General'),
                "tags": metadata.get('tags', []),
                "category": metadata.get('category', 'general'),
                "file_path": str(md_file)
            }
        }
        documents.append(doc)
    
    # Save documents for GraphRAG
    with open('graphrag_documents.json', 'w') as f:
        json.dump(documents, f, indent=2)
    
    print(f"Prepared {len(documents)} documents for GraphRAG")
    return documents

def create_graphrag_queries():
    """Create example queries for the knowledge graph"""
    queries = [
        {
            "id": "stack_oz_ag",
            "query": "What opportunities can I stack with Opportunity Zones in rural agricultural areas?",
            "expected_entities": ["OPPORTUNITY_ZONES", "AGRICULTURAL_SUBSIDIES", "RURAL_AREAS"],
            "expected_relations": ["STACKS_WITH", "LOCATED_IN"]
        },
        {
            "id": "nyc_investor_300k",
            "query": "What are the best opportunities for a NYC investor with $300K to invest?",
            "expected_entities": ["NYC", "CAPITAL_300K", "INVESTMENT_OPPORTUNITY"],
            "expected_relations": ["REQUIRES", "QUALIFIES_FOR"]
        },
        {
            "id": "defense_minerals",
            "query": "How can I profit from critical minerals funding through defense contracts?",
            "expected_entities": ["CRITICAL_MINERALS", "DOD", "DEFENSE_CONTRACTS"],
            "expected_relations": ["PROVIDES", "ADMINISTERED_BY"]
        },
        {
            "id": "qsbs_structure",
            "query": "How do I structure investments to maximize the $75M QSBS exemption?",
            "expected_entities": ["QSBS", "TAX_EXEMPTION", "INVESTMENT_STRUCTURE"],
            "expected_relations": ["QUALIFIES_FOR", "REQUIRES"]
        },
        {
            "id": "border_state_stack",
            "query": "What funding opportunities stack together in border states?",
            "expected_entities": ["BORDER_SECURITY", "BORDER_STATES", "FUNDING"],
            "expected_relations": ["STACKS_WITH", "LOCATED_IN", "COMBINES_WITH"]
        }
    ]
    
    with open('graphrag_queries.json', 'w') as f:
        json.dump(queries, f, indent=2)
    
    print(f"Created {len(queries)} example queries")
    return queries

def create_graphrag_script():
    """Create the main GraphRAG implementation script"""
    script = '''#!/usr/bin/env python3
"""Fast GraphRAG implementation for OBBB research"""

from fast_graphrag import GraphRAG, Entity, Relation
import json
import asyncio
from typing import List, Dict, Any

class OBBBGraphRAG:
    def __init__(self, config_path: str = "graphrag_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize GraphRAG
        self.graph = GraphRAG(
            llm_model=self.config["llm"]["model"],
            embedding_model=self.config["embedding"]["model"],
            entity_types=self.config["graph"]["entity_types"],
            relation_types=self.config["graph"]["relation_types"]
        )
    
    async def build_graph(self, documents_path: str = "graphrag_documents.json"):
        """Build the knowledge graph from documents"""
        with open(documents_path, 'r') as f:
            documents = json.load(f)
        
        print(f"Building graph from {len(documents)} documents...")
        
        for doc in documents:
            # Add document to graph
            await self.graph.add_document(
                doc_id=doc["id"],
                content=doc["content"],
                metadata=doc["metadata"]
            )
        
        print("Graph construction complete!")
        
        # Save graph
        await self.graph.save("obbb_knowledge_graph.pkl")
    
    async def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge graph"""
        # Extract entities and relations from question
        entities = await self.graph.extract_entities(question)
        
        # Search graph
        results = await self.graph.search(
            query=question,
            k=10,  # Top 10 results
            include_relations=True
        )
        
        # Generate answer
        answer = await self.graph.generate_answer(
            question=question,
            context=results,
            include_sources=True
        )
        
        return {
            "question": question,
            "entities": entities,
            "answer": answer["text"],
            "sources": answer["sources"],
            "confidence": answer["confidence"]
        }
    
    async def find_stacking_opportunities(self, base_opportunity: str) -> List[Dict]:
        """Find opportunities that stack with a given one"""
        query = f"What opportunities can be combined or stacked with {base_opportunity}?"
        
        results = await self.graph.search_relations(
            source_entity=base_opportunity,
            relation_type="STACKS_WITH",
            k=20
        )
        
        stacking = []
        for result in results:
            stacking.append({
                "opportunity": result.target_entity,
                "relation": result.relation_type,
                "confidence": result.confidence,
                "explanation": result.explanation
            })
        
        return stacking
    
    async def find_by_criteria(self, sector: str = None, 
                              capital_level: str = None,
                              location: str = None) -> List[Dict]:
        """Find opportunities by specific criteria"""
        filters = []
        if sector:
            filters.append(f"sector:{sector}")
        if capital_level:
            filters.append(f"capital:{capital_level}")
        if location:
            filters.append(f"location:{location}")
        
        query = f"Find investment opportunities with filters: {', '.join(filters)}"
        
        results = await self.graph.search(
            query=query,
            filters=filters,
            k=20
        )
        
        return results

async def main():
    """Main execution"""
    # Initialize GraphRAG
    graphrag = OBBBGraphRAG()
    
    # Build graph (only need to do this once)
    # await graphrag.build_graph()
    
    # Load existing graph
    await graphrag.graph.load("obbb_knowledge_graph.pkl")
    
    # Example queries
    print("\\n=== GraphRAG Query Examples ===\\n")
    
    # 1. Stacking opportunities
    print("1. Finding stacking opportunities with Opportunity Zones:")
    stacking = await graphrag.find_stacking_opportunities("Opportunity Zones")
    for opp in stacking[:5]:
        print(f"   - {opp['opportunity']} (confidence: {opp['confidence']:.2f})")
    
    # 2. NYC investor query
    print("\\n2. Opportunities for NYC investor with $300K:")
    result = await graphrag.query(
        "What are the best opportunities for a NYC investor with $300K?"
    )
    print(f"   Answer: {result['answer'][:200]}...")
    print(f"   Sources: {', '.join(result['sources'][:3])}")
    
    # 3. Sector-specific search
    print("\\n3. Agricultural opportunities in border states:")
    ag_opps = await graphrag.find_by_criteria(
        sector="Agriculture",
        location="Border States"
    )
    for opp in ag_opps[:5]:
        print(f"   - {opp['title']}")
    
    # 4. Complex stacking query
    print("\\n4. Complex stacking strategy:")
    result = await graphrag.query(
        "How can I combine QSBS, Opportunity Zones, and agricultural subsidies?"
    )
    print(f"   Strategy: {result['answer'][:300]}...")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open('scripts/run_graphrag.py', 'w') as f:
        f.write(script)
    
    os.chmod('scripts/run_graphrag.py', 0o755)
    print("Created Fast GraphRAG implementation script")

def main():
    """Setup Fast GraphRAG for OBBB research"""
    print("Setting up Fast GraphRAG for OBBB research...\n")
    
    # Create configuration
    create_graphrag_config()
    
    # Prepare documents
    documents = prepare_documents()
    
    # Create example queries
    queries = create_graphrag_queries()
    
    # Create implementation script
    create_graphrag_script()
    
    print("\n=== Setup Complete ===")
    print("\nTo use Fast GraphRAG:")
    print("1. Install: pip install fast-graphrag")
    print("2. Build graph: python scripts/run_graphrag.py --build")
    print("3. Query: python scripts/run_graphrag.py")
    
    print("\nExample queries you can run:")
    for query in queries[:3]:
        print(f"- {query['query']}")

if __name__ == '__main__':
    main()