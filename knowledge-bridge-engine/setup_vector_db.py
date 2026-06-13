import os
import chromadb

def seed_research_database():
    vault_dir = "./obsidian_vault/02-Research-Library"
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="internal_research")

    if not os.path.exists(vault_dir):
        print(f"[!] Path folder missing: {vault_dir}")
        return

    files = [f for f in os.listdir(vault_dir) if f.endswith(".md")]
    print(f"[*] Found {len(files)} research files for database ingestion.")

    for filename in files:
        file_path = os.path.join(vault_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse titles cleanly out of first heading or frontmatter
        title = filename.replace(".md", "").replace("-", " ")
        for line in content.splitlines():
            if line.startswith("# "):
                title = line.replace("# ", "").strip()
                break

        collection.upsert(
            documents=[content],
            metadatas=[{"title": title}],
            ids=[filename]
        )
        print(f"[OK] Successfully indexed: {filename}")

    print("[OK] Database optimization step finalized.")

if __name__ == "__main__":
    seed_research_database()
