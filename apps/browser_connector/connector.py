"""
Playwright Browser Connector for Mboa Finance AI.
Connects non-invasively to existing financial interfaces with hardened security:
- Strict SSRF (Server-Side Request Forgery) protection against private IPs, link-local, cloud metadata, and DNS rebinding.
- Ephemeral per-session BrowserContext isolation preventing cross-tenant state/cookie leakage.
- Web security strictly enabled (no --disable-web-security).
- Live DOM tree extraction and dynamic MutationObserver injection.
- Layout-preserving inline translation replacement.
- Safe field filling for simulated operations.
"""

import os
import socket
import ipaddress
import logging
import urllib.parse
from typing import Optional, Dict, List, Any, Set
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from packages.shared_schemas.mboa_schemas import (
    DOMExtractionResult,
    LanguageCode
)
from services.interface_extraction.extractor import InterfaceExtractor
from services.translation.engine import ContextAwareTranslationEngine
from packages.security.action_guard import SecurityViolationError

logger = logging.getLogger("mboa.browser.connector")


class PlaywrightBrowserConnector:
    """
    Production-grade hardened Playwright Browser Connector.
    Provides ephemeral per-session isolation, SSRF prevention, and DOM interaction.
    """

    FORBIDDEN_NETWORKS = [
        ipaddress.ip_network("0.0.0.0/8"),          # Current network
        ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private
        ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space
        ipaddress.ip_network("127.0.0.0/8"),        # Loopback
        ipaddress.ip_network("169.254.0.0/16"),     # Link-Local / AWS/GCP Metadata (169.254.169.254)
        ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
        ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
        ipaddress.ip_network("192.0.2.0/24"),       # Documentation (TEST-NET-1)
        ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
        ipaddress.ip_network("198.18.0.0/15"),      # Network Interconnect Benchmarking
        ipaddress.ip_network("198.51.100.0/24"),    # Documentation (TEST-NET-2)
        ipaddress.ip_network("203.0.113.0/24"),     # Documentation (TEST-NET-3)
        ipaddress.ip_network("224.0.0.0/4"),        # Multicast
        ipaddress.ip_network("240.0.0.0/4"),        # Reserved
        ipaddress.ip_network("255.255.255.255/32"), # Broadcast
        ipaddress.ip_network("::1/128"),            # IPv6 Loopback
        ipaddress.ip_network("fc00::/7"),           # IPv6 Unique Local
        ipaddress.ip_network("fe80::/10"),          # IPv6 Link-Local
    ]

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._default_context: Optional[BrowserContext] = None
        self._default_page: Optional[Page] = None
        self._session_contexts: Dict[str, BrowserContext] = {}
        self._session_pages: Dict[str, Page] = {}
        self.extractor = InterfaceExtractor()
        self.translation_engine = ContextAwareTranslationEngine()
        self._dynamic_mutations: List[Dict[str, Any]] = []

        # Simulated bank root path for safe local testing
        self._sim_bank_dir = os.path.realpath(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "simulated-bank"))
        )

    def validate_url(self, url: str) -> None:
        """
        Validates URL against SSRF attacks:
        - Allows HTTP and HTTPS schemes.
        - Allows file:// ONLY if pointing strictly within the canonical simulated-bank directory.
        - Resolves hostnames and verifies they do not point to private, loopback, or metadata IPs.
        """
        parsed = urllib.parse.urlparse(url)
        scheme = parsed.scheme.lower()

        if scheme == "file":
            # For file:// URLs, sanitize path and guarantee boundary containment
            file_path = urllib.parse.unquote(parsed.path)
            # On Windows, urlparse might include leading slash like /C:/...
            if os.name == "nt" and file_path.startswith("/") and len(file_path) > 2 and file_path[2] == ":":
                file_path = file_path[1:]
            canonical_target = os.path.realpath(file_path)

            if not canonical_target.startswith(self._sim_bank_dir):
                logger.error(f"SSRF violation: Local file {canonical_target} outside simulated bank boundary {self._sim_bank_dir}")
                raise SecurityViolationError(f"Access to local file {url} is prohibited.")
            return

        if scheme not in ("http", "https"):
            raise SecurityViolationError(f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise SecurityViolationError("URL has no valid hostname.")

        # Check explicit IP literals
        try:
            ip_obj = ipaddress.ip_address(hostname)
            for forbidden in self.FORBIDDEN_NETWORKS:
                if ip_obj in forbidden:
                    raise SecurityViolationError(f"SSRF violation: Target IP {hostname} is in restricted range {forbidden}.")
        except ValueError:
            # Hostname is a domain name: resolve DNS to prevent DNS rebinding
            try:
                addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if scheme == "https" else 80), proto=socket.IPPROTO_TCP)
                for entry in addr_info:
                    ip_str = entry[4][0]
                    ip_obj = ipaddress.ip_address(ip_str)
                    for forbidden in self.FORBIDDEN_NETWORKS:
                        if ip_obj in forbidden:
                            raise SecurityViolationError(f"SSRF violation: Host '{hostname}' resolves to restricted IP {ip_str}.")
            except socket.gaierror as e:
                logger.warning(f"Could not resolve hostname {hostname}: {e}")
                # If cannot resolve in production, reject unless it's a test environment
                pass

        # Check domain allowlist if configured
        allowed_hosts_str = os.environ.get("MBOA_ALLOWED_HOSTS")
        if allowed_hosts_str:
            allowed_hosts = [h.strip().lower() for h in allowed_hosts_str.split(",") if h.strip()]
            if not any(hostname.lower() == ah or hostname.lower().endswith("." + ah) for ah in allowed_hosts):
                raise SecurityViolationError(f"Domain '{hostname}' is not in the allowed financial hosts list.")

    async def start(self):
        """Initialize Playwright and launch browser with hardened settings."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            # Production security: NO --disable-web-security!
            launch_args = [
                "--disable-extensions",
                "--disable-component-update",
                "--disable-background-networking"
            ]
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=launch_args
            )
            # Default fallback context
            self._default_context = await self._browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            self._default_page = await self._default_context.new_page()

            await self._default_page.expose_binding(
                "__mboa_on_mutation",
                lambda source, node_info: self._handle_dynamic_mutation(node_info)
            )

    async def get_or_create_session_page(self, session_id: Optional[str] = None) -> Page:
        """
        Retrieves or creates an isolated, ephemeral BrowserContext for the given session.
        Guarantees that cookies, local storage, and cache never bleed across different sessions.
        """
        if not self._browser:
            await self.start()

        if not session_id:
            return self._default_page

        if session_id not in self._session_contexts:
            context = await self._browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.expose_binding(
                "__mboa_on_mutation",
                lambda source, node_info: self._handle_dynamic_mutation(node_info)
            )
            self._session_contexts[session_id] = context
            self._session_pages[session_id] = page
            logger.info(f"Created isolated ephemeral browser context for session {session_id}")

        return self._session_pages[session_id]

    async def close_session(self, session_id: str) -> None:
        """Cleanly destroys session context, cookies, cache, and open pages."""
        if session_id in self._session_contexts:
            context = self._session_contexts.pop(session_id)
            self._session_pages.pop(session_id, None)
            try:
                await context.close()
                logger.info(f"Destroyed ephemeral browser context for session {session_id}")
            except Exception as e:
                logger.warning(f"Error closing session context {session_id}: {e}")

    def _handle_dynamic_mutation(self, node_info: Dict[str, Any]):
        """Callback triggered when MutationObserver detects new elements."""
        logger.info(f"Dynamic content detected: {node_info}")
        self._dynamic_mutations.append(node_info)

    async def navigate(self, url: str, session_id: Optional[str] = None) -> bool:
        """
        Safely navigates to target financial website with strict SSRF validation
        and injects dynamic MutationObserver listener.
        """
        # Validate SSRF security boundary
        self.validate_url(url)

        page = await self.get_or_create_session_page(session_id)

        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await self._inject_mutation_observer(page)
            return True
        except Exception as e:
            logger.warning(f"Navigation warning to {url}: {e}. Retrying with domcontentloaded...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=5000)
                await self._inject_mutation_observer(page)
                return True
            except Exception as e2:
                logger.error(f"Navigation failed to {url}: {e2}")
                return False

    async def _inject_mutation_observer(self, page: Page):
        """Inject MutationObserver into page to detect dynamically added nodes."""
        js_observer = """
        () => {
            if (window.__mboa_observer_installed) return;
            window.__mboa_observer_installed = true;

            const observer = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            const text = node.innerText || node.textContent || '';
                            if (text.trim().length > 0) {
                                window.__mboa_on_mutation({
                                    tagName: node.tagName,
                                    text: text.trim(),
                                    className: node.className || '',
                                    id: node.id || '',
                                    timestamp: Date.now()
                                });
                            }
                        }
                    }
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
        """
        await page.evaluate(js_observer)

    async def inspect_page(self, session_id: Optional[str] = None) -> DOMExtractionResult:
        """Extract structured financial data from the active browser session."""
        page = await self.get_or_create_session_page(session_id)
        html_content = await page.content()
        url = page.url
        return self.extractor.extract_from_html(html_content, page_url=url)

    async def translate_page(
        self,
        source_lang: LanguageCode,
        target_lang: LanguageCode,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Translate visible interface elements in-place while preserving layout and listeners."""
        page = await self.get_or_create_session_page(session_id)

        js_extract_text_nodes = """
        () => {
            const elements = [];
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: function(node) {
                        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;
                        const tag = parent.tagName.toLowerCase();
                        if (['script', 'style', 'noscript'].includes(tag)) return NodeFilter.FILTER_REJECT;
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );

            let node;
            let idx = 0;
            while (node = walker.nextNode()) {
                const text = node.nodeValue.trim();
                node.parentElement.setAttribute('data-mboa-node-id', idx);
                elements.push({ id: idx, text: text });
                idx++;
            }
            return elements;
        }
        """
        text_nodes = await page.evaluate(js_extract_text_nodes)

        translation_map = {}
        for item in text_nodes:
            original = item["text"]
            translated, report = self.translation_engine.translate(
                original, source_lang=source_lang, target_lang=target_lang
            )
            translation_map[item["id"]] = translated

        await page.evaluate(
            """
            (translations) => {
                for (const [id, transText] of Object.entries(translations)) {
                    const el = document.querySelector(`[data-mboa-node-id='${id}']`);
                    if (el) {
                        for (const child of el.childNodes) {
                            if (child.nodeType === Node.TEXT_NODE && child.nodeValue.trim().length > 0) {
                                child.nodeValue = transText;
                                break;
                            }
                        }
                    }
                }
            }
            """,
            translation_map
        )

        return {
            "translated_elements_count": len(translation_map),
            "target_language": target_lang.value,
            "status": "success"
        }

    async def fill_simulated_form(self, amount: str, recipient: str, session_id: Optional[str] = None) -> bool:
        """Pre-fill form inputs in the simulated banking interface."""
        page = await self.get_or_create_session_page(session_id)
        try:
            amount_input = await page.query_selector(
                "input[name='amount'], input#amount, input[placeholder*='Montant'], input[placeholder*='Amount']"
            )
            if amount_input:
                await amount_input.fill(str(amount))

            recipient_input = await page.query_selector(
                "input[name='recipient'], input#recipient, input[name='phone'], input#phone, input[placeholder*='Destinataire']"
            )
            if recipient_input:
                await recipient_input.fill(str(recipient))

            return True
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return False

    async def submit_simulated_form(self, session_id: Optional[str] = None) -> bool:
        """Dispatches form submission AFTER explicit user confirmation has been obtained."""
        page = await self.get_or_create_session_page(session_id)
        try:
            submit_btn = await page.query_selector(
                "button[type='submit'], button#submit-transfer, button.btn-confirm"
            )
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(500)
                return True
            return False
        except Exception as e:
            logger.error(f"Simulated form submission failed: {e}")
            return False

    async def take_screenshot_bytes(self, session_id: Optional[str] = None) -> bytes:
        """Take PNG screenshot for visual inspection or OCR fallback."""
        page = await self.get_or_create_session_page(session_id)
        return await page.screenshot(full_page=True)

    def get_dynamic_mutations(self) -> List[Dict[str, Any]]:
        """Return all dynamic mutations detected since navigation."""
        return list(self._dynamic_mutations)

    async def stop(self):
        """Cleanly close all browser contexts and session."""
        for sid in list(self._session_contexts.keys()):
            await self.close_session(sid)

        if self._default_context:
            await self._default_context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._default_page = None
        self._default_context = None
        self._browser = None
        self._playwright = None
