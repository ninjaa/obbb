#!/usr/bin/env python3
"""
Interactive browser for OBBB profit opportunities
"""
import asyncio
import streamlit as st
from scripts.build_graphrag import OBBBGraphRAG
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class OBBBBrowser:
    def __init__(self):
        self.grag = OBBBGraphRAG()
    
    async def search_opportunities(self, query: str) -> str:
        """Search for profit opportunities"""
        return await self.grag.query_opportunities(query)
    
    def get_predefined_queries(self) -> dict:
        """Get predefined queries for common use cases"""
        return {
            "High-Capital Opportunities": "What are the largest funding opportunities requiring significant capital investment?",
            "NYC Real Estate": "What opportunities exist for New York City real estate investors and developers?",
            "Defense Contractors": "What defense spending opportunities are available for contractors?",
            "Border Security": "What border security and immigration enforcement opportunities exist?",
            "Tax Benefits": "What tax benefits are available for households earning $250K-400K?",
            "Healthcare Disruption": "What opportunities exist from healthcare market disruption?",
            "Small Business": "What opportunities are available for small businesses and consultants?",
            "Tech Opportunities": "What technology and government contracting opportunities exist?",
            "Regional Analysis": "What are the regional differences in profit opportunities?",
            "Timeline Analysis": "What is the implementation timeline for major opportunities?"
        }

def create_streamlit_app():
    """Create Streamlit web interface"""
    st.set_page_config(
        page_title="OBBB Profit Opportunities Browser",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("🏛️ One Big Beautiful Bill - Profit Opportunities Browser")
    st.markdown("*Co-authored with Claude (Anthropic) for AI-assisted analysis*")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    browser = OBBBBrowser()
    
    # Search interface
    st.header("🔍 Search Opportunities")
    
    # Predefined queries
    st.subheader("Quick Searches")
    queries = browser.get_predefined_queries()
    
    selected_query = st.selectbox("Select a predefined query:", list(queries.keys()))
    
    if st.button("Run Quick Search"):
        with st.spinner("Searching knowledge graph..."):
            result = asyncio.run(browser.search_opportunities(queries[selected_query]))
            st.markdown("### Results:")
            st.markdown(result)
    
    # Custom query
    st.subheader("Custom Query")
    custom_query = st.text_area("Enter your custom query:", height=100)
    
    if st.button("Search Custom Query"):
        if custom_query:
            with st.spinner("Searching knowledge graph..."):
                result = asyncio.run(browser.search_opportunities(custom_query))
                st.markdown("### Results:")
                st.markdown(result)
        else:
            st.warning("Please enter a query first.")
    
    # Graph statistics
    st.sidebar.header("📊 Graph Statistics")
    stats = browser.grag.get_graph_stats()
    for key, value in stats.items():
        st.sidebar.metric(key.replace("_", " ").title(), value)
    
    # Export options
    st.sidebar.header("📤 Export Options")
    if st.sidebar.button("Export to Markdown"):
        st.sidebar.success("Export functionality coming soon!")
    
    if st.sidebar.button("Generate Report"):
        st.sidebar.success("Report generation coming soon!")

def create_jupyter_interface():
    """Create Jupyter notebook interface"""
    notebook_content = '''
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# OBBB Profit Opportunities - Interactive Analysis\\n",
    "*Co-authored with Claude (Anthropic)*"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Import libraries\\n",
    "import asyncio\\n",
    "from scripts.build_graphrag import OBBBGraphRAG\\n",
    "import pandas as pd\\n",
    "import matplotlib.pyplot as plt\\n",
    "\\n",
    "# Initialize GraphRAG\\n",
    "obbb = OBBBGraphRAG()\\n",
    "print(\\"Knowledge graph loaded!\\")\\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Helper function for queries\\n",
    "async def query(question: str):\\n",
    "    result = await obbb.query_opportunities(question)\\n",
    "    print(f\\"Query: {question}\\")\\n",
    "    print(f\\"Result: {result}\\")\\n",
    "    return result\\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "# Example queries\\n",
    "queries = [\\n",
    "    \\"What are the top 5 largest funding opportunities?\\",\\n",
    "    \\"Which opportunities are best for NYC-based investors?\\",\\n",
    "    \\"What defense contractor opportunities exist?\\",\\n",
    "    \\"How can households earning $300K benefit from tax changes?\\"\\n",
    "]\\n",
    "\\n",
    "# Run queries\\n",
    "for q in queries:\\n",
    "    result = await query(q)\\n",
    "    print(\\"\\\\n\\" + \\"-\\"*50 + \\"\\\\n\\")\\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
'''
    
    return notebook_content

async def main():
    """Main function"""
    print("OBBB Interactive Browser")
    print("Options:")
    print("1. Launch Streamlit web interface")
    print("2. Create Jupyter notebook")
    print("3. CLI query mode")
    
    choice = input("Choose option (1-3): ")
    
    if choice == "1":
        print("Starting Streamlit app...")
        import subprocess
        subprocess.run(["streamlit", "run", "scripts/interactive_browser.py"])
    elif choice == "2":
        with open("notebooks/obbb_analysis.ipynb", "w") as f:
            f.write(create_jupyter_interface())
        print("Jupyter notebook created at notebooks/obbb_analysis.ipynb")
    elif choice == "3":
        browser = OBBBBrowser()
        while True:
            query = input("Enter query (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break
            result = await browser.search_opportunities(query)
            print(f"Result: {result}\n")

if __name__ == "__main__":
    create_streamlit_app()