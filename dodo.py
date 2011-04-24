# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os, os.path, shutil, codecs, yaml, pystache, pystache.template, textile
from contextlib import closing
from doit.tools import create_folder

# ----------------------------------------------------------------------------
# CONFIGURATION --------------------------------------------------------------
# ----------------------------------------------------------------------------

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
options:
    template: templates/template.mustache   # path to template
    media: media                            # path to media folder
'''

# ----------------------------------------------------------------------------
# PREPARATION ----------------------------------------------------------------
# ----------------------------------------------------------------------------

DOIT_CONFIG = {
    'default_tasks': ['gen'],
    'continue': True,
    'verbosity': 2
}

def get_pages():
    for page in SITEMAP:
        name, title = page.items()[0]
        yield {'title': title, 'name': name}

def get_files(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

get_media_files = lambda: get_files(CONF['options']['media'])

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

# ----------------------------------------------------------------------------
# CREATE ---------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_create():
    """
    Create a new site.
    """

    try: DATA_DIR = os.environ['PP_DATA']
    except KeyError: print 'PP_DATA environment variable not set.'

    def existing(dirname, filenames):
        return [f for f in filenames
            if os.path.exists(os.path.join(dirname, f))]

    def mkdir_copy(src, dst):
        create_folder(os.path.split(dst)[0])
        shutil.copy2(src, dst)

    for target in get_files(DATA_DIR):
        dst = target.replace(DATA_DIR, '')
        yield {
            'name': dst,
            'actions': [(mkdir_copy, (target, dst))],
            'run_once': True
        }

# ----------------------------------------------------------------------------
# GEN ------------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_gen():
    """
    Generate the site.
    """

    def rm_unneeded():
        targets = (get_files(CONF['output']['dir']))
        targets = (t for t in targets if not t in MEDIAFILES_DST)
        targets = (t for t in targets if not t in PAGES_DST)
        for target in targets: os.remove(target)

    yield {
        'name': 'cleanup_output',
        'actions': [(rm_unneeded,)]
    }

    yield {
        'name': 'pages',
        'actions': None,
        'task_dep': ['process_page'],
        'clean': True
    }

    yield {
        'name': 'mediafiles',
        'actions': None,
        'task_dep': ['copy_mediafile'],
        'clean': True

    }

# ----------------------------------------------------------------------------
# SERVE ----------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_serve():
    """
    Serve the site via SimpleHTTPServer.
    """

    def serve_site():
        root = os.curdir
        os.chdir(CONF['output']['dir'])
        import shlex, subprocess
        subprocess.Popen(shlex.split('python -m SimpleHTTPServer 8000'))
        os.chdir(root)

    yield {
        'name': 'serve',
        'actions': [(serve_site,)],
        'task_dep': ['gen']
    }

# ----------------------------------------------------------------------------
# HELPERS --------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_process_page():
    '''
    Process individual page.
    '''
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
            'setup': ['load_template'],
            'file_dep': [dep, CONF['options']['template']],
            'targets': [target],
            'clean': True
        }

def task_copy_mediafile():
    '''
    Copy individual file (media -> output).
    '''
    def safe_copy(src, dst):
        create_folder(os.path.split(dst)[0])
        shutil.copy2(src, dst)

    for dep, target in zip(MEDIAFILES_SRC, MEDIAFILES_DST):
        yield {
            'name': os.path.sep.join(dep.split(os.path.sep)[1:]),
            'actions': [(safe_copy, (dep, target))],
            'file_dep': [dep],
            'targets': [target],
            'clean': True
        }

def task_load_template():
    '''
    Load the template.
    '''
    INPUT_ENC = CONF['input']['enc']

    def load_template():
        with closing(codecs.open(CONF['options']['template'],
            encoding=INPUT_ENC)) as templatef:
            global TEMPLATE
            TEMPLATE = templatef.read()
            return True
        return False

    return {
        'actions': [(load_template,)]
    }
