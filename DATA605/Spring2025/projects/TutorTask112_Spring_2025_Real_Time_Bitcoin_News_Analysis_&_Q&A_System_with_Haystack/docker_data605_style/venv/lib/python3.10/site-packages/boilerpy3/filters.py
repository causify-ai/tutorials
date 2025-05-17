"""
This file is licensed under the terms of the Apache License, Version 2.0. See the LICENSE file in the root of this
repository for complete details.
"""

# -----------------------------------------------------------------------
#                           FILTER MANIFEST
# -----------------------------------------------------------------------
#
# --------------------- Simple Filters: -----------------------
# MarkEverythingContentFilter - Marks all blocks as content.
# InvertedFilter - Reverts the "is_content" flag for all TextBlocks
# BoilerplateBlockFilter - Removes TextBlocks which have explicitly been marked as "not content".
# MinWordsFilter - Keeps only those content blocks which contain at least k words.
# MinClauseWordsFilter - Keeps only blocks that have at least one segment fragment ("clause") with at least k words
# SplitParagraphBlocksFilter - Splits TextBlocks at paragraph boundaries
# SurroundingToContentFilter
# LabelToBoilerplateFilter - Marks all blocks that contain a given label as "boilerplate".
# LabelToContentFilter - Marks all blocks that contain a given label as "content".
#
# --------------------- Heuristic Filters: -----------------------
# SimpleBlockFusionProcessor - Merges two subsequent blocks if their text densities are equal.
# ContentFusion
# LabelFusion - Fuses adjacent blocks if their labels are equal.
# BlockProximityFusion - Fuses adjacent blocks if their distance (in blocks) does not exceed a certain limit.
# KeepLargestBlockFilter - Keeps the largest TextBlock only (by the number of words)
# ExpandTitleToContentFilter - Marks all TextBlocks "content" which are between the headline and the part that has
#                              already been marked content, if they are marked MIGHT_BE_CONTENT
# ArticleMetadataFilter
# AddPrecedingLabelsFilter - Adds the labels of the preceding block to the current block, optionally adding a prefix.
# DocumentTitleMatchClassifier - Marks TextBlocks which contain parts of the HTML TITLE tag
#
# --------------------- English-trained Heuristic Filters: -----------------------
# MinFulltextWordsFilter - Keeps only those content blocks which contain at least k full-text words
# KeepLargestFulltextBlockFilter - Keeps the largest TextBlock only (by the number of words)
# IgnoreBlocksAfterContentFilter - Marks all blocks as "non-content" that occur after blocks that have been marked
#                                  INDICATES_END_OF_TEXT
# IgnoreBlocksAfterContentFromEndFilter - like above
# TerminatingBlocksFinder - Finds blocks which are potentially indicating the end of an article text and marks them with
#                           INDICATES_END_OF_TEXT
# NumWordsRulesClassifier - Classifies TextBlocks as content/not-content through rules that have been determined using
#                           the C4.8 machine learning algorithm
# DensityRulesClassifier - Classifies TextBlocks as content/not-content through rules that have been determined using
#                          the C4.8 machine learning algorithm
# CanolaFilter - A full-text extractor trained on krdwrd Canola


import re
from typing import List, Pattern, Union

from boilerpy3.document import DefaultLabels, TextBlock, TextDocument


class BoilerpipeFilter:
    """
    Boilerpipe abstract interface
    """
    
    def process(self, doc: TextDocument) -> bool:
        pass
    
    def subtract_blocks(self, block_arr: List[TextBlock], blocks_to_remove: List[TextBlock]) -> List[TextBlock]:
        """
        inefficient but in place: for block in blocksToRemove: blockArr.remove(blocksToRemove) efficiently subtracts
        second array from first assuming blocksToRemove shows up in the same order as blocArr
        """
        
        if len(blocks_to_remove) == 0:
            return block_arr
        new_block_arr = []
        remove_iter = iter(blocks_to_remove)
        cur_block_to_remove = next(remove_iter)
        for idx, block in enumerate(block_arr):
            if block == cur_block_to_remove:
                try:
                    cur_block_to_remove = next(remove_iter)
                except StopIteration:
                    # add the rest
                    new_block_arr.extend(block_arr[idx + 1:])
                    break
            else:
                new_block_arr.append(block)
        return new_block_arr


class FilterChain(BoilerpipeFilter):
    """
    Chain together multiple filters in sequence
    """
    
    def __init__(self, filter_arr: List[BoilerpipeFilter]) -> None:
        super(FilterChain, self).__init__()
        self.filter_arr = filter_arr
    
    def process(self, doc: TextDocument) -> bool:
        is_updated = False
        for filtr in self.filter_arr:
            is_updated |= filtr.process(doc)
        return is_updated


# -----------------------------------------------------------------------
#                           SIMPLE FILTERS
# -----------------------------------------------------------------------


class MarkEverythingContentFilter(BoilerpipeFilter):
    """
    Marks all blocks as content.
    """
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if not tb.is_content:
                tb.set_is_content(True)
                changes = True
        return changes


class InvertedFilter(BoilerpipeFilter):
    """
    Reverts the "is_content" flag for all TextBlocks
    """
    
    def process(self, doc: TextDocument) -> bool:
        tbs = doc.text_blocks
        if len(tbs) == 0:
            return False
        for tb in tbs:
            tb.set_is_content(not tb.is_content)
        return True


class BoilerplateBlockFilter(BoilerpipeFilter):
    """
    Removes TextBlocks which have explicitly been marked as "not content".
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        new_blocks = [tb for tb in text_blocks if tb.is_content]
        has_changes = len(new_blocks) < len(text_blocks)
        doc.text_blocks = new_blocks
        
        return has_changes


class MinWordsFilter(BoilerpipeFilter):
    """
    Keeps only those content blocks which contain at least <em>k</em> words.
    """
    
    def __init__(self, min_words: int) -> None:
        super(MinWordsFilter, self).__init__()
        self.min_words = min_words
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if not tb.is_content:
                continue
            if tb.num_words < self.min_words:
                tb.set_is_content(False)
                changes = True
        return changes


class MinClauseWordsFilter(BoilerpipeFilter):
    """
    Keeps only blocks that have at least one segment fragment ("clause") with at least <em>k</em> words (default: 5).

    NOTE: You might consider using the SplitParagraphBlocksFilter
    upstream.

    See SplitParagraphBlocksFilter
    """
    
    PAT_CLAUSE_DELIMITER = re.compile(r"\b[,.:;!?]+(?:\s+|\Z)", re.UNICODE)
    PAT_WHITESPACE = re.compile(r"\s+")
    
    def __init__(self, min_words: int = 5, accept_clauses_without_delimiter: bool = False) -> None:
        super(MinClauseWordsFilter, self).__init__()
        self.min_words = min_words
        self.accept_clauses_without_delimiter = accept_clauses_without_delimiter
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if not tb.is_content:
                continue
            has_clause = False
            possible_clause_arr = self.PAT_CLAUSE_DELIMITER.split(tb.text)
            for possible_clause in possible_clause_arr[:-1]:
                has_clause = self.is_clause_accepted(possible_clause)
                if has_clause:
                    break
            
            # since clauses should *always end* with a delimiter, we normally don't consider text without one
            if self.accept_clauses_without_delimiter:
                has_clause |= self.is_clause_accepted(possible_clause_arr[-1])
            if not has_clause:
                tb.set_is_content(False)
                changes = True
        return changes
    
    def is_clause_accepted(self, text: str):
        n = 1
        for _ in self.PAT_WHITESPACE.finditer(text):
            n += 1
            if n >= self.min_words:
                return True
        return n >= self.min_words


class SplitParagraphBlocksFilter(BoilerpipeFilter):
    """
    Splits TextBlocks at paragraph boundaries.

    NOTE: This is not fully supported (i.e., it will break highlighting support via #getContainedTextElements()), but
    this one probably is necessary for some other filters.

    See MinClauseWordsFilter
    """
    
    NEWLINE_REGEX = re.compile(r"[\n\r]+")
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        blocks = doc.text_blocks
        blocks_new = []
        for tb in blocks:
            text = tb.text
            paragraphs = self.NEWLINE_REGEX.split(text)
            if len(paragraphs) < 2:
                blocks_new.append(tb)
                continue
            is_content = tb.is_content
            labels = tb.labels
            for p in paragraphs:
                tb_p = TextBlock(p)
                tb_p.set_is_content(is_content)
                tb_p.add_labels(labels)
                blocks_new.append(tb_p)
                changes = True
        
        if changes:
            doc.text_blocks = blocks_new
        return changes


class SurroundingToContentFilter(BoilerpipeFilter):
    def __init__(self, condition: callable = lambda tb: tb.linkDensity == 0 and tb.num_words > 6) -> None:
        """
        this is now default when no arguments are passed
        
        INSTANCE_TEXT = SurroundingToContentFilter(TextBlockCondition())
        
        ctor - condition is an function for an additional condition to determine if it can be made content
        """
        
        super(SurroundingToContentFilter, self).__init__()
        self.cond = condition
    
    def process(self, doc: TextDocument) -> bool:
        tbs = doc.text_blocks
        n = len(tbs)
        has_changes = False
        i = 1
        while i < n - 1:
            prev_block = tbs[i - 1]
            cur_block = tbs[i]
            next_block = tbs[i + 1]
            if not cur_block.is_content and prev_block.is_content and next_block.is_content and self.cond(cur_block):
                cur_block.set_is_content(True)
                has_changes = True
                i += 2
            else:
                # WARNING: POSSIBLE BUG - in original i+=2 regardless of whether content is found. this seems illogical
                # to me - should be +=1
                i += 1
        
        return has_changes


class LabelToBoilerplateFilter(BoilerpipeFilter):
    """
    Marks all blocks that contain a given label as "boilerplate".
    
    INSTANCE_STRICTLY_NOT_CONTENT = LabelToBoilerplateFilter(DefaultLabels.STRICTLY_NOT_CONTENT)
    """
    
    def __init__(self, *labels: str) -> None:
        super(LabelToBoilerplateFilter, self).__init__()
        self.labels = labels
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if tb.is_content and any(tb.has_label(label) for label in self.labels):
                tb.set_is_content(False)
                changes = True
        return changes


class LabelToContentFilter(BoilerpipeFilter):
    """
    Marks all blocks that contain a given label as "content".
    """
    
    def __init__(self, *labels: str) -> None:
        super(LabelToContentFilter, self).__init__()
        self.labels = labels
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if not tb.is_content and any(tb.has_label(label) for label in self.labels):
                tb.set_is_content(True)
                changes = True
        return changes


# -----------------------------------------------------------------------
#                       GENERIC HEURISTIC FILTERS
# -----------------------------------------------------------------------


class SimpleBlockFusionProcessor(BoilerpipeFilter):
    """
    Merges two subsequent blocks if their text densities are equal.
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        changes = False
        if len(text_blocks) < 2:
            return False
        prev_block = text_blocks[0]
        blocks_to_remove = []
        for block in text_blocks[1:]:
            if prev_block.text_density == block.text_density:
                prev_block.merge_next(block)
                blocks_to_remove.append(block)
                changes = True
            else:
                prev_block = block
        
        if changes:
            doc.text_blocks = self.subtract_blocks(text_blocks, blocks_to_remove)
        
        return changes


class ContentFusion(BoilerpipeFilter):
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        # WARNING: POSSIBLE BUG FOUND: shouldn't prev_block be reset every passthrough?
        changes = False
        # if it has been changed on the previous passthrough
        changed_on_pass = True
        while changed_on_pass:
            changed_on_pass = False
            prev_block = text_blocks[0]
            blocks_to_remove = []
            for block in text_blocks[1:]:
                if prev_block.is_content and block.link_density < 0.56 \
                        and not block.has_label(DefaultLabels.STRICTLY_NOT_CONTENT):
                    prev_block.merge_next(block)
                    blocks_to_remove.append(block)
                    changed_on_pass = True
                    changes = True
                else:
                    prev_block = block
                text_blocks = self.subtract_blocks(text_blocks, blocks_to_remove)
        if changes:
            doc.text_blocks = text_blocks
        
        return changes


class LabelFusion(BoilerpipeFilter):
    """
    Fuses adjacent blocks if their labels are equal.
    """
    
    def __init__(self, label_prefix: str = "") -> None:
        """
        Creates a new LabelFusion instance.
        
        :param label_prefix: The maximum distance in blocks.
        """
        
        super(LabelFusion, self).__init__()
        self.label_prefix = label_prefix
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        changes = False
        prev_block = text_blocks[0]
        blocks_to_remove = []
        for block in text_blocks[1::]:
            if self.equal_labels(prev_block.labels, block.labels):
                prev_block.merge_next(block)
                blocks_to_remove.append(block)
                changes = True
            else:
                prev_block = block
        
        if changes:
            doc.text_blocks = self.subtract_blocks(text_blocks, blocks_to_remove)
        
        return changes
    
    def equal_labels(self, labels1: List[str], labels2: List[str]) -> bool:
        if labels1 is None or labels2 is None:
            return False
        
        # NOTE: Should blocks be merged if neither of them have labels???  i.e. labels1==labels2==empty set
        return self.markup_labels_only(labels1) == self.markup_labels_only(labels2)
    
    def markup_labels_only(self, labels: List[str]) -> set:
        return {label for label in labels if label.startswith(DefaultLabels.MARKUP_PREFIX)}


class BlockProximityFusion(BoilerpipeFilter):
    """
    Fuses adjacent blocks if their distance (in blocks) does not exceed a certain limit. This probably makes sense only
    in cases where an upstream filter already has removed some blocks.
    
    MAX_DISTANCE_1 = BlockProximityFusion(1, False, False)
    MAX_DISTANCE_1_SAME_TAGLEVEL = BlockProximityFusion(1, False, True)
    MAX_DISTANCE_1_CONTENT_ONLY = BlockProximityFusion(1, True, False)
    MAX_DISTANCE_1_CONTENT_ONLY_SAME_TAGLEVEL = BlockProximityFusion(1, True, True)
    """
    
    def __init__(self, max_blocks_distance: int = 1, content_only: bool = False,
                 same_tag_level_only: bool = False) -> None:
        """
        Creates a new BlockProximityFusion instance.
        
        :param max_blocks_distance: The maximum distance in blocks.
        :param content_only:
        :param same_tag_level_only:
        """
        
        super(BlockProximityFusion, self).__init__()
        self.max_blocks_distance = max_blocks_distance
        self.content_only = content_only
        self.same_tag_level_only = same_tag_level_only
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        changes = False
        
        if self.content_only:
            start_idx = None
            for idx, block in enumerate(text_blocks):
                if block.is_content:
                    start_idx = idx
                    break
            if start_idx is None:
                return False
        else:
            start_idx = 0
        
        prev_block = text_blocks[start_idx]
        blocks_to_remove = []
        for block in text_blocks[start_idx + 1:]:
            if not block.is_content:
                prev_block = block
                continue
            diff_blocks = block.offset_blocks_start - prev_block.offset_blocks_end - 1
            if diff_blocks <= self.max_blocks_distance:
                ok = True
                if self.content_only:
                    if not prev_block.is_content or not block.is_content:
                        ok = False
                if self.same_tag_level_only and prev_block.tag_level != block.tag_level:
                    ok = False
                if ok:
                    prev_block.merge_next(block)
                    # remove current block
                    blocks_to_remove.append(block)
                    changes = True
                else:
                    prev_block = block
            else:
                prev_block = block
        
        if len(blocks_to_remove) > 0:
            doc.text_blocks = self.subtract_blocks(text_blocks, blocks_to_remove)
            changes = True
        
        return changes


class KeepLargestBlockFilter(BoilerpipeFilter):
    """
    Keeps the largest TextBlock only (by the number of words). In case of more than one block with the same
    number of words, the first block is chosen. All discarded blocks are marked "not content" and flagged as
    DefaultLabels.

    Note that, by default, only TextBlocks marked as "content" are taken into consideration.
    
    INSTANCE = KeepLargestBlockFilter(False)
    INSTANCE_EXPAND_TO_SAME_TAGLEVEL = KeepLargestBlockFilter(True)
    """
    
    def __init__(self, expand_to_same_level_text: bool = False) -> None:
        super(KeepLargestBlockFilter, self).__init__()
        self.expand_to_same_level_text = expand_to_same_level_text
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        
        try:
            largest_block = max((tb for tb in text_blocks if tb.is_content), key=lambda tb: tb.num_words)
        except ValueError:
            # no content blocks exist / largest block not found
            largest_block = None
        
        for tb in text_blocks:
            if tb == largest_block:
                tb.set_is_content(True)
            else:
                tb.set_is_content(False)
                tb.add_label(DefaultLabels.MIGHT_BE_CONTENT)
        
        if self.expand_to_same_level_text and largest_block is not None:
            level = largest_block.tag_level
            largest_block_idx = text_blocks.index(largest_block)
            
            for tb in text_blocks[largest_block_idx::-1]:
                tl = tb.tag_level
                if tl < level:
                    break
                elif tl == level:
                    tb.set_is_content(True)
            
            for tb in text_blocks[largest_block_idx:]:
                tl = tb.tag_level
                if tl < level:
                    break
                elif tl == level:
                    tb.set_is_content(True)
        
        return True


class ExpandTitleToContentFilter(BoilerpipeFilter):
    """
    Marks all TextBlocks "content" which are between the headline and the part that has already been marked
    content, if they are marked DefaultLabels#MIGHT_BE_CONTENT.
    
    This filter is quite specific to the news domain.
    """
    
    def process(self, doc: TextDocument) -> bool:
        i = 0
        title_idx = -1
        content_start = -1
        for tb in doc.text_blocks:
            if content_start == -1 and tb.has_label(DefaultLabels.TITLE):
                title_idx = i
            if content_start == -1 and tb.is_content:
                content_start = i
            i += 1
        
        if content_start <= title_idx or title_idx == -1:
            return False
        
        changes = False
        for tb in doc.text_blocks[title_idx:content_start]:
            if tb.has_label(DefaultLabels.MIGHT_BE_CONTENT):
                changes |= tb.set_is_content(True)
        return changes


class ArticleMetadataFilter(BoilerpipeFilter):
    # checks for date/time/author blocks
    PATTERNS_SHORT = [
        re.compile(r"^[0-9 ,./]*\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|"
                   r"July|August|September|October|November|December)?\b[0-9 ,:apm./]*(?:[CPSDMGET]{2,3})?$"),
        re.compile("^[Bb]y ")
    ]
    
    def process(self, doc: TextDocument) -> bool:
        changed = False
        for tb in doc.text_blocks:
            if tb.num_words > 10:
                continue
            for p in self.PATTERNS_SHORT:
                text = tb.text
                if p.search(text):
                    changed = True
                    tb.set_is_content(True)
                    tb.add_label(DefaultLabels.ARTICLE_METADATA)
                    break
        return changed


class AddPrecedingLabelsFilter(BoilerpipeFilter):
    """
    Adds the labels of the preceding block to the current block, optionally adding a prefix.
    """
    
    def __init__(self, label_prefix: str = "") -> None:
        """
        Creates a new AddPrecedingLabelsFilter instance.
        
        INSTANCE = AddPrecedingLabelsFilter("")
        INSTANCE_PRE = AddPrecedingLabelsFilter("^")
        """
        
        super(AddPrecedingLabelsFilter, self).__init__()
        self.label_prefix = label_prefix
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        changes = False
        block_below = None
        
        for block in text_blocks[::-1]:
            if block_below is not None:
                labels = block.labels
                if labels is not None and len(labels) > 0:
                    for l in labels:
                        block_below.add_label(self.label_prefix + l)
                    changes = True
            block_below = block
        
        return changes


class DocumentTitleMatchClassifier(BoilerpipeFilter):
    """
    Marks TextBlocks which contain parts of the HTML <code>&lt;TITLE&gt;</code> tag, using some heuristics which
    are quite specific to the news domain.
    """
    
    TITLE_REGEXES = [
        re.compile(r"[ ]*[|:][ ]*"),
        re.compile(r"[ ]*[|:()][ ]*"),
        re.compile(r"[ ]*[|:()\-][ ]*"),
        re.compile(r"[ ]*[|,:()\-][ ]*")
    ]
    WORD_REGEX = re.compile(r"\w+", re.UNICODE)
    
    def __init__(self, title: Union[str, None], use_doc_title: bool = False) -> None:
        super(DocumentTitleMatchClassifier, self).__init__()
        self.use_doc_title = use_doc_title
        if use_doc_title:
            self.potential_titles = None
        else:
            self.potential_titles = self.find_potential_titles(title)
    
    def find_potential_titles(self, title: str):
        if title is None:
            return None
        title = title.strip()
        if len(title) == 0:
            return None
        else:
            potential_titles = set()
            potential_titles.add(title)
            for regex in self.TITLE_REGEXES:
                p = self.get_longest_part(title, regex)
                if p is not None:
                    potential_titles.add(p)
        return potential_titles
    
    def get_longest_part(self, title: str, pattern: Pattern):
        parts = pattern.split(title)
        if len(parts) == 1:
            return None
        
        longest_num_words = 0
        longest_part = ""
        for p in parts:
            if ".com" in p:
                continue
            num_words = self.get_num_words(p)
            if num_words > longest_num_words or len(p) > len(longest_part):
                longest_num_words = num_words
                longest_part = p
        if len(longest_part) == 0:
            return None
        else:
            return longest_part.strip()
    
    def get_num_words(self, text: str):
        return len(self.WORD_REGEX.findall(text))
    
    def process(self, doc: TextDocument) -> bool:
        if self.use_doc_title:
            self.potential_titles = self.find_potential_titles(doc.title)
        if self.potential_titles is None:
            return False
        changes = False
        for tb in doc.text_blocks:
            text = tb.text.strip().lower()
            if any(candidate.lower() == text for candidate in self.potential_titles):
                tb.add_label(DefaultLabels.TITLE)
                changes = True
        return changes


# -----------------------------------------------------------------------
#                          ENGLISH HEURISTIC FILTERS
# -----------------------------------------------------------------------
# --- Heuristic Filters that have been trained on English laguage text


class HeuristicFilterBase(BoilerpipeFilter):
    """
    Base class for some heuristics that are used by boilerpipe filters.
    """
    
    def get_num_full_text_words(self, tb: TextBlock, min_text_density: int = 9):
        if tb.text_density >= min_text_density:
            return tb.num_words
        else:
            return 0


class MinFulltextWordsFilter(HeuristicFilterBase):
    """
    Keeps only those content blocks which contain at least k full-text words (measured by
    HeuristicFilterBase#get_num_full_text_words(TextBlock). k is 30 by default.
    """
    
    def __init__(self, min_words: int = 30) -> None:
        self.min_words = min_words
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        for tb in doc.text_blocks:
            if tb.is_content and self.get_num_full_text_words(tb) < self.min_words:
                tb.set_is_content(False)
                changes = True
        return changes


class KeepLargestFulltextBlockFilter(HeuristicFilterBase):
    """
    Keeps the largest TextBlock only (by the number of words). In case of more than one block with the same
    number of words, the first block is chosen. All discarded blocks are marked "not content" and flagged as
    DefaultLabels. As opposed to KeepLargestBlockFilter, the number of words are computed using HeuristicFilterBase
    get_num_full_text_words(TextBlock), which only counts words that occur in text elements with at least 9 words and
    are thus believed to be full text.

    NOTE: Without language-specific fine-tuning (i.e., running the default instance), this filter may lead to suboptimal
    results. You better use KeepLargestBlockFilter instead, which works at the level of number-of-words instead
    of text densities.
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        if len(text_blocks) < 2:
            return False
        content_blocks = [block for block in text_blocks if block.is_content]
        if len(content_blocks) == 0:
            return False
        largest_block = max(content_blocks, key=self.get_num_full_text_words)
        
        for tb in text_blocks:
            if tb == largest_block:
                tb.set_is_content(True)
            else:
                tb.set_is_content(False)
                tb.add_label(DefaultLabels.MIGHT_BE_CONTENT)
        return True


class IgnoreBlocksAfterContentFilter(HeuristicFilterBase):
    """
    Marks all blocks as "non-content" that occur after blocks that have been marked DefaultLabels#INDICATES_END_OF_TEXT.
    These marks are ignored unless a minimum number of words in content blocks occur before this mark (default: 60).
    This can be used in conjunction with an upstream TerminatingBlocksFinder.
    """
    
    def __init__(self, min_num_words: int = 60) -> None:
        """
        DEFAULT_INSTANCE = IgnoreBlocksAfterContentFilter(60)
        INSTANCE_200 = IgnoreBlocksAfterContentFilter(200)
        """
        
        self.min_num_words = min_num_words
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        num_words = 0
        found_end_of_text = False
        for block in doc.text_blocks:
            if block.is_content:
                num_words += self.get_num_full_text_words(block)
            if block.has_label(DefaultLabels.INDICATES_END_OF_TEXT) and num_words >= self.min_num_words:
                found_end_of_text = True
            if found_end_of_text:
                changes = True
                block.set_is_content(False)
        
        return changes


class IgnoreBlocksAfterContentFromEndFilter(HeuristicFilterBase):
    """
    Marks all blocks as "non-content" that occur after blocks that have been marked DefaultLabels#INDICATES_END_OF_TEXT,
    and after any content block. This filter can be used in conjunction with an upstream TerminatingBlocksFinder.
    
    See TerminatingBlocksFinder
    """
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        words = 0
        blocks = doc.text_blocks
        if len(blocks) == 0:
            return False
        for tb in blocks[::-1]:
            if tb.has_label(DefaultLabels.INDICATES_END_OF_TEXT):
                tb.add_label(DefaultLabels.STRICTLY_NOT_CONTENT)
                tb.remove_label(DefaultLabels.MIGHT_BE_CONTENT)
                tb.set_is_content(False)
                changes = True
            elif tb.is_content:
                words += tb.num_words
                if words > 200:
                    break
        return changes


class TerminatingBlocksFinder(BoilerpipeFilter):
    """
    Finds blocks which are potentially indicating the end of an article text and marks them with
    DefaultLabels#INDICATES_END_OF_TEXT. This can be used in conjunction with a downstream
    IgnoreBlocksAfterContentFilter.
    """
    
    DIGIT_REGEX = re.compile(r'\D')
    
    def process(self, doc: TextDocument) -> bool:
        changes = False
        
        for tb in doc.text_blocks:
            if tb.num_words >= 15:
                continue
            text = tb.text.strip()
            if len(text) < 8:
                continue
            text_lc = text.lower()
            
            startmatches = (" reuters", "please rate this", "post a comment")
            inmatches = ("what you think...", "add your comment", "add comment", "reader views", "have your say",
                         "reader comments", "rtta artikeln")
            eqmatch = "thanks for your comments - this feedback is now closed"
            
            if text_lc.startswith("comments") or self.starts_with_number(text_lc, " comments", " users responded in") \
                    or any(text_lc.startswith(match_str) for match_str in startmatches) \
                    or any(match_str in text_lc for match_str in inmatches) or text_lc == eqmatch:
                tb.add_label(DefaultLabels.INDICATES_END_OF_TEXT)
                changes = True
        
        return changes
    
    def starts_with_number(self, text: str, *match_str_arr: str):
        """
        Checks whether the given text t starts with a sequence of digits, followed by one of the given strings.
        
        :param text: The text to examine
        :param match_str_arr: Any strings that may follow the digits.
        :return: true if at least one combination matches
        """
        
        number_match = self.DIGIT_REGEX.search(text)
        if number_match is None:
            pos = len(text)
        else:
            pos = number_match.start()
        if pos == 0:
            return False
        else:
            return any(text.startswith(match_str, pos) for match_str in match_str_arr)


class NumWordsRulesClassifier(BoilerpipeFilter):
    """
    Classifies TextBlocks as content/not-content through rules that have been determined using the C4.8 machine
    learning algorithm, as described in the paper "Boilerplate Detection using Shallow Text Features" (WSDM 2010),
    particularly using number of words per block and link density per block.
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        has_changes = False
        
        n = len(text_blocks)
        for i, currentBlock in enumerate(text_blocks):
            if i > 0:
                prev_block = text_blocks[i - 1]
            else:
                prev_block = TextBlock.EMPTY_START
            if i + 1 < n:
                next_block = text_blocks[i + 1]
            else:
                next_block = TextBlock.EMPTY_START
            has_changes |= self.classify(prev_block, currentBlock, next_block)
        return has_changes
    
    def classify(self, prev_block: TextBlock, curr_block: TextBlock, next_block: TextBlock):
        if curr_block.link_density <= 0.333333:
            if prev_block.link_density <= 0.555556:
                if curr_block.num_words <= 16:
                    if next_block.num_words <= 15:
                        if prev_block.num_words <= 4:
                            is_content = False
                        else:
                            is_content = True
                    else:
                        is_content = True
                else:
                    is_content = True
            else:
                if curr_block.num_words <= 40:
                    if next_block.num_words <= 17:
                        is_content = False
                    else:
                        is_content = True
                else:
                    is_content = True
        else:
            is_content = False
        
        return curr_block.set_is_content(is_content)


class DensityRulesClassifier(BoilerpipeFilter):
    """
    Classifies TextBlocks as content/not-content through rules that have been determined using the C4.8 machine learning
    algorithm, as described in the paper "Boilerplate Detection using Shallow Text Features", particularly using text
    densities and link densities.
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        has_changes = False
        
        n = len(text_blocks)
        for i, current_block in enumerate(text_blocks):
            if i > 0:
                prev_block = text_blocks[i - 1]
            else:
                prev_block = TextBlock.EMPTY_START
            if i + 1 < n:
                next_block = text_blocks[i + 1]
            else:
                next_block = TextBlock.EMPTY_START
            has_changes |= self.classify(prev_block, current_block, next_block)
        return has_changes
    
    def classify(self, prev_block: TextBlock, curr_block: TextBlock, next_block: TextBlock):
        if curr_block.link_density <= 0.333333:
            if prev_block.link_density <= 0.555556:
                if curr_block.text_density <= 9:
                    if next_block.text_density <= 10:
                        if prev_block.text_density <= 4:
                            is_content = False
                        else:
                            is_content = True
                    else:
                        is_content = True
                else:
                    if next_block.text_density == 0:
                        is_content = False
                    else:
                        is_content = True
            else:
                if next_block.text_density <= 11:
                    is_content = False
                else:
                    is_content = True
        else:
            is_content = False
        
        return curr_block.set_is_content(is_content)


class CanolaFilter(BoilerpipeFilter):
    """
    A full-text extractor trained on http://krdwrd.org/,
    https://krdwrd.org/trac/attachment/wiki/Corpora/Canola/CANOLA.pdf. Works well with SimpleEstimator, too.
    """
    
    def process(self, doc: TextDocument) -> bool:
        text_blocks = doc.text_blocks
        has_changes = False
        
        n = len(text_blocks)
        for i, current_block in enumerate(text_blocks):
            if i > 0:
                prev_block = text_blocks[i - 1]
            else:
                prev_block = TextBlock.EMPTY_START
            if i + 1 < n:
                next_block = text_blocks[i + 1]
            else:
                next_block = TextBlock.EMPTY_START
            has_changes |= self.classify(prev_block, current_block, next_block)
        return has_changes
    
    def classify(self, prev_block: TextBlock, curr_block: TextBlock, next_block: TextBlock):
        cond1 = curr_block.link_density > 0 and next_block.num_words > 11
        cond2 = curr_block.num_words > 19
        cond3 = next_block.num_words > 6 and next_block.link_density == 0 and prev_block.link_density == 0 and \
                (curr_block.num_words > 6 or prev_block.num_words > 7 or next_block.num_words > 19)
        is_content = cond1 or cond2 or cond3
        
        return curr_block.set_is_content(is_content)
