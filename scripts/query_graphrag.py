#!/usr/bin/env python3
"""Query the GraphRAG knowledge base"""

from fast_graphrag import GraphRAG, DefaultLLMService, DefaultEmbeddingService
import os
import asyncio

async def query_graphrag():
    """Query existing GraphRAG database"""
    
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
        example_queries="What opportunities can be stacked?",
        entity_types=[
            "OPPORTUNITY", "TAX_BENEFIT", "PROGRAM", "FUNDING_SOURCE",
            "LOCATION", "SECTOR", "REQUIREMENT", "DEADLINE", "AGENCY"
        ],
        config=config
    )
    
    print("GraphRAG loaded. Enter queries (type 'quit' to exit)\n")
    
    # Example queries
    examples = [
        "What can I do with $400K in agricultural investments?",
        "How do I stack Opportunity Zones with other programs?",
        "What are the deadlines I need to know about?",
        "Which counties should I target for farmland?",
        "How do I structure QSBS investments?"
    ]
    
    print("Example queries:")
    for i, ex in enumerate(examples, 1):
        print(f"{i}. {ex}")
    print()
    
    while True:
        query = input("\nQuery> ").strip()
        
        if query.lower() == 'quit':
            break
            
        if query.isdigit() and 1 <= int(query) <= len(examples):
            query = examples[int(query) - 1]
            print(f"Using: {query}")
        
        if query:
            try:
                result = await grag.async_query(query, mode='hybrid')
                print(f"\nAnswer: {result.response}\n")
                
                # Show some entities if available
                if hasattr(result, 'context') and result.context.entities:
                    print("Related entities found:")
                    for entity, score in result.context.entities[:3]:
                        print(f"  - {entity.name}: {entity.description}")
                
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(query_graphrag())