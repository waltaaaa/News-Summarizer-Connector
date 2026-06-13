import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("KnowledgeBridgeHost")

@mcp.tool()
def get_pending_links_count() -> str:
    path = "./links.txt"
    if not os.path.exists(path):
        return "Queue link tracker file does not exist."
    with open(path, "r") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return f"Detected {len(links)} unprocessed items inside links.txt storage container."

@mcp.tool()
def execute_bridge_pipeline(operational_mode: str, start_date: str, end_date: str) -> str:
    try:
        execution_args = [
            "python", "pipeline.py",
            "--mode", operational_mode,
            "--start", start_date,
            "--end", end_date
        ]
        runtime_capture = subprocess.run(
            execution_args,
            capture_output=True,
            text=True,
            check=True
        )
        return f"Pipeline Finished.\nStdout:\n{runtime_capture.stdout}"
    except subprocess.CalledProcessError as err:
        return f"Backend System Failure Code: {err.returncode}\nError Log:\n{err.stderr}"

if __name__ == "__main__":
    mcp.run()
