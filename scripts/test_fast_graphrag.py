#!/usr/bin/env python3
"""Quick test of Fast GraphRAG"""

from fast_graphrag import GraphRAG, DefaultLLMService, DefaultEmbeddingService
import os
import asyncio

async def test():
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
        working_dir="./test_graphrag",
        domain="Investment opportunities from HR119",
        example_queries="What are the best tax benefits?",
        entity_types=["OPPORTUNITY", "TAX_BENEFIT", "PROGRAM"],
        config=config
    )
    
    # Test with simple content
    print("Inserting test content...")
    await grag.async_insert("""
    Opportunity Zones provide 30% bonus depreciation in rural areas.
    QSBS exemption expanded to $75M from $10M.
    Agricultural subsidies include 30 million new base acres.
    """)
    
    print("Querying...")
    result = await grag.async_query("What tax benefits are available?")
    print(f"Result: {result}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test())