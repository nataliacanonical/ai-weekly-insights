# Read Data for Humans

Short scripts that show how to use local LLMs (via Ollama) to read raw CSVs and generate human-friendly summaries.
Think of it as "reading data for humans" — turning numbers into stories, privately, on your own machine.

## Features

Local & Private: All runs on your machine via Ollama

Flexible Prompts: Swap between weekly trends, anomaly radar, exec briefs, etc.

Tiny-Friendly: Works even on 8 GB RAM with small models like phi3:mini.

Markdown Outputs: Clean summaries you can paste into slides, docs, or reports.

## Project Structure
.
├─ .env.example          # Environment variables (copy to .env)
├─ prompts/              # Prompt templates (Markdown)
│  ├─ weekly_trends.md
│  ├─ anomaly_radar.md
│  └─ exec_brief.md
├─ data/                 # CSV inputs (your raw data here)
│  └─ sample_weekly_metrics.csv
├─ outputs/              # AI-generated summaries (gitignored)
├─ summarize.py          # Main script
└─ pyproject.toml        # Poetry config

## Setup
1. Install Ollama

Download Ollama and make sure it’s running.
Pull model that would work locally depending on your RAM capacity. Example below works for tiny RAM:

ollama pull phi3:mini

2. Install dependencies with Poetry
poetry install

3. Copy .env
cp .env.example .env


Adjust settings inside if needed:

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini
CSV_GLOB=data/*.csv
OUTPUT_DIR=outputs

## Usage
Default (weekly trends)

Summarize all CSVs in data/ using the weekly trends prompt:

poetry run python summarize.py

Use a different prompt
poetry run python summarize.py --prompt prompts/anomaly_radar.md

Target a single file
poetry run python summarize.py --glob "data/weekly_metrics.csv"

Change model
poetry run python summarize.py --model "qwen2.5:3b-instruct"

### Example Input
week,region,mqls,sqls,conversions
2025-07-28,EMEA,120,45,18
2025-07-28,APAC,80,22,9
2025-07-28,AMER,150,70,30
2025-08-04,EMEA,135,52,20
2025-08-04,APAC,60,15,5
2025-08-04,AMER,155,75,32

### Example Output
# Summary: weekly_metrics.csv

- EMEA grew steadily (+12% MQLs, +11% conversions).  
- AMER was stable with slight gains.  
- APAC dropped sharply (–25% MQLs, –44% conversions).  

**Actions:**  
1. Investigate APAC campaigns; engagement is falling fast.  
2. Double down on EMEA channels to sustain growth.  

## Privacy

All processing happens locally.
No CSV data leaves your machine.
