"""
Capture visual verification screenshots of the redesigned Mboa Finance AI portal
in both Mobile (iPhone 14/15 - 390x844) and Desktop (1280x800) viewports,
matching the dark-mode Electric Lime & Cobalt Blue reference archetype.
"""

import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.async_api import async_playwright

async def capture_screenshots():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
    os.makedirs(output_dir, exist_ok=True)

    bank_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulated-bank", "index.html"))
    file_url = f"file:///{bank_path.replace(os.sep, '/')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Mobile Viewport (iPhone 14/15 Pro: 390 x 844)
        context_mobile = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page_mobile = await context_mobile.new_page()
        await page_mobile.goto(file_url)
        await page_mobile.wait_for_timeout(1000)

        mobile_main_path = os.path.join(output_dir, "mobile_portal_view.png")
        await page_mobile.screenshot(path=mobile_main_path, full_page=True)
        print(f"[OK] Saved mobile portal view: {mobile_main_path}")

        # Open Mboa Assistant in mobile view
        await page_mobile.click("#mboa-assistant-bubble-btn")
        await page_mobile.wait_for_timeout(600)
        mobile_assistant_path = os.path.join(output_dir, "mobile_assistant_open.png")
        await page_mobile.screenshot(path=mobile_assistant_path, full_page=True)
        print(f"[OK] Saved mobile assistant open view: {mobile_assistant_path}")

        await context_mobile.close()

        # 2. Desktop Viewport (1280 x 800)
        context_desktop = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1.5
        )
        page_desktop = await context_desktop.new_page()
        await page_desktop.goto(file_url)
        await page_desktop.wait_for_timeout(1000)

        desktop_main_path = os.path.join(output_dir, "desktop_portal_view.png")
        await page_desktop.screenshot(path=desktop_main_path, full_page=True)
        print(f"[OK] Saved desktop portal view: {desktop_main_path}")

        await context_desktop.close()
        await browser.close()

    print("\nAll UI verification screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
