import logging

from . import ContentGeneratorExtension
from .. import MetaProcessor, PageGenerator
from .. import ContentPage, ContentListingPage
from ..util import rfc2822_now


log = logging.getLogger('flask_flatearth.ext.topics')


class TopicPage(ContentPage):
    """
    Topic Page
    """
    CONTENT_TYPE = "topic"
    TEMPLATE = "topic.html"
    RULES = ['/topics/{slug}/', ]
    pass


class TopicListingPage(ContentListingPage):
    """
    Topic Listing Page
    """
    CONTENT_TYPE = "topic"
    SLUG = "topics"
    TEMPLATE = "topics.html"
    RULES = ['/topics/', ]
    pass


class TopicMetaProcessor(MetaProcessor):
    """
    Topic MetaProcessor
    """
    def _process(self, data):
        full = ",".join(data)
        result = set([t.strip() for t in full.split(',')])
        for r in result:
            if r.lower() in [n.lower() for n in result if r is not n]:
                msg = "Possible duplicate topic case '{topic}' in " \
                      "set {topics}".format(topic=r, topics=result)
                log.warn(msg)
        msg = "MetaProcessor {mp} processed data '{d}' resulting in " \
              "{r}".format(mp=self,
                           d=data,
                           r=result)
        log.debug(msg)
        return result


class TopicPageGenerator(PageGenerator):
    """
    Topic PageGenerator
    """
    PAGE_CLS = TopicPage


class TopicPageListingGenerator(PageGenerator):
    """
    Topic Listing PageGenerator
    """
    PAGE_CLS = TopicListingPage


class TopicExtension(ContentGeneratorExtension):
    """
    Provides topic functionality for pages
    """
    EXTENSION_NAME = "topic_extension"

    def _setup(self):
        self.topics = {}
        self.publish = rfc2822_now()

    def _register(self):
        mp = TopicMetaProcessor(self.g,
                                ext=self)
        self.g.add_meta_processor("topics", mp)
        self.generators.update({
            'topic':
            TopicPageGenerator(self.g,
                               ext=self)})
        self.set_generators.update({
            'topics':
            TopicPageListingGenerator(self.g,
                                      ext=self)})

    def _process_page(self, meta, html, file_name):
        for topic in meta.get('topics', []):
            msg = "Extension {e} processing topic {t}".format(e=self, t=topic)
            log.debug(msg)
            if topic not in self.topics:
                slug = topic.lower().replace(" ", "-")
                m = {'type': 'topic',
                     'slug': slug,
                     'title': topic,
                     'publish': self.publish,
                     'set': 'topics',
                     'meta': meta,
                     'html': html}
                self.topics.update({slug: m})
                msg = "{e} added topic '{t}'".format(e=self, t=topic)
                log.debug(msg)

    def generate_context(self):
        return {'topics': self.topics}

    def _load_pages(self):
        for topic in self.topics:
            refs = [self.g.pages[p] for p in self.g.pages if 'topics' in
                    self.g.pages[p].meta and topic in
                    self.g.pages[p].meta['topics']]
            page = self.generators['topic'](app=self.g.app,
                                            slug=topic,
                                            meta=self.topics[topic]['meta'],
                                            html=self.topics[topic]['html'])
            page[topic].refs = refs
            msg = "{e} adding topic '{t}' with refs {r} for page " \
                  "'{p}'".format(e=self,
                                 t=topic,
                                 r=refs,
                                 p=page)
            log.debug(msg)
            self.pages.update(page)
