# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os, os.path, shutil, codecs, yaml, pystache, pystache.template, textile
from contextlib import closing
from doit.tools import create_folder

DOIT_CONFIG = {'default_tasks': ['gen']}

YAML_SITEMAP = '''
- index: Homepage
- pages: Page Layout
- paragraphs: Writing Paragraph Text
- phrasemods: Using Phrase Modifiers
'''

YAML_CONF = '''
input:
    enc: utf-8
    ext: .textile
    dir: pages
output:
    enc: utf-8
    ext: .html
    dir: output
media:
    dir: media
template:
    path: template.mustache
options:
    preview: true
'''

def get_pages():
    for page in SITEMAP:
        name, title = page.items()[0]
        yield {'title': title, 'name': name}

def get_media_files():
    for dirpath, _, filenames in os.walk(CONF['media']['dir']):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

page_src_name = lambda page: os.path.join(
    CONF['input']['dir'], page['name'] + CONF['input']['ext'])
page_dst_name = lambda page: os.path.join(
    CONF['output']['dir'], page['name'] + CONF['output']['ext'])
media_dst_name = lambda mediafile: os.path.join(
    CONF['output']['dir'],
    os.path.sep.join(mediafile.split(os.path.sep)[1:]))

CONF = yaml.load(YAML_CONF)
SITEMAP = yaml.load(YAML_SITEMAP)

TEMPLATE = None

PAGES = list(get_pages())
PAGES_SRC = [page_src_name(p) for p in PAGES]
PAGES_DST = [page_dst_name(p) for p in PAGES]
MEDIAFILES_SRC = list(get_media_files())
MEDIAFILES_DST = [media_dst_name(f) for f in MEDIAFILES_SRC]

def task_create():
    """
    Create a new site.
    """

    FOLDERS = (
        CONF['input']['dir'],
        CONF['media']['dir'],
        CONF['output']['dir'],
    )
    
    FILES = (
        (os.path.join(FOLDERS[0], 'index' + CONF['input']['ext']),
            'h1. Index'),
        (os.path.join(FOLDERS[1], 'style.css'), ''),
        (os.path.join(FOLDERS[1], 'plugins.js'), ''),
        (os.path.join(CONF['template']['path']),
            '<html><head><title>{{title}}</title></head>'
            '<body>{{{content}}</body></html>'),
    )

    def write_default(target, content):
        input_enc = CONF['input']['enc']

        with closing(codecs.open(target, mode='wb',
            encoding=input_enc)) as targetf:
            targetf.write(content)

    def makedirs_catch_errors(target):
        try: os.makedirs(target)
        except OSError: pass

    for target in FOLDERS:
        yield {
            'name': target,
            'actions': [(makedirs_catch_errors, (target,))],
            'run_once': True
        }

    for target, content in FILES:
        yield {
            'name': target,
            'actions': [(write_default, (target, content))],
            'run_once': True
        }

def task_load_template():
    '''
    Load the template.
    '''
    INPUT_ENC = CONF['input']['enc']

    def load_template():
        with closing(codecs.open(CONF['template']['path'],
            encoding=INPUT_ENC)) as templatef:
            global TEMPLATE
            TEMPLATE = templatef.read()
            print 'Template loaded.'
            return True
        return False

    return {
        'actions': [(load_template,)]
    }

def task_gen():
    """
    Generate a site.
    """

    yield {
        'name': 'pages',
        'actions': None,
        'task_dep': ['process_page']
    }

    yield {
        'name': 'mediafiles',
        'actions': None,
        'task_dep': ['copy_mediafile']
    }

def task_process_page():
    INPUT_ENC = CONF['input']['enc']
    OUTPUT_ENC = CONF['output']['enc']

    navi_entry = lambda page: {'title': page['title'],
        'url': page['name'] + CONF['output']['ext']}

    def process_page(src, dst, page):
        with closing(codecs.open(src, encoding=INPUT_ENC)) as srcf:
            context = {
                'title': page['title'],
                'navigation': map(navi_entry, get_pages()),
                'content': textile.textile(srcf.read())}
            transformed = pystache.render(template=TEMPLATE, context=context)
        create_folder(os.path.split(dst)[0])
        with closing(codecs.open(dst, mode='wb', encoding=OUTPUT_ENC)) as dstf:
            dstf.write(transformed)
            return True
        return False

    for dep, target, page in zip(PAGES_SRC, PAGES_DST, PAGES):
        yield {
            'name': page['name'],
            'actions': [(process_page, (dep, target, page))],
            'task_dep': ['load_template'],
            'file_dep': ['dodo.py', dep, CONF['template']['path']],
            'targets': [target],
            'clean': True
        }

def task_copy_mediafile():
    def safe_copy(src, dst):
        create_folder(os.path.split(dst)[0])
        shutil.copy2(src, dst)

    for dep, target in zip(MEDIAFILES_SRC, MEDIAFILES_DST):
        yield {
            'name': os.path.sep.join(dep.split(os.path.sep)[1:]),
            'actions': [(safe_copy, (dep, target))],
            'file_dep': ['dodo.py', dep],
            'targets': [target],
            'clean': True
        }

