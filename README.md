# LinkedIn Job Scraper AI Agent

An AI-powered project designed to scrape LinkedIn job listings based on your resume and preferences—and then collect the job URLs for you. This agent uses Gradio for a user-friendly interface, OpenAI for LLM-based analysis of your resume, and uv Astral to manage dependencies. It also requires Google Chrome (with remote debugging) for automated browser interactions.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Usage](#usage)
5. [Screenshots](#screenshots)
6. [How It Works](#how-it-works)
7. [Limitations & Future Improvements](#limitations--future-improvements)
8. [License](#license)

---

## Overview

This project automates the process of:

1. **Analyzing your resume** to generate relevant job search keywords.
2. **Building LinkedIn job search URLs** based on those keywords.
3. **Scraping** the **latest job listings** on LinkedIn (within a user-defined limit).
4. **Collecting** the **job URLs** for you to review.

**Note**: The project **stops** at **gathering** the job listing URLs. No auto-apply is performed.

---

## Prerequisites

1. **OpenAI API Key**  
   - Set your `OPENAI_API_KEY` in your environment variables.  
   - The agent uses LLM calls via OpenAI (e.g., GPT-4).

2. **uv Astral**  
   - This project uses **uv Astral** for dependency management. Ensure it's installed or accessible.

3. **Google Chrome**  
   - **Chrome** is launched in **remote debugging** mode to let Playwright control the browser.  
   - Must be installed and in your system's PATH (on Windows, Mac, or Linux).

4. **Other**  
   - Python 3.8+ recommended.  
   - Basic command line familiarity.

---

## Installation & Setup

1. **Clone** the repository:

   ```bash
   git clone https://github.com/DataMonarch/linkedin-job-scraper-ai-agent.git
   cd linkedin-job-scraper-ai-agent
   ```

2. Install dependencies (via uv Astral or however your environment is set up):

   ```bash
   uv sync
   ```
   - If you don't have uv Astral, see [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

3. Set your OpenAI key:

   ```bash
   export OPENAI_API_KEY=sk-xxxxxx
   # On Windows: set OPENAI_API_KEY=sk-xxxxxx
   ```

Ensure Chrome is installed. The script will attempt to launch Chrome with `--remote-debugging-port=9222`.

## Usage

1. Run the main script:

   ```bash
   uv run start.py
   ```

2. This will launch the Gradio dashboard in your default browser (or show the URL in the terminal).

3. In the Gradio UI:
   - Upload your PDF resume
   - Set how many keyword combos to generate and optionally specify your main job search focus
   - Click "Analyze & Generate (ResumeParser)" to parse the resume and build `user_data.json`
   - Review the extracted fields (positions, location, skills, etc.) and the generated keyword combinations
   - Click "Scrape Jobs" to start the LinkedIn scraping process (only up to a certain number of search URLs)

4. The script will:
   - Launch Chrome in remote debugging mode
   - Scrape job listings
   - Display job listings in the Gradio UI table
   - Provide a list of the actual search URLs

5. Watch the terminal for agent logs. You'll see step-by-step instructions about what the agent is doing, which job pages it's visiting, etc.

## Screenshots

Below are some placeholders for images or GIFs showing the process:

### Dashboard (Resume Analysis & Scraping):
[Insert screenshot here]

### Terminal Logs:
[Insert screenshot here]

## How It Works

### Resume Parsing
- The user's resume is parsed by an LLM (OpenAI), extracting relevant positions, skills, etc.
- Generates search keyword combos stored in `user_data.json`.

### Building Search URLs
- The code reads `user_data.json` to build LinkedIn job search URLs with location, posted date filter, etc.

### Scraping
- Launches Chrome (via remote debugging)
- Playwright visits each search URL and gathers job data from `.job-card-container` elements
- The script stores job data in `jobs_data.json` and also returns it in the Gradio DataFrame

### Result
- The user has a list of job URLs and metadata, ready to be reviewed or applied to manually

## Limitations & Future Improvements

- **Captchas / Login**: If LinkedIn blocks your automation or shows a captcha, you'll need to login manually or add captcha handling
- **Changing DOM**: LinkedIn's structure might change. You may need to update selectors
- **Application**: Currently stops after collecting job URLs. Auto-apply is not implemented
- **Resume**: If your resume has unusual formatting, the LLM extraction might need refinement



*Enjoy scraping the latest LinkedIn job listings and collecting their URLs with minimal hassle!*