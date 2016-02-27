from goose import Goose, Configuration
from myStemmer import pstem as stem
import lxml
import re

class Html_parser(object):
    """
    use goose to parse raw html and
    """
    def __init__(self,need_stem):
        #set up goose
        config = Configuration()
        config.enable_image_fetching = False
        self._g = Goose(config)
        self._need_stem = need_stem

    def get_text(self,file_path):
        raw_html = ""
        with open(file_path) as f:
            raw_html = f.read()

        if not raw_html:
            return None
        try:
            article = self._g.extract(raw_html = raw_html)
        except lxml.etree.ParserError as e:
            return None

        text = article.title + "\n" + article.cleaned_text 
        if self._need_stem:
            words = re.findall("\w+",text,re.MULTILINE)
            w = map(stem,words)
            text = " ".join(w)
        return text
