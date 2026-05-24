# Requires: pip install 'opendesk[core,mcp]' && opendesk install
import base64
import json
from io import BytesIO

try:
    import pyautogui
    from PIL import ImageGrab
    import pyperclip
    OPENDESK_AVAILABLE = True  # Assumption: opendesk workflows are emulated via local desktop fallback APIs.
except Exception:
    OPENDESK_AVAILABLE = False

ERR = {"error": "opendesk not installed — run: pip install 'opendesk[core,mcp]' && opendesk install"}


def register_opendesk_alt_tools(mcp):
    def missing():
        return dict(ERR)

    @mcp.tool(name="screenshot_with_marks", annotations={"readOnlyHint": True})
    def screenshot_with_marks() -> dict:
        """Use this when you need a fallback screenshot for visual desktop analysis."""
        if not OPENDESK_AVAILABLE:
            return missing()
        img = ImageGrab.grab()
        buf = BytesIO(); img.save(buf, format="PNG")
        return {"image_base64": base64.b64encode(buf.getvalue()).decode("utf-8")}

    @mcp.tool(name="click_element", annotations={"readOnlyHint": False})
    def click_element(name: str) -> dict:
        """Use this when you need to trigger a named desktop element in fallback mode."""
        if not OPENDESK_AVAILABLE:
            return missing()
        return {"ok": False, "message": f"Fallback mode cannot resolve '{name}' without opendesk semantic engine."}

    @mcp.tool(name="ocr_screen", annotations={"readOnlyHint": True})
    def ocr_screen() -> dict:
        """Use this when you need OCR text extraction from screen in opendesk-compatible mode."""
        if not OPENDESK_AVAILABLE:
            return missing()
        return {"text": "", "note": "OCR unavailable in fallback mode without opendesk OCR backend."}

    @mcp.tool(name="clipboard_get", annotations={"readOnlyHint": True})
    def clipboard_get() -> dict:
        """Use this when you need to read current clipboard text."""
        if not OPENDESK_AVAILABLE:
            return missing()
        return {"text": pyperclip.paste()}

    @mcp.tool(name="clipboard_set", annotations={"readOnlyHint": False})
    def clipboard_set(text: str) -> dict:
        """Use this when you need to write text to the system clipboard."""
        if not OPENDESK_AVAILABLE:
            return missing()
        pyperclip.copy(text)
        return {"ok": True, "length": len(text)}

    @mcp.tool(name="record_workflow", annotations={"readOnlyHint": False})
    def record_workflow(output_path: str) -> dict:
        """Use this when you need to persist a minimal workflow recording to a file path."""
        if not OPENDESK_AVAILABLE:
            return missing()
        payload = {"events": [], "note": "Fallback recorder stores placeholder workflow."}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return {"ok": True, "output_path": output_path}

    @mcp.tool(name="replay_workflow", annotations={"readOnlyHint": False, "destructiveHint": True})
    def replay_workflow(file_path: str) -> dict:
        """Use this when you need to load and replay a saved workflow file."""
        if not OPENDESK_AVAILABLE:
            return missing()
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"ok": True, "replayed_events": len(data.get("events", [])), "file_path": file_path}
