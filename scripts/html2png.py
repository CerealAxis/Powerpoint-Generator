#!/usr/bin/env python3
"""HTML to PNG -- 将 HTML 文件截图生成 PNG 图片

使用 Playwright Python 对每个 HTML 文件进行截图，支持多页并行。
Playwright 是 Python 原生库，不需要 Node.js 环境。

用法:
  python html2png.py <slides_dir> -o <output_dir>
  python html2png.py ppt-output/slides/ -o ppt-output/png/
  python html2png.py ppt-output/slides/ -o ppt-output/png/ -c 4
"""

import argparse
import asyncio
import sys
from pathlib import Path

# -------------------------------------------------------------------
# 配置
# -------------------------------------------------------------------
SLIDE_WIDTH = 1280
SLIDE_HEIGHT = 720


# -------------------------------------------------------------------
# Playwright 截图核心（Python 原生，无需 Node.js）
# -------------------------------------------------------------------
async def screenshot_html(
    browser,
    html_path: Path,
    output_path: Path,
    page_number: int = 0
) -> bool:
    """对单个 HTML 文件截图。"""
    page = None
    try:
        page = await browser.new_page()
        await page.set_viewport_size({"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT})

        # 加载 HTML 文件
        html_url = f"file://{html_path.absolute()}"
        await page.goto(html_url, wait_until="networkidle")

        # 等待字体加载完成
        try:
            await page.evaluate("document.fonts.ready")
        except Exception:
            pass  # 字体等待超时不影响截图

        # 截图
        await page.screenshot(
            path=str(output_path),
            type="png",
            full_page=False,
            clip={"x": 0, "y": 0, "width": SLIDE_WIDTH, "height": SLIDE_HEIGHT}
        )

        print(f"  [{page_number:02d}] {html_path.name} -> {output_path.name}")
        return True

    except Exception as e:
        print(f"  [!] {html_path.name}: {e}", file=sys.stderr)
        return False

    finally:
        if page:
            await page.close()


async def batch_screenshot(
    slides_dir: Path,
    output_dir: Path,
    concurrency: int = 4
) -> int:
    """批量截图，支持并发控制。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = sorted(slides_dir.glob("*.html"))
    if not html_files:
        print(f"WARNING: No HTML files found in {slides_dir}", file=sys.stderr)
        return 0

    print(f"Found {len(html_files)} HTML files, processing with concurrency={concurrency}...")

    # 检查 Playwright 可用性
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        print("Run: pip install playwright && playwright install chromium", file=sys.stderr)
        return 0

    # 使用信号量控制并发
    semaphore = asyncio.Semaphore(concurrency)

    async def process_file(html_file: Path, idx: int) -> bool:
        output_file = output_dir / f"slide-{idx:02d}.png"
        async with semaphore:
            async with async_playwright() as p:
                browser = None
                try:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage"
                        ]
                    )
                    return await screenshot_html(browser, html_file, output_file, idx)
                finally:
                    if browser:
                        await browser.close()

    # 为每个 HTML 文件创建任务
    tasks = [process_file(f, i) for i, f in enumerate(html_files, 1)]
    results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    print(f"\nCompleted: {success}/{len(results)} screenshots")
    return success


def main():
    parser = argparse.ArgumentParser(
        description="HTML to PNG screenshot generator (Playwright Python)"
    )
    parser.add_argument(
        "slides_dir", type=Path,
        help="Directory containing HTML slide files"
    )
    parser.add_argument(
        "-o", "--output", type=Path, required=True,
        help="Output directory for PNG files"
    )
    parser.add_argument(
        "-c", "--concurrency", type=int, default=4,
        help="Max concurrent screenshots (default: 4)"
    )
    parser.add_argument(
        "--width", type=int, default=1280,
        help="Viewport width (default: 1280)"
    )
    parser.add_argument(
        "--height", type=int, default=720,
        help="Viewport height (default: 720)"
    )

    args = parser.parse_args()

    global SLIDE_WIDTH, SLIDE_HEIGHT
    SLIDE_WIDTH = args.width
    SLIDE_HEIGHT = args.height

    if not args.slides_dir.exists():
        print(f"ERROR: Slides directory not found: {args.slides_dir}", file=sys.stderr)
        sys.exit(1)

    success = asyncio.run(batch_screenshot(
        args.slides_dir, args.output, args.concurrency
    ))
    sys.exit(0 if success > 0 else 1)


if __name__ == "__main__":
    main()
