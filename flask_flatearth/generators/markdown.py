import logging

from markdown import Extension
from markdown import Markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree

from . import BasicContentGenerator


log = logging.getLogger('flask_flatearth.generators.markdown')


class UrlForExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.md = md
        log.info("Registering Markdown Extension: "
                 "{cls}".format(cls=self.__class__.__name__))
        URLFOR_RE = r'(\[([^\[\]]+)\])?\{\{([\w_-]+)\}\}'
        urlforPattern = UrlForInlineProcessor(URLFOR_RE,
                                              self.getConfigs())
        urlforPattern.md = md
        md.inlinePatterns.add('urlfor', urlforPattern, "<not_strong")


class UrlForInlineProcessor(Pattern):
    def __init__(self, pattern, config):
        super(UrlForInlineProcessor, self).__init__(pattern)

    def handleMatch(self, m):
        if m.group(1).strip():
            log.debug("handleMatch: {groups} in "
                      "{filename}".format(groups=m.groups(),
                                          filename=__name__))
            slug = m.group(4).strip()
            url = "{{url_for('" + slug + "')}}"
            text = m.group(3).strip() if m.group(3) else url
            a = etree.Element('a')
            a.text = text
            a.set('href', url)
        else:
            a = ''
        return a


class MarkdownGenerator(BasicContentGenerator):
    """
    Markdown content generator
    """

    def load_pages(self):
        for page in self.page_files:
            msg = "Opening page {pg} for Markdown processing" \
                  ".".format(pg=page)
            log.debug(msg)
            with open(page, 'r') as page_file:
                md = Markdown(
                    extensions=['markdown.extensions.meta',
                                UrlForExtension()],
                    output_format='html5'
                )
                html = md.convert(
                    page_file.read()
                )
                msg = "Generated html {h} for {p}".format(h=html, p=page_file)
                log.debug(msg)
                meta = self._process_meta(md.Meta)
                if meta['type'] in self.generators:
                    if meta['slug'] in self.pages:
                        msg = "page slug {} already added to " \
                              "pages".format(meta['slug'])
                        raise KeyError(msg)
                    else:
                        self._process_page(meta=meta,
                                           html=html,
                                           file_name=page)
                        self.pages.update(self.generators[meta['type']](
                                app=self.app,
                                slug=meta['slug'],
                                meta=meta,
                                html=html,
                                file_name=page
                        ))
        msg = "Generated pages {p}".format(p=self.pages)
        log.debug(msg)
        for article in self.pages:
            msg = "Evaluating {p}".format(p=self.pages[article])
            log.debug(msg)
            if 'author' in self.pages[article].meta:
                for author in self.pages[article].meta['author']:
                    msg = "Searching for existing author '{a}' " \
                          "page".format(a=author)
                    log.debug(msg)
                    if author in self.pages:
                        self.pages[author].refs \
                            += [self.pages[article], ]
                    else:
                        msg = "No existing author {author} for " \
                              "{article}".format(author=author,
                                                 article=article)
                        log.warn(msg)
