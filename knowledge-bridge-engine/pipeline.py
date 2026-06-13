import os
import sys
import argparse
from datetime import datetime
from typing import List, Optional
import httpx
import trafilatura
import pandas as pd
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import chromadb

# --- 1. Structured Data Output Schemas ---

class MacroThemeCluster(BaseModel):
    primary_theme: str = Field(description="The core anxiety or structural trend common across this article cluster.")
    implied_questions: List[str] = Field(description="2-3 specific, pressing questions raised by this trend loop.")
    distinctive_keywords: List[str] = Field(description="3-5 highly specific entities, tool names, or non-generic markers. No generic terms like 'AI' or 'Labor'.")
    associated_urls: List[str] = Field(description="The original source web links grouped under this trend.")

class ConsolidatedAnalysis(BaseModel):
    clusters: List[MacroThemeCluster] = Field(description="The list of extracted high-level macroeconomic macro-themes.")

# --- 2. Initial Setup and Client Initializations ---

client = genai.Client()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
research_collection = chroma_client.get_or_create_collection(name="internal_research")

# --- 3. Stage 0: Web Scraping Layer ---

def fetch_and_clean_article(url: str) -> Optional[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
        response.raise_for_status()

        extracted_text = trafilatura.extract(response.text)
        metadata = trafilatura.extract_metadata(response.text)

        if not extracted_text:
            return None

        publish_date = metadata.date if (metadata and metadata.date) else datetime.today().strftime('%Y-%m-%d')

        return {
            "url": url,
            "text": extracted_text,
            "publish_date": publish_date
        }
    except Exception as e:
        print(f"Error executing scrape on URL {url}: {str(e)}", file=sys.stderr)
        return None

# --- 4. Stage 1: Trend Extraction and Clustering Layer ---

def extract_macro_themes(articles: List[dict], start_date: str, end_date: str) -> ConsolidatedAnalysis:
    context_blocks = []
    for idx, art in enumerate(articles):
        context_blocks.append(f"--- Article {idx+1} ---\nURL: {art['url']}\nDate: {art['publish_date']}\nContent: {art['text']}\n")

    master_text_input = "\n".join(context_blocks)

    prompt = f"""
    You are an elite, institutional-grade economic analyst tracking public trends between {start_date} and {end_date}.
    Analyze the following collection of real-world articles. Identify the primary macro-themes or
    structural industrial anxieties cutting across these materials. Group similar URLs together.

    CRITICAL FILTERING RULES FOR KEYWORDS:
    - You must completely avoid generic baseline terms (e.g., do not use 'AI', 'Technology', 'Economy', 'Jobs', 'Business').
    - Instead, extract low-entropy, highly unique identifiers: specific tool designations, explicit economic indexes,
      legislative names, specific companies, or unique regional contexts.
    - If calculating proportional metrics, use the phrase 'per cent' instead of the symbol '%'.
    - If tracking general merchant patterns, use the phrase 'Index of Consumer Spending' rather than 'ICS'.

    Articles Context:
    {master_text_input}
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ConsolidatedAnalysis,
            temperature=0.15,
        ),
    )
    return response.parsed

# --- 5. Stage 2: Database Matchmaking (RAG Bridge) ---

def match_theme_to_research(keywords: List[str], theme_narrative: str) -> List[dict]:
    search_query = f"{theme_narrative} {' '.join(keywords)}"
    results = research_collection.query(
        query_texts=[search_query],
        n_results=2
    )

    matched_papers = []
    if results and results['documents'] and len(results['documents'][0]) > 0:
        for i in range(len(results['documents'][0])):
            matched_papers.append({
                "title": results['metadatas'][0][i].get("title", "Unknown Publication Title"),
                "filename": results['ids'][0][i],
                "summary": results['documents'][0][i][:400]
            })
    return matched_papers

# --- 6. Stage 3 & 4: Output Synthesis & Obsidian Exporter ---

def write_brief_to_obsidian(cluster: MacroThemeCluster, papers: List[dict], vault_path: str):
    date_stamp = datetime.today().strftime('%Y-%m-%d')
    safe_title = "".join([c for c in cluster.primary_theme if c.isalnum() or c in (' ', '_', '-')]).rstrip()
    filename = f"Brief-{date_stamp}-{safe_title.replace(' ', '_')[:40]}.md"
    target_path = os.path.join(vault_path, "03-Synthesized-Briefs", filename)

    research_links_section = ""
    if papers:
        for idx, paper in enumerate(papers):
            research_links_section += f"{idx+1}. Analysis tracking to core institutional data fields: see [[{paper['filename'].replace('.md', '')}]]\n"
    else:
        research_links_section = "No highly relevant matching internal publications were discovered for this trend loop."

    markdown_payload = f"""---
type: executive_brief
generated_dt: {date_stamp}
distinctive_keywords: [{', '.join([f"'{k}'" for k in cluster.distinctive_keywords])}]
associated_sources: [{', '.join([f"'{u}'" for u in cluster.associated_urls])}]
---

## Public Discourse Theme
{cluster.primary_theme}

## Core Implicit Questions
{chr(10).join([f'* {q}' for q in cluster.implied_questions])}

## Matched Internal Research Portfolio
Our analysis draws direct evidence from our primary institutional assets:

{research_links_section}
"""
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(markdown_payload)
    print(f"[OK] Successfully exported brief file: {filename}")

# --- 7. Pipeline Execution Controller ---

def main():
    parser = argparse.ArgumentParser(description="Knowledge Bridge Processing Infrastructure.")
    parser.add_argument("--mode", type=str, default="aggregated", choices=["individual", "aggregated"])
    parser.add_argument("--start", type=str, default="2026-05-01")
    parser.add_argument("--end", type=str, default="2026-06-12")
    args = parser.parse_args()

    vault_dir = "./obsidian_vault"
    links_file = "./links.txt"

    if not os.path.exists(links_file) or os.path.getsize(links_file) == 0:
        print("[!] Execution aborted: Input file links.txt is empty or missing.", file=sys.stderr)
        return

    with open(links_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[*] Beginning execution. Ingesting {len(urls)} source links...")
    scraped_data = []
    for url in urls:
        data = fetch_and_clean_article(url)
        if data:
            scraped_data.append(data)
            safe_url_name = "".join([c for c in url if c.isalnum()])[:50]
            with open(f"{vault_dir}/01-News-Ingest/{data['publish_date']}-{safe_url_name}.md", "w", encoding="utf-8") as cf:
                cf.write(data['text'])

    if not scraped_data:
        print("[!] Scrape yielded no clean structural text bodies.", file=sys.stderr)
        return

    df = pd.DataFrame(scraped_data)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    mask = (df['publish_date'] >= pd.to_datetime(args.start)) & (df['publish_date'] <= pd.to_datetime(args.end))
    filtered_df = df.loc[mask]

    target_articles = filtered_df.to_dict(orient="records")
    print(f"[*] Date filters applied. {len(target_articles)} items fall within processing window.")

    if not target_articles:
        return

    analysis_payload = extract_macro_themes(target_articles, args.start, args.end)

    for cluster in analysis_payload.clusters:
        matched_papers = match_theme_to_research(cluster.distinctive_keywords, cluster.primary_theme)
        write_brief_to_obsidian(cluster, matched_papers, vault_dir)

    print("[OK] Knowledge Bridge Execution Complete.")

if __name__ == "__main__":
    main()
