#!/usr/bin/env python3
"""Fast GraphRAG lite version - process key documents only"""

from fast_graphrag import GraphRAG, DefaultLLMService, DefaultEmbeddingService
import os
from pathlib import Path
import asyncio
import yaml

async def main():
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        return
    
    # Configure services
    llm_service = DefaultLLMService(
        model="o4-mini",
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    embedding_service = DefaultEmbeddingService(
        model="text-embedding-3-small",
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Initialize GraphRAG
    config = GraphRAG.Config(
        llm_service=llm_service,
        embedding_service=embedding_service
    )
    
    grag = GraphRAG(
        working_dir="./graphrag_workspace_lite",
        domain="Investment opportunities and tax benefits from HR119 (One Big Beautiful Bill)",
        example_queries="""
        - What opportunities can be stacked with Opportunity Zones?
        - How can I maximize returns with $400K investment?
        - What are the time-sensitive opportunities before 2026?
        """,
        entity_types=[
            "OPPORTUNITY", "TAX_BENEFIT", "PROGRAM", "FUNDING_SOURCE",
            "LOCATION", "SECTOR", "REQUIREMENT", "DEADLINE", "AGENCY"
        ],
        config=config
    )
    
    # Load only key documents
    key_docs = [
        "research/nyc-investor-quick-start.md",
        "research/opportunity-stack-ranking.md",
        "research/enrichments/opportunity-zones-nyc-playbook.md",
        "research/enrichments/agricultural-subsidies-nyc-playbook.md",
        "research/enrichments/qsbs-75m-arbitrage-guide.md"
    ]
    
    print("Loading key documents...")
    for i, doc_path in enumerate(key_docs):
        path = Path(doc_path)
        if path.exists():
            with open(path, 'r') as f:
                content = f.read()
            
            # Skip frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2]
            
            print(f"Processing {i+1}/{len(key_docs)}: {path.name}")
            await grag.async_insert(content)
    
    print("\nRunning focused queries...")
    
    queries = [
        "What are the top 3 opportunities for a NYC investor with $400K?",
        "How do I stack Opportunity Zones with agricultural subsidies?",
        "What deadlines are coming up before July 2026?",
        "What's the exact structure to combine QSBS with OZ investments?",
        "What are the highest ROI opportunities that require less than $100K?"
    ]
    
    results = []
    for query in queries:
        print(f"\nQ: {query}")
        result = await grag.async_query(query, mode='hybrid')
        print(f"A: {result.response}")
        results.append({
            'query': query,
            'answer': result.response
        })
    
    # Save results
    with open('graphrag_results_lite.yaml', 'w') as f:
        yaml.dump(results, f, default_flow_style=False)
    
    print("\n\nResults saved to graphrag_results_lite.yaml")
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE - Type 'quit' to exit")
    print("="*80)
    
    while True:
        query = input("\nEnter query (or 'quit'): ").strip()
        if query.lower() == 'quit':
            break
        
        if query:
            result = await grag.async_query(query, mode='hybrid')
            print(f"\nAnswer: {result.response}")

if __name__ == "__main__":
    asyncio.run(main())