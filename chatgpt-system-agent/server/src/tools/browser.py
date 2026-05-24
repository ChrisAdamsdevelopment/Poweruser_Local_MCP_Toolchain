import asyncio
import base64
from io import BytesIO
from typing import Any

from PIL import Image
from playwright.async_api import async_playwright

_PLAYWRIGHT = None
_BROWSER = None
_PAGE = None
_LOCK = asyncio.Lock()


async def _ensure_page():
    global _PLAYWRIGHT, _BROWSER, _PAGE
    async with _LOCK:
        if _PAGE is not None:
            return _PAGE
        _PLAYWRIGHT = await async_playwright().start()
        _BROWSER = await _PLAYWRIGHT.chromium.launch(headless=False)
        context = await _BROWSER.new_context()
        _PAGE = await context.new_page()
        return _PAGE


async def _page_png_bytes() -> bytes:
    page = await _ensure_page()
    return await page.screenshot(type="png")


def register_browser_tools(mcp):
    @mcp.tool(name="browser_navigate", annotations={"readOnlyHint": False, "openWorldHint": True})
    async def browser_navigate(url: str) -> dict[str, Any]:
        """Use this when you need to open a URL in the shared Chromium browser."""
        page = await _ensure_page()
        response = await page.goto(url, wait_until="domcontentloaded")
        return {"url": page.url, "status": getattr(response, "status", None)}

    @mcp.tool(name="browser_screenshot", annotations={"readOnlyHint": True})
    async def browser_screenshot() -> dict[str, str]:
        """Use this when you need a PNG screenshot of the current browser page."""
        png = await _page_png_bytes()
        return {"image_base64": base64.b64encode(png).decode("utf-8")}

    @mcp.tool(name="browser_click", annotations={"readOnlyHint": False, "openWorldHint": True})
    async def browser_click(selector: str) -> dict[str, Any]:
        """Use this when you need to click an element on the current page by CSS selector."""
        page = await _ensure_page()
        await page.click(selector)
        return {"clicked": selector}

    @mcp.tool(name="browser_type", annotations={"readOnlyHint": False, "openWorldHint": True})
    async def browser_type(selector: str, text: str) -> dict[str, Any]:
        """Use this when you need to type text into a page element selected by CSS selector."""
        page = await _ensure_page()
        await page.fill(selector, text)
        return {"typed_into": selector, "length": len(text)}

    @mcp.tool(name="browser_get_content", annotations={"readOnlyHint": True})
    async def browser_get_content() -> dict[str, Any]:
        """Use this when you need page text plus button/input metadata for analysis."""
        page = await _ensure_page()
        page_text = await page.evaluate("() => document.body?.innerText || ''")
        buttons = await page.evaluate(
            """() => Array.from(document.querySelectorAll('button, input[type=button], input[type=submit]'))
                  .map(el => ({text: (el.innerText || el.value || '').trim(), id: el.id || null, className: el.className || null}))"""
        )
        inputs = await page.evaluate(
            """() => Array.from(document.querySelectorAll('input, textarea, select'))
                  .map(el => ({name: el.name || null, id: el.id || null, type: el.type || el.tagName.toLowerCase()}))"""
        )
        return {"page_text": page_text[:20000], "buttons": buttons, "inputs": inputs}

    @mcp.tool(name="browser_execute_js", annotations={"readOnlyHint": False, "openWorldHint": True})
    async def browser_execute_js(code: str) -> dict[str, Any]:
        """Use this when you need to run JavaScript in the active browser page context."""
        page = await _ensure_page()
        result = await page.evaluate(f"() => {{ {code} }}")
        return {"result": result}

    @mcp.tool(name="browser_press_key", annotations={"readOnlyHint": False, "openWorldHint": True})
    async def browser_press_key(key: str) -> dict[str, str]:
        """Use this when you need to send a keyboard key press to the active browser page."""
        page = await _ensure_page()
        await page.keyboard.press(key)
        return {"pressed": key}

    @mcp.tool(name="browser_close", annotations={"readOnlyHint": False, "destructiveHint": True})
    async def browser_close() -> dict[str, str]:
        """Use this when you need to close the shared browser instance and release resources."""
        global _PLAYWRIGHT, _BROWSER, _PAGE
        async with _LOCK:
            if _BROWSER:
                await _BROWSER.close()
            if _PLAYWRIGHT:
                await _PLAYWRIGHT.stop()
            _PLAYWRIGHT = None
            _BROWSER = None
            _PAGE = None
        return {"status": "closed"}


async def get_browser_screenshot_bytes() -> bytes:
    return await _page_png_bytes()
