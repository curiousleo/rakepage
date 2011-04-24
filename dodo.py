# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish (<- not yet)
#
# TODO: Publish task

import os, os.path, shutil, codecs, yaml
from contextlib import closing
from doit.tools import create_folder
import markdown, pystache

# ----------------------------------------------------------------------------
# SETTINGS -------------------------------------------------------------------
# ----------------------------------------------------------------------------

CONF_PATH = 'site.yaml'

# ----------------------------------------------------------------------------
# PREPARATION ----------------------------------------------------------------
# ----------------------------------------------------------------------------

# Don't change this -- put your settings in 'site.yaml'
DEFAULT_CONF = '''
input:
    enc: utf-8
    ext: .mkd
    dir: pages
output:
    enc: utf-8
    ext: .html
    dir: output
options:
    template: templates/template.mustache   # path to template
    media: media                            # path to media folder
'''

DOIT_CONFIG = {'default_tasks': ['gen']}

def deep_merge(dst, src):
    '''Merges src into dst, returns dst.
    Credits: Manuel Muradas <http://bit.ly/fOPgyW>'''
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

def get_pages():
    for page in get_files(CONF['input']['dir']):
        if not page.endswith(CONF['input']['ext']): continue
        yield {
            'name': os.path.split(page)[1],
            'path': os.path.relpath(page, CONF['input']['dir'])}

def get_files(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

get_media_files = lambda: get_files(CONF['options']['media'])
page_src_name = lambda page: os.path.join(
    CONF['input']['dir'], page['path'])
page_dst_name = lambda page: os.path.join(
    CONF['output']['dir'],
    page['path'][:-len(CONF['input']['ext'])] + CONF['output']['ext'])
media_dst_name = lambda mediafile: os.path.join(
    CONF['output']['dir'],
    os.path.sep.join(mediafile.split(os.path.sep)[1:]))

DEFAULT_CONF = yaml.load(DEFAULT_CONF)
CONF = DEFAULT_CONF
SITEMAP = None

MENU = None
TEMPLATE = None

MEDIAFILES_SRC = list(get_media_files())
MEDIAFILES_DST = [media_dst_name(f) for f in MEDIAFILES_SRC]

PID = None

# ----------------------------------------------------------------------------
# CREATE ---------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_create():
    """
    Create a new site.
    """

    DATA_DIR = None
    try: DATA_DIR = os.environ['PP_DATA']
    except KeyError: pass

    def existing(dirname, filenames):
        return [f for f in filenames
            if os.path.exists(os.path.join(dirname, f))]

    def mkdir_copy(src, dst):
        create_folder(os.path.split(dst)[0])
        shutil.copy2(src, dst)

    if DATA_DIR:
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
        targets = (t for t in targets if not t in
            (page_dst_name(p) for p in get_pages()))

        for target in targets: os.remove(target)

    yield {
        'name': 'cleanup',
        'actions': [(rm_unneeded,)]
    }

    yield {
        'name': 'pages',
        'actions': None,
        'task_dep': ['load_conf', 'create_menu', 'process_page'],
        'clean': True
    }

    yield {
        'name': 'mediafiles',
        'actions': None,
        'task_dep': ['load_conf', 'copy_mediafile'],
        'clean': True

    }

# ----------------------------------------------------------------------------
# SERVE ----------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_serve():
    """
    Serve the site via SimpleHTTPServer.
    """

    def serve_site(preview):
        global PID
        if PID == None:
            root = os.path.abspath(os.curdir)
            os.chdir(CONF['output']['dir'])
            import shlex, subprocess, signal, webbrowser, atexit
            PID = subprocess.Popen(shlex.split(
                'python -m SimpleHTTPServer 8000')).pid
            atexit.register(os.kill, PID, signal.SIGKILL)
            if preview: webbrowser.open('http://0.0.0.0:8000/')
            os.chdir(root)

    yield {
        'name': 'serve',
        'actions': [(serve_site,)],
        'task_dep': ['gen'],
        'params': [{
            'name': 'preview',
            'long': 'preview',
            'short': 'p',
            'default': True}]
    }

# ----------------------------------------------------------------------------
# HELPERS --------------------------------------------------------------------
# ----------------------------------------------------------------------------

def task_load_conf():
    def load_conf():
        global CONF, SITEMAP
        CONF = yaml.load(codecs.open(
            CONF_PATH, encoding=DEFAULT_CONF['input']['enc']))
        CONF = deep_merge(DEFAULT_CONF, CONF)
        SITEMAP = CONF['menu']

    return {
        'actions': [(load_conf,)],
        'file_dep': [CONF_PATH, 'dodo.py']}

def task_create_menu():
    """
    Generate the site.
    """
    INPUT_ENC = CONF['input']['enc']

    output_url = lambda page_path: \
        page_path[len(CONF['input']['dir']) + 1: \
            -len(CONF['input']['ext'])] + CONF['output']['ext']

    def navi_entry(page):
        page_path = os.path.join(CONF['input']['dir'],
            page + CONF['input']['ext'])
        md = markdown.Markdown(extensions=['meta'])
        with closing(codecs.open(page_path, encoding=INPUT_ENC)) as srcf:
            md.convert(srcf.read()),
        return {
            'title': md.Meta['title'][0],
            'url': output_url(page_path)}

    def create_menu():
        global MENU
        MENU = map(navi_entry, SITEMAP)
        return str(MENU)

    return {
        'actions': [(create_menu,)],
        'file_dep': [CONF_PATH, 'dodo.py']}

def task_process_page():
    '''
    Process individual page.
    '''

    INPUT_ENC = CONF['input']['enc']
    OUTPUT_ENC = CONF['output']['enc']

    def process_page(src, dst, page):
        md = markdown.Markdown(extensions=['meta'])
        with closing(codecs.open(src, encoding=INPUT_ENC)) as srcf:
            context = {
                'navigation': MENU,
                'content': md.convert(srcf.read()),
                'title': md.Meta['title'][0]}
            transformed = pystache.render(template=TEMPLATE, context=context)
        create_folder(os.path.split(dst)[0])
        with closing(codecs.open(dst, mode='wb', encoding=OUTPUT_ENC)) as dstf:
            dstf.write(transformed)
            return True
        return False

    src_dst_p = lambda p: (page_src_name(p), page_dst_name(p), p)

    for dep, target, page in (src_dst_p(p) for p in get_pages()):
        yield {
            'name': page['name'],
            'actions': [(process_page, (dep, target, page))],
            'setup': ['load_template'],
            'file_dep': [CONF_PATH, 'dodo.py', dep,
                CONF['options']['template']],
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
            'file_dep': ['dodo.py', dep],
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
