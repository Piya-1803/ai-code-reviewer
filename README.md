 AI Code Reviewer

An autonomous AI-powered Pull Request reviewer built with Claude API and GitHub Actions.

 What it does
Automatically reviews every Pull Request — finds bugs, security vulnerabilities, 
and bad practices — and posts detailed comments directly on the PR.

 Files
- `codereview.py` — the main AI code reviewer (production code)
- `learn_claude.py` — practice file for Claude API basics
- `learn_tools.py` — practice file for tool use / function calling
- `learn_github.py` — practice file for GitHub API integration

Tech Stack
Python • Anthropic Claude API • PyGithub • GitHub Actions

 How to run
1. Set `ANTHROPIC_API_KEY` and `GITHUB_TOKEN` environment variables
2. Run `python codereview.py`
