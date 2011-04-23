# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os
import os.path
from contextlib import closing
import yaml

DEFAULT_CONF = '''
input:
    enc: utf-8
    ext: .textile
options:
    preview: true
output:
    enc: utf-8
    ext: .html
    type: local
'''
CONF = yaml.load(DEFAULT_CONF)

PAGE_DIR = 'pages'
OUTPUT_DIR = 'output'
PAGES = []
SRC_FILES = []
DST_FILES = []

def get_pages():
    for page in CONF['sitemap']:
        name, title = page.items()[0]
        # yield {'title': title, 'path': name}
        PAGES.append({'title': title, 'path': name})

def get_dst_files():
    for page in PAGES:
        # yield os.path.join(
            # conf['output']['dir'], page['name'] + conf['output']['ext'])
        DST_FILES.append(os.path.join(
            OUTPUT_DIR, page['name'] + CONF['output']['ext']))

def get_src_files():
    for page in PAGES:
        # yield os.path.join(
            # conf['input']['dir'], page['name'] + conf['input']['ext'])
        DST_FILES.append(os.path.join(
            PAGE_DIR, page['name'] + CONF['input']['ext']))

def load_conf(confpath):
    def deep_merge(dst, src):
        '''
        Merges src into dst, returns dst.
        Credits: Manuel Muradas <http://bit.ly/fOPgyW>
        '''
        stack = [(dst, src)]
        while stack:
            current_dst, current_src = stack.pop()
            for key in current_src:
                if key not in current_dst: current_dst[key] = current_src[key]
                else:
                    if isinstance(current_src[key], dict) and \
                        isinstance(current_dst[key], dict):
                        stack.append((current_dst[key], current_src[key]))
                    else:
                        current_dst[key] = current_src[key]
        return dst

    with closing(open(confpath)) as confpath:
        deep_merge(CONF, yaml.load(confpath))

def task_create():
    """
    Create a new site.
    """
    
    new_site = {
        'config.yaml': DEFAULT_CONF,
        'pages':
            {'index.textile': ''},
        'media':
            {'default.css': ''},
        'templates':
            {'default.mustache': ''},
        'site': {},
        'output': {},
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

    yield  {'name': 'create',
            'actions': [(write_defaults,)],
            'targets': get_targets(),
            # 'params':[{'name': 'layout',
                       # 'short': 'l',
                       # 'default': 'basic'}],
            'run_once': True,
            'clean': ['rm -rf %s' % 'output']
            }

def task_gen():
    """
    Generate a site.
    """

    return {'actions': [(load_conf, get_pages, get_src_files, get_dst_files)],
            'targets': ['test'],
            'params':[{'name': 'confpath',
                       'short': 'c',
                       'long': 'conf',
                       'default': CONF['options']['conf']}],
            }

# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

