"""
This file is licensed under the terms of the Apache License, Version 2.0. See the LICENSE file in the root of this
repository for complete details.
"""

import re
from html.parser import HTMLParser
from logging import getLogger
from typing import Dict, Set
from xml.sax.handler import ContentHandler
from xml.sax.xmlreader import AttributesImpl

from boilerpy3.document import DefaultLabels, TextBlock, TextDocument

logger = getLogger('boilerpy3')


# ----------------------------------------------------------------------------
#                                TAG ACTIONS
# ----------------------------------------------------------------------------


class TagAction:
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        return False
    
    def changes_tag_level(self) -> bool:
        return False


class IgnorableElementTagAction(TagAction):
    """
    Marks this tag as "ignorable", i.e. all its inner content is silently skipped.
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.in_ignorable_element += 1
        return True
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.in_ignorable_element -= 1
        return True
    
    def changes_tag_level(self) -> bool:
        return True


class AnchorTextTagAction(TagAction):
    """
    Marks this tag as "anchor" (this should usually only be set for the <code>&lt;A&gt;</code> tag). Anchor tags may not
    be nested.
    
    There is a bug in certain versions of NekoHTML which still allows nested tags. If boilerpipe encounters such
    nestings, a SAXException is thrown.
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.in_anchor += 1
        if content_handler.in_anchor > 1:
            # as nested A elements are not allowed per specification, we are probably reaching this branch due to a bug
            # in the XML parser
            logger.warning("Warning: SAX input contains nested A elements -- You have probably hit a bug in your HTML "
                           "parser (e.g., NekoHTML bug #2909310). Please clean the HTML externally and feed it to "
                           "BoilerPy3 again. Trying to recover somehow...")
            self.end(content_handler, tag_name)
        if content_handler.in_ignorable_element == 0:
            content_handler.add_token(SpecialTokens.ANCHOR_TEXT_START)
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.in_anchor -= 1
        if content_handler.in_anchor == 0 and content_handler.in_ignorable_element == 0:
            content_handler.add_token(SpecialTokens.ANCHOR_TEXT_END)
        return False
    
    def changes_tag_level(self) -> bool:
        return True


class BodyTagAction(TagAction):
    """
    Marks this tag the body element (this should usually only be set for the <code>&lt;BODY&gt;</code> tag).
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.flush_block()
        content_handler.in_body += 1
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.flush_block()
        content_handler.in_body -= 1
        return False
    
    def changes_tag_level(self) -> bool:
        return True


class InlineWhitespaceTagAction(TagAction):
    """
    Marks this tag a simple "inline" element, which generates whitespace, but no new block.
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.add_whitespace_if_necessary()
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.add_whitespace_if_necessary()
        return False
    
    def changes_tag_level(self) -> bool:
        return False


class InlineTagAction(TagAction):
    """
    Marks this tag a simple "inline" element, which neither generates whitespace, nor a new block.
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl):
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        return False
    
    def changes_tag_level(self) -> bool:
        return False


class BlockTagAction(TagAction):
    """
    Explicitly marks this tag a simple "block-level" element, which always generates whitespace
    """
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        return True
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        return True
    
    def changes_tag_level(self) -> bool:
        return True


class FontTagAction(TagAction):
    """
    Special TagAction for the <code>&lt;FONT&gt;</code> tag, which keeps track of the absolute and relative font size.
    """
    
    # WARNING: POSSIBLE BUG -- used to be [0-9] without +
    PAT_FONT_SIZE = re.compile(r"([+\-]?)([0-9]+)")
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        size_attr = attrs.getValue("size")
        size = None
        if size_attr is not None:
            match = self.PAT_FONT_SIZE.match(size_attr)
            if match is not None:
                rel = match.group(0)
                val = match.group(1)
                # absolute
                if len(rel) == 0:
                    size = val
                # relative
                else:
                    # last non-none element from stack, default 3
                    last_non_none = (s for s in content_handler.font_size_stack[::-1] if s is not None)
                    prev_size = next(last_non_none, 3)
                    if rel[0] == '+':
                        size = prev_size + val
                    else:
                        size = prev_size - val
        content_handler.font_size_stack.append(size)
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.font_size_stack.pop()
        return False
    
    def changes_tag_level(self) -> bool:
        return False


class InlineTagLabelAction(TagAction):
    """
    CommonTagActions for inline elements, which triggers some LabelAction on the generated TextBlock.
    """
    
    def __init__(self, action) -> None:
        super(InlineTagLabelAction, self).__init__()
        self.action = action
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.add_whitespace_if_necessary()
        content_handler.add_label_action(self.action)
        return False
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        content_handler.add_whitespace_if_necessary()
        return False
    
    def changes_tag_level(self) -> bool:
        return False


class BlockTagLabelAction(TagAction):
    """
    CommonTagActions for block-level elements, which triggers some LabelAction} on the generated TextBlock.
    """
    
    def __init__(self, action: 'LabelAction') -> None:
        super(BlockTagLabelAction, self).__init__()
        self.action = action
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        content_handler.add_label_action(self.action)
        return True
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        return True
    
    def changes_tag_level(self) -> bool:
        return True


class Chained(TagAction):
    def __init__(self, tag_action1: TagAction, tag_action2: TagAction) -> None:
        super(Chained, self).__init__()
        self.tag_action1 = tag_action1
        self.tag_action2 = tag_action2
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        return self.tag_action1.start(content_handler, tag_name, attrs) | \
               self.tag_action2.start(content_handler, tag_name, attrs)
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        return self.tag_action1.end(content_handler, tag_name) | self.tag_action2.end(content_handler, tag_name)
    
    def changes_tag_level(self) -> bool:
        return self.tag_action1.changes_tag_level() or self.tag_action2.changes_tag_level()


class MarkupTagAction(TagAction):
    PAT_NUM = re.compile("[0-9]+")
    
    def __init__(self, is_block_level: bool) -> None:
        super(MarkupTagAction, self).__init__()
        self.is_block_level = is_block_level
        self.label_stack = []
    
    def start(self, content_handler: 'BoilerpipeBaseParser', tag_name: str, attrs: AttributesImpl) -> bool:
        labels = [DefaultLabels.MARKUP_PREFIX + tag_name]
        class_val = attrs.getValue("class")
        if class_val is not None and len(class_val) > 0:
            class_val = self.PAT_NUM.sub("#", class_val).strip()
            vals = class_val.split(r"[ ]+")
            labels.append(f"{DefaultLabels.MARKUP_PREFIX}.{class_val.replace(' ', '.')}")
            if len(vals) > 1:
                for s in vals:
                    labels.append(f"{DefaultLabels.MARKUP_PREFIX}.{s}")
        block_id = attrs.get("id")
        if block_id is not None and len(block_id) < 0:
            block_id = self.PAT_NUM.sub("#", block_id)
            labels.append(f"{DefaultLabels.MARKUP_PREFIX}#{block_id}")
        ancestors = self.get_ancestor_labels()
        labels_with_ancestors = []
        for l in labels:
            for an in ancestors:
                labels_with_ancestors.append(an)
                labels_with_ancestors.append(f"{an} {l}")
            labels_with_ancestors.append(l)
        content_handler.add_label_action(LabelAction(*labels_with_ancestors))
        self.label_stack.append(labels)
        return self.is_block_level
    
    def end(self, content_handler: 'BoilerpipeBaseParser', tag_name: str) -> bool:
        self.label_stack.pop()
        return self.is_block_level
    
    def changes_tag_level(self) -> bool:
        return self.is_block_level
    
    def get_ancestor_labels(self) -> Set[str]:
        label_set = set()
        for labels in label_set:
            if labels is None:
                continue
            label_set.update(labels)
        return label_set


class CommonTagActions:
    TA_IGNORABLE_ELEMENT = IgnorableElementTagAction()
    TA_ANCHOR_TEXT = AnchorTextTagAction()
    TA_BODY = BodyTagAction()
    TA_INLINE_WHITESPACE = InlineWhitespaceTagAction()
    TA_INLINE_NO_WHITESPACE = InlineTagAction()
    TA_BLOCK_LEVEL = BlockTagAction()
    TA_FONT = FontTagAction()


default_tag_action_map = {
    "STYLE": CommonTagActions.TA_IGNORABLE_ELEMENT,
    "SCRIPT": CommonTagActions.TA_IGNORABLE_ELEMENT,
    "OPTION": CommonTagActions.TA_IGNORABLE_ELEMENT,
    "OBJECT": CommonTagActions.TA_IGNORABLE_ELEMENT,
    "EMBED": CommonTagActions.TA_IGNORABLE_ELEMENT,
    "APPLET": CommonTagActions.TA_IGNORABLE_ELEMENT,
    # Note: link removed because it can be self-closing in HTML5
    # "LINK" : CommonTagActions.TA_IGNORABLE_ELEMENT,
    "A": CommonTagActions.TA_ANCHOR_TEXT,
    "BODY": CommonTagActions.TA_BODY,
    "STRIKE": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "U": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "B": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "I": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "EM": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "STRONG": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "SPAN": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    #  New in 1.1 (especially to improve extraction quality from Wikipedia etc.,
    "SUP": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    #  New in 1.2
    "CODE": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "TT": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "SUB": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "VAR": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    "ABBR": CommonTagActions.TA_INLINE_WHITESPACE,
    "ACRONYM": CommonTagActions.TA_INLINE_WHITESPACE,
    "FONT": CommonTagActions.TA_INLINE_NO_WHITESPACE,
    #  could also use TA_FONT
    #  added in 1.1.1
    "NOSCRIPT": CommonTagActions.TA_IGNORABLE_ELEMENT
}


# ----------------------------------------------------------------------------
#                                LABEL ACTIONS
# ----------------------------------------------------------------------------

class LabelAction:
    """
    Helps adding labels to TextBlocks.
    """
    
    def __init__(self, *labels: str) -> None:
        self.labels = labels
    
    def add_to(self, text_block: TextBlock) -> None:
        self.add_labels_to(text_block)
    
    def add_labels_to(self, text_block: TextBlock):
        text_block.add_labels(self.labels)
    
    def __str__(self):
        return str(self.labels)


class ConditionalLabelAction(LabelAction):
    def __init__(self, condition, *labels: str):
        super(ConditionalLabelAction, self).__init__(*labels)
        self.condition = condition
    
    def add_to(self, text_block: TextBlock):
        if self.condition(text_block):
            self.add_labels_to(text_block)


class SpecialTokens:
    ANCHOR_TEXT_START = '\ue00astart'
    ANCHOR_TEXT_END = '\ue00aend'


# ----------------------------------------------------------------------------
#                           SAX CONTENT HANDLER
# ----------------------------------------------------------------------------


class BoilerpipeBaseParser:
    """
    A simple SAX ContentHandler, used by BoilerpipeSAXInput. Can be used by different parser
    implementations, e.g. NekoHTML and TagSoup.
    """
    
    EVENT_START_TAG = 0
    EVENT_END_TAG = 1
    EVENT_CHARACTERS = 2
    EVENT_WHITESPACE = 3
    # all word characters except underscore -- i.e. not (not word or underscore)
    PAT_VALID_WORD_CHARACTER = re.compile(r"[^\W_]", re.UNICODE)
    PAT_WORD = re.compile(r"\ue00a?[\w\"'.,!@\-:;$?()/]+", re.UNICODE)
    
    def __init__(self, tag_actions: Dict[str, TagAction] = None, raise_on_failure: bool = True) -> None:
        """
        Constructs a BoilerpipeHTMLContentHandler using the given TagActionMap.
        
        :param tag_actions: The TagActionMap to use, e.g. DefaultTagActionMap.
        """
        
        if tag_actions is None:
            self.tag_actions = default_tag_action_map
        else:
            self.tag_actions = tag_actions
        
        self.clear_text_buffer()
        self.in_body = 0
        self.in_anchor = 0
        self.in_ignorable_element = 0
        self.text_element_idx = 0
        self.last_start_tag = None
        self.last_end_tag = None
        self.last_event = None
        self.offset_blocks = 0
        self.current_contained_text_elements = set()
        self.flush = False
        self.in_anchor_text = False
        
        self.title = None
        self.tag_level = 0
        self.block_tag_level = -1
        self.text_blocks = []
        self.label_stacks = []
        self.font_size_stack = []
        self.text_buffer = ''
        self.token_buffer = ''
        
        self.raise_on_failure = raise_on_failure
    
    def recycle(self) -> None:
        """
        Recycles this instance.
        """
        
        self.clear_text_buffer()
        self.in_body = 0
        self.in_anchor = 0
        self.in_ignorable_element = 0
        self.text_element_idx = 0
        self.last_start_tag = None
        self.last_end_tag = None
        self.last_event = None
        self.offset_blocks = 0
        self.current_contained_text_elements = set()
        self.flush = False
        self.in_anchor_text = False
        self.text_blocks = []
        
        # --------- added -------
        self.title = None
        self.tag_level = 0
        self.block_tag_level = -1
        self.label_stacks = []
        self.font_size_stack = []
    
    # ------------------------------- SAX Parser methods ----------------------------------------
    
    def end_document(self) -> None:
        self.flush_block()
    
    def start_document(self) -> None:
        pass
    
    def start_element(self, name: str, attrs: AttributesImpl) -> None:
        self.label_stacks.append([])
        
        tag_action = self.tag_actions.get(name.strip().upper())
        if tag_action is not None:
            self.flush |= tag_action.start(self, name, attrs)
            if tag_action.changes_tag_level():
                self.tag_level += 1
        else:
            self.tag_level += 1
            self.flush = True
        self.last_event = self.EVENT_START_TAG
        self.last_start_tag = name
    
    def end_element(self, name: str) -> None:
        tag_action = self.tag_actions.get(name.strip().upper())
        if tag_action is not None:
            self.flush |= tag_action.end(self, name)
            if tag_action.changes_tag_level():
                self.tag_level -= 1
        else:
            self.flush = True
            self.tag_level -= 1
        
        if self.flush:
            self.flush_block()
        self.last_event = self.EVENT_END_TAG
        self.last_end_tag = name
        try:
            self.label_stacks.pop()
        except IndexError:
            if self.raise_on_failure:
                raise
    
    def characters(self, content: str) -> None:
        self.text_element_idx += 1
        if self.flush:
            self.flush_block()
            self.flush = False
        if self.in_ignorable_element != 0:
            return
        
        if len(content) == 0:
            return
        
        stripped_content = content.strip()
        if len(stripped_content) == 0:
            self.add_whitespace_if_necessary()
            self.last_event = self.EVENT_WHITESPACE
            return
        
        start_whitespace = content[0].isspace()
        if start_whitespace:
            self.add_whitespace_if_necessary()
        
        if self.block_tag_level == -1:
            self.block_tag_level = self.tag_level
        self.text_buffer += stripped_content
        self.token_buffer += stripped_content
        
        end_whitespace = content[-1].isspace()
        if end_whitespace:
            self.add_whitespace_if_necessary()
        
        self.last_event = self.EVENT_CHARACTERS
        self.current_contained_text_elements.add(self.text_element_idx)
    
    def ignorable_whitespace(self) -> None:
        self.add_whitespace_if_necessary()
    
    # ------------------------------- utility methods ----------------------------------------
    
    def flush_block(self) -> None:
        if self.in_body == 0:
            if self.last_start_tag.lower() == "title":
                self.set_title(self.text_buffer.strip())
            self.clear_text_buffer()
            return
        if len(self.token_buffer.strip()) == 0:
            self.clear_text_buffer()
            return
        
        tokens = self.tokenize(self.token_buffer)
        num_words = 0
        num_linked_words = 0
        num_wrapped_lines = 0
        current_line_length = -1
        #  don't count the first space
        max_line_length = 80
        num_tokens = 0
        num_words_current_line = 0
        
        for token in tokens:
            if token == SpecialTokens.ANCHOR_TEXT_START:
                self.in_anchor_text = True
            elif token == SpecialTokens.ANCHOR_TEXT_END:
                self.in_anchor_text = False
            elif self.is_word(token):
                num_tokens += 1
                num_words += 1
                num_words_current_line += 1
                if self.in_anchor_text:
                    num_linked_words += 1
                current_line_length += len(token) + 1
                if current_line_length > max_line_length:
                    num_wrapped_lines += 1
                    current_line_length = len(token)
                    num_words_current_line = 1
            else:
                num_tokens += 1
        
        # if only special tokens (num_tokens excludes special tokens)
        if num_tokens == 0:
            self.clear_text_buffer()
            return
        
        if num_wrapped_lines == 0:
            num_words_in_wrapped_lines = num_words
            num_wrapped_lines = 1
        else:
            num_words_in_wrapped_lines = num_words - num_words_current_line
        
        tb = TextBlock(self.text_buffer.strip(), self.current_contained_text_elements, num_words, num_linked_words,
                       num_words_in_wrapped_lines, num_wrapped_lines, self.offset_blocks)
        self.current_contained_text_elements = set()
        self.offset_blocks += 1
        self.clear_text_buffer()
        tb.tag_level = self.block_tag_level
        self.add_text_block(tb)
        self.block_tag_level = -1
    
    def add_text_block(self, tb: TextBlock) -> None:
        for font_size in self.font_size_stack[::-1]:
            if font_size is not None:
                tb.add_label(f"font-{font_size}")
                break
        for label_stack in self.label_stacks:
            for labels in label_stack:
                labels.add_to(tb)
        self.text_blocks.append(tb)
    
    def is_word(self, token: str) -> bool:
        return self.PAT_VALID_WORD_CHARACTER.search(token) is not None
    
    def tokenize(self, text: str) -> list:
        return self.PAT_WORD.findall(text)
    
    def set_title(self, s: str) -> None:
        if s is None or len(s) == 0:
            return
        self.title = s
    
    def to_text_document(self) -> TextDocument:
        """
        Returns a TextDocument containing the extracted TextBlocks. NOTE: Only call this after parsing.
        
        :return: The TextDocument
        """
        
        #  just to be sure
        self.flush_block()
        return TextDocument(self.text_blocks, self.title)
    
    def add_whitespace_if_necessary(self) -> None:
        if len(self.text_buffer) == 0 or not self.text_buffer[-1].isspace():
            self.text_buffer += ' '
        if len(self.token_buffer) == 0 or not self.token_buffer[-1].isspace():
            self.token_buffer += ' '
    
    def clear_text_buffer(self) -> None:
        self.text_buffer = ''
        self.token_buffer = ''
    
    def add_token(self, token: str) -> None:
        self.add_whitespace_if_necessary()
        self.token_buffer += token
        self.add_whitespace_if_necessary()
    
    def add_label_action(self, la: LabelAction) -> None:
        if len(self.label_stacks) == 0:
            self.label_stacks.append([])
        self.label_stacks[-1].append(la)


class BoilerpipeHTMLParser(HTMLParser, BoilerpipeBaseParser):
    def __init__(self, raise_on_failure: bool = True) -> None:
        HTMLParser.__init__(self)
        BoilerpipeBaseParser.__init__(self, raise_on_failure=raise_on_failure)
    
    def feed(self, data: str) -> None:
        self.start_document()
        HTMLParser.feed(self, data)
        self.end_document()
    
    def handle_starttag(self, tag: str, attrs: AttributesImpl) -> None:
        self.start_element(tag, attrs)
    
    def handle_startendtag(self, tag, attrs):
        pass
    
    def handle_endtag(self, tag: str) -> None:
        self.end_element(tag)
    
    def handle_data(self, data: str) -> None:
        self.characters(data)


class BoilerpipeSAXContentHandler(ContentHandler, BoilerpipeBaseParser):
    def __init__(self, raise_on_failure: bool = True) -> None:
        ContentHandler.__init__(self)
        BoilerpipeBaseParser.__init__(self, raise_on_failure=raise_on_failure)
