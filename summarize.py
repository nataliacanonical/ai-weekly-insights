import os
import glob
import argparse
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def load_env():
    load_dotenv()
    return {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
        "model": os.getenv("OLLAMA_MODEL", "phi3:mini"),
        "csv_glob": os.getenv("CSV_GLOB", "data/*.csv"),
        "max_chars": int(os.getenv("MAX_CHARS", "40000")),
        "bullets": os.getenv("SUMMARY_BULLETS", "6"),
        "out_dir": os.getenv("OUTPUT_DIR", "outputs"),
    }

def ensure_ollama(host: str):
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        r.raise_for_status()
    except Exception as e:
        raise SystemExit(
            f"Could not reach Ollama at {host}. Is it running?"
        ) from e

def read_head(path: Path, max_chars: int) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read(max_chars)

def render_prompt(template_path: Path, csv_text: str, bullets: str) -> str:
    tmpl = template_path.read_text(encoding="utf-8")
    return tmpl.replace("{{CSV}}", csv_text).replace("{{BULLETS}}", str(bullets))

def generate(host: str, model: str, prompt: str) -> str:
    resp = requests.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()

def main():
    cfg = load_env()

    ap = argparse.ArgumentParser(description="Summarize CSVs with local Ollama.")
    ap.add_argument("--prompt", default="prompts/weekly_trends.md",
                    help="Path to a prompt template (*.md).")
    ap.add_argument("--glob", default=cfg["csv_glob"],
                    help="CSV glob (overrides CSV_GLOB).")
    ap.add_argument("--model", default=cfg["model"], help="Model name.")
    ap.add_argument("--outdir", default=cfg["out_dir"], help="Output directory.")
    ap.add_argument("--max-chars", type=int, default=cfg["max_chars"],
                    help="Max chars to read from CSV.")
    ap.add_argument("--bullets", default=cfg["bullets"],
                    help="Bullet limit injected into prompt.")
    args = ap.parse_args()

    host = cfg["host"]
    ensure_ollama(host)

    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        raise SystemExit(f"Prompt not found: {prompt_path}")

    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_paths = sorted(glob.glob(args.glob))
    if not csv_paths:
        print(f"ℹNo CSVs matched: {args.glob}")
        return

    print(f"Using prompt: {prompt_path}")
    print(f"Model: {args.model}")
    print(f"Found {len(csv_paths)} CSV(s)")

    for p in csv_paths:
        csv_path = Path(p)
        print(f"→ Summarizing {csv_path.name} ...")
        csv_text = read_head(csv_path, args.max_chars)
        prompt = render_prompt(prompt_path, csv_text, args.bullets)
        summary = generate(host, args.model, prompt)

        stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        out_name = f"{csv_path.stem}.{prompt_path.stem}.summary.{stamp}.md"
        out_path = out_dir / out_name
        out_path.write_text(f"# Summary: {csv_path.name}\n\n{summary}\n", encoding="utf-8")
        print(f"Saved: {out_path}")

    print("Done.")

if __name__ == "__main__":
    main()
