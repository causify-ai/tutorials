"""
This file is licensed under the terms of the Apache License, Version 2.0. See the LICENSE file in the root of this
repository for complete details.
"""

import copy
import sys
from typing import List, Set, Tuple, Union


class DefaultLabels:
    """
    Some pre-defined labels which can be used in conjunction with TextBlock
    """
    
    TITLE = "de.l3s.boilerpipe/TITLE"
    ARTICLE_METADATA = "de.l3s.boilerpipe/ARTICLE_METADATA"
    INDICATES_END_OF_TEXT = "de.l3s.boilerpipe/INDICATES_END_OF_TEXT"
    MIGHT_BE_CONTENT = "de.l3s.boilerpipe/MIGHT_BE_CONTENT"
    STRICTLY_NOT_CONTENT = "de.l3s.boilerpipe/STRICTLY_NOT_CONTENT"
    HR = "de.l3s.boilerpipe/HR"
    MARKUP_PREFIX = "<"


class TextBlock:
    """
    Describes a block of text. A block can be an "atomic" text element (i.e., a sequence of text that is not interrupted
    by any HTML markup) or a compound of such atomic elements.
    """
    
    EMPTY_START: 'TextBlock'
    EMPTY_END: 'TextBlock'
    
    def __init__(self, text: str, contained_text_elements=None, num_words: int = 0, num_words_in_anchor_text: int = 0,
                 num_words_in_wrapped_lines: int = 0, num_wrapped_lines: int = 0, offset_blocks: int = 0) -> None:
        self.is_content = False
        self.labels = set()
        self.num_full_text_words = 0
        self.tag_level = 0
        
        self.text = text
        if contained_text_elements is None:
            contained_text_elements = set()
        self.contained_text_elements = contained_text_elements
        self.num_words = num_words
        self.num_words_in_anchor_text = num_words_in_anchor_text
        self.num_words_in_wrapped_lines = num_words_in_wrapped_lines
        self.num_wrapped_lines = num_wrapped_lines
        self.offset_blocks_start = offset_blocks
        self.offset_blocks_end = offset_blocks
        self.text_density = 0
        self.link_density = 0
        self._init_densities()
    
    def _init_densities(self) -> None:
        if self.num_words_in_wrapped_lines == 0:
            self.num_words_in_wrapped_lines = self.num_words
            self.num_wrapped_lines = 1
        self.text_density = self.num_words_in_wrapped_lines / float(self.num_wrapped_lines)
        self.link_density = 0 if self.num_words == 0 else self.num_words_in_anchor_text / float(self.num_words)
    
    def set_is_content(self, is_content: bool) -> bool:
        if is_content != self.is_content:
            self.is_content = is_content
            return True
        else:
            return False
    
    def merge_next(self, next_text_block: 'TextBlock') -> None:
        if self.text is None:
            self.text = ""
        self.text = f'{self.text}\n{next_text_block.text}'
        self.num_words += next_text_block.num_words
        self.num_words_in_anchor_text += next_text_block.num_words_in_anchor_text
        self.num_words_in_wrapped_lines += next_text_block.num_words_in_wrapped_lines
        self.num_wrapped_lines += next_text_block.num_wrapped_lines
        self.offset_blocks_start = min(self.offset_blocks_start, next_text_block.offset_blocks_start)
        self.offset_blocks_end = max(self.offset_blocks_end, next_text_block.offset_blocks_end)
        self._init_densities()
        self.is_content |= next_text_block.is_content
        self.contained_text_elements |= next_text_block.contained_text_elements
        self.num_full_text_words += next_text_block.num_full_text_words
        self.labels |= next_text_block.labels
        self.tag_level = min(self.tag_level, next_text_block.tag_level)
    
    def __repr__(self) -> str:
        return f"[{self.offset_blocks_start}-{self.offset_blocks_end}; tl={self.tag_level}; nw={self.num_words};" \
               f"nwl={self.num_wrapped_lines}; ld={self.link_density}]\t" \
               f"{'CONTENT' if self.is_content else 'boilerplate'},{self.labels}\n{self.text}"
    
    def add_label(self, label) -> None:
        """
        Adds an arbitrary String label to this TextBlock.

        :param label: The label
        """
        
        self.labels.add(label)
    
    def has_label(self, label: str) -> bool:
        """
        Checks whether this TextBlock has the given label.

        :param label: The label
        :return: <code>true</code> if this block is marked by the given label.
        """
        
        return label in self.labels
    
    def remove_label(self, label: str) -> bool:
        try:
            self.labels.remove(label)
            return True
        except KeyError:
            return False
    
    def add_labels(self, *labels: Union[List, Set, Tuple]):
        """
        Adds a set of labels to this TextBlock. <code>null</code>-references are silently ignored.

        :param labels: The labels to be added.
        """
        
        if len(labels) == 0 or labels[0] is None:
            return
        if self.labels is None:
            self.labels = set()
        elif len(labels) == 1 and isinstance(labels[0], (set, list)):
            self.labels |= set(labels[0])
        else:
            self.labels |= set(labels)
    
    def clone(self):
        try:
            clone = copy.copy(self)
        except copy.error:
            raise copy.error
        if self.labels is not None:
            clone.labels = self.labels.copy()
        if self.contained_text_elements is not None:
            clone.contained_text_elements = self.contained_text_elements.copy()
        
        return clone


TextBlock.EMPTY_START = TextBlock("", set(), 0, 0, 0, 0, -1)
TextBlock.EMPTY_END = TextBlock("", set(), 0, 0, 0, 0, sys.maxsize)


class TextDocument:
    """
    A text document, consisting of one or more TextBlocks.
    """
    
    def __init__(self, text_blocks: List[TextBlock], title: str = None):
        """
        Creates a new TextDocument with given TextBlocks and given title.

        :param text_blocks: The text blocks of this document.
        :param title: The "main" title for this text document.
        """
        
        self.title = title
        self.text_blocks = text_blocks
    
    @property
    def content(self) -> str:
        """
        Returns the TextDocument's content.
        
        :return: The content text.
        """
        
        return self.get_text(True, False)
    
    def get_text(self, include_content: bool, include_non_content: bool) -> str:
        """
        Returns the TextDocument's content, non-content or both.
        
        :param include_content: Whether to include TextBlocks marked as "content".
        :param include_non_content: Whether to include TextBlocks marked as "non-content".
        :return: The text.
        """
        
        sb = []
        for block in self.text_blocks:
            if block.is_content:
                if not include_content:
                    continue
            else:
                if not include_non_content:
                    continue
            sb.append(f'{block.text}\n')
        
        return ''.join(sb)
    
    @property
    def debug_string(self) -> str:
        """
        Returns detailed debugging information about the contained TextBlocks.

        :return: Debug information.
        """
        
        return ''.join([f'{tb}\n' for tb in self.text_blocks])


class TextDocumentStatistics:
    """
    Provides shallow statistics on a given TextDocument
    """
    
    def __init__(self, doc: TextDocument, content_only: bool) -> None:
        """
        Computes statistics on a given TextDocument.
        
        :param doc: The TextDocument.
        :param content_only: if true then o
        """
        
        self.num_words = 0
        self.num_blocks = 0
        for tb in doc.text_blocks:
            if content_only and not tb.is_content:
                continue
            self.num_words += tb.num_words
            self.num_blocks += 1
    
    def avg_num_words(self) -> float:
        """
        Returns the average number of words at block-level (= overall number of words divided by the number of blocks).
        
        :return: Average
        """
        
        return self.num_words / float(self.num_blocks)
