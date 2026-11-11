"""
Playwright Browser Connector for Mboa Finance AI.
Connects non-invasively to existing financial interfaces.
Features:
- Live page inspection and DOM tree extraction.
- Dynamic MutationObserver injection to capture newly introduced messages.
- Layout-preserving inline translation replacement.
- Safe field filling for simulated operations.
- Screenshot capture and OCR fallback integration.
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from packages.shared_schemas.mboa_schemas import (
    DOMExtractionResult,
    LanguageCode
)
from services.interface_extraction.extractor import InterfaceExtractor
from services.translation.engine import ContextAwareTranslationEngine

logger = logging.getLogger("mboa.browser.connector")


class PlaywrightBrowserConnector:
    """
    Manages Playwright browser sessions and provides DOM-level operations.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self.extractor = InterfaceExtractor()
        self.translation_engine = ContextAwareTranslationEngine()
        self._dynamic_mutations: List[Dict[str, Any]] = []

    async def start(self):
        """Initialize Playwright and launch browser."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-web-security", "--no-sandbox"]
            )
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 800}
            )
            self._page = await self._context.new_page()

            # Register dynamic mutation callback via binding
            await self._page.expose_binding(
                "__mboa_on_mutation",
                lambda source, node_info: self._handle_dynamic_mutation(node_info)
            )

    def _handle_dynamic_mutation(self, node_info: Dict[str, Any]):
        """Callback triggered when MutationObserver detects new elements."""
        logger.info(f"Dynamic content detected: {node_info}")
        self._dynamic_mutations.append(node_info)

    async def navigate(self, url: str) -> bool:
        """Navigate to target financial website and inject dynamic listener."""
        if not self._page:
            await self.start()
        try:
            await self._page.goto(url, wait_until="networkidle", timeout=15000)
            await self._inject_mutation_observer()
            return True
        except Exception as e:
            logger.error(f"Navigation error to {url}: {e}")
            # Fallback to domcontentloaded if networkidle times out
            try:
                await self._page.goto(url, wait_until="domcontentloaded", timeout=5000)
                await self._inject_mutation_observer()
                return True
            except Exception as e2:
                logger.error(f"Fallback navigation failed: {e2}")
                return False

    async def _inject_mutation_observer(self):
        """
        Inject MutationObserver into page to detect dynamically added nodes
        (such as flash messages, modals, new balances, alerts).
        """
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
        await self._page.evaluate(js_observer)

    async def inspect_page(self) -> DOMExtractionResult:
        """Extract structured financial data from the active browser session."""
        if not self._page:
            await self.start()

        html_content = await self._page.content()
        url = self._page.url
        return self.extractor.extract_from_html(html_content, page_url=url)

    async def translate_page(
        self,
        source_lang: LanguageCode,
        target_lang: LanguageCode
    ) -> Dict[str, Any]:
        """
        Translate visible interface elements in-place while preserving layout and listeners.
        """
        if not self._page:
            await self.start()

        # Step 1: Extract translatable nodes
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
        text_nodes = await self._page.evaluate(js_extract_text_nodes)

        # Step 2: Translate elements with financial entity protection
        translation_map = {}
        for item in text_nodes:
            original = item["text"]
            translated, report = self.translation_engine.translate(
                original, source_lang=source_lang, target_lang=target_lang
            )
            translation_map[item["id"]] = translated

        # Step 3: Inject translated text back into DOM
        await self._page.evaluate(
            """
            (translations) => {
                for (const [id, transText] of Object.entries(translations)) {
                    const el = document.querySelector(`[data-mboa-node-id='${id}']`);
                    if (el) {
                        // Replace only matching text node content to avoid clearing child elements
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

    async def fill_simulated_form(self, amount: str, recipient: str) -> bool:
        """
        Pre-fill form inputs in the simulated banking interface.
        Does NOT submit without explicit confirmation.
        """
        if not self._page:
            await self.start()

        try:
            # Locate amount input
            amount_input = await self._page.query_selector(
                "input[name='amount'], input#amount, input[placeholder*='Montant'], input[placeholder*='Amount']"
            )
            if amount_input:
                await amount_input.fill(str(amount))

            # Locate recipient input
            recipient_input = await self._page.query_selector(
                "input[name='recipient'], input#recipient, input[name='phone'], input#phone, input[placeholder*='Destinataire']"
            )
            if recipient_input:
                await recipient_input.fill(str(recipient))

            return True
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            return False

    async def submit_simulated_form(self) -> bool:
        """
        Dispatches form submission AFTER explicit user confirmation has been obtained.
        """
        if not self._page:
            return False

        try:
            submit_btn = await self._page.query_selector(
                "button[type='submit'], button#submit-transfer, button.btn-confirm"
            )
            if submit_btn:
                await submit_btn.click()
                await self._page.wait_for_timeout(500)
                return True
            return False
        except Exception as e:
            logger.error(f"Simulated form submission failed: {e}")
            return False

    async def take_screenshot_bytes(self) -> bytes:
        """Take PNG screenshot for visual inspection or OCR fallback."""
        if not self._page:
            await self.start()
        return await self._page.screenshot(full_page=True)

    def get_dynamic_mutations(self) -> List[Dict[str, Any]]:
        """Return all dynamic mutations detected since navigation."""
        return list(self._dynamic_mutations)

    async def stop(self):
        """Cleanly close browser context and session."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

