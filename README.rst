Flask-FlatEarth
===============

Generates pages based on static text files. Currently only tested on Python 3. Requires flask and markdown. Intended to be used with Frozen-Flask.

Usage
-----

Not packaged yet, but if imported it defaults to looking for a directory named "pages" in the working directory when called. Requires:

* flask

  The Flask code base. While intended to be used with Frozen-Flask, it is not a dependency, and using flask.Flask.run() works fine for testing.

* markdown

  This is required for the generator. Currently tested with 2.6.9 and 2.6.11.

Using the markdown generator in the a subfolder from the cwd::

    from flask import Flask
    from flask_flatearth.markdown import MarkdownGenerator
    from flask_flatearth.ext.topics import TopicsExtension

    app = Flask(__name__)
    app.config.update(SERVER_NAME="localhost:8080") # Needed for url_for references

    topics = TopicsExtension()
    mdg = MarkdownGenerator(app, extensions=[topics, ]) # Flask has no routes at this point
    mdg.generate() # Flask now has routes and view functions
    
    app.run(host="localhost",port=8080) # Must match SERVER_NAME for links to work

This will read through all .md files in a folder named 'pages' by default, and use those to generate files. For a comparable Frozen_Flask example with a default configuration defining SERVER_NAME::

    from flask import Flask
    from flask_frozen import Freezer
    from flask_flatearth.markdown import MarkdownGenerator
    from flask_flatearth.ext.topics import TopicsExtension

    from .config import DebugConf

    app = Flask(__name__)
    app.config.from_object(DebugConf)

    topics = TopicsExtension()
    mdg = MarkdownGenerator(app, extensions=[topics, ])
    mdg.generate()

    freezer = Freezer(app)
    freezer.freeze()

Configuration
-------------

The following configurations actually do something, and are read in from the Flask app config.

* FLATEARTH_SEARCH_PATH - Overrides default content files search path $CWD/pages
* FLATEARTH_FILE_EXT - Overrides default content files extension .md
* FLATEARTH_LOGLEVEL - The default log level for the 'flask-flatearth' logger

Extensions may provide additional options.

Metadata
--------

Generators include an interface for metadata. Currently, the markdown metadata is based on simple yaml style labels. Future generators may provide other interfaces, but the most important aspect of all metadata is label. The <MetaProcessor `flask_flatearth.MetaProcessor`> objects registered with a <generator `flask_flatearth.ContentGenerator`> are responsible for the data storage format used in template processing.

.. note::
   All metadata is directly accessible to templates with the `meta` template context variable.

Attributes
~~~~~~~~~~

Labels may have various attributes.

* `contingent`

  When a label is contingent, it depends on the value of another label.

* `unique`
  
  When a label is unique, it should only be defined once. Multiple entries would result in a `RuntimeError`. Non-unique labels can be specified multiple times.

* `primary`

  Primary labels must exist. Ommision of this label would result in a `RuntimeError`.

* `secondary`

  Secondary labels may be included, but are not considered a `RuntimeError` if ommitted.

Base Labels
~~~~~~~~~~~

These are the base labels available without any extensions loaded:

* `type` : primary, unique

  This defines the content_type, and depending on the value may prompt processing through a specific extension or warrant unique behavior in other metadata label processing.

* `slug` : primary, unique

  Unique identifier for the content. Across all page content, this must be unique. These are typically used as endpoints in the <flask url map `flask.Flask.url_map`>.

* `title` : primary, unique
  
  This label defines a title that may be uniquely utilized across content types.

* `publish` : primary, unique

  This is an RFC 2822 formatted date and used to identify the date the content is published.

* `set` : secondary, unique

  This label defines the set that a page belongs to.

* `description` : secondary, unique

  This label defines an excerpt to represent the content

* `author` : secondary

  This label defines the article is associated with an author slug.

* `order` : contingent, secondary

  For `type: set`, this label defines the ordering for the set of pages belonging to the set. The default behavior is to sort ordering by publish values.

* `sequence` : secondary

  For pages with `set`, this provides a index ordering of the pages.

* `updates` : secondary

  These entries take the format of "{date}: {reason}" where date is an RFC 2822 date of update, and reason is a brief outline of the content changes applied.

Extensions may introduce additional labels for content types, and as with any attributes may result in `RuntimeError` failures if not used properly in the content definitions.


Pages
-----

In the base application, there are two page types; page and set. The content `type` metadata label is used by the page generators and set generators. The sets are processed only after all the pages are processed. All types are processed by the base <PageContent `flask_flatearth.PageContent`>, however the template behavior and order of processing will vary accorrding to the type.

All page content sources are loaded. Then the registered <PageGenerators `flask_flatearth.PageGenerator`> are executed on them. This populates the pages. Then the <PageGenerators `flask_flatearth.PageGenerator`> for Sets are processed, iterating through all the generated pages, in turn adding additonal pages to the <ContentGenerator `flask_flatearth.ContentGenerator`>. Once all the sets are processed, the generator registers the rules with the <flask app `flask.Flask`> and then makes another pass to generate the view functions for rendering all templates.


Page Type
~~~~~~~~~

A `Page Type` is essentially a single item page. The <PageContent `flask_flatearth.PageContent`> here would not need references to other pages. Standard examples of these include:

* article

  - An article page. This typically includes blog entries, how-to, guide and reference editorial content. The URL maps to "/articles/{slug}/"

* author

  - An Author page. This typically includes small bio entries for contributors to the site/content. The URL maps to "/authors/{slug}/".
  
* index

  - The landing/index page for this site/content. Commonly the "home page" users see when visiting a site. The URL maps to "/".

* page

  - A one-off page, typically static. This is a base type, and can be leveraged for one-off content like the generally static "About Us" and "Contact Us" content. The URL maps to "/{slug}/"

Set Type
~~~~~~~~

A `Set Type` is a page designed to provide a content reference to a set of pages. The <PageContent `flask_flatearth.PageContent`> here would typically assess the associations to other pages, and therefor these types of pages are only processed after all `Page Type` pages are processed. Some examples of these include:

* articles

  - An article listing page. This typically includes a listing of articles or provide some type of navigational means. The URL maps to "/articles/"

* authors

  - An author listing page. This typically includes a listing of authors. The URL maps to "/authors/"

Author Page
~~~~~~~~~~~

These pages define author/bio pages. An example file::

    type: author
    slug: jcastillo2nd
    title: Javier Castillo II
    publish: Thu, 31 May 2018 03:46:13 +0000
    author-name: Javier
    author-long: Javier Castillo II
    social-twitter: @jcastillo2nd
    
    Javier likes spending time with his children and computers. Not necessarily in that order. {:smirk:}
    
    # From the Author #
    
    What can I say? Hey, I like Linux! I'm always happy to explore software and love learning new programming languages.

In this example, metadata entries `author-name`, `author-long` and `social-twitter` would require extensions to have any meaningful rendering. Similarly, a custom Markdown extension would need to be loaded to handle the `{:smirk:}` reference.

Articles
~~~~~~~~

These pages define content and topics. The articles support using a markdown extension to link to other pages. An example file::

    type: article
    slug: example
    title: An Example Page
    publish: Fri, 16 Mar 2018 01:27:18 +0000
    description: A basic page to showcase simple functionality
    topics: hello world,examples,simple
    author: jcastillo2nd
    updates: Fri, May 25 2018 07:13:00 GMT+1000: lorem ipsum capitalized
    
    ## An Example Article ##
    
    This is better than Lorem Ipsum. Don't you think?
    
    ### Example Article Subsection ###
    
    This could have been something more. But it's not.
    
    I tried though.
    
    ### The Final Section for Example Article ###
    
    One last note. I can still use links based on slugs to an [author]{{jcastillo2nd}} or any other page including [this one]{{example}}.
    
    ## Finally ##
    
    That was it for the example.

In this example, the metadata lable `topics` would require an extension to process any sets related with topics. Additionally, an extension would be required for handling the markdown `[label]{{slug}}` formatted links to other page slugs.

Templates
---------

The content rendering will search for specific template files. The layout/inheritence is entirely up to the developer. There is context data that is automatically available with each template as well as integration to support url_for handling within the Markdown content.


Required Files
~~~~~~~~~~~~~~
The templates require the following files:

* author.html
  A template page for the author content

* authors.html
  A template page for the author listing

* article.html
  A template page for the article content

* articles.html
  A template page for the article listing

* topic.html
  A listing page for articles associated with a listing

* topics.html
  A listing page for topic pages

Available Context
~~~~~~~~~~~~~~~~~

The following variables are available within the Context of a template:

* page_content
  This is the html rendered from the markdown. It is unprocessed, so the `{{url_for(item)}}` strings generated by the markdown must be filtered with `markdown_render`.

* authors
  This is a list of all content authors ( author pages ) by author slug keys. This allows for all author content to be available to each template.

* refs
  This is a list of references passed to a Page object. This primarily used for articles associated with authors or topics.

* meta
  This is a dictionary of markdown metadata. This commonly includes the following entries:

  * type
    The page type ( article, author, topic )::
        type: article

  * slug
    The endpoint/function name for flask to reference with `url_for()`::
        slug: article-name

  * topics
    The topics associated with the article ( list )::
        topics: testing,documentation entry,readme

  * title
    The page title::
        title: Article Name

  * description
    The page description::
        description:: This is an article

  * author
    The authors associated with the page ( list )::
        author: authorslug1
        author: authorslug2

  * publish
    The date the page was originally published::
        publish: Fri, May 25 2018 04:23:00 GMT+1000

  * updates
    RFC 2822 date for recent edit and reason for edit::
        updates: Sat, Apr 12 2014 12:22:00 GMT+1000: Updated to reflect new spec
        updates: Sun, May 27 2018 06:03:00 GMT+1000: Updated to reflect deprecated status

Any other metadata included in the article markdowns will be available as well.

Pages
-----

The collection of content to be generated should be kept to a single directory. By default, this directory is named "pages" and searched for in the current working directory from where the generator command is called from. The current supported file format is markdown. While the directory organization is completely up to the user, the recommended outline would be::

    pages/
    ├── articles
    │   ├── article-group-1
    │   │   └── article-1.md
    │   └── article-group-2
    │       ├── article-2.md
    │       └── article-3.md
    ├── authors
    │   ├── author1.md
    │   └── author2.md
    ├── coming-soon.md
    ├── example.md
    └── index.md

All content in the pages directory will be processed, and any pages of 'author' type will have slugs available for use with the authors listing.

Future Work
-----------

Some todo items include:

* Docs on the mechanism by which the system works including:

  - The core generator concepts

  - The extension concepts

  - The context available within the template

  - Real examples

* Clean up logging to leverage info, warn, error and multiple levels of debug

* Site map extension
  This would generate a sitemap file with various options for formats.

* Atom Feed extension
  This would generate an atom feed for the site.

* RSS Feed extension
  This would generate an rss feed for the site.

* reST generator
  A Generator capable of reading reST files.

* Update the module and package to support functioning as an actual Flask extension ( including setup.py and real tests ).
