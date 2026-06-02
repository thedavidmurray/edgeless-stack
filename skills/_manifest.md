# Skill Manifest

Index of all included skills with applicability metadata.

**Total skills**: 106 | **Core**: 5 | **Domain**: 101

## Core Skills

Broadly useful in most sessions. Load these by default.

| Skill | Domain | When to Apply |
|-------|--------|---------------|
| `memory-system` | kernel | Session start, recalling past context, searching memory, checking health |
| `session-planning` | kernel | Task has 3+ phases, complex multi-step work, risk of goal drift |
| `verify-completion` | kernel | Before declaring any task complete; evidence-first, defaults to FAIL |
| `retrospective-learning` | kernel | End of session, after completing a feature, switching major tasks |
| `cleanup` | product | Codebase has dead code, unused imports, bloated dependencies |

**Location**: `skills/core/`

## Domain Skills

Load on demand for particular task types.

| Skill | Domain | When to Apply |
|-------|--------|---------------|
| `article-extractor` | knowledge | Extracting clean content from web articles and URLs |
| `changelog-generator` | product | Generating changelogs from git history or release notes |
| `code-review` | product | After writing significant code, before declaring done |
| `commit-hygiene` | product | Validating commit size, message quality, and splitting strategies |
| `content-research-writer` | knowledge | Writing blog posts, articles, newsletters requiring research |
| `csv-summarizer` | knowledge | Summarizing, analyzing, or exploring CSV/tabular data |
| `dev-docs` | product | Generating READMEs, API docs, architecture decision records |
| `diagnose` | product | Hard bugs, performance regressions, broken/failing systems |
| `file-organizer` | tooling | Messy directories, scattered files, duplicates, structure cleanup |
| `image-enhancer` | creative | Upscaling, sharpening, format conversion, platform-specific presets |
| `link-ingest` | knowledge | Ingesting and processing content from URLs |
| `make-interfaces-feel-better` | creative | UI polish, motion, typography, spacing, interaction details |
| `mcp-server-scaffold` | tooling | Scaffolding new MCP servers |
| `prd-to-criteria` | product | Converting PRD acceptance criteria into verifiable checks |
| `precommit-validation` | product | Pre-commit security and quality validation before git commit |
| `prompt-engineering` | product | Writing agent instructions, skill prompts, LLM-facing prompts |
| `research-deep` | knowledge | Complex topic requiring multi-step investigation and synthesis |
| `skill-creator` | kernel | Creating new Claude Code skills from scratch |
| `soul-extraction` | knowledge | Building a SOUL.md persona/voice profile from public social profiles |
| `test-driven-development` | product | Implementing any feature or bugfix -- RED-GREEN-REFACTOR |
| `test-runner` | product | Running tests, generating test scaffolds, checking coverage |
| `deep-technology-research` | knowledge | When investigating a technology or comparing OSS repos for a strategic build/buy/switch decision. |
| `dispatch-handoff` | product | When handing off work between agents and a human owner with standardized acceptance criteria. |
| `hermes-agent` | kernel | When configuring, extending, or contributing to Hermes Agent itself. |
| `system-health` | tooling | When checking infrastructure health, validating uptime, or building monitoring around services. |
| `telegram-ops-alerting` | tooling | When sending operational alerts to Telegram with rate limiting and consistent formatting. |

| `obsidian` | knowledge | When reading, searching, creating, or editing notes in an Obsidian vault. |
| `vault-knowledge-ops` | knowledge | When auditing or curating a knowledge vault's taxonomy and structure end-to-end. |
| `recall` | knowledge | When searching past Claude Code session transcripts for prior work on a topic. |
| `arxiv` | knowledge | When searching arXiv for papers by keyword, author, category, or ID. |
| `youtube-summarizer` | knowledge | When fetching a YouTube transcript and turning it into a structured summary or KB entry. |
| `ascii-art` | creative | When generating ASCII art (pyfiglet, cowsay, boxes, toilet, image-to-ASCII). |
| `ascii-video` | creative | When converting video or audio into colored ASCII MP4/GIF output. |
| `manim-video` | creative | When producing 3Blue1Brown-style math/algorithm animations with Manim CE. |
| `p5js` | creative | When building p5.js sketches: generative art, shaders, interactive, or 3D. |
| `excalidraw` | creative | When producing hand-drawn Excalidraw diagrams (architecture, flow, sequence). |
| `architecture-diagram` | creative | When generating a dark-themed SVG architecture/cloud/infra diagram as HTML. |
| `pixel-art` | creative | When converting images into retro pixel art with hardware-accurate palettes. |
| `humanizer` | creative | When stripping AI-isms from text to add genuine voice. |
| `popular-web-designs` | creative | When you want concrete examples from real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| `claude-design` | creative | When you need a one-off HTML artifact (landing page, deck, prototype). |
| `google-workspace` | product | When using Gmail, Calendar, Drive, Docs, or Sheets via the gws CLI or Python. |
| `notion` | product | When working with Notion: pages, databases, markdown via API or the ntn CLI. |
| `linear` | product | When managing Linear issues, projects, and teams via the GraphQL API. |
| `airtable` | product | When CRUD-ing Airtable records — filters, upserts via REST. |
| `ocr-and-documents` | knowledge | When extracting text from PDFs or scanned documents (pymupdf, marker-pdf). |
| `nano-pdf` | product | When editing PDF text/typos/titles via the nano-pdf CLI with natural-language prompts. |
| `powerpoint` | product | When creating, reading, or editing .pptx decks, slides, notes, or templates. |
| `maps` | product | When geocoding, looking up POIs, computing routes, or finding timezones via OpenStreetMap/OSRM. |
| `apple-notes` | product | When managing Apple Notes on macOS via the memo CLI: create, view, search, edit. |
| `apple-reminders` | product | When managing Apple Reminders on macOS via the remindctl CLI. |
| `imessage` | product | When sending or receiving iMessages/SMS on macOS via the imsg CLI. |
| `findmy` | product | When tracking Apple devices and AirTags via FindMy.app on macOS. |
| `macos-computer-use` | tooling | When driving the macOS desktop in the background — screenshots, mouse, keyboard. |
| `chroma` | tooling | When storing or querying embeddings in ChromaDB for semantic search or RAG. |
| `dspy` | tooling | When building declarative LM programs with DSPy and auto-optimizing prompts. |
| `huggingface-hub` | tooling | When searching, downloading, or uploading models and datasets via the hf CLI. |
| `llama-cpp` | tooling | When running local GGUF inference with llama.cpp or discovering models on HF. |
| `outlines` | tooling | When generating structured JSON/regex/Pydantic output from an LLM. |
| `whisper` | tooling | When transcribing audio with OpenAI's Whisper speech recognition. |
| `axolotl` | tooling | When fine-tuning an LLM with Axolotl (YAML configs for LoRA/DPO/GRPO). |
| `unsloth` | tooling | When fine-tuning faster with Unsloth (2-5× speedup, less VRAM). |
| `weights-and-biases` | tooling | When logging ML experiments, sweeps, and model registry to Weights & Biases. |
| `plan` | product | When you need to write an implementation plan to a markdown file without executing. |
| `spike` | product | When running a throwaway experiment to validate an idea before building. |
| `systematic-debugging` | product | When debugging a hard issue: 4-phase root-cause loop before fixing. |
| `proof-of-completion` | product | When delivering work — include a structured proof-of-completion block before marking done. |
| `python-debugpy` | product | When debugging Python via pdb REPL or debugpy remote (DAP). |
| `node-inspect-debugger` | product | When debugging Node.js via --inspect and Chrome DevTools Protocol. |
| `subagent-driven-development` | product | When executing a plan via delegate_task subagents with 2-stage review. |
| `web-dev-ops` | product | When operating a web dev project end-to-end: audit dev sites and validate. |
| `understand-anything` | knowledge | When analyzing, visualizing, or explaining a codebase with Understand-Anything. |
| `browser-automation-patterns` | product | When automating browser/web-UI tasks with reliable patterns and the right tools. |
| `github-pr-workflow` | product | When managing the GitHub PR lifecycle: branch, commit, open, CI, merge. |
| `github-issues` | product | When creating, triaging, labeling, or assigning GitHub issues. |
| `github-code-review-v2` | product | When reviewing a PR by analyzing diffs and leaving inline comments. |
| `github-repo-management` | product | When cloning, creating, forking repos and managing remotes and releases. |
| `codebase-inspection` | knowledge | When inspecting codebases with pygount: LOC, languages, ratios. |
| `xurl` | product | When using X/Twitter via the xurl CLI: post, search, DM, media, v2 API. |
| `agent-fleet-capability-audit` | tooling | When surveying available skills/tools across an agent fleet and auditing capability gaps. |
| `mcp-to-skill-proxy` | tooling | When converting an MCP server into a Hermes skill via the proxy pattern. |

| `ideation` | creative | When generating project ideas via creative constraints. |
| `modal-serverless-gpu` | tooling | When running on-demand serverless GPU workloads on Modal. |
| `serving-llms-vllm` | tooling | When serving LLMs with high-throughput vLLM (OpenAI API, quantization). |
| `fine-tuning-with-trl` | tooling | When fine-tuning an LLM with TRL (SFT, DPO, PPO, GRPO, reward modeling). |
| `peft-fine-tuning` | tooling | When fine-tuning with parameter-efficient methods (LoRA/QLoRA and 25+ PEFT variants). |
| `evaluating-llms-harness` | tooling | When benchmarking LLMs with lm-evaluation-harness (MMLU, GSM8K, etc.). |

| `graphify` | knowledge | When turning code, docs, papers, or images into a clustered, queryable knowledge graph. |
| `cli-dashboards` | creative | When building Tufte-minimal data dashboards in the terminal using rich + sqlite. |
| `verify-before-claiming` | kernel | Before claiming success, verify external state with a concrete command — anti-confabulation disc… |
| `comfyui` | creative | When generating images, video, or audio with ComfyUI — install, manage nodes/models, run workflows. |
| `stable-diffusion-image-generation` | creative | When generating images with Stable Diffusion via HuggingFace Diffusers. |
| `audiocraft-audio-generation` | creative | When generating music or sound with AudioCraft (MusicGen / AudioGen). |
| `segment-anything-model` | tooling | When doing zero-shot image segmentation via SAM with points, boxes, or masks. |
| `fleet-self-healing-operations` | tooling | When building self-monitoring, self-healing infrastructure for an agent fleet. |
| `swarm-observability` | tooling | When instrumenting a multi-agent system with OpenTelemetry and Jaeger. |
| `academic-paper` | knowledge | When writing academic papers via a multi-agent pipeline (plan/full/outline/revision modes). |
| `academic-research` | knowledge | When doing deep academic research via a multi-agent investigation pipeline. |
| `academic-review` | knowledge | When simulating peer review of an academic paper with a multi-judge panel. |
| `signal-extraction-layer` | knowledge | When extracting structured insights from arbitrary content sources via the SEL pattern. |
| `llm-wiki` | knowledge | When building or querying a Karpathy-style interlinked-markdown LLM knowledge base. |


**Location**: `skills/domains/`

## Vendor Skills

Third-party skills from external vendors, integrated into the Edgeless stack.

| Skill | Vendor | When to Apply |
|-------|--------|---------------|
| `aiq-research` | NVIDIA | AI research workflows via AI-Q Blueprint |
| `dynamo-recipe-runner` | NVIDIA | Deploy LLM serving recipes on Kubernetes |
| `dynamo-router-starter` | NVIDIA | Set up LLM routing for inference serving |
| `dynamo-troubleshoot` | NVIDIA | Troubleshoot NVIDIA Dynamo deployment issues |
| `mcore-testing` | NVIDIA | Large-scale distributed training with Megatron-Core |

**Location**: `skills/vendors/nvidia/`

## Skill File Structure

Each skill is a single markdown file with YAML frontmatter:

```yaml
---
name: skill-name
description: >
  What this skill does and when to use it.
metadata:
  tags: [tag1, tag2]
  tier: general          # or task-specific
  domain: kernel         # kernel, product, knowledge, workflow
when_to_apply: >
  One-sentence trigger description
---
```

## Adding New Skills

1. Create `skills/<tier>/<skill-name>.md` with frontmatter
2. Add entry to this manifest
3. Include `<!-- CUSTOMIZE -->` comments for user-specific values
4. Keep the pattern: When to Use, Workflow, Implementation, Anti-Patterns, Related Skills

## Tiered Loading Pattern

To reduce context window usage, skills can be loaded on demand:

```bash
# Load all core skills (always relevant)
cat skills/core/*.md

# Load domain skills when needed
cat skills/domains/code-review.md
```

For large skill libraries (50+), implement a loader script that reads
the manifest and loads only relevant skills based on task domain.
