import logging
import os
import warnings

import flask
import markdown

from .mdurlfor import FlaskUrlForExtension 

from . import AuthorPage, ArticlePage, IndexPage
from . import TopicPage, TopicListingPage, LOGGER_NAME


log = logging.getLogger(LOGGER_NAME)

BASEPATH = os.getcwd()
SEARCHPATH = os.path.abspath(os.path.join(BASEPATH, "pages"))
EXTENSION = '.md'

content = lambda content: (lambda: content)

class MarkdownGenerator(object):
    """
    Markdown content generator

    Takes a Flask app and searches `search_path` for files of `extension` for
    generating `ContentPage`
    """
    def __init__(self, app, search_path=None, extension=None):
        """
        Initialize MarkdownGenerator
        :param app: Flask instance
        :type app: `Flask`
        :param search_path: Search path for pages
        :type search_path: `str`
        :param extension: Pages file extension(s)
        :type extension: `str` or `list`
        """
        self.app = app
        self.path = search_path if search_path else \
            app.config.get('FLATEARTH_SEARCH_PATH', SEARCHPATH)
        self.extension = extension if extension else \
            app.config.get('FLATEARTH_EXTENSION', EXTENSION)
        self.pages = []
        self.articles = {}
        self.topics = {}
        self.authors = {}
        for dirpath, dirnames, files in os.walk(self.path):
            for name in files:
                if name.lower().split('.')[-1] == self.extension \
                or name.lower().split('.')[-1] in self.extension:
                    self.pages += [os.path.join(dirpath, name),]

    def get_article(self, slug):
        """
        Return article
        :param slug: Slug of article
        :type slug: `str`
        :return: `dict` of article content
        """
        return self.articles[slug]

    def get_author(self, slug):
        """
        Return author
        :param slug: Slug of author
        :type slug: `str`
        :return: `dict` of author content
        """
        return self.authors[slug]

    def get_topic(self, topic):
        return self.topics[topic]

    def author_url_generator(self):
        for author in self.authors:
            yield self.authors[author]

    def article_url_generator(self):
        for article in self.articles:
            yield self.articles[article]

    def topic_url_generator(self):
        for topic in self.topics:
            yield self.topics[topic]

    def load_pages(self):
        for page in self.pages:
            with open(page, 'r') as page_file:
                md = markdown.Markdown(
                    extensions=['markdown.extensions.meta', FlaskUrlForExtension()],
                    output_format='html5'
                )
                html = md.convert(
                    page_file.read()
                )
                meta = {k: md.Meta[k][0].split(',') if k == 'topics' \
                    else md.Meta[k][0] if len(md.Meta[k]) == 1 \
                        and k != 'author' \
                    else md.Meta[k] for k in md.Meta}
                if meta['type'] == 'article':
                    if meta['slug'] in self.articles:
                        msg = "article slug {} already added to articles".format(meta['slug'])
                        raise KeyError(msg)
                    else:
                        self.articles[meta['slug']] = ArticlePage(
                                self.app,
                                meta['slug'],
                                meta=meta,
                                html=html,
                                file_name=page
                        )
                    for topic in meta.get('topics', []):
                        topic_slug = "{}".format(topic).replace(" ", "-")
                        if not self.topics.get(topic):
                            self.topics[topic] = TopicPage(
                                self.app,
                                topic_slug,
                                meta=meta
                            )
                        if meta['slug'] not in self.topics[topic].refs:
                            self.topics[topic].refs += [self.articles[meta['slug']],]
                        else:
                            msg = "article slug '{}' already added to topic".format(slug)
                            raise KeyError(msg)
                if meta['type'] == 'author':
                    if meta['slug'] in self.authors:
                        msg = "author slug {} already added to articles".format(slug)
                        raise KeyError(msg)
                    else:
                        self.authors[meta['slug']] = AuthorPage(
                            self.app,
                            meta['slug'],
                            meta=meta,
                            html=html,
                            file_name=page
                        )
                if meta['type'] == 'index':
                    self.articles[meta['slug']] = IndexPage(
                            self.app,
                            meta['slug'],
                            meta=meta,
                            html=html,
                            file_name=page
                    )
        for article in self.articles:
            if self.articles[article].meta.get('author'):
                for author in self.articles[article].meta['author']:
                    if author in self.authors:
                        self.authors[author].refs += [self.articles[article],]
                    else:
                        msg = "No existing author {author} for {article}".format(
                            author=author,
                            article=article
                        )
                        warnings.warn(msg)

    def generate(self):
        self.load_pages()
        runthru = {**self.authors, **self.articles, **self.topics}
        runthru.update(topics=TopicListingPage(self.app, 'topics'))
        for p in runthru:
            runthru[p].register_rules()
        for p in runthru:
            runthru[p].register_view(
                page_content=runthru[p].html,
                authors=self.authors,
                topics=self.topics,
                meta=runthru[p].meta,
                refs=runthru[p].refs
            )
