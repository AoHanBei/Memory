"""Capture the real workbench against a temporary, synthetic-data memory API."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from threading import Thread
from typing import Any
from urllib.parse import urlsplit

import httpx
import uvicorn
from playwright.sync_api import Browser, Page, Route, expect, sync_playwright

from evolvable_memory import frontend
from evolvable_memory.api.app import create_app
from evolvable_memory.config import Settings

ROOT = Path(__file__).resolve().parents[1]
SCOPE = {"tenant_id": "demo", "subject_id": "alice"}


class QuietFrontendHandler(frontend.FrontendRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        del args


def wait_ready(url: str) -> None:
    deadline = time.monotonic() + 15
    with httpx.Client(trust_env=False, timeout=0.5) as client:
        while time.monotonic() < deadline:
            try:
                response = client.get(url)
                response.raise_for_status()
                return
            except httpx.HTTPError:
                time.sleep(0.05)
    raise RuntimeError("Documentation service did not become ready")


@contextmanager
def isolated_console() -> Iterator[tuple[str, str]]:
    api_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    api_socket.bind(("127.0.0.1", 0))
    api_url = f"http://127.0.0.1:{api_socket.getsockname()[1]}"
    handler = partial(
        QuietFrontendHandler,
        directory=str(ROOT / "src/evolvable_memory/api/static"),
        public_api_url=api_url,
    )
    web = frontend.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    web_url = f"http://127.0.0.1:{web.server_address[1]}"
    settings = Settings(
        host="127.0.0.1",
        store="memory",
        frontend_url=web_url,
        public_api_url=api_url,
        cors_origins=(web_url,),
    )
    api = uvicorn.Server(
        uvicorn.Config(create_app(settings=settings), log_level="critical", access_log=False)
    )
    api_thread = Thread(target=api.run, kwargs={"sockets": [api_socket]}, daemon=True)
    web_thread = Thread(target=web.serve_forever, daemon=True)
    api_thread.start()
    web_thread.start()
    try:
        wait_ready(f"{api_url}/readyz")
        wait_ready(web_url)
        yield api_url, web_url
    finally:
        web.shutdown()
        web.server_close()
        api.should_exit = True
        web_thread.join(timeout=5)
        api_thread.join(timeout=5)
        api_socket.close()


def seed_preferences(api_url: str) -> None:
    with httpx.Client(base_url=api_url, trust_env=False, timeout=5) as client:
        created = client.post(
            "/v1/preferences",
            json={
                **SCOPE,
                "source": "documentation-demo",
                "idempotency_key": "docs:preference",
                "key": "drink.preference",
                "value": "低因咖啡",
                "context": {"time_of_day": "evening"},
                "evidence_text": "晚上我喝低因咖啡",
                "confidence": 0.92,
            },
        )
        created.raise_for_status()
        record: dict[str, Any] = created.json()
        corrected = client.post(
            f"/v1/preferences/{record['record_id']}/corrections",
            json={
                **SCOPE,
                "source": "documentation-demo",
                "idempotency_key": "docs:correction",
                "value": "花草茶",
                "evidence_text": "现在晚上改喝花草茶",
                "reason": "synthetic documentation correction",
            },
        )
        corrected.raise_for_status()


def capture(page: Page, web_url: str, output: Path) -> None:
    page.goto(f"{web_url}/?tour=0", wait_until="networkidle")
    expect(page.locator("#status-label")).to_have_text("API 在线")
    page.locator('[data-view="recall"]').click()
    page.locator('#recall-form input[name="query"]').fill("drink.preference 花草茶")
    page.locator('#recall-form button[type="submit"]').click()
    expect(page.locator(".result-card")).to_have_count(1)
    expect(page.locator(".result-card h3")).to_have_text("花草茶")
    page.locator(".result-card").get_by_role("button", name="有帮助", exact=True).click()
    expect(page.locator(".utility-update")).to_be_visible()
    page.evaluate("() => document.fonts.ready")
    page.evaluate(
        """() => {
          const badge = document.createElement('p');
          badge.textContent = 'SYNTHETIC DEMO DATA / TEMPORARY IN-MEMORY API';
          badge.style.cssText = 'font:12px monospace;color:#42654a;margin:0 0 12px';
          document.querySelector('#view-recall').prepend(badge);
        }"""
    )
    page.screenshot(path=str(output / "memory-recall.png"), full_page=True, animations="disabled")
    page.locator(".result-card").get_by_role("button", name="查看历史", exact=True).click()
    dialog = page.locator("#history-modal")
    expect(dialog).to_be_visible()
    expect(dialog.locator(".history-item")).to_have_count(2)
    dialog.evaluate(
        """element => {
          const badge = document.createElement('p');
          badge.textContent = 'SYNTHETIC DEMO DATA';
          badge.style.cssText = 'font:12px monospace;color:#42654a;margin:16px 24px';
          element.querySelector('.modal-shell').prepend(badge);
        }"""
    )
    dialog.screenshot(path=str(output / "memory-revisions.png"), animations="disabled")


def render_architecture(browser: Browser, output: Path) -> None:
    page = browser.new_page(viewport={"width": 1600, "height": 1020})
    try:
        source = output / "evolvable-memory-technical-architecture.svg"
        page.set_content(source.read_text(encoding="utf-8"))
        outside = page.locator("svg text").evaluate_all(
            """nodes => nodes.filter(node => {
              const box = node.getBBox();
              return box.x < 0 || box.y < 0 || box.x + box.width > 1600
                || box.y + box.height > 1020;
            }).map(node => node.textContent)"""
        )
        if outside:
            raise RuntimeError(f"Architecture text outside SVG: {outside}")
        page.locator("svg").screenshot(
            path=str(output / "evolvable-memory-technical-architecture.png")
        )
    finally:
        page.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-executable", help="Optional installed Chromium executable")
    options = parser.parse_args()
    output = ROOT / "docs/assets"
    output.mkdir(parents=True, exist_ok=True)
    with isolated_console() as (api_url, web_url), sync_playwright() as playwright:
        seed_preferences(api_url)
        browser = playwright.chromium.launch(
            headless=True, executable_path=options.browser_executable, args=["--no-proxy-server"]
        )
        try:
            render_architecture(browser, output)
            context = browser.new_context(
                viewport={"width": 1500, "height": 1100},
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
            )
            allowed = {urlsplit(api_url).netloc, urlsplit(web_url).netloc}

            def local_only(route: Route) -> None:
                if urlsplit(route.request.url).netloc in allowed:
                    route.continue_()
                else:
                    route.abort()

            context.route("**/*", local_only)
            page = context.new_page()
            page.set_default_timeout(15_000)
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            capture(page, web_url, output)
            if errors:
                raise RuntimeError(f"Workbench errors: {errors}")
            revision = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip()
            (output / "screenshots.json").write_text(
                json.dumps(
                    {
                        "baseRevision": revision,
                        "dataKind": "synthetic-preferences",
                        "backend": "temporary-in-memory-api",
                        "source": "src/evolvable_memory/api/static",
                        "capture": "examples/capture_docs.py",
                        "browser": browser.version,
                        "files": ["memory-recall.png", "memory-revisions.png"],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            print("Documentation capture passed: recall, Outcome, and two immutable revisions.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
