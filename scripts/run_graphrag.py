#!/usr/bin/env python3
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
    print("\n=== GraphRAG Query Examples ===\n")
    
    # 1. Stacking opportunities
    print("1. Finding stacking opportunities with Opportunity Zones:")
    stacking = await graphrag.find_stacking_opportunities("Opportunity Zones")
    for opp in stacking[:5]:
        print(f"   - {opp['opportunity']} (confidence: {opp['confidence']:.2f})")
    
    # 2. NYC investor query
    print("\n2. Opportunities for NYC investor with $300K:")
    result = await graphrag.query(
        "What are the best opportunities for a NYC investor with $300K?"
    )
    print(f"   Answer: {result['answer'][:200]}...")
    print(f"   Sources: {', '.join(result['sources'][:3])}")
    
    # 3. Sector-specific search
    print("\n3. Agricultural opportunities in border states:")
    ag_opps = await graphrag.find_by_criteria(
        sector="Agriculture",
        location="Border States"
    )
    for opp in ag_opps[:5]:
        print(f"   - {opp['title']}")
    
    # 4. Complex stacking query
    print("\n4. Complex stacking strategy:")
    result = await graphrag.query(
        "How can I combine QSBS, Opportunity Zones, and agricultural subsidies?"
    )
    print(f"   Strategy: {result['answer'][:300]}...")

if __name__ == "__main__":
    asyncio.run(main())
