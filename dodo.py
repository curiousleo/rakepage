# To be used with 'doit'.
# Tasks defined: create, gen, serve, publish

import os
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

        def create_targets_list(site=new_site, root='.'):
            for target, content in site.iteritems():
                target = os.path.join(root, target)
                if isinstance(content, basestring):
                    yield \
                        sitepath + os.path.sep + target if sitepath else target
                elif type(content) == dict:
                    if content: yield create_targets_list(content, target)
        
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

    return {'actions': [(write_defaults,)],
            'targets': get_targets(),
            # 'params':[{'name': 'layout',
                       # 'short': 'l',
                       # 'default': 'basic'}],
            'clean': False
            }

# vim: set fileencoding=utf8 expandtab tabstop=4 shiftwidth=4 softtabstop=4:

