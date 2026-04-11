---
name: ppt-agent
description: Professional full-process PPT presentation AI generation assistant. Simulates the complete workflow of a top-tier PPT design company (requirements research -> information gathering -> outline planning -> draft planning -> design draft), outputting high-quality HTML presentations. Triggered when users mention making PPT, presentations, slides, training materials, roadshow decks, or product introduction pages. Also applies when users say "help me make an introduction about X" or "I need to present Y to my boss" - any scenario requiring structured multi-page presentation content.
---

# PPT Agent -- Professional Full-Process Presentation Generation

## Core Philosophy

Mimics the complete workflow of a professional PPT design company (priced at 10,000+ RMB per page), not "give an outline and apply a template":

1. **Research before generation** -- Fill content with real data, never fabricate
2. **Separate planning from design** -- Verify information structure first, then apply visual packaging
3. **Content-driven layout** -- Bento Grid card-style layout, each page's layout determined by its content
4. **Consistent global style** -- Lock in style first, then generate page by page, ensuring cross-page consistency
5. **Smart illustrations** -- Use image generation capabilities to add illustrations for each page (available in most environments)

---

## Environment Setup [Required for First Use]

### Node.js Environment

**China Mainland mirror installation** (must set, otherwise puppeteer Chrome binary download will fail):

```bash
export PUPPETEER_DOWNLOAD_HOST=https://storage.googleapis.com.cnpmjs.org
npm install -g puppeteer --unsafe-perm
npm install -g dom-to-svg esbuild
```

**Verification**: `node -e "require('puppeteer'); console.log('puppeteer OK')"`

If full puppeteer fails to install (Chrome download blocked in China mainland), scripts will automatically fall back to `puppeteer-core` with system Chrome at `/usr/bin/google-chrome`. You can also install it directly:

```bash
npm install -g puppeteer-core
````

### Python Environment

```bash
pip install python-pptx lxml Pillow playwright
playwright install chromium  # 安装 Chromium 浏览器（首次需运行）
```

> **注意**：html2png.py 使用 Playwright Python（纯 Python 库），不需要 Node.js。
> html2svg.py 使用 Node.js Puppeteer（如只需 SVG/PPTX 分支且 Node.js 可用，可跳过 Playwright）。
> 两者互不影响，可独立使用。

---

## Pre-Flight: Output Directory Check [STOP -- Must Verify]

> 每次启动 PPT 流程前，**必须**检查 `OUTPUT_DIR` 是否为空。若有遗留文件，可能污染本次产物。

**Execute**:
```bash
ls -la OUTPUT_DIR/
```

**Decision Table**:

| 检查结果 | 行为 |
|---------|------|
| 目录不存在或为空 | 直接进入 Step 1 |
| 有遗留文件 | **停止并告知用户**：列出所有文件，说明风险，等待用户确认删除或更换目录 |
| 用户要求删除 | 执行 `rm -rf OUTPUT_DIR/*` 后继续 |
| 用户指定新目录 | 更新 `OUTPUT_DIR` 变量，重新检查 |

**强制提示文案**（直接发给用户）:
```
⚠️ 工作目录 ppt-output/ 不为空，检测到以下文件：
  - xiaomi_su7_pptx.pptx (2026-04-11 08:22)
  - presentation-svg.pptx (2026-04-11 08:20)
  ...
这些文件与本次「苹果公司介绍」主题不符。若继续可能造成产物混乱。

请选择：
1. 删除所有旧文件（推荐）
2. 使用新的输出目录
3. 取消本次任务
```

**断点恢复检查**（目录为空或清理后，Main Agent 启动时必须执行）:
```bash
python SKILL_DIR/scripts/milestone_check.py OUTPUT_DIR/ --summary
```

根据 milestone 状态决定从哪个 Step 继续。若已有历史产物，禁止无视并重复生成。

---

## Pipeline Mandatory Declaration [Red Lines]

> The following rules must not be violated. Any bypass will cause severe degradation in output quality.

### Six-Step Pipeline Order is Fixed, No Skipping

```
Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6
```

### Prohibited Behaviors

- ❌ Skip Step 1 and directly generate PPT
- ❌ Enter Step 5c without a planning draft
- ❌ Stop at preview.html without executing SVG and PPTX
- ❌ Use other tools/pipelines to replace this workflow

### Only Allowed Degradation

- Node.js unavailable → Skip SVG branch (html2svg.py needs Node.js), PNG branch continues (html2png.py is pure Python).
- Python unavailable → Skip SVG + PNG + PPTX branches, output preview.html only. Notify user and wait for feedback.
- Playwright unavailable → Skip PNG branch (visual_qa.py also skipped). SVG branch continues.
- Vision model unavailable → Skip visual audit in visual_qa.py, DOM assertion still runs.
- Vision model unavailable → Skip visual audit in visual_qa.py, DOM assertion still runs.

### Step Enforcement Levels

| Step | Enforcement Level |
|------|------------------|
| Step 1 | STOP -- Cannot skip, must wait for user reply |
| Step 2-3 | Cannot skip |
| Step 4 | Cannot skip, must wait for user confirmation of outline |
| Step 5 internal | Fixed order: 5a → 5b → 5c |
| Step 6 | Cannot skip, must execute all post-processing pipeline |

---

## Environment Awareness

Self-reflect on the agent's tool capabilities before starting work:

| Capability | Degradation Strategy |
|------------|---------------------|
| **Information retrieval** (search/URL/docs/knowledge base) | All missing -> rely on user-provided materials |
| **Image generation** (available in most environments) | Missing -> pure CSS decoration instead |
| **File output** | Must have |
| **Script execution** (Python/Node.js) | Missing -> skip auto-packaging and SVG conversion |

**Principle**: Check the actually callable tool list, use whatever is available.

---

## Path Conventions

Paths used repeatedly throughout the process. Determine immediately after Step 1:

| Variable | Meaning | How to Get |
|----------|---------|------------|
| `SKILL_DIR` | Absolute path of the directory where this SKILL.md resides | The directory from which SKILL.md is read when the skill is triggered |
| `OUTPUT_DIR` | Output root directory | `ppt-output/` under the user's current working directory (mkdir -p on first use) |

All subsequent paths are based on these two variables and will not be explained again.

---

## Input Modes and Complexity Assessment

### Entry Detection

| Entry | Example | Start from |
|-------|---------|------------| 
| Topic only | "Make a Dify company introduction PPT" | Step 1 full flow |
| Topic + requirements | "15-page AI security PPT, dark tech style" | Step 1 (skip some known issues)|
| Source material | "Turn this report into a PPT" | Step 1 (material-focused)|
| Existing outline | "I have an outline, generate the design" | Step 4 or 5 |

### Skip Rules

When skipping pre-requisite steps, must complete corresponding dependent outputs:

| Starting Step | Missing Dependency | How to Fill |
|--------------|--------------------| ------------|
| Step 4 | Page content text | First use Prompt #3 to generate content allocation for each page |
| Step 5 | Planning draft JSON | User provides or execute Step 4 first |

### Complexity Adaptation

Automatically adjust process granularity based on target page count:

| Scale | Pages | Research | Search | Planning | Generation |
|-------|-------|----------|--------|----------|------------|
| **Light** | <= 8 pages | 3-question abbreviated version (scenario + audience + supplementary info) | 3-5 queries | Step 3 can be merged with Step 4 | Page by page |
| **Standard** | 9-18 pages | Full 7 questions | 8-12 queries | Full process | By Part, 3-5 pages per batch |
| **Large** | > 18 pages | Full 7 questions | 10-15 queries | Full process | By Part, 3-5 pages per batch, confirm between batches |

---

## Breakpoint Recovery
> The workflow is stateless. After interruption, use milestone_check.py to determine the recovery point automatically.

**Execute**:
```bash
python SKILL_DIR/scripts/milestone_check.py OUTPUT_DIR/ --summary
```

**Milestone States**:
| Milestone | Check | Resume From |
|-----------|-------|------------|
| P0 | No artifacts found | Step 1 |
| P1 | `requirements-interview.txt` exists | Step 2 |
| P2 | `search.txt` exists | Step 3 |
| P3 | `outline.json` exists | Step 4 |
| P3.5 | `style.json` exists | Step 5a |
| P4 | `slides/slide-*.html` exist | Step 6 |
| P5 | `presentation-svg.pptx` or `presentation-png.pptx` exists | Done |

**Rules**:
- Partial HTML files count as P4 reached (resume from Step 6)
- Artifacts already written are never deleted during recovery
- Run `milestone_check.py --check P3` to verify a specific milestone

---

## Subagent Scheduling (Subagent Dispatch)

> Each stage has a dedicated Subagent to avoid Context pollution. Context isolation ensures each Subagent only carries its own stage's information.

### Subagent Architecture

```
Main Agent (Decision + Dispatch)
    │
    ├── ResearchAgent ──→ search.txt
    │       Model: MUST pass --model parameter
    │
    ├── OutlineAgent ──→ outline.txt
    │       Model: MUST pass --model parameter
    │
    ├── StyleAgent ──→ style.json
    │       Model: MUST pass --model parameter
    │
    ├── PlanningAgent ──→ planning-N.json (per page)
    │       Model: MUST pass --model parameter
    │
    ├── PageAgent-1 ──→ slide-1.html (parallel)
    ├── PageAgent-2 ──→ slide-2.html (parallel)
    │         ... (all pages parallel)
    └── PageAgent-N ──→ slide-N.html (parallel)
        Model: MUST pass --model parameter for each

Main Agent ← All Subagents complete ← Step 6 Post-processing
```

### Subagent Rules

| Rule | Description |
|------|-------------|
| **Must specify --model** | Every Subagent MUST receive explicit --model parameter, no default fallback |
| **Context isolation** | Each Subagent only reads/writes its own stage's artifacts |
| **Failure isolation** | Single Subagent failure does not block other Subagents |
| **Retry on failure** | Failed Subagent retries up to 2 times before escalation to Main Agent |

### Artifact Naming Convention

| Artifact | Filename |
|----------|----------|
| Requirements | `requirements-interview.txt` |
| Search Results | `search.txt` |
| Outline | `outline.txt` |
| Style Definition | `style.json` |
| Planning Draft | `planning-N.json` (N = page number) |
| Design Draft | `slides/slide-N.html` |
| Screenshot | `slides/slide-N.png` |
| SVG | `svg/slide-N.svg` |

---


## 6-Step Pipeline

### Step 1: Requirements Interview [STOP -- Cannot Skip]

> **Cannot skip.** No matter how simple the topic, must ask questions and wait for user reply before continuing. Do not make decisions for the user.

**Execute**: Use `references/prompts.md` Prompt #1
1. Search topic background information (3-5 items)
2. Based on complexity, choose full 7 questions or abbreviated 3 questions, send to user in one go
3. **Wait for user reply** (blocking point)
4. Organize into requirements JSON

**7-Question Three-Tier Structure** (light mode only asks questions 1, 2, 7):

| Tier | Question | Determines |
|------|----------|------------|
| Scenario | 1. Presentation scenario (live/self-reading/training) | Information density and visual style |
| Scenario | 2. Core audience (dynamically generated profile) | Professional depth and persuasion strategy |
| Scenario | 3. Desired action (decision/understanding/execution/change perception) | Final content arrangement direction |
| Content | 4. Narrative structure (problem->solution/educational/comparison/timeline) | Outline skeleton logic |
| Content | 5. Content focus (dynamically generated from search results, multi-select) | Each Part's theme weight |
| Content | 6. Persuasion elements (data/case/authority/method, multi-select) | Card content type preferences |
| Execution | 7. Supplementary info (speaker/brand colors/must-include/must-avoid/page count/illustration preference) | Specific execution details |

**Output**: Requirements JSON (topic + requirements)

---

### Step 2: Information Gathering

> Take inventory of all information retrieval capabilities and use them all.

**Execute**:
1. Plan queries based on topic (quantity reference complexity table)
2. Use all available information retrieval tools for parallel search
3. Summarize each group of results

**Output**: Search results collection JSON

---

### Step 3: Outline Planning

**Execute**: Use `references/prompts.md` Prompt #2 (Outline Architect v2.0)

**Methodology**: Pyramid Principle -- Conclusion first, above to below, categorize and group, logical progression

**Self-check**: Page count meets requirements / each part >= 2 pages / key points have data support

**Output**: `[PPT_OUTLINE]` JSON

---

### Step 3.5: Contract Validation

Before proceeding to content planning, validate the artifacts generated so far:

**Execute**:
```bash
# Validate outline contract
python SKILL_DIR/scripts/contract_validator.py outline OUTPUT_DIR/outline.json

# Validate style contract (if style.json already exists)
python SKILL_DIR/scripts/contract_validator.py style OUTPUT_DIR/style.json
```

**⚠️ 环境要求**: 需要 Python ≥ 3.8（`Tuple` 类型注解）。若 Python 版本过低导致导入失败，请升级 Python 或在支持的环境中运行。

**Outline Contract** (`outline.json` must contain):
- `ppt_outline.parts[]` — at least 1 part
- Each part has `part_title` and `pages[]` — at least 2 content pages per part
- Each page has `title` and `content`

**Style Contract** (`style.json` must contain):
- `style_id` — one of the 16 preset style IDs
- `background`, `card`, `text`, `accent` — all present

**If validation fails**: Return to Step 3 to regenerate the defective artifact.

---

### Step 4: Content Allocation + Planning Draft [Cannot Skip -- Must Wait for User Confirmation of Outline]

> Combine content allocation and planning draft generation into one step. While thinking about what content each page should have, also decide layout and card types, making it more natural and efficient.

**Execute**: Use `references/prompts.md` Prompt #3 (Content Allocation and Planning Draft)

**Key Points**:
- Precisely map search materials to each page
- Design multi-layer content structure for each page (main card 40-100 chars + data highlight + supporting points)
- Also determine page_type / layout_hint / cards[] structure
- **Each content page at least 3 cards + 2 card_types + 1 data card**
- Layout selection reference `references/bento-grid.md` decision matrix

Show planning draft overview to user, recommend waiting for user confirmation before entering Step 5.

**Output**: Per-page planning card JSON array -> Save as `OUTPUT_DIR/planning.json`

---

### Step 4.5: Planning Validation

Before entering design draft generation, validate planning.json's density contract:

**Execute**:
```bash
python SKILL_DIR/scripts/planning_validator.py OUTPUT_DIR/planning.json --strict --summary
```

**⚠️ 环境要求**: 需要 Python ≥ 3.8（`Tuple` / `List` 类型注解）。若 Python 版本过低导致导入失败，请升级 Python 或在支持的环境中运行。

**Density Contract Checks (strict mode)**:
- Content pages must have **≥ 3 cards**
- Content pages must have **≥ 2 different card_types**
- Content pages must have **≥ 1 data-type card**

**If validation fails**: Return to Step 4 to supplement page content.

---

### Step 5: Style Decision + Design Draft Generation

Split into three sub-steps, **order cannot be reversed**:

#### 5a. Style Decision

**Execute**: Read `references/style-system.md`, select or infer style

Match one of **16 preset styles** based on topic keywords:

dark tech / xiaomi orange / blue white / royal red / fresh green / luxury purple / minimal gray / vibrant rainbow / gradient blue / warm sunset / nordic white / cyber punk / elegant gold / ocean depth / retro film / corporate blue

See `references/style-system.md` for detailed matching rules and full JSON definitions.

**Output**: Style definition JSON -> Save as `OUTPUT_DIR/style.json`

#### 5b. Smart Illustrations [Execute Based on Step 1 Question 7 Answer]

> If user selected "no illustrations needed" in Step 1, skip this entire section.

**Step 1 Answer Routing**:

| Step 1 Answer | Action |
|---------------|--------|
| "User provides images" | Use images from user-provided paths |
| "AI generation" | Call image_generate tool |
| "Unsplash" | Call Unsplash API |

##### Illustration Timing

Before generating each page's HTML, generate that page's illustration first. At least 1 per page (cover page, section cover must have), save to `OUTPUT_DIR/images/`.

**⚠️ Image Path Rule -- MUST FOLLOW**: All images must be downloaded to `OUTPUT_DIR/images/` **before** generating HTML. Use `<img src="images/xxx.png">` with relative paths in HTML. **Never** reference external URLs (Unsplash etc.) directly in HTML -- they cannot load under `file://` protocol.

**Degradation Chain** (automatic degradation, no need to ask user again):

```
AI generation (image_generate)
  └─ Tool available → Generate image
  └─ Tool unavailable/failed → Unsplash API
                                 └─ Key configured → Search and get
                                 └─ Key not configured/failed → Pure CSS decoration degradation

User provides images
  └─ Path valid and semantically matches → Use that image
  └─ Path invalid/semantically mismatched → Degrade to Unsplash or CSS decoration

Unsplash
  └─ UNSPLASH_ACCESS_KEY configured → Call API
  └─ Key not configured/failed → Pure CSS decoration degradation
```

**Image Quantity by Page Type**:

| Page Type | With Illustrations | Without |
|-----------|-------------------|---------|
| Cover page | **Must have** | Pure CSS decoration |
| Section cover | **Must have** | Pure CSS decoration |
| Content page | Optional 1 per page | No image |
| End page | Optional | Pure CSS decoration |

**Output**: Illustration files under `OUTPUT_DIR/images/` (if any)

##### image_generate Prompt Construction Formula

Prompt must satisfy **4 dimensions** simultaneously, assembled by formula:

[Content Topic] + [Visual Style] + [Image Composition] + [Technical Constraints]

| Dimension | Description | Example |
|-----------|-------------|---------|
| Content topic | Extracted from that page's planning draft JSON core concept, specific to scene/object | "DMSO molecular purification process, crystallization flask with clear liquid" |
| Visual style | Aligned with style.json color scheme and emotional tone | Dark tech -> "deep blue dark tech background, subtle cyan glow, futuristic" |
| Image composition | Decided by how the image is placed in the page | Right side semi-transparent -> "clean composition, main subject on left, fade to transparent on right" |
| Technical constraints | Fixed suffix ensuring output quality | "no text, no watermark, high quality, professional illustration" |

##### Style and Illustration Keyword Mapping

| PPT Style | Illustration Style Keywords |
|-----------|---------------------------|
| Dark tech | dark tech background, neon glow, futuristic, digital, cyber |
| Xiaomi orange | minimal dark background, warm orange accent, clean product shot, modern |
| Blue white business | clean professional, light blue, corporate, minimal, bright |
| Royal red | traditional Chinese, elegant red gold, ink painting, cultural |
| Fresh green | fresh green, organic, nature, soft light, watercolor |
| Luxury purple | luxury, purple gold, premium, elegant, metallic |
| Minimal gray | minimal, grayscale, clean, geometric, academic |
| Vibrant rainbow | colorful, vibrant, energetic, playful, gradient, pop art |
| Gradient blue | gradient blue, tech, futuristic, clean, digital, professional |
| Warm sunset | warm orange, sunset, lifestyle, travel, food, cozy lighting |
| Nordic white | minimal, white, clean, scandinavian, lifestyle, bright |
| Cyber punk | neon, cyber, dark, futuristic, gaming, vibrant, holographic |
| Elegant gold | gold, luxury, elegant, premium, metallic, champagne |
| Ocean depth | ocean blue, deep sea, marine, aquatic, serene, gradient |
| Retro film | vintage, film grain, retro, warm tones, nostalgic, cinematic |
| Corporate blue | corporate, professional, blue, business, formal, trustworthy |

##### Adjustment by Page Type

| Page Type | Image Characteristics | Prompt Additional Keywords |
|-----------|---------------------|---------------------------|
| Cover page | Topic overview, visual impact | "hero image, wide composition, dramatic lighting" |
| Section cover | Symbolic visual of that chapter's topic | "symbolic, conceptual, centered composition" |
| Content page | Supporting illustration, not overwhelming | "supporting illustration, subtle, background-suitable" |
| Data page | Abstract data visualization atmosphere | "abstract data visualization, flowing lines, tech" |

##### Prohibited Items
- No text in images (AI-generated text quality is poor)
- No colors conflicting with page color scheme (dark theme with dark images, light theme with light images)
- No irrelevant decorative images (every image must be semantically related to that page's content)
- No duplicate prompts (each page's image must be unique)

**Output**: Illustration files under `OUTPUT_DIR/images/`

#### 5c. PageAgent Parallel Generation

> **Cannot skip planning draft and directly generate.** Each page must first have Step 4's structure JSON.

**Parallel Scheduling**: All pages are generated in parallel via PageAgent-N subagents. Each PageAgent is responsible for one page only.

**Parallel Strategy**:

| Scale | Pages | Strategy |
|-------|-------|----------|
| **Small** | <= 5 pages | All pages parallel |
| **Standard** | 6-18 pages | All pages parallel (independent) |
| **Large** | > 18 pages | By Part parallel, pages within Part parallel |

**PageAgent Workflow**:
```
PageAgent-N
    │
    ├── 1. Read planning-N.json
    ├── 2. Read style.json
    ├── 3. Read images/planning-N.png (if exists)
    ├── 4. Generate slide-N.html
    ├── 5. ⛔ DOM Assertion（强制，必须）— Run visual_qa.py:
    │       python SKILL_DIR/scripts/visual_qa.py OUTPUT_DIR/slides/slide-N.html --verbose
    │       Check: overflow:hidden / no forbidden CSS / no SVG text / valid image refs
    │       FORBIDDEN 项目（conic-gradient / ::before-decoration / border-triangle）直接失败
    │       失败重试 1 次，仍失败则报告 Main Agent 介入修复 HTML 后继续
    └── 6. Output: --- PAGE N COMPLETE ---
```

**DOM Assertion Checks**:
- `overflow:hidden` present on root container
- No `::before`/`::after` used for visual decoration
- No `conic-gradient`
- No CSS border triangle tricks
- No SVG `<text>` elements (use HTML overlays instead)
- All `<img>` src paths resolve to existing files

**Failure Handling**:
- Single page failure does not affect other pages
- Failed page enters PagePatchAgent retry queue (max 2 retries)
- Main Agent waits for all PageAgents to complete before proceeding to Step 6

**Per-Page Prompt Assembly Formula**:
```
Prompt #4 template
+ Style definition JSON (5a output) [required]
+ That page's planning draft JSON (Step 4 output, containing cards[]/card_type/position/layout_hint) [required]
+ That page's content text (Step 4 output) [required]
+ Illustration path (5b output) [optional -- omit IMAGE_INFO block when no illustration]
```

**Core Design Constraints** (complete checklist in Prompt #4):
- Canvas 1280x720px, overflow:hidden
- All colors referenced via CSS variables, no hardcoding
- All visually visible elements must be real DOM nodes, graphics prefer inline SVG
- Prohibited: `::before`/`::after` pseudo-elements for visual decoration, `conic-gradient`, CSS border triangles
- Illustration integration: fade blend / tinted overlay / ambient background / crop viewport / circular crop (techniques in Prompt #4)

**Cross-Page Visual Narrative**:

| Strategy | Rule | Reason |
|----------|------|--------|
| **Density alternation** | High-density pages followed by low-density pages | Avoid visual fatigue |
| **Chapter color progression** | Each Part uses a different accent main color | Unconsciously perceive chapter transitions |
| **Cover-ending echo** | End page echoes cover page | Complete closed-loop |
| **Progressive revelation** | Complexity increases across pages | Guide audience to deeper understanding |

**Output**: One HTML file per page -> `OUTPUT_DIR/slides/`

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

**Dependency check** (auto-execute on first run):
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

   dom-to-svg bundle (`dom-to-svg.bundle.js`) is auto-built on first run.
   **Degradation**: If dom-to-svg fails, SVG branch aborts. PNG branch continues independently.

3. **SVG PPTX Export** -- Run `svg2pptx.py`
   ```bash
   python SKILL_DIR/scripts/svg2pptx.py OUTPUT_DIR/svg/ \
       -o OUTPUT_DIR/presentation-svg.pptx \
       --html-dir OUTPUT_DIR/slides/
   ```

   In PPT 365: right-click SVG image -> "Convert to Shape" to edit text.

4. **PNG Screenshot** -- Run `html2png.py`
   ```bash
   python SKILL_DIR/scripts/html2png.py OUTPUT_DIR/slides/ \
       -o OUTPUT_DIR/png/ -c 4
   ```

   **Degradation**: If Playwright unavailable, skip PNG branch entirely (SVG branch continues).

5. **PNG PPTX Export** -- Run `png2pptx.py`
   ```bash
   python SKILL_DIR/scripts/png2pptx.py OUTPUT_DIR/png/ \
       -o OUTPUT_DIR/presentation-png.pptx
   ```

7. **Notify User** -- Inform output location and usage:
   - `preview.html` -- Open in browser for paginated preview
   - `presentation-svg.pptx` -- PPTX with editable text and shapes (SVG vectors)
   - `presentation-png.pptx` -- PPTX with pixel-perfect visuals (PNG backgrounds, text not editable)
   - `svg/` -- Each SVG can also be dragged individually into PPT
   - `png/` -- PNG screenshots (for Visual QA reference)
   - **If SVG branch was skipped**, explain reason and tell user they can install Node.js and rerun
   - **If PNG branch was skipped**, note that PNG screenshots are used for Visual QA only

**Output**: preview.html + svg/*.svg + png/*.png + presentation-svg.pptx + presentation-png.pptx

---

## Output Directory Structure

```
ppt-output/
  slides/                  # Per-page HTML
  svg/                     # Vector SVG (importable into PPT for editing)
  png/                     # PNG screenshots (for Visual QA + PNG PPTX export)
  images/                  # AI illustrations
  preview.html             # Paginated preview
  presentation-svg.pptx    # Editable PPTX (SVG vectors, PPT 365 "Convert to Shape")
  presentation-png.pptx    # Pixel-perfect PPTX (PNG backgrounds, not editable)
  outline.json             # Outline
  planning.json            # Planning draft
  style.json               # Style definition
```

---

## Quality Self-Check

| Dimension | Check Items |
|-----------|-------------|
| Content | Each page >= 2 info cards / >= 60% content pages contain data / chapters have progression |
| Visual | Global style consistent / illustration style unified / cards don't overlap / text doesn't overflow |
| Technical | CSS variables unified / SVG-friendly constraints followed / HTML renderable by Puppeteer / `pipeline-compat.md` prohibited list checked |

---

## Reference File Index

| File | When to Read | Key Content |
|------|-------------|-------------|
| `references/prompts.md` | Before each generation step | 5 Prompt templates (research/outline/planning/design/notes) |
| `references/style-system.md` | Step 5a | 16 preset styles + CSS variables + style JSON model |
| `references/bento-grid.md` | Step 5c | 7 layout specs + 12 card types + decision matrix |
| `references/method.md` | First-time understanding | Core philosophy and methodology |
| `references/pipeline-compat.md` | **During Step 5c design draft generation** | CSS prohibited list + image paths + font size mixing + SVG text + ring charts + svg2pptx notes |
