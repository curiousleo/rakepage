# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os, os.path
from contextlib import closing
import yaml, jinja2, textile, codecs

DOIT_CONFIG = {'default_tasks': ['gen']}

SITEMAP = yaml.load('''
- index: Homepage
- pages: Page Layout
- paragraphs: Writing Paragraph Text
- phrasemods: Using Phrase Modifiers
''')

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
    path: template.html
options:
    preview: true
'''

CONF = yaml.load(YAML_CONF)

TEMPLATE = None

def task_create():
    """
    Create a new site.
    """
    
    NEW_SITE = (
        (os.path.join(CONF['input']['dir'], 'index' + CONF['input']['ext']),
            'h1. Index'),
        (os.path.join(CONF['media']['dir'], 'default.css'), 
            ''),
        (os.path.join(CONF['template']['path']),
            '<html><head><title>{{ title }}</title></head>'
            '<body>{{ content }}</body></html>'),
    )

    def write_default(target, content):
        input_enc = CONF['input']['enc']

        with closing(codecs.open(target, mode='wb',
            encoding=input_enc)) as targetf:
            targetf.write(content)

    for target, content in NEW_SITE:
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
            TEMPLATE = jinja2.Template(templatef.read())
            return True
        return False

    return {
        'actions': [(load_template,)]
    }

def task_gen():
    """
    Generate a site.
    """

    INPUT_ENC = CONF['input']['enc']
    OUTPUT_ENC = CONF['output']['enc']

    src_name = lambda page: os.path.join(
        CONF['input']['dir'], page['name'] + CONF['input']['ext'])
    dst_name = lambda page: os.path.join(
        CONF['output']['dir'], page['name'] + CONF['output']['ext'])
    navi_entry = lambda page: {'title': page['title'],
        'url': page['name'] + CONF['output']['ext']}

    def get_pages():
        for page in SITEMAP:
            name, title = page.items()[0]
            yield {'title': title, 'name': name}

    def ensure_dir_exists(dirname):
        if not os.path.isdir(dirname): os.makedirs(dirname)

    def process_page(src, dst, page):
        with closing(codecs.open(src, encoding=INPUT_ENC)) as srcf:
            context = {
                'title': page['title'],
                'navigation': map(navi_entry, get_pages()),
                'content': textile.textile(srcf.read())}
            transformed = TEMPLATE.render(context)
        ensure_dir_exists(os.path.split(dst)[0])
        with closing(codecs.open(dst, mode='wb', encoding=OUTPUT_ENC)) as dstf:
            dstf.write(transformed)
            return True
        return False

    for page in list(get_pages()):
        dep = src_name(page); target = dst_name(page)

        yield {
            'name': page['name'],
            'actions': [(process_page, (dep, target, page))],
            'task_dep': ['load_template'],
            'file_dep': ['dodo.py', dep, CONF['template']['path']],
            'targets': [target]
        }


