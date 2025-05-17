"""
This file is licensed under the terms of the Apache License, Version 2.0. See the LICENSE file in the root of this
repository for complete details.
"""

import http.client
import re
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from logging import getLogger
from typing import Union

from boilerpy3 import filters, parser
from boilerpy3.document import TextDocument
from boilerpy3.exceptions import HTMLExtractionError
from boilerpy3.filters import BoilerpipeFilter
from boilerpy3.marker import HTMLBoilerpipeMarker

logger = getLogger('boilerpy3')


class Extractor:
    """
    The base class of Extractors. Also provides some helper methods to quickly retrieve the text that remained after
    processing.
    """
    
    SCRIPT_REGEX = re.compile(r'<(?:script|SCRIPT)[^>]*>.*?</(?:script|SCRIPT)>', re.DOTALL)
    
    def __init__(self, filtr: BoilerpipeFilter, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param filtr: filter
        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        self.filter = filtr
        self.raise_on_failure = raise_on_failure
        if request_kwargs is None:
            request_kwargs = {}
        self._request_kwargs = request_kwargs
    
    def get_content(self, text: str) -> str:
        return self.get_doc(text).content
    
    def get_content_from_url(self, url: str, request_kwargs: dict = None) -> str:
        return self.get_doc_from_url(url, request_kwargs).content
    
    def get_content_from_file(self, filename: str) -> str:
        return self.get_doc_from_file(filename).content
    
    def get_doc_from_file(self, filename: str) -> TextDocument:
        return self.get_doc(self.read_from_file(filename))
    
    def get_doc_from_url(self, url: str, request_kwargs: dict = None) -> TextDocument:
        return self.get_doc(self.read_from_url(url, request_kwargs))
    
    def get_doc(self, text: str) -> TextDocument:
        doc = self.parse_doc(text)
        self.filter.process(doc)
        return doc
    
    def get_marked_html(self, text: str) -> str:
        doc = self.get_doc(text)
        marker = HTMLBoilerpipeMarker(raise_on_failure=self.raise_on_failure)
        return marker.process(doc, text)
    
    def get_marked_html_from_url(self, url: str) -> str:
        text = self.read_from_url(url)
        return self.get_marked_html(text)
    
    def get_marked_html_from_file(self, filename: str) -> str:
        text = self.read_from_file(filename)
        return self.get_marked_html(text)
    
    def read_from_file(self, filename: str) -> str:
        with open(filename) as text_file:
            return text_file.read()
    
    def read_from_url(self, url: str, request_kwargs: dict = None) -> str:
        all_request_kwargs = deepcopy(self._request_kwargs)
        if request_kwargs is not None:
            all_request_kwargs.update(request_kwargs)
        
        with urllib.request.urlopen(url, **all_request_kwargs) as url_obj:
            text = url_obj.read()
            encoding = self.get_url_encoding(url_obj)
        
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            pass
        return text
    
    def get_url_encoding(self, f: http.client.HTTPResponse) -> str:
        try:
            return f.headers['content-type'].split('charset=')[1].split(';')[0]
        except:
            return 'utf8'
    
    def parse_doc(self, input_str: str) -> Union[TextDocument, None]:
        bp_parser = parser.BoilerpipeHTMLParser(raise_on_failure=self.raise_on_failure)
        try:
            bp_parser.feed(input_str)
        except:
            # in case of error, try again, first removing script tag content
            bp_parser = parser.BoilerpipeHTMLParser(raise_on_failure=self.raise_on_failure)
            input_str = self.SCRIPT_REGEX.sub('<script></script>', input_str)
            try:
                bp_parser.feed(input_str)
            except Exception as ex:
                logger.exception('Error parsing HTML')
                if self.raise_on_failure:
                    raise HTMLExtractionError from ex
                else:
                    return TextDocument([])
        doc = bp_parser.to_text_document()
        return doc


class DefaultExtractor(Extractor):
    """
    Usually worse than ArticleExtractor, but simpler/no heuristics. A quite generic full-text extractor.
    """
    
    _filter_chain = filters.FilterChain([
        filters.SimpleBlockFusionProcessor(),
        filters.BlockProximityFusion(1, False, False),
        filters.DensityRulesClassifier()
    ])
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter_chain, raise_on_failure, request_kwargs)


class ArticleExtractor(Extractor):
    """
    A full-text extractor which is tuned towards news articles. In this scenario it achieves higher accuracy than
    DefaultExtractor. Works very well for most types of Article-like HTML.
    """
    
    _filter_chain = filters.FilterChain([
        filters.TerminatingBlocksFinder(),
        filters.DocumentTitleMatchClassifier(None, True),
        filters.NumWordsRulesClassifier(),
        filters.IgnoreBlocksAfterContentFilter(),
        filters.BlockProximityFusion(1, False, False),
        filters.BoilerplateBlockFilter(),
        filters.BlockProximityFusion(1, True, False),
        filters.KeepLargestBlockFilter(),
        filters.ExpandTitleToContentFilter()
    ])
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter_chain, raise_on_failure, request_kwargs)


class LargestContentExtractor(Extractor):
    """
    A full-text extractor which extracts the largest text component of a page. For news articles, it may perform better
    than the DefaultExtractor, but usually worse than ArticleExtractor. Like DefaultExtractor, but keeps the largest
    text block only.
    """
    
    _filter_chain = filters.FilterChain([
        filters.NumWordsRulesClassifier(),
        filters.BlockProximityFusion(1, False, False),
        filters.KeepLargestBlockFilter()
    ])
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter_chain, raise_on_failure, request_kwargs)


class CanolaExtractor(Extractor):
    """
    Trained on krdwrd Canola (different definition of "boilerplate"). You may give it a try.
    """
    
    _filter = filters.CanolaFilter()
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter, raise_on_failure, request_kwargs)


class KeepEverythingExtractor(Extractor):
    """
    Marks everything as content. Dummy Extractor; should return the input text. Use this to double-check that your
    problem is within a particular BoilerpipeExtractor, or somewhere else.
    """
    
    _filter = filters.MarkEverythingContentFilter()
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter, raise_on_failure, request_kwargs)


class NumWordsRulesExtractor(Extractor):
    """
    A quite generic full-text extractor solely based upon the number of words per block (the current, the previous and
    the next block).
    """
    
    _filter = filters.NumWordsRulesClassifier()
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter, raise_on_failure, request_kwargs)


class ArticleSentencesExtractor(Extractor):
    """
    A full-text extractor which is tuned towards extracting sentences from news articles.
    """
    
    _filter_chain = filters.FilterChain([
        ArticleExtractor._filter_chain,
        filters.SplitParagraphBlocksFilter(),
        filters.MinClauseWordsFilter()
    ])
    
    def __init__(self, raise_on_failure: bool = True, request_kwargs: dict = None) -> None:
        """
        Initialize extractor

        :param raise_on_failure: whether or not to raise an exception if a text extraction failure is encountered.
        :param request_kwargs: kwargs to pass to urllib.request
        """
        
        super().__init__(self._filter_chain, raise_on_failure, request_kwargs)


class KeepEverythingWithMinKWordsFilter(filters.FilterChain):
    """
    A full-text extractor which extracts the largest text component of a page. For news articles, it may perform better
    than the DefaultExtractor, but usually worse than ArticleExtractor.
    """
    
    def __init__(self, k_min: int) -> None:
        # Note: variable was not used initially, seems it should be passed to super() call
        filter_arr = [
            filters.SimpleBlockFusionProcessor(),
            filters.MarkEverythingContentFilter(),
            filters.MinWordsFilter(k_min)
        ]
        super().__init__(filter_arr)
