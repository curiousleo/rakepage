# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os.path
from contextlib import closing

def task_create():
    """
    Create a new site.
    """
    
    new_site = {
        'config.yaml': '',
        'pages':
            {'index.textile': ''},
        'media':
            {'default.css': ''},
        'templates':
            {'default.mustache': ''},
        'site': {}
    }


    def get_targets(sitepath=''):
        def flatten(x):
            result = []
            for el in x:
                if hasattr(el, "__iter__") and not isinstance(el, basestring):
                    result.extend(flatten(el))
                else: result.append(el)
            return result

        def create_targets_list(content=new_site, target=''):
            for target, content in new_site.iteritems():
                if type(content) == str:
                    yield \
                        sitepath + os.path.sep + target if sitepath else target
                elif type(content) == dict:
                    if content: yield create_targets_list(content, target)

        return flatten(create_targets_list())

    def write_defaults(content=new_site, target='', sitepath=''):
        for target, content in new_site.iteritems():
            if type(content) == str or type(content) == unicode:
                fname = sitepath + os.path.sep + target if sitepath else target
                with closing(fname) as f: f.write(content)
            elif type(content) == dict:
                if content: write_defaults(content, target)

    return {'actions': [(write_defaults,)],
            'targets': get_targets(),
            # 'params':[{'name': 'layout',
                       # 'short': 'l',
                       # 'default': 'basic'}],
            'verbosity': 2,
            'clean': True
            }

# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

