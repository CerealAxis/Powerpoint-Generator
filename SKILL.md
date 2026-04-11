---
name: powerpoint-generator
description: Professional full-process PPT presentation AI generation assistant. Simulates the complete workflow of a top-tier PPT design company (requirements research -> information gathering -> outline planning -> draft planning -> design draft), outputting high-quality HTML presentations. Triggered when users mention making PPT, presentations, slides, training materials, roadshow decks, or product introduction pages. Also applies when users say "help me make an introduction about X" or "I need to present Y to my boss" - any scenario requiring structured multi-page presentation content.
---

# PPT Agent -- Professional Full-Process Presentation Generation

## Core Philosophy

Mimic the complete workflow of a professional PPT design company (pricing at 10,000+ RMB per page level), not "give an outline and apply a template":

1. **Research Before Generation** -- Fill content with real data, don't fabricate
2. **Planning and Design Separation** -- Verify information structure first, then do visual packaging
3. **Content-Driven Layout** -- Bento Grid card-style layout, each page's layout determined by content
4. **Global Style Consistency** -- Set style first, then generate page by page, ensuring cross-page uniformity
5. **Smart Image Matching** -- Use image generation capabilities (AI-generated or unsplash) to add illustrations to each page

---

## Environment Setup [Required for First Use]

### Node.js Environment

#### Puppeteer Installation

```bash
npm install -g puppeteer --unsafe-perm
npm install -g dom-to-svg esbuild
```

**Verification**: `node -e "require('puppeteer'); console.log('puppeteer OK')"`

**If installation fails, try using a mirror**:

```bash
export PUPPETEER_DOWNLOAD_HOST=https://storage.googleapis.com.cnpmjs.org
npm install -g puppeteer --unsafe-perm
npm install -g dom-to-svg esbuild
```

**Verification**: `node -e "require('puppeteer'); console.log('puppeteer OK')"`

### Python Environment

```bash
pip install python-pptx lxml Pillow playwright
playwright install chromium  # Install Chromium browser (run for first time)
```

---

## Pre-Flight Check: Output Directory Check [STOP -- Must Verify]

> Before starting each PPT process, **must** check if `OUTPUT_DIR` is empty. If there are leftover files, they may contaminate this run's output.

**Execute**:
```bash
ls -la OUTPUT_DIR/
```

**Decision Table**:

| Check Result | Action |
|--------------|--------|
| Directory does not exist or is empty | Proceed to Step 1 |
| Has leftover files | **Stop and inform user**: List all files, explain risks, wait for user to confirm deletion or change directory |
| User requests deletion | Execute `rm -rf OUTPUT_DIR/*` then continue |
| User specifies new directory | Update `OUTPUT_DIR` variable, re-check |

**Mandatory Prompt** (directly send to user):
```
⚠️ Working directory ppt-output/ is not empty, detected the following files:
  - xxx
  ...
These files do not match the current topic. Continuing may cause output confusion.

Please choose:
1. Delete all old files (Recommended)
2. Use a new output directory
3. Cancel this task
```

**Breakpoint Recovery Check** (after directory is empty or cleaned, must execute when Main Agent starts):
```bash
python SKILL_DIR/scripts/milestone_check.py OUTPUT_DIR/ --summary
```

Based on milestone status, decide from which Step to continue. If historical products exist, absolutely cannot ignore and regenerate.

---

## Pipeline Mandatory Declaration [Red Line]

> The following rules cannot be violated; any bypassing will cause serious output quality degradation.

### Six-Step Pipeline Order is Fixed, No Skipping Allowed

```
Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6
```

### Forbidden Actions

- ❌ Skip Step 1 and directly generate PPT
- ❌ Enter Step 5c without a draft
- ❌ Stop at preview.html without executing SVG and PPTX
- ❌ Use other tools/pipelines to replace this process

### Only Allowed Degradation

- Node.js unavailable → Skip SVG branch, only output preview.html, inform user
- Python unavailable → Skip SVG + PNG + PPTX branches, only output preview.html, inform user and wait for feedback
- Playwright unavailable → Skip PNG branch (visual_qa.py also skipped), SVG branch continues
- Node.js unavailable → Skip SVG branch, PNG branch continues (html2png.py does not depend on Node.js)
- Visual model unavailable → Skip visual audit, DOM assertions still run normally

### Mandatory Levels by Step

| Step | Mandatory Level |
|------|----------------|
| Step 1 | STOP -- Cannot skip, must wait for user reply |
| Step 2-3 | Cannot skip |
| Step 4 | Cannot skip, must wait for user to confirm outline |
| Step 5 Internal | Fixed order: 5a → 5b → 5c |
| Step 6 | Cannot skip, must execute all post-processing pipeline |

---

## Environment Awareness

Self-reflect on agent's tool capabilities before starting work:

| Capability | Degradation Strategy |
|------------|---------------------|
| **Information Retrieval** (search/URL/documents/knowledge base) | All missing -> Rely on user-provided materials |
| **Image Generation** (available in most environments) | Missing -> Pure CSS decoration instead |
| **File Output** | Must have |
| **Script Execution** (Python/Node.js) | Missing -> Skip auto packaging and SVG conversion |

**Principle**: Check the actual callable tool list, use what's available.

---

## Path Conventions

The following paths are repeatedly used throughout the process, confirmed immediately after Step 1 completion:

| Variable | Meaning | How to Get |
|----------|---------|------------|
| `SKILL_DIR` | Absolute path of the directory where this SKILL.md is located | The directory where SKILL.md is located when skill is triggered |
| `OUTPUT_DIR` | Root directory for output | User's current working directory's `ppt-output/` (mkdir -p on first use) |

All subsequent paths are based on these two variables, no further explanation needed.

---

## Input Mode and Complexity Judgment

### Entry Point Judgment

| Entry | Example | Start from Which Step |
|-------|---------|----------------------|
| Pure topic | "Make a Dify company introduction PPT" | Step 1 full process |
| Topic + Requirements | "15 pages AI security PPT, dark theme" | Step 1 (skip some known issues) |
| Source material | "Make this report into PPT" | Step 1 (material-centric) |
| Existing outline | "I have an outline, generate design draft" | Step 4 or 5 |

### Skip Rules

When skipping prerequisite steps, must supplement corresponding dependency products:

| Starting Step | Missing Dependencies | How to Supplement |
|---------------|---------------------|-------------------|
| Step 4 | Each page's content text | First use Prompt #3 to allocate content for each page |
| Step 5 | Draft JSON | User provides or execute Step 4 first |

### Complexity Adaptation

Automatically adjust process granularity based on target page count:

| Scale | Pages | Research | Search | Planning | Generation |
|-------|-------|----------|--------|----------|------------|
| **Light** | <= 8 pages | 3-question simplified version (scenario + audience + supplementary info) | 3-5 queries | Step 3 can be merged with Step 4 | All pages generated in parallel |
| **Standard** | 9-18 pages | Full 7 questions | 8-12 queries | Full process | All pages generated in parallel |
| **Large** | > 18 pages | Full 7 questions | 10-15 queries | Full process | All pages generated in parallel |

---

## Breakpoint Recovery
> Workflow is stateless. After interruption, use milestone_check.py to determine recovery point.

**Execute**:
```bash
python SKILL_DIR/scripts/milestone_check.py OUTPUT_DIR/ --summary
```

**Milestone Status**:
| Milestone | Judgment Condition | Recovery From |
|-----------|-------------------|---------------|
| P0 | No products | Step 1 |
| P1 | `requirements-interview.txt` exists | Step 2 |
| P2 | `search.txt` exists | Step 3 |
| P3 | `outline.json` exists | Step 4 |
| P3.5 | `style.json` exists | Step 5a |
| P4 | `slides/slide-*.html` exists | Step 6 |
| P5 | `presentation-svg.pptx` or `presentation-png.pptx` exists | Complete |

**Rules**:
- Partial HTML files existing counts as P4 (continue from Step 6)
- Never delete existing products when recovering
- Can use `milestone_check.py --check P3` to verify specific milestone

---

## Subagent Dispatch Table
> Each stage has independent Subagent to avoid Context contamination. Each Subagent only carries its own stage's information.

### Subagent Architecture

```
Main Agent (Decision + Dispatch)
    │
    ├── ResearchAgent ──→ search.txt
    │       Model: Must pass --model parameter
    │
    ├── OutlineAgent ──→ outline.txt
    │       Model: Must pass --model parameter
    │
    ├── StyleAgent ──→ style.json
    │       Model: Must pass --model parameter
    │
    ├── PlanningAgent ──→ planning-N.json (per page)
    │       Model: Must pass --model parameter
    │
    ├── PageAgent-1 ──→ slide-1.html (parallel)
    ├── PageAgent-2 ──→ slide-2.html (parallel)
    │         ... (all pages in parallel)
    └── PageAgent-N ──→ slide-N.html (parallel)
        Model: Each PageAgent must pass --model parameter
Main Agent ← All Subagents Complete ← Step 6 Post-Processing
```

### Subagent Rules

| Rule | Description |
|------|-------------|
| **Must specify --model** | Each Subagent must pass --model parameter, no default fallback allowed |
| **Context Isolation** | Each Subagent only reads/writes its own stage's products |
| **Failure Isolation** | Single Subagent failure does not affect other Subagents |
| **Failure Retry** | Failed Subagent retries up to 2 times, if exceeded then report to Main Agent |

### Product Naming Convention

| Product | Filename |
|---------|----------|
| Requirements Interview | `requirements-interview.txt` |
| Information Gathering | `search.txt` |
| Outline | `outline.txt` |
| Style Definition | `style.json` |
| Draft | `planning-N.json` (N = page number) |
| Design Draft | `slides/slide-N.html` |
| Screenshot | `slides/slide-N.png` |
| SVG | `svg/slide-N.svg` |

---

## 6-Step Pipeline

### Step 1: Requirements Research [STOP -- Cannot Skip]

> **Cannot skip.** No matter how simple the topic, must ask questions and wait for user reply before continuing. Don't make decisions for the user.

**Execute**: Use Prompt #1 from `references/prompts.md`
1. Search topic background (3-5 items)
2. Based on complexity, choose full 7 questions or simplified 3 questions, send to user at once, and inform user of supported style options for selection (16 preset styles)
3. **Wait for user reply** (blocking point)
4. Compile into requirements JSON

**7-Question Three-Layer Progressive Structure** (light mode only asks questions 1, 2, 7):

| Layer | Question | Determines |
|-------|----------|------------|
| Scenario Layer | 1. Presentation scenario (live/self-read/training) | Information density and visual style |
| Scenario Layer | 2. Core audience (dynamically generate profile) | Professional depth and persuasion strategy |
| Scenario Layer | 3. Expected action (decision/understanding/execution/cognitive change) | Final content arrangement direction |
| Content Layer | 4. Narrative structure (problem->solution/education/comparison/timeline) | Outline skeleton logic |
| Content Layer | 5. Content focus (dynamically generated from search results, can select multiple) | Part topic weights |
| Content Layer | 6. Persuasion elements (data/case studies/authority/methodology, can select multiple) | Card content type preferences |
| Execution Layer | 7. Supplementary info (speaker/brand color/must-include/must-avoid/page count/image preferences/PPT style) | Specific execution details |

**Product**: Requirements JSON (topic + requirements)

---

### Step 2: Information Gathering

> Inventory all information retrieval capabilities and use them all.

**Execute**:
1. Plan queries based on topic (quantity reference complexity table)
2. Use all available information retrieval tools for parallel search
3. Summarize each group of results

**Product**: Search results collection JSON

---

### Step 3: Outline Planning

**Execute**: Use Prompt #2 from `references/prompts.md` (Outline Architect v2.0)

**Methodology**: Pyramid Principle -- Conclusion first, summarize above, categorize and group, logical progression

**Self-check**: Page count meets requirements / Each part >= 2 pages / Key points have data support

**Product**: `[PPT_OUTLINE]` JSON

---

### Step 3.5: Contract Verification

Before entering content planning, verify contract completeness of generated artifacts:

**Execute**:
```bash
# Verify outline contract
python SKILL_DIR/scripts/contract_validator.py outline OUTPUT_DIR/outline.json

# Verify style definition contract (if style.json exists)
python SKILL_DIR/scripts/contract_validator.py style OUTPUT_DIR/style.json
```

**⚠️ Environment requirement**: Requires Python ≥ 3.8 (`Tuple` type annotations). If Python version is too low causing import failure, inform user they need to upgrade Python or run in a supported environment.

**Outline Contract** (`outline.json` must include):
- `ppt_outline.parts[]` — At least 1 part
- Each part has `part_title` and `pages[]` — Each part has at least 2 content pages
- Each page has `title` and `content`

**Style Contract** (`style.json` must include):
- `style_id` — One of 16 preset style IDs
- `background`, `card`, `text`, `accent` — All exist

**Verification failure**: Return to Step 3 to regenerate corresponding artifact.

---

### Step 4: Content Allocation + Draft [Cannot Skip -- Must Wait for User to Confirm Outline Before Executing]

> Combine content allocation and draft generation into one step. While thinking about what content should go on each page, also decide layout and card types, which is more natural and efficient.

**Execute**: Use Prompt #3 from `references/prompts.md` (Content Allocation and Draft)

**Key Points**:
- Precisely map search materials to each page
- Design multi-level content structure for each page (main card 40-100 chars + data highlights + supporting points)
- Also determine page_type / layout_hint / cards[] structure
- **Each content page must have at least 3 cards + 2 card_types + 1 data card**
- Layout selection reference decision matrix in `references/bento-grid.md`

Show draft overview to user, recommend waiting for user confirmation before entering Step 5.

**Product**: Each page's draft card JSON array -> Save as `OUTPUT_DIR/planning.json`

---

### Step 4.5: Draft Verification

Before entering design draft generation, verify density contract of planning.json:

**Execute**:
```bash
python SKILL_DIR/scripts/planning_validator.py OUTPUT_DIR/planning.json --strict --summary
```

**Density Contract Check** (strict mode):
- Content pages must have **≥ 3 cards**
- Content pages must have **≥ 2 card_types**
- Content pages must have **≥ 1 data type card**

**⚠️ Environment requirement**: Requires Python ≥ 3.8 (`Tuple` / `List` type annotations). If Python version is too low causing import failure, upgrade Python or run in a supported environment.

**Verification failure**: Return to Step 4 to supplement page content.

---

### Step 5: Style Decision + Design Draft Generation

Three sub-steps, **order cannot be reversed**:

#### 5a. Style Decision

**Execute**: Read `references/style-system.md`, select or infer style

Match one of 16 preset styles based on topic keywords (Dark Tech / Xiaomi Orange / Blue-White Business / Vermilion Red Wall / Fresh Nature / Purple-Gold Luxury / Minimalist Gray-White / Vibrant Rainbow / Gradient Blue / Warm Sunset / Nordic Minimal / Cyberpunk / Elegant Gold / Deep Sea Blue / Vintage Film / Stable Blue). See `references/style-system.md` for detailed matching rules and complete JSON definitions.

**Product**: Style definition JSON -> Save as `OUTPUT_DIR/style.json`

#### 5b. Smart Image Matching [Execute Based on Step 1 Question 7 Answer]

> If Step 1 user chose "no images needed", skip all content in this section.

**Step 1 Answer Routing**:

| Step 1 Answer | Action |
|---------------|--------|
| "User provides images" | Use images from user-provided paths |
| "AI generation" | Call image_generate tool |
| "Unsplash" | Call Unsplash API |

##### Image Timing

Before generating each page's HTML, first generate images for that page. At least 1 per page (cover page, chapter covers must have), save to `OUTPUT_DIR/images/` after generation.

**Degradation Chain** (automatic degradation, no need to ask user again):

```
AI Generation (image_generate)
  └─ Tool available → Generate image
  └─ Tool unavailable/failed → Unsplash API
                        └─ Key configured → Search and get
                        └─ Key not configured/failed → Pure CSS decoration degradation

User provided images
  └─ Path valid and semantically matches → Use that image
  └─ Path invalid/semantically doesn't match → Degrade to Unsplash or CSS decoration

Unsplash
  └─ UNSPLASH_ACCESS_KEY configured → Call API
  └─ Key not configured/failed → Pure CSS decoration degradation
```

**Image count by page type**:

| Page Type | When Images Needed | When Not Needed |
|-----------|-------------------|-----------------|
| Cover page | **Must have** | Pure CSS decoration |
| Chapter cover | **Must have** | Pure CSS decoration |
| Content page | Optional 1 per page | No image |
| Ending page | Optional | Pure CSS decoration |

**Product**: Image files under `OUTPUT_DIR/images/` (if any)

##### image_generate Prompt Construction Formula

Prompt must satisfy **4 dimensions** simultaneously, assembled by formula:

[Content Topic] + [Visual Style] + [Image Composition] + [Technical Constraints]

| Dimension | Description | Example |
|-----------|-------------|---------|
| Content Topic | Extracted from the page's draft JSON core concept, specific to scene/object | "DMSO molecular purification process, crystallization flask with clear liquid" |
| Visual Style | Aligned with style.json's color scheme and emotional tone | Dark tech -> "deep blue dark tech background, subtle cyan glow, futuristic" |
| Image Composition | Determined by how image is placed on page | Right side semi-transparent -> "clean composition, main subject on left, fade to transparent on right" |
| Technical Constraints | Fixed suffix ensuring output quality | "no text, no watermark, high quality, professional illustration" |

##### Style and Image Keyword Mapping

| PPT Style | Image Style Keywords |
|-----------|---------------------|
| Dark Tech | dark tech background, neon glow, futuristic, digital, cyber |
| Xiaomi Orange | minimal dark background, warm orange accent, clean product shot, modern |
| Blue-White Business | clean professional, light blue, corporate, minimal, bright |
| Vermilion Red Wall | traditional Chinese, elegant red gold, ink painting, cultural |
| Fresh Nature | fresh green, organic, nature, soft light, watercolor |
| Purple-Gold Luxury | luxury, purple gold, premium, elegant, metallic |
| Minimalist Gray-White | minimal, grayscale, clean, geometric, academic |
| Vibrant Rainbow | colorful, vibrant, energetic, playful, gradient, pop art |
| Gradient Blue | gradient blue, tech, futuristic, clean, digital, professional |
| Warm Sunset | warm orange, sunset, lifestyle, travel, food, cozy lighting |
| Nordic Minimal | minimal, white, clean, scandinavian, lifestyle, bright |
| Cyberpunk | neon, cyber, dark, futuristic, gaming, vibrant, holographic |
| Elegant Gold | gold, luxury, elegant, premium, metallic, champagne |
| Deep Sea Blue | ocean blue, deep sea, marine, aquatic, serene, gradient |
| Vintage Film | vintage, film grain, retro, warm tones, nostalgic, cinematic |
| Stable Blue | corporate, professional, blue, business, formal, trustworthy |

##### Adjustment by Page Type

| Page Type | Image Features | Additional Prompt Keywords |
|-----------|---------------|---------------------------|
| Cover page | Topic overview, visual impact | "hero image, wide composition, dramatic lighting" |
| Chapter cover | Symbolic visual of chapter topic | "symbolic, conceptual, centered composition" |
| Content page | Supporting illustration, not overwhelming | "supporting illustration, subtle, background-suitable" |
| Data page | Abstract data visualization atmosphere | "abstract data visualization, flowing lines, tech" |

##### Prohibited Items
- No text in images (AI-generated text quality is poor)
- No colors conflicting with page color scheme (dark theme with dark images, light theme with light images)
- No decorative images unrelated to content (each image must be semantically related to page content)
- No reusing the same prompt (each page's image must be unique)

**Product**: Image files under `OUTPUT_DIR/images/`

#### 5c. PageAgent Parallel Generation

> **Cannot skip draft and generate directly.** Each page must first have Step 4's structure JSON.

**Parallel Scheduling**: All pages generated in parallel through PageAgent-N subagents, each PageAgent only responsible for one page.

**Parallel Strategy**:

| Scale | Pages | Strategy |
|-------|-------|----------|
| **Small** | <= 5 pages | All pages in parallel |
| **Standard** | 6-18 pages | All pages in parallel (independent) |
| **Large** | > 18 pages | Parallel by Part, all parallel within Part |

**PageAgent Workflow**:
```
PageAgent-N
    │
    ├── 1. Read planning-N.json
    ├── 2. Read style.json
    ├── 3. Read images/planning-N.png (if exists)
    ├── 4. Generate slide-N.html
    ├── 5. ⛔ DOM Assertion (mandatory, must) — Execute visual_qa.py:
    │       python SKILL_DIR/scripts/visual_qa.py OUTPUT_DIR/slides/slide-N.html --verbose
    │       Check: overflow:hidden / forbidden CSS / SVG text / image paths valid
    │       FORBIDDEN items (conic-gradient / ::before-decoration / border-triangle) fail directly
    │       Retry 1 time on failure, still fails then report Main Agent to fix HTML and continue
    └── 6. Output: --- PAGE N COMPLETE ---
```

**DOM Assertion Check Items**:
- Root container has `overflow:hidden`
- No `::before`/`::after` for visual decoration
- No `conic-gradient`
- No CSS border triangle technique
- No SVG `<text>` elements (use HTML overlay instead)
- All `<img>` src paths point to existing files

**Failure Handling**:
- Single page failure does not affect other pages
- Failed page enters PagePatchAgent retry queue (up to 2 retries)
- Main Agent waits for all PageAgents to complete then enters Step 6

**Per-Page Prompt Assembly Formula**:
```
Prompt #4 template
+ Style definition JSON (5a product) [required]
+ Page draft JSON (Step 4 product, contains cards[]/card_type/position/layout_hint) [required]
+ Page content text (Step 4 product) [required]
+ Image path (5b product) [optional -- omit IMAGE_INFO block when no image]
```

**Core Design Constraints** (complete list in Prompt #4):
- Canvas 1280x720px, overflow:hidden
- All colors referenced via CSS variables, no hardcoding
- All visually visible elements must be real DOM nodes, graphics prefer inline SVG
- No `::before`/`::after` pseudo-elements for visual decoration, no `conic-gradient`, no CSS border triangles
- Image integration into design: fade merge/color tone mask/atmospheric background/cropped viewport/circular crop (techniques detailed in Prompt #4)

**Cross-Page Visual Narrative**:

| Strategy | Rule | Reason |
|----------|------|--------|
| **Density Alternation** | High-density page followed by low-density page | Avoid visual fatigue |
| **Chapter Color Progression** | Each Part uses different accent color | Unconsciously perceive chapter transitions |
| **Cover-Ending Echo** | Ending page echoes cover page | Complete closure feeling |
| **Progressive Revelation** | Complexity increases page by page | Guide audience to gradually deepen |

**Product**: One HTML file per page -> `OUTPUT_DIR/slides/`

---

### Step 6: Post-Processing [Must Do -- Execute Immediately After HTML Generation]

> **Cannot skip, must execute.** After HTML generation, must immediately execute the following pipeline steps.

```
slides/*.html
  ├── html_packager.py --> preview.html
  ├── html2svg.py --> svg/*.svg
  ├── svg2pptx.py --> presentation-svg.pptx
  ├── html2png.py --> png/*.png
  └── png2pptx.py --> presentation-png.pptx
```

**Dependency Check** (auto-execute on first run):
```bash
pip install python-pptx lxml Pillow 2>/dev/null
npm install puppeteer dom-to-svg 2>/dev/null
```

**Execute in order**:

1. **Merge Preview** -- Run `html_packager.py`
   ```bash
   python SKILL_DIR/scripts/html_packager.py OUTPUT_DIR/slides/ \
       -o OUTPUT_DIR/preview.html --title "PPT Preview"
   ```

2. **SVG Conversion** -- Run `html2svg.py`
   > **Important**: HTML design drafts must comply with `references/pipeline-compat.md` rules.
   ```bash
   python SKILL_DIR/scripts/html2svg.py OUTPUT_DIR/slides/ \
       -o OUTPUT_DIR/svg/
   ```

   First run will auto-build dom-to-svg bundle (`dom-to-svg.bundle.js`).
   **Degradation**: If dom-to-svg fails, SVG branch stops, PNG branch continues.

3. **SVG PPTX Export** -- Run `svg2pptx.py`
   ```bash
   python SKILL_DIR/scripts/svg2pptx.py OUTPUT_DIR/svg/ \
       -o OUTPUT_DIR/presentation-svg.pptx \
       --html-dir OUTPUT_DIR/slides/
   ```

   In PPT 365, right-click image -> "Convert to Shape" to edit text.

4. **PNG Screenshot** -- Run `html2png.py`
   ```bash
   python SKILL_DIR/scripts/html2png.py OUTPUT_DIR/slides/ \
       -o OUTPUT_DIR/png/ -c 4
   ```

   **Degradation**: If Playwright unavailable, skip PNG branch (SVG branch continues).

5. **PNG PPTX Export** -- Run `png2pptx.py`
   ```bash
   python SKILL_DIR/scripts/png2pptx.py OUTPUT_DIR/png/ \
       -o OUTPUT_DIR/presentation-png.pptx
   ```

7. **Notify User** -- Inform product locations and usage:
   - `preview.html` -- Open in browser to flip through preview
   - `presentation-svg.pptx` -- SVG vector PPTX (text editable, "Convert to Shape" in PPT 365)
   - `presentation-png.pptx` -- PNG pixel PPTX (perfect visual effect, text not editable)
   - `svg/` -- Each SVG can also be dragged into PPT individually
   - `png/` -- PNG screenshots (for Visual QA reference)
   - **If SVG branch was degraded/skip**, explain reason and inform user they can manually install Node.js and rerun
   - **If PNG branch was degraded/skip**, explain PNG screenshots are only for Visual QA

**Product**: preview.html + svg/*.svg + png/*.png + presentation-svg.pptx + presentation-png.pptx

---

## Output Directory Structure

```
ppt-output/
  slides/                    # Each page HTML
  svg/                       # Vector SVG (can import to PPT for editing)
  png/                       # PNG screenshots (for Visual QA + PNG PPTX export)
  images/                    # AI-generated images
  preview.html               # Pageable preview
  presentation-svg.pptx      # SVG vector PPTX (text editable)
  presentation-png.pptx      # PNG pixel PPTX (perfect visual effect)
  outline.json               # Outline
  planning.json              # Draft
  style.json                 # Style definition
```

---

## Quality Self-Check

| Dimension | Check Items |
|-----------|-------------|
| Content | Each page >= 2 info cards / >= 60% content pages contain data / chapters have progression |
| Visual | Global style consistent / image style unified / cards don't overlap / text doesn't overflow |
| Technical | CSS variables unified / SVG-friendly constraints followed / HTML renderable by Puppeteer / `pipeline-compat.md` prohibited list checked |

---

## Reference File Index

| File | When to Read | Key Content |
|------|--------------|-------------|
| `references/prompts.md` | Before each step generation | 5 Prompt templates (research/outline/planning/design/notes) |
| `references/style-system.md` | Step 5a | 16 preset styles + CSS variables + style JSON model |
| `references/bento-grid.md` | Step 5c | 7 layouts + 12 card types + decision matrix |
| `references/method.md` | Initial understanding | Core philosophy and methodology |
| `references/pipeline-compat.md` | **Step 5c design draft generation** | CSS prohibited list + image paths + font size mixing + SVG text + ring charts + svg2pptx notes |