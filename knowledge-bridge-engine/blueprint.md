# KNOWLEDGE BRIDGE ENGINE - DEVELOPMENT BLUEPRINT

This single file contains the complete workspace architecture, strict system constraints, and functional code implementations required to build the local semantic link between external public media and our internal research portfolio.

> NOTE: In this repository the project lives in the `knowledge-bridge-engine/` subdirectory
> (the repo root hosts the separate News Summarizer & Connector pipeline). All relative
> paths below resolve from inside `knowledge-bridge-engine/`.

---

## 1. WORKSPACE STRUCTURE & FILE LAYOUT

The project repository must be structured exactly as follows:

```text
knowledge-bridge-engine/
├── CLAUDE.md                 # System instructions and coding constraints
├── requirements.txt          # Python environment dependencies
├── pipeline.py               # Core processing, scraping, and matching engine
├── fastmcp_server.py         # Local MCP communication bridge for Claude Artifacts
├── setup_vector_db.py        # Automated tool to seed internal research into ChromaDB
├── links.txt                 # Input queue file for target news URLs
└── obsidian_vault/           # Direct folder mapping to the desktop Obsidian Vault
    ├── 01-News-Ingest/       # Storage path for raw crawled text cache files
    ├── 02-Research-Library/  # Storage path for your existing internal research papers (.md)
    └── 03-Synthesized-Briefs/# Export target path for generated response briefs (.md)
```

## 2. SYSTEM INSTRUCTIONS & CODE RULES

See `CLAUDE.md` — project persona, the "per cent" / "Index of Consumer Spending"
language constraints, and the complete-code generation mandate.

## 3. DEPENDENCY CONFIGURATION

See `requirements.txt` — fastmcp, google-genai, pydantic, trafilatura, httpx,
pandas, chromadb.

## 4. THE CORE PROCESSING PIPELINE

See `pipeline.py` — stages:

- **Stage 0** `fetch_and_clean_article()`: httpx fetch + trafilatura extraction with
  publish-date metadata fallback.
- **Stage 1** `extract_macro_themes()`: Gemini 2.5 Flash structured output against the
  `ConsolidatedAnalysis` / `MacroThemeCluster` Pydantic schemas, with strict
  non-generic keyword filtering rules.
- **Stage 2** `match_theme_to_research()`: ChromaDB query of the `internal_research`
  collection (top 2 matches per theme).
- **Stage 3/4** `write_brief_to_obsidian()`: frontmatter-tagged executive briefs with
  `[[wikilinks]]` into `03-Synthesized-Briefs/`.
- **Controller** `main()`: reads `links.txt`, caches raw text into `01-News-Ingest/`,
  applies the `--start`/`--end` date window via pandas, then runs Stages 1–3.

Requires the `GEMINI_API_KEY` environment variable (the genai client is initialized at
module import).

## 5. LOCAL MCP HOST SERVER

See `fastmcp_server.py` — stdio FastMCP server `KnowledgeBridgeHost` exposing:

- `get_pending_links_count()` — counts non-comment lines in `links.txt`.
- `execute_bridge_pipeline(operational_mode, start_date, end_date)` — subprocess wrapper
  around `pipeline.py` returning stdout or the captured failure log.

Register it in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "knowledge-bridge": {
      "command": "python",
      "args": ["fastmcp_server.py"],
      "cwd": "<absolute path to knowledge-bridge-engine>",
      "env": { "GEMINI_API_KEY": "<your key>" }
    }
  }
}
```

## 6. AUTOMATED RESEARCH DATABASE INITIALIZATION

See `setup_vector_db.py` — loops through `obsidian_vault/02-Research-Library/*.md`,
extracts each note's first `# ` heading as its title, and upserts the documents into
the persistent ChromaDB collection `internal_research` (stored in `./chroma_db/`,
gitignored) so `pipeline.py` can immediately perform matches.

Run order on a new machine:

```bash
pip install -r requirements.txt
python setup_vector_db.py     # seed the research library
python fastmcp_server.py      # or register via Claude Desktop config above
```
