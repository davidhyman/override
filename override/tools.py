import argparse
import ast
import os

import pystache

# TODO: logging instead of printing
# TODO: boilerplate handling (or silencing)
# TODO: alternative handling for updates
# TODO: think of a way round the 'test mode' problem
# TODO: 'safe' mode (dont set keys that don't already exist)?
# TODO: 'safe' json/yaml/ini override config file

# TODO: config differ


DEFAULT_TEMPLATE = """
# This file is autogenerated by {{template_blame}}

from {{config_module}}.{{config_name}} import *

{{#runtime_override_key}}
# runtime overrides
from override.tools import RuntimeUpdates as _RTU
_RTU('{{runtime_override_key}}').apply_all(locals())
{{/runtime_override_key}}


print(42*'#')
print('# ', 'configuration: %s' % '{{config_name}}')
print('# ', 'version: unknown')
print(42*'#')

"""


class RuntimeUpdates:
    def __init__(self, runtime_override_key='set'):
        self.key = runtime_override_key.lower()

    def get_command_parameters(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--%s' % self.key, action='append', dest='from_user')
        assignments = parser.parse_known_args()[0].from_user or []
        # FIXME: this is quite bombproof, but users may prefer something less prone to swallowing errors
        return dict(x.split('=', 1) for x in assignments if x and '=' in x)

    def get_environ_parameters(self):
        return dict(x.split('=', 1) for k, x in os.environ.items() if k.lower().startswith(self.key) and x and '=' in x)

    def deep_update(self, original, key, value):
        path = key.split('.', 1)
        if len(path) == 1:
            k = path[0]
            if isinstance(original, dict):
                original[k] = value
            else:
                setattr(original, k, value)
        else:
            if isinstance(original, dict):
                ref = original[path[0]]
            else:
                ref = getattr(original, path[0])

            self.deep_update(ref, path[1], value)

    def module_update(self, original, updates, reason):
        for k, v in updates.items():
            try:
                v = ast.literal_eval(v)
            except (SyntaxError, ValueError):
                pass  # else string anyway
            print('setting %s -> %r %s as %s' % (k, v, reason, type(v).__name__))
            self.deep_update(original, k, v)
        return self

    def apply_all(self, config_module):
        # TODO perhaps a way to only apply one of them
        self.module_update(config_module, self.get_command_parameters(), 'from command line')
        self.module_update(config_module, self.get_environ_parameters(), 'from env variable')
        return self


class Project:
    """
    A project is an instance of the configuration system.
    """

    def __init__(
        self,
        config_path='configs',
        config_module='config.py',
        template=DEFAULT_TEMPLATE,
        template_path=None,
        relative_root=None,
        runtime_override_key=None,
    ):
        self.config_path = config_path
        self.config_module = config_module
        self.template_path = template_path
        self.template = template
        self.relative_root = os.path.abspath(os.path.dirname(relative_root)) if relative_root else None
        self.selected = None
        self.runtime_override_key=runtime_override_key

        if self.relative_root:
            # set all internal paths based on a relative directory
            self.config_path = os.path.join(self.relative_root, self.config_path)
            if self.template_path:
                self.template_path = os.path.join(self.relative_root, self.template_path)

        if self.template_path:
            with open(template, 'r') as fh:
                self.template = fh.read()

    def select_config(self, name):
        self.selected = name
        return self

    def validate_config(self):
        return self

    def apply_config(self):
        templated = pystache.render(self.template, dict(
            template_blame=__file__,
            config_module=self.config_module,
            config_name=self.selected,
            runtime_override_key=self.runtime_override_key
        ))
        print('writing config `%s` into %s' % (self.selected, self.config_path))
        with open(self.config_path, 'w+') as fh:
            fh.write(templated)

        return self
