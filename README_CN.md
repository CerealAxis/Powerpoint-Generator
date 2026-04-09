# Powerpoint-Generator

> 一个高质量 PPT 生成工具，模仿 Kimi PPT Agent 的设计理念，输出专业级 HTML 演示文稿 + 可编辑矢量 PPTX。

**[English](README.md)** | [中文](README_CN.MD) | [MIT License](LICENSE)

---

## 工作流概览

```
需求调研 → 资料搜集 → 大纲策划 → 策划稿 → 风格+配图+HTML设计稿 → 后处理(SVG+PPTX)
```

---

## 功能特性

### 支持的卡片类型

项目支持 12 种专业卡片类型，可满足各种演示场景需求：

| 卡片类型 | 用途 |
|---------|------|
| **text** | 文本内容卡片 |
| **data** | 数据展示卡片 |
| **list** | 列表卡片 |
| **tag_cloud** | 标签云 |
| **process** | 流程卡片 |
| **timeline** | 时间线卡片 |
| **comparison** | 对比卡片 |
| **quote** | 引用卡片 |
| **stat_block** | 统计块卡片 |
| **feature_grid** | 特性网格卡片 |
| **image_text** | 图文叠加卡片 |
| **data_highlight** | 大数据高亮区 |

### 支持的视觉风格

项目内置 16 种专业设计风格：

| 风格ID | 风格名称 | 适用场景 |
|--------|---------|---------|
| `dark_tech` | 高阶暗黑科技风 | AI/SaaS/数据平台 |
| `xiaomi_orange` | 小米橙 | 硬件产品/IoT |
| `blue_white` | 蓝白商务 | 企业/培训/教育 |
| `royal_red` | 朱红宫墙 | 文化/历史/中国风 |
| `fresh_green` | 清新自然 | 环保/健康/农业 |
| `luxury_purple` | 紫金奢华 | 奢侈品/高端地产 |
| `minimal_gray` | 极简灰白 | 学术/法务/咨询 |
| `vibrant_rainbow` | 活力彩虹 | 社交/营销/年轻品牌 |
| `gradient_blue` | 渐变蓝 | 科技发布会/产品 |
| `warm_sunset` | 暖阳夕照 | 生活方式/旅游 |
| `nordic_white` | 北欧极简 | 家居/品质生活 |
| `cyber_punk` | 赛博朋克 | 游戏/电竞/潮流 |
| `elegant_gold` | 优雅金 | 珠宝/宴会/奢侈品 |
| `ocean_depth` | 深海蓝 | 海洋公益/航海 |
| `retro_film` | 复古胶片 | 摄影/婚礼/民宿 |
| `corporate_blue` | 稳重蓝 | 咨询/投行/政府 |

![img1](ppt-output/png/card_demo-cards.png)

![img2](ppt-output/png/card-demo-cards2.png)

![img3](ppt-output/png/card-demo-styles.png)

---

## 效果展示

> 以「新一代小米SU7发布」为主题的示例输出（小米橙风格）：

| 封面页 | 配置对比页 |
|:---:|:---:|
| ![封面页](ppt-output/png/slide_01_cover.png) | ![配置对比](ppt-output/png/slide_02_models.png) |

| 动力续航页 | 智驾安全页 |
|:---:|:---:|
| ![动力续航](ppt-output/png/slide_03_power.png) | ![智驾安全](ppt-output/png/slide_04_smart.png) |

| 结束页 |
|:---:|
| ![结束页](ppt-output/png/slide_05_end.png) |

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **6步Pipeline** | 需求 → 搜索 → 大纲 → 策划 → 设计 → 后处理，模拟专业 PPT 公司工作流 |
| **16种预置风格** | 暗黑科技 / 小米橙 / 蓝白商务 / 朱红宫墙 / 清新自然 / 紫金奢华 / 极简灰白 / 活力彩虹 / 渐变蓝 / 暖阳夕照 / 北欧极简 / 赛博朋克 / 优雅金 / 深海蓝 / 复古胶片 / 稳重蓝 |
| **12种卡片类型** | text / data / list / tag_cloud / process / timeline / comparison / quote / stat_block / feature_grid / image_text / data_highlight |
| **7种Bento布局** | 单一焦点 / 50/50对称 / 非对称两栏 / 三栏等宽 / 主次结合 / 顶部英雄式 / 混合网格 |
| **智能配图** | Unsplash 图库 + 5 种视觉融入技法（渐隐融合/色调蒙版/氛围底图等） |
| **排版系统** | 7 级字号阶梯 + 间距层级 + 中英文混排规则 |
| **色彩比例** | 60-30-10 法则 + accent 色使用约束 |
| **数据可视化** | 8 种纯 CSS/SVG 图表（进度条/环形图/迷你折线/点阵图/KPI 卡等） |
| **跨页叙事** | 密度交替节奏 / 章节色彩递进 / 封面-结尾呼应 / 渐进揭示 |
| **页脚系统** | 统一页脚（章节信息 + 页码），跨页导航 |
| **PPTX 兼容** | HTML → SVG → PPTX 管线，PPT 365 中右键"转换为形状"即可编辑 |

---

## 输出产物

| 文件 | 说明 |
|------|------|
| `preview.html` | 浏览器翻页预览（自动生成） |
| `presentation.pptx` | PPTX 文件，Office 365 中右键"转换为形状"可编辑 |
| `svg/*.svg` | 单页矢量 SVG，可直接拖入 PPT |
| `slides/*.html` | 单页 HTML 源文件 |

---

## 环境依赖

**必须：**
- **Node.js** >= 18（Puppeteer + dom-to-svg）
- **Python** >= 3.8
- **python-pptx**（PPTX 生成）

**可选（用于配图）：**
- **Unsplash API Key**：从 [Unsplash Developers](https://unsplash.com/developers) 申请

**一键安装：**
```bash
pip install python-pptx lxml Pillow
npm install puppeteer dom-to-svg
```

---

## 配图配置（可选）

项目支持 Unsplash 免费图库作为配图来源。配置步骤：

1. 申请 API Key：[Unsplash Developers](https://unsplash.com/developers) → New Application → 获取 Access Key

2. 配置环境变量：
   ```bash
   # 复制模板文件
   copy .env.example .env
   
   # 编辑 .env，填入你的 Access Key
   UNSPLASH_ACCESS_KEY=你的_Access_Key
   ```

3. 使用 `.env` 文件时，API Key 不会提交到 Git 仓库（已配置 .gitignore）

> 不配置也可使用，Agent 会使用纯文字/数据驱动的设计方式。

---

## 目录结构

```
Powerpoint-Generator/
  SKILL.md                    # 主工作流指令（Agent 入口）
  README.md                   # 本文件（中文）
  README_EN.md                # English documentation
  .env.example                # 环境变量模板（Unsplash API Key）
  references/
    prompts.md                # 5 套 Prompt 模板
    style-system.md           # 16 种预置风格 + CSS 变量
    bento-grid.md             # 7 种布局规格 + 12 种卡片类型
    card-demo.html            # 卡片类型 & 风格可视化演示
    method.md                 # 核心方法论
  scripts/
    html_packager.py          # 多页 HTML 合并为翻页预览
    html2svg.py               # HTML → SVG（dom-to-svg，保留文字可编辑）
    svg2pptx.py               # SVG → PPTX（OOXML 原生 SVG 嵌入）
```

---

## 使用方式

在对话中直接描述你的需求即可触发，Agent 会自动执行完整 6 步工作流：

```
你："帮我做一个关于 X 的 PPT"
  → Agent 提问调研需求（等你回复）
  → 自动搜索资料 → 生成大纲 → 策划稿 → 逐页设计 HTML
  → 自动后处理：HTML → SVG → PPTX
  → 输出全部产物到 ppt-output/
```

**触发示例**：

| 场景 | 说法 |
|------|------|
| 纯主题 | "帮我做个 PPT" / "做一个关于 X 的演示" |
| 带素材 | "把这篇文档做成 PPT" / "用这份报告做 slides" |
| 带要求 | "做 15 页暗黑风的 AI 安全汇报材料" |
| 隐式触发 | "我要给老板汇报 Y" / "做个培训课件" / "做路演 deck" |

> 全程无需手动执行任何脚本，所有后处理（预览合并、SVG 转换、PPTX 生成）由 Agent 在 Step 6 自动完成。

---

## 特别鸣谢

本项目基于 [ppt-agent-skill](https://github.com/Akxan/ppt-agent-skill) 创作，感谢原项目作者的出色工作和开源精神。
