import base64
from io import BytesIO
from typing import Any

import pyautogui

pyautogui.FAILSAFE = True


def _capture_png(region=None) -> bytes:
    img = pyautogui.screenshot(region=region)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def register_screen_tools(mcp):
    @mcp.tool(name="screen_capture", annotations={"readOnlyHint": True})
    def screen_capture(region: str = "full") -> dict[str, Any]:
        """Use this when you need a desktop screenshot of the full screen or a region."""
        size = pyautogui.size()
        cap_region = None
        if region != "full":
            x, y, w, h = [int(v.strip()) for v in region.split(",")]
            cap_region = (x, y, w, h)
        png = _capture_png(cap_region)
        return {
            "image_base64": base64.b64encode(png).decode("utf-8"),
            "screen_size": {"width": size.width, "height": size.height},
        }

    @mcp.tool(name="mouse_position", annotations={"readOnlyHint": True})
    def mouse_position() -> dict[str, int]:
        """Use this when you need the current mouse cursor coordinates."""
        x, y = pyautogui.position()
        return {"x": x, "y": y}

    @mcp.tool(name="mouse_move", annotations={"readOnlyHint": False})
    def mouse_move(x: int, y: int, duration: float = 0.5) -> dict[str, Any]:
        """Use this when you need to move the mouse pointer to a specific coordinate."""
        pyautogui.moveTo(x, y, duration=duration)
        return {"moved_to": {"x": x, "y": y}, "duration": duration}

    @mcp.tool(name="mouse_click", annotations={"readOnlyHint": False})
    def mouse_click(x: int, y: int, button: str = "left") -> dict[str, Any]:
        """Use this when you need to click a specific screen coordinate."""
        pyautogui.click(x=x, y=y, button=button)
        return {"clicked": {"x": x, "y": y}, "button": button}

    @mcp.tool(name="mouse_double_click", annotations={"readOnlyHint": False})
    def mouse_double_click(x: int, y: int) -> dict[str, Any]:
        """Use this when you need to double-click at a coordinate."""
        pyautogui.doubleClick(x=x, y=y)
        return {"double_clicked": {"x": x, "y": y}}

    @mcp.tool(name="keyboard_type", annotations={"readOnlyHint": False})
    def keyboard_type(text: str, interval: float = 0.05) -> dict[str, Any]:
        """Use this when you need to type text into the active window."""
        pyautogui.write(text, interval=interval)
        return {"typed_length": len(text), "interval": interval}

    @mcp.tool(name="keyboard_press", annotations={"readOnlyHint": False})
    def keyboard_press(key: str) -> dict[str, Any]:
        """Use this when you need to press a key or hotkey combination."""
        keys = [k.strip() for k in key.split("+") if k.strip()]
        if len(keys) > 1:
            pyautogui.hotkey(*keys)
        elif keys:
            pyautogui.press(keys[0])
        return {"pressed": keys}

    @mcp.tool(name="scroll", annotations={"readOnlyHint": False})
    def scroll(clicks: int) -> dict[str, int]:
        """Use this when you need to scroll vertically in the active window."""
        pyautogui.scroll(clicks)
        return {"clicks": clicks}


def get_desktop_screenshot_bytes() -> bytes:
    return _capture_png()
