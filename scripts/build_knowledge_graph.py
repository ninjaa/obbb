#!/usr/bin/env python3
"""Build a simple knowledge graph from the research data"""

import json
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt

def build_graph():
    """Build knowledge graph from opportunities.json"""
    # Load opportunities
    with open('research/opportunities.json', 'r') as f:
        opportunities = json.load(f)
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes for each opportunity
    for opp in opportunities:
        G.add_node(opp['title'], 
                   type='opportunity',
                   sector=opp.get('sector', 'General'),
                   category=opp.get('category', 'general'),
                   file_path=opp.get('file_path', ''))
    
    # Add sector nodes
    sectors = set(opp.get('sector', 'General') for opp in opportunities)
    for sector in sectors:
        G.add_node(sector, type='sector')
    
    # Add tag nodes
    all_tags = set()
    for opp in opportunities:
        all_tags.update(opp.get('tags', []))
    
    for tag in all_tags:
        G.add_node(tag, type='tag')
    
    # Add edges
    for opp in opportunities:
        # Link to sector
        G.add_edge(opp['title'], opp.get('sector', 'General'), relation='in_sector')
        
        # Link to tags
        for tag in opp.get('tags', []):
            G.add_edge(opp['title'], tag, relation='has_tag')
    
    # Find opportunities that can stack
    stacking_keywords = {
        'Opportunity Zones': ['OZ', 'opportunity zone'],
        'QSBS': ['QSBS', 'qualified small business'],
        'Tax Benefits': ['tax', 'deduction', 'credit'],
        'Agriculture': ['farm', 'agriculture', 'rural'],
        'Defense': ['defense', 'military', 'DoD']
    }
    
    # Add stacking relationships
    for i, opp1 in enumerate(opportunities):
        for j, opp2 in enumerate(opportunities[i+1:], i+1):
            # Check if they share tags that suggest stacking
            tags1 = set(opp1.get('tags', []))
            tags2 = set(opp2.get('tags', []))
            
            if tags1 & tags2:  # Intersection
                G.add_edge(opp1['title'], opp2['title'], 
                          relation='stacks_with',
                          shared_tags=list(tags1 & tags2))
    
    return G, opportunities

def find_stacking_opportunities(G, base_opportunity):
    """Find opportunities that stack with a given one"""
    stacking = []
    
    # Find all nodes connected with 'stacks_with' relation
    for neighbor in G.neighbors(base_opportunity):
        edge_data = G.get_edge_data(base_opportunity, neighbor)
        if edge_data and edge_data.get('relation') == 'stacks_with':
            stacking.append({
                'opportunity': neighbor,
                'shared_tags': edge_data.get('shared_tags', [])
            })
    
    # Also check reverse direction
    for predecessor in G.predecessors(base_opportunity):
        edge_data = G.get_edge_data(predecessor, base_opportunity)
        if edge_data and edge_data.get('relation') == 'stacks_with':
            stacking.append({
                'opportunity': predecessor,
                'shared_tags': edge_data.get('shared_tags', [])
            })
    
    return stacking

def query_graph(G, opportunities):
    """Example queries against the graph"""
    print("=== Knowledge Graph Analysis ===\n")
    
    # 1. Find all opportunities in Agriculture sector
    print("1. Agriculture Sector Opportunities:")
    ag_opps = [n for n, d in G.nodes(data=True) 
               if d.get('type') == 'opportunity' and d.get('sector') == 'Agriculture']
    for opp in ag_opps[:5]:
        print(f"   - {opp}")
    print()
    
    # 2. Find opportunities with multiple tags
    print("2. Opportunities with 3+ Tags (High Complexity):")
    multi_tag = []
    for opp in opportunities:
        if len(opp.get('tags', [])) >= 3:
            multi_tag.append((opp['title'], len(opp['tags'])))
    
    for title, tag_count in sorted(multi_tag, key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {title} ({tag_count} tags)")
    print()
    
    # 3. Find stacking opportunities
    print("3. Best Stacking Opportunities:")
    oz_title = "Opportunity Zones Made Permanent - The $100B+ Tax Haven Nobody's Talking About"
    if G.has_node(oz_title):
        stacking = find_stacking_opportunities(G, oz_title)
        print(f"   Opportunities that stack with Opportunity Zones:")
        for stack in stacking[:5]:
            print(f"   - {stack['opportunity'][:50]}...")
            print(f"     Shared: {', '.join(stack['shared_tags'])}")
    print()
    
    # 4. Find central nodes (most connected)
    print("4. Most Connected Opportunities (Hub Nodes):")
    centrality = nx.degree_centrality(G)
    opp_centrality = [(n, c) for n, c in centrality.items() 
                      if G.nodes[n].get('type') == 'opportunity']
    
    for node, cent in sorted(opp_centrality, key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {node[:50]}... (centrality: {cent:.3f})")
    print()
    
    # 5. Sector analysis
    print("5. Opportunities by Sector:")
    sector_counts = {}
    for opp in opportunities:
        sector = opp.get('sector', 'General')
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {sector}: {count} opportunities")

def save_graph_data(G):
    """Save graph in multiple formats"""
    # Save as GraphML for import into graph databases
    nx.write_graphml(G, 'research/knowledge_graph.graphml')
    
    # Save as JSON for web visualization
    data = nx.node_link_data(G)
    with open('research/knowledge_graph.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\nGraph data saved:")
    print("- research/knowledge_graph.graphml (for Neo4j import)")
    print("- research/knowledge_graph.json (for D3.js visualization)")

def main():
    """Build and analyze the knowledge graph"""
    G, opportunities = build_graph()
    
    print(f"Built knowledge graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n")
    
    # Run example queries
    query_graph(G, opportunities)
    
    # Save graph data
    save_graph_data(G)
    
    # Simple stats
    print(f"\nGraph Statistics:")
    print(f"- Nodes: {G.number_of_nodes()}")
    print(f"- Edges: {G.number_of_edges()}")
    print(f"- Opportunity nodes: {len([n for n, d in G.nodes(data=True) if d.get('type') == 'opportunity'])}")
    print(f"- Sector nodes: {len([n for n, d in G.nodes(data=True) if d.get('type') == 'sector'])}")
    print(f"- Tag nodes: {len([n for n, d in G.nodes(data=True) if d.get('type') == 'tag'])}")

if __name__ == '__main__':
    main()