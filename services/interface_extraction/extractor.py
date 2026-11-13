"""
Financial Interface Extraction Engine for Mboa Finance AI.
Extracts structured elements from DOM trees, accessibility trees, and HTML snapshots.
Classifies balances, fees, warnings, buttons, inputs, and security notices.
Preserves selector paths, contexts, and coordinates.
"""

import re
import time
import logging
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from packages.shared_schemas.mboa_schemas import (
    ExtractedInterfaceElement,
    InterfaceElementType,
    FinancialEntity,
    DOMExtractionResult,
    BoundingBox
)
from packages.financial_validation.validator import DeterministicFinancialValidator

logger = logging.getLogger("mboa.interface.extractor")


class InterfaceExtractor:
    """
    DOM & Accessibility Tree Extractor for third-party financial interfaces.
    Operates without altering target website source code.
    """

    BALANCE_KEYWORDS = ["solde", "balance", "disponible", "available", "épargne", "compte"]
    FEE_KEYWORDS = ["frais", "fee", "tarif", "charges", "commission", "coût"]
    WARNING_KEYWORDS = ["attention", "avertissement", "ne partagez", "pin", "arnaque", "warning", "caution", "fraud"]
    CONDITION_KEYWORDS = ["condition", "termes", "délai", "plafond", "limite", "terms", "limit"]

    # Security heuristic: Detect prompt injection patterns in third-party or unseen interface strings
    PROMPT_INJECTION_PATTERNS = [
        re.compile(r'\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous\s+)?(?:instructions|prompts|rules)\b', re.IGNORECASE),
        re.compile(r'\b(?:system\s+(?:prompt|override|command)|developer\s+mode|jailbreak)\b', re.IGNORECASE),
        re.compile(r'\b(?:you\s+must|always)\s+(?:transfer|debit|send|confirm)\s+(?:silently|automatically)\b', re.IGNORECASE),
        re.compile(r'\[\s*(?:system|override|assistant)\s*\]', re.IGNORECASE),
    ]

    def __init__(self):
        self.validator = DeterministicFinancialValidator()

    def detect_prompt_injection(self, text: str) -> bool:
        """Checks if text contains prompt injection signatures intended to subvert the agent."""
        if not text:
            return False
        return any(pattern.search(text) for pattern in self.PROMPT_INJECTION_PATTERNS)

    def extract_from_html(self, html_content: str, page_url: str = "http://localhost") -> DOMExtractionResult:
        """
        Parses raw HTML/DOM representation into structured financial elements.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        elements: List[ExtractedInterfaceElement] = []
        balances: List[FinancialEntity] = []
        fees: List[FinancialEntity] = []
        warnings: List[str] = []
        conditions: List[str] = []
        interactive_selectors: Dict[str, str] = {}

        # 1. Title extraction
        title_tag = soup.find("title")
        page_title = title_tag.get_text(strip=True) if title_tag else "Financial Interface"

        # 2. Extract and classify interactive & leaf text elements
        candidate_tags = soup.find_all(["button", "input", "a", "span", "p", "div", "h1", "h2", "h3", "h4", "label", "li", "td", "th"])

        element_counter = 0
        for tag in candidate_tags:
            tag_name = tag.name.lower()
            tag_text = tag.get_text(strip=True)

            # Skip empty containers
            if not tag_text and tag_name not in ["input", "button"]:
                continue

            # Only extract leaf nodes or inputs/buttons to avoid huge duplicated parent blocks
            if tag_name not in ["input", "button"]:
                has_child_elements = any(c.name for c in tag.find_all(True))
                if has_child_elements:
                    continue

            # Check for adversarial prompt injection in interface text
            is_injected = self.detect_prompt_injection(tag_text)
            if is_injected:
                logger.warning(f"Adversarial prompt injection pattern detected in DOM element: '{tag_text}'")
                warnings.append("Alerte de sécurité : tentative d'injection de commande dans l'interface détectée et neutralisée.")
                tag_text = f"[CONTENU NEUTRALISÉ : {tag_text[:40]}...]"

            # Classify element type
            el_type = self._classify_element_type(tag, tag_text)
            el_id = tag.get("id") or f"el_{element_counter}_{tag_name}"
            selector = self._compute_css_selector(tag)
            element_counter += 1

            # Check if interactive
            is_interactive = tag_name in ["button", "input", "a"] or tag.get("onclick") is not None

            # Collect interactive selectors for quick access
            if is_interactive:
                role = tag.get("name") or tag.get("id") or tag_text[:20]
                if role:
                    interactive_selectors[role.lower()] = selector

            # Financial Entity Extraction
            amount = self.validator.parse_amount(tag_text)

            if el_type == InterfaceElementType.BALANCE and amount is not None:
                balances.append(FinancialEntity(
                    name=tag_text,
                    raw_value=tag_text,
                    parsed_numeric_value=amount,
                    currency="FCFA" if "FCFA" in tag_text else "XAF",
                    associated_element_id=el_id,
                    verified=True
                ))
            elif el_type == InterfaceElementType.FEE and amount is not None:
                fees.append(FinancialEntity(
                    name=tag_text,
                    raw_value=tag_text,
                    parsed_numeric_value=amount,
                    currency="FCFA" if "FCFA" in tag_text else "XAF",
                    associated_element_id=el_id,
                    verified=True
                ))
            elif el_type == InterfaceElementType.SECURITY_WARNING and tag_text:
                warnings.append(tag_text)
            elif el_type == InterfaceElementType.CONDITION and tag_text:
                conditions.append(tag_text)

            # Clean attributes for schema compatibility
            clean_attrs = {}
            if hasattr(tag, "attrs") and tag.attrs:
                for k, v in tag.attrs.items():
                    clean_attrs[k] = " ".join(v) if isinstance(v, list) else str(v)

            # Store element record
            elements.append(ExtractedInterfaceElement(
                id=el_id,
                element_type=el_type,
                selector=selector,
                original_text=tag_text,
                translated_text=None,
                bounding_box=BoundingBox(),
                is_interactive=is_interactive,
                is_dynamic=bool(tag.get("data-dynamic") or "toast" in tag.get("class", []) or "alert" in tag.get("class", [])),
                context=tag.parent.name if tag.parent else None,
                attributes=clean_attrs
            ))

        return DOMExtractionResult(
            page_url=page_url,
            title=page_title,
            timestamp=time.time(),
            elements=elements,
            balances=balances,
            fees=fees,
            warnings=warnings,
            conditions=conditions,
            interactive_selectors=interactive_selectors,
            raw_text=soup.get_text(separator=" ", strip=True)
        )

    def _classify_element_type(self, tag: Any, text: str) -> InterfaceElementType:
        """Classify DOM element according to financial semantics."""
        tag_name = tag.name.lower()
        text_lower = text.lower()
        classes = " ".join(tag.get("class", [])).lower() if isinstance(tag.get("class"), list) else str(tag.get("class", "")).lower()
        tag_id = str(tag.get("id", "")).lower()

        # Gather surrounding context from parent and previous sibling
        parent_classes = ""
        if tag.parent:
            parent_classes = " ".join(tag.parent.get("class", [])).lower() if isinstance(tag.parent.get("class"), list) else str(tag.parent.get("class", "")).lower()

        prev_sibling_text = ""
        prev = tag.find_previous_sibling()
        if prev:
            prev_sibling_text = prev.get_text(separator=" ", strip=True).lower()

        context_all = f"{text_lower} {classes} {tag_id} {parent_classes} {prev_sibling_text}"

        if tag_name == "button" or tag.get("type") == "button":
            return InterfaceElementType.BUTTON
        if tag_name == "input":
            return InterfaceElementType.INPUT

        # Security warnings
        if any(w in text_lower or w in classes for w in self.WARNING_KEYWORDS):
            return InterfaceElementType.SECURITY_WARNING

        # Balances
        if any(b in text_lower or b in classes or b in tag_id for b in self.BALANCE_KEYWORDS):
            if any(char.isdigit() for char in text):
                return InterfaceElementType.BALANCE
            return InterfaceElementType.LABEL

        # Fees
        if any(f in context_all for f in self.FEE_KEYWORDS):
            if any(char.isdigit() for char in text):
                return InterfaceElementType.FEE
            return InterfaceElementType.LABEL

        # Conditions
        if any(c in text_lower or c in classes or c in tag_id for c in self.CONDITION_KEYWORDS):
            return InterfaceElementType.CONDITION

        # Notifications
        if "notification" in classes or "alert" in classes or "toast" in classes:
            return InterfaceElementType.NOTIFICATION

        if tag_name in ["label", "th"]:
            return InterfaceElementType.LABEL

        return InterfaceElementType.TEXT

    def _compute_css_selector(self, tag: Any) -> str:
        """Generate unique CSS selector for DOM manipulation."""
        if tag.get("id"):
            return f"#{tag['id']}"
        if tag.get("name"):
            return f"{tag.name}[name='{tag['name']}']"

        classes = tag.get("class")
        if classes and isinstance(classes, list):
            class_str = ".".join(classes[:2])
            return f"{tag.name}.{class_str}"

        return tag.name
