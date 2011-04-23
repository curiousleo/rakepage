# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os, os.path
from contextlib import closing
import yaml, jinja2, textile, codecs

SITEMAP = yaml.load('''
- index: My Index
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

def task_create():
    """
    Create a new site.
    """
    
    new_site = {
        CONF['input']['dir']:
            {'index.textile': 'h1. Index'},
        CONF['media']['dir']:
            {'default.css': ''},
        CONF['template']['path']: '',
        CONF['output']['dir']: {},
    }


    def get_targets(sitepath=''):
        def flatten(x):
            result = []
            for el in x:
                if hasattr(el, "__iter__") and not isinstance(el, basestring):
                    result.extend(flatten(el))
                else: result.append(el)
            return result

        def create_targets_list(site=new_site, root='.'):
            for target, content in site.iteritems():
                target = os.path.join(root, target)
                if isinstance(content, basestring):
                    yield \
                        os.path.join(sitepath, target) if sitepath else target
                elif type(content) == dict:
                    if content:
                        yield \
                            os.path.join(sitepath, target) if sitepath \
                                                           else target
                        yield create_targets_list(content, target)
        
        return map(os.path.normpath, flatten(create_targets_list()))

    def write_defaults(site=new_site, root='.', sitepath='.'):
        for target, content in site.iteritems():
            target = os.path.join(root, target)
            if isinstance(content, basestring):
                fname = os.path.join(sitepath, target) if sitepath else target
                with closing(open(fname, 'w')) as f: f.write(content)
            elif type(content) == dict:
                if content: 
                    if not os.path.exists(target): os.mkdir(target)
                    write_defaults(content, target)
        return True

    yield  {'name': 'create',
            'actions': [(write_defaults,)],
            'targets': get_targets(),
            'run_once': True
            }

def task_gen():
    """
    Generate a site.
    """

    INPUT_ENC = CONF['input']['enc']
    OUTPUT_ENC = CONF['output']['enc']

    def load_template():
        with closing(codecs.open(CONF['template']['path'],
            encoding=INPUT_ENC)) as templatef:
            return jinja2.Template(templatef.read())

    TEMPLATE = load_template()
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

    def process_page(src, dst, page):
        with closing(codecs.open(src, encoding=INPUT_ENC)) as srcf:
            context = {
                'title': page['title'],
                'navigation': map(navi_entry, get_pages()),
                'content': textile.textile(srcf.read())}
            transformed = TEMPLATE.render(context)
        with closing(codecs.open(dst, mode='wb', encoding=OUTPUT_ENC)) as dstf:
            dstf.write(transformed)
            return True
        return False

    for page in list(get_pages()):
        dep = src_name(page); target = dst_name(page)

        yield {
            'name': page['name'],
            'actions': [(process_page, (dep, target, page))],
            'file_dep': [dep, CONF['template']['path']],
            'targets': [target]
        }

