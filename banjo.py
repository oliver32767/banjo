#!/usr/bin/env python
# -*- coding: latin-1 -*-

###############################################################################
#     Copyright (c) 2012 Andrew Nelder.  Licensed under the MIT License.      #
#                  Copyright (c) 2013 Oliver Bartley                          #
#                  See LICENSE.txt for full details.                          #
###############################################################################


# I M P O R T S ###############################################################

import logging
import re
import os
import datetime
from collections import namedtuple

import json
from markdown2 import markdown
from bottle import request, route, run, view, template, error, static_file, abort, redirect

import config

# I N I T I A L I Z A T I O N #################################################

# Logger
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.addHandler(ch)

# Regular Expressions
RE_VALID_FILE_EXTENSIONS = re.compile(r'''(?:.md|.markdown|.txt)$''')
RE_METADATA = r'''(?:\:%s[ =])(.*?)(?:[\n\r]|$)'''

# Named tuple pseudo-class
BlogPost = namedtuple('BlogPost', 'date, meta, summary, contents, locator')
Topic = namedtuple('Topic', 'meta, subtopics, contents, locator')

# Constants
POSTS = {}
TOPICS = {}
TAGS = {}
#POST_KEYS = []

# C O N F I G #################################################################

def process_config():
    defaults = {'TITLE': '',
                'SUBTITLE': '',
                'AUTHOR': '',
                'TOPIC_METADATA_TAGS': ['title', 'priority', 'tags'],
                'POST_METADATA_TAGS': ['title', 'author', 'tags'],
                'POSTS_PER_PAGE': 15,
                'SUMMARY_DELIMITER': '~~',
                'DISQUS_SHORTNAME': '',
                'MARKDOWN_EXTRAS': ['fenced-code-blocks'],
                'DEFAULT_STYLE': 'airdale.css',
                'MOBILE_STYLE': 'airdale.css',
                'PYGMENT_STYLE': 'friendly.css'}

    for k, v in defaults.items():
        if not hasattr(config, k):
            print('%s not set, defaulting to %s' %  (k, repr(v)))
            setattr(config, k, v)

# F U N C T I O N S ###########################################################

def process_content():
    # reset this stuff so 
    POSTS = {}
    TOPICS = {}
    TAGS = {}
    #POST_KEYS = []
    
    process_posts()
    process_topics()

def process_topics():
    '''
    Migrates the text files contained in the 'content/posts' directory
    to the database.
    These files will have their meta-data removed and their markdown
    interpreted and converted to HTML.

    NOTE: This is only run once -- when the server starts.
    '''
    LOGGER.info("Processing topics...")
    # Walk the topics dir to build a tree
    topics = path_join('content', 'topics')
    for root, dirs, files in os.walk(topics):

        # remove the base content/topics part of the path
        root = root.replace(topics, '')
        
        #print('#####################################')
        #print('root = %s' % repr(root))
        #print('dirs = %s' % repr(dirs))
        #print('files= %s' % repr(files))

        
        title = root.split('/')[-1:][0].capitalize()

        meta = {'title': title, 'tags': [], 'priority': 0, 'subtopics': []}
        
        subtopics = [path_join('/', root, d) for d in dirs]
        
        html_contents = ''
        
        locator = path_join('/', root)

        for file in files:
            if RE_VALID_FILE_EXTENSIONS.search(file):                
                # Open the file
                if root == '/':
                    file_handle = open(topics + root + file, 'r')
                else:
                    file_handle = open(topics + root + '/' + file, 'r')
                try:
                    subcontents = file_handle.read().decode('utf-8')
                except UnicodeDecodeError:
                    LOGGER.warning('Ignoring file <%s/%s>. UnicodeDecodeError.'
                                   % (root, file))
                    continue
                
                file_rel = os.path.splitext(file)[0]
                subtitle = file_rel
 
                # Extract metadata
                submeta = {'title': subtitle, 'tags': [], 'priority':0}
                for tag in config.TOPIC_METADATA_TAGS:
                    re_meta = re.compile(RE_METADATA % tag)
                    if re_meta.search(subcontents):
                        value = re_meta.findall(subcontents)[0]
                        if tag == 'tags':
                            # tags is a comma separated list
                            submeta[tag] = [x.strip() for x in value.split(',')]
                        else:
                            submeta[tag] = value
                        subcontents = re_meta.sub('', subcontents)
                subcontents = subcontents.strip()

                sublocator = path_join('/', locator, file_rel)
                
                if file_rel == '__index__':
                    # then replace the top-level topic information with the
                    # stuff extracted from __index__
                    submeta['title'] = meta['title']
                    meta = submeta
                    html_contents = markdown(subcontents, extras=config.MARKDOWN_EXTRAS)
                    print("Setting contents for %s\n%s" % (locator, html_contents))
                else:
                    subtopics.append(sublocator)
                    html_subcontents = \
                        markdown(subcontents, extras=config.MARKDOWN_EXTRAS)
                    TOPICS[sublocator] = \
                        Topic(\
                            meta = submeta,\
                            subtopics = [],\
                            contents = html_subcontents,\
                            locator = sublocator)
                file_handle.close()
                
        # now that we've parsed files for subcategories, add the root
        TOPICS[locator] = \
            Topic(\
                meta = meta,\
                subtopics = subtopics,\
                contents = html_contents,\
                locator = locator)
   
    #print(json.dumps(TOPICS, sort_keys = True, indent = 4))

def process_posts():
    '''
    Migrates the text files contained in the 'content/posts' directory
    to the database.
    These files will have their meta-data removed and their markdown
    interpreted and converted to HTML.

    NOTE: This is only run once -- when the server starts.
    '''
    LOGGER.info("Processing posts...")
    # Open every blog post
    path = os.path.join('content', 'posts') + os.path.sep
    for input_file in os.listdir(path):
        if RE_VALID_FILE_EXTENSIONS.search(input_file):

            # Extract date from filename
            try:
                (yy, mm, dd) = input_file.split('-')[:3]
                yy = int('20' + yy) if len(yy) is 2 else int(yy)
                mm = int(mm)
                dd = int(dd)
            except:
                LOGGER.warning('Ignoring file <%s>.  Invalid formatting.' %
                        (input_file,))
                continue

            # Validate date
            if yy > 2500 or mm > 12 or dd > 31:
                LOGGER.warning('Ignoring file <%s>.  Invalid date range.' %
                        (input_file,))
                continue

            # Open the file
            file_handle = open(path + input_file, 'r')
            try:
                contents = file_handle.read().decode('utf-8')
            except UnicodeDecodeError:
                LOGGER.warning('Ignoring file <%s>. UnicodeDecodeError'
                               % (path + input_file))

            # Find the slug
            slug = input_file.split('-', 3)[-1]
            slug = RE_VALID_FILE_EXTENSIONS.sub('', slug)

            # Extract metadata
            meta = {'title': slug, 'author': config.AUTHOR, 'tags':[]}
            for tag in config.POST_METADATA_TAGS:
                re_meta = re.compile(RE_METADATA % tag)
                if re_meta.search(contents):
                    value = re_meta.findall(contents)[0]
                    if tag == 'tags':
                        # tags is a comma separated list
                        meta[tag] = [x.strip() for x in value.split(',')]
                    else:
                        meta[tag] = value
                    contents = re_meta.sub('', contents)

            # Strip the contents of supurfluous whitespace -- now that the
            # metatags have been removed.
            contents = contents.strip()

            # Populate the summary
            # Look for the SUMMARY_DELIM character sequence and use it to
            # form the summary, if it exists.  Otherwise, simply take the first
            # paragraph of the post.
            summary = None
            if re.search(config.SUMMARY_DELIMITER, contents):  # Use delimiter
                summary = contents.split(config.SUMMARY_DELIMITER)[0]
                contents = re.sub(config.SUMMARY_DELIMITER, '', contents)
            else:                                   # Use first paragraph
                summary = re.split(r'''[\r\n]{2}''', contents)[0]
            html_summary = markdown(summary, extras=config.MARKDOWN_EXTRAS)

            locator = '/%04d/%02d/%02d/%s' % (yy, mm, dd, slug, )

            # Enter the file into the database
            html_contents = markdown(contents, extras=config.MARKDOWN_EXTRAS)
            POSTS[locator] = \
                BlogPost(\
                    date=datetime.date(yy, mm, dd),\
                    meta=meta,\
                    summary=html_summary,\
                    contents=html_contents,\
                    locator=locator\
                    )
            
            # Enter the post into the TAGS index
            for tag in meta['tags']:
                if (tag not in TAGS):
                    TAGS[tag] = []
                if locator not in TAGS[tag]:
                    TAGS[tag].append(locator)
                

            # Remove the file
            file_handle.close()

    # TAGS[''] replaces POST_KEYS
    post_keys = []
    post_keys.extend(POSTS.keys())
    TAGS['*'] = post_keys
    
    # now sort all the posts in reverse chronological order according to the slug
    for tag in TAGS:
        TAGS[tag].sort(reverse=True)

#    POST_KEYS.extend(POSTS.keys())
#    POST_KEYS.sort(reverse=True)
    
def get_subtopics(parentLocator):
    '''
    return a list of topics that are subtopics of the Topics with a given locator
    '''
    rv = []
    if parentLocator in TOPICS:
        for subtopicLocator in TOPICS[parentLocator].subtopics:
            if subtopicLocator in TOPICS:
                rv.append(TOPICS[subtopicLocator])
    return rv

def get_breadcrumb(subtopicLocator):
    '''
    return a list of topics that are parents to the given subtopic
    '''
    rv = []
    parent = [subtopicLocator]
    while parent[0] != '':
        if parent[0] != '/':
            rv.append(TOPICS[parent[0]])
        parent = parent[0].rsplit('/', 1)
    
    rv.reverse()
    return rv
        
    

def get_posts(tags):
    '''
    return a list of post locators that match all of the given tags.
    accepts either a single string or a list of strings
    '''
    
    print("getting posts for tags:" + repr(tags))
    posts = []
    print TAGS.keys()
    for tag in tags:
        if tag in TAGS.keys():
            posts = posts + [t for t in TAGS[tag] if t not in posts]
            
    # posts now contains a list of locators
    rv = [POSTS[p] for p in posts]
    return rv       

def path_join(*items):
    '''
    takes an arbitrary list of items and intellegently joins them with a path
    separator. Note that a leading slash is NOT prepended unless the first value is '/'.
    example:
        >>> path_join('/', '/foo/', 'bar/', '/derp.md')
        foo/bar/derp.md
    '''
    rv = ''
    for i in items:
        j = i.strip('/')
        if j != '':
            rv += '/' + j
    rv = rv.strip('/')
    if items[0] == '/':
        rv = '/' + rv
    return rv
    

# P A G E   R O U T I N G #####################################################

@route('/files/<filepath:path>')
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='files')

@route('/favicon.ico')
def favicon():
    return static_file('favicon.ico', root='files')

@route('/<yy:int>/<mm:int>/<dd:int>/<slug>')
@route('/<topicLocator:path>/<yy:int>/<mm:int>/<dd:int>/<slug>')
@view('readpost')
def readpost(yy, mm, dd, slug, topicLocator = '/'):
    topicLocator = path_join('/', topicLocator)
    topic = TOPICS[topicLocator]
    subtopics = get_subtopics(topicLocator)
    breadcrumb = get_breadcrumb(topicLocator)
    
    locator = '/%04d/%02d/%02d/%s' % \
              (yy, mm, dd, slug, )
    if locator not in POSTS:
        abort(404, 'Article not found!')
    post = POSTS[locator]

    return {'title': config.TITLE,
            'topic': topic,
            'subtopics': subtopics,
            'breadcrumb': breadcrumb,
            'post': post,
            'disqus_shortname': config.DISQUS_SHORTNAME,
            'style': config.DEFAULT_STYLE,
            'pygment_style': config.PYGMENT_STYLE}


@route('/')
@route("/<topicLocator:path>")
@route('/<topicLocator:path>/<page:int>')
@route('/<page:int>')
@view('index')
def index(topicLocator = '/', page=0):
    topicLocator = path_join('/', topicLocator)
    topic = TOPICS[topicLocator]
    subtopics = get_subtopics(topicLocator)
    breadcrumb = get_breadcrumb(topicLocator)
    
    print(topic.contents)
    
    if (len(request.query.getall('tag')) > 0):
        topic = Topic(\
                meta = topic.meta,\
                subtopics = topic.subtopics,\
                contents = "<p>Showing tag query results</p>",\
                locator = topic.locator)
        tags = request.query.getall('tag')
        if topicLocator == '/':
            posts = get_posts(tags)
        else:
            #perform an intersection on the two lists, so we only show tags belonging in the topic
            posts = get_posts(list(set(tags).intersection(topic.meta['tags'])))
            
    else:
        # give them the standard stuff
        tags = topic.meta['tags']
        if topicLocator == '/':
            posts = get_posts('*')
        else:
            posts = get_posts(topic.meta['tags'])

    tags.sort()
    
    posts = posts[page * config.POSTS_PER_PAGE:(page + 1) * config.POSTS_PER_PAGE]
    print("topic.lcator = %s" % topic.locator)
    return {'title': config.TITLE,
            'subtitle': config.SUBTITLE,
            'topic': topic,
            'tags': tags,
            'subtopics': subtopics,
            'breadcrumb': breadcrumb,
            'page': page,
            'posts': posts,
            'has_prev': (page > 0),
            'has_next': (len(POSTS) > (page + 1) * config.POSTS_PER_PAGE),
            'style': config.DEFAULT_STYLE,
            'pygment_style': config.PYGMENT_STYLE}

@error(403)
@error(404)
@view('error')
def error_route(error):
    return {'title': config.TITLE,
            'status': error.status,
            'body': error.body,
            'style': config.DEFAULT_STYLE}



# E X E C U T I O N ###########################################################

if __name__ == '__main__':
    print("Executing...")
    path_join('/', '/', 'foo')
    path_join('foo', 'bar')
    process_config()
    process_content()
    if os.environ.get('HEROKU', False):
        run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
    else:
        run(host="localhost", port=8080, debug=True, reloader = True)

# E N D   O F   F I L E #######################################################

