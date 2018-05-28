import logging
import re

from markdown import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree


log = logging.getLogger('flask_flatearth')

class FlaskUrlForExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.md = md
        log.info("")
        URLFOR_RE = r'(\[([^\[\]]+)\])?\{\{([\w_-]+)\}\}'
        urlforPattern = FlaskUrlForInlineProcessor(URLFOR_RE, self.getConfigs())
        urlforPattern.md = md
        md.inlinePatterns.add('urlfor', urlforPattern, "<not_strong")


class FlaskUrlForInlineProcessor(Pattern):
    def __init__(self, pattern, config):
        super(FlaskUrlForInlineProcessor, self).__init__(pattern)

    def handleMatch(self, m):
        if m.group(1).strip():
            log.debug("handleMatch: {groups} in {filename}".format(
                groups=m.groups(),
                filename=__name__)
            )
            slug = m.group(4).strip()
            url = "{{url_for('" + slug + "')}}"
            text = m.group(3).strip() if m.group(3) else url
            a = etree.Element('a')
            a.text = text
            a.set('href', url)
        else:
            a = ''
        return a


def makeExtension(**kwargs):  # pragma: no cover
    return FlaskUrlForExtension(**kwargs)
    log.debug("Making extension: {file}".format(__name__))
