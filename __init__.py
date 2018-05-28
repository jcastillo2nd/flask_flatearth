import logging

import flask

try:
    from ..config import DefaultConfig
    LOGGER_NAME = DefaultConfig.LOGGER_NAME
except:
    LOGGER_NAME = __name__

log = logging.getLogger(LOGGER_NAME)

class ContentPage(object):
    """
    Content page interface object
    """
    CONTENT_TYPE = "page"
    TEMPLATE     = "base.html"
    RULES        = ['/',]
    def __init__(self, app, slug, meta=None, rules=None, content_type=None, template=None, html=None, file_name=None):
        """
        Initialize the ContentPage
        :param app: Flask app
        :type app: `flask.Flask`
        :param slug: Slug of page
        :type slug: `str`
        :param rules: Endpoint rules for page
        :type rules: `list` of `str`
        :param content_type: Type of content
        :type content_type: `str`
        :param template: Flask template name
        :type template: `str`
        """
        self.app = app
        if slug is None:
            msg = "Slug cannot be empty or None for {cls}".format(
                cls=self.__class__.__name__
            )
            raise RuntimeError(msg)
        self.slug = slug
        self.meta = meta
        if rules is None:
            self.rules = self.__class__.RULES
        else:
            if isinstance(rules, str):
                msg = "Rule not single item list for {}.".format(self.slug)
                msg += "Use rules=[rule,] to avoid this warning."
                log.warn(msg)
                self.rules = [rules,]
            else:
                self.rules = rules
        self.content_type = content_type if content_type \
            else self.__class__.CONTENT_TYPE
        self.template = template if template \
            else self.__class__.TEMPLATE
        self.html = html
        self.file_name = file_name
        self.rules_set = False
        self.views_set = False
        self.refs = []

    def page_content(self, **kwargs):
        """
        Generate the page_content values
        :param kwargs: Parameters passed to request
        :return: `dict` of parameters
        """
        return kwargs

    def register_rules(self, **kwargs):
        """
        Add rules to app

        Used to ensure that endpoints are registered. This is called prior to
        `register_view()`.
        :param kwargs: Keyword args to be passed to `rule.format(**kwargs)`
        """
        for rule in self.rules:
            r = rule.format(slug=self.slug, **kwargs)
            self.app.add_url_rule(r, endpoint=self.slug)
        self.rules_set = True
        return self

    def register_view(self, **kwargs):
        """
        Set view functions
        :param kwargs: Parameters to be passed into view generation
        """
        if not self.rules_set:
            msg = "Attempting to register view function before calling " \
                  "register_rules() for {}".format(self.slug)
            raise RuntimeError(msg)
        params = self.page_content(**kwargs)
        with self.app.app_context():
            content = flask.render_template(self.template, **params)
        view_fn = lambda c: (lambda: c)
        self.app.view_functions[self.slug] = view_fn(content)
        self.views_set = True
        return self

    def __repr__(self):
        msg = "{cls}({app}, '{slug}', content_type='{content}')".format(
            cls=self.__class__.__name__,
            app=self.app,
            slug=self.slug,
            content=self.content_type
        )
        return msg

    def __str__(self):
        msg = "<{cls} slug={slug}>".format(
            cls=self.__class__.__name__,
            slug=self.slug
        )
        return msg

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self.slug)


class AuthorPage(ContentPage):
    """
    Author Page
    """
    CONTENT_TYPE = "author"
    TEMPLATE     = "author.html"
    RULES        = ['/authors/{slug}/',]
    pass


class ArticlePage(ContentPage):
    """
    Article Page
    """
    CONTENT_TYPE = "article"
    TEMPLATE     = "article.html"
    RULES        = ['/articles/{slug}/',]
    pass

class IndexPage(ContentPage):
    """
    Index Page
    """
    CONTENT_TYPE = "index"
    TEMPLATE     = "article.html"
    RULES        = ['/']
    pass


class TopicPage(ContentPage):
    """
    Topic Page
    """
    CONTENT_TYPE = "topic"
    TEMPLATE     = "topic.html"
    RULES        = ['/topics/{slug}/',]
    pass


class TopicListingPage(ContentPage):
    """
    Topic Listing Page
    """
    CONTENT_TYPE = "topics"
    TEMPLATE     = "topics.html"
    RULES        = ['/topics/',]
    pass
