# News Summarizer & Connector — Vault Home

This vault holds the processed news repository.

- **[[articles/news|News articles]]** — one note per article: summary, key takeaway, and
  keyword wikilinks. Filenames are `YYYY-MM-DD Headline (id).md`, so they sort chronologically.
- **Keywords** (`keywords/`) — one hub note per taxonomy keyword. Open a hub note and check
  its backlinks to see every article on that theme; in graph view these are the cluster centres.
- **Insights** (`articles/insights/`) — reserved for the second list of insight articles
  (future phase). Connectors between the two maps will be keywords whose backlinks span both
  folders.

## Graph view tips

Settings → Graph view → Groups:

- `path:articles/news` → one color (news map)
- `path:keywords` → another color (theme hubs)
- `path:articles/insights` → a third color (insight map, future)

Filter `-path:keywords` to hide hubs, or increase link distance to spread clusters.
