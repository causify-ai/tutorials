"""
This file is licensed under the terms of the Apache License, Version 2.0. See the LICENSE file in the root of this
repository for complete details.
"""

from html import escape
from typing import Iterable
from xml.sax.xmlreader import AttributesImpl

from boilerpy3.document import TextDocument
from boilerpy3.parser import BoilerpipeHTMLParser


class AnotherBoilerPipeHTMLParser(BoilerpipeHTMLParser):
    def __init__(self, raise_on_failure: bool = True) -> None:
        super(AnotherBoilerPipeHTMLParser, self).__init__(raise_on_failure=raise_on_failure)
    
    def error(self, message: str):
        pass
    
    def handle_starttag(self, tag: str, attributes) -> None:
        self.start_element(tag, AttributesImpl(dict(attributes)))


class HTMLBoilerpipeMarker:
    ALLOWED_ATTRIBUTES = {'class', 'href', 'src'}
    TA_IGNORABLE_ELEMENTS = {'STYLE', 'SCRIPT', 'OPTION', 'NOSCRIPT', 'OBJECT', 'EMBED', 'APPLET', 'LINK', 'HEAD',
                             'SVG', 'SELECT', 'FORM'}
    VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param',
                     'source', 'track', 'wbr'}
    
    def __init__(self, remove_elements: Iterable = None, allowed_attributes: Iterable = None,
                 raise_on_failure: bool = True) -> None:
        self.TA_IGNORABLE_ELEMENTS = set(remove_elements) if remove_elements else self.TA_IGNORABLE_ELEMENTS
        self.ALLOWED_ATTRIBUTES = set(allowed_attributes) if allowed_attributes else self.ALLOWED_ATTRIBUTES
        self.raise_on_failure = raise_on_failure
    
    def process(self, doc: TextDocument, is_: str) -> str:
        implementation = Implementation(self, raise_on_failure=self.raise_on_failure)
        implementation.process(doc, is_)
        return implementation.html


class Implementation(AnotherBoilerPipeHTMLParser):
    html = ""
    in_ignorable_element = 0
    character_element_idx = 0
    content_bit_set = set()
    
    def __init__(self, hl: HTMLBoilerpipeMarker, raise_on_failure: bool = True) -> None:
        self.hl = hl
        super(Implementation, self).__init__(raise_on_failure=raise_on_failure)
    
    def _xml_encode(self, s: str) -> str:
        return escape(s)
    
    def process(self, doc: TextDocument, is_: str):
        for block in doc.text_blocks:
            if block.is_content:
                bs = block.contained_text_elements
                if bs:
                    self.content_bit_set = self.content_bit_set.union(bs)
        
        self.feed(is_)
    
    def end_document(self):
        pass
    
    def start_document(self):
        pass
    
    def start_element(self, q_name: str, atts: dict) -> None:
        if q_name.upper() in self.hl.TA_IGNORABLE_ELEMENTS:
            if q_name.lower() not in self.hl.VOID_ELEMENTS:
                self.in_ignorable_element += 1
        
        if self.in_ignorable_element == 0:
            self.html += f'<{q_name}'
            
            if self.character_element_idx + 1 in self.content_bit_set:
                self.html += ' x-boilerpipe-marker'
            
            for attr_name, attr_value in atts.items():
                if attr_name not in self.hl.ALLOWED_ATTRIBUTES:
                    continue
                self.html += f' {attr_name}=\"{self._xml_encode(attr_value or "")}\"'
            
            self.html += '>'
    
    def end_element(self, q_name: str) -> None:
        try:
            if self.in_ignorable_element == 0:
                self.html += f'</{q_name}>'
        finally:
            if q_name.upper() in self.hl.TA_IGNORABLE_ELEMENTS:
                self.in_ignorable_element -= 1
    
    def characters(self, ch: str) -> None:
        self.character_element_idx += 1
        if self.in_ignorable_element == 0:
            if self.character_element_idx not in self.content_bit_set:
                return
            
            self.html += self._xml_encode(str(ch))
