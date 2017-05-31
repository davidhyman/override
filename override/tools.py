import argparse
import ast
import importlib
import logging
import os
import traceback

import pystache

# TODO: boilerplate handling (or silencing)
# TODO: alternative handling logic for updates (tuples, lists, sets etc)
# TODO: think of a way round the 'test mode' problem
# TODO: 'safe' mode (dont set keys that don't already exist)?
# TODO: 'safe' json/yaml/ini override config file

# TODO: config differ


DEFAULT_TEMPLATE = '''# -*- coding: utf-8 -*-
# This file is auto-generated from settings in:
# {{template_blame}}

from {{config_module}}.{{config_name}} import *
{{#post_import_handler}}
{{post_import_handler}}(locals())
{{/post_import_handler}}

{{#runtime_override_key}}
from override.tools import RuntimeUpdates as _RTU
_RTU('{{runtime_override_key}}').apply_all(locals())
{{/runtime_override_key}}
{{#post_load_handler}}
{{post_load_handler}}(locals())
{{/post_load_handler}}
'''


def get_logger(name):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(name)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)
    return logger

logger = get_logger('override')


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
            logger.info('setting %s -> %r %s as %s', k, v, reason, type(v).__name__)
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
        post_import_handler=None,
        post_load_handler=None,
    ):
        self.config_path = config_path
        self.config_module = config_module
        self.template_path = template_path
        self.template = template
        self.relative_root = os.path.abspath(os.path.dirname(relative_root)) if relative_root else None
        self.runtime_override_key=runtime_override_key
        self.post_import_handler = post_import_handler
        self.post_load_handler = post_load_handler

        # catch the current stack to see where we were invoked, and then str it to avoid holding references
        self.caused_by = str(traceback.extract_stack()[-2][0])

        self._selected = None

        if self.relative_root:
            # set all internal paths based on a relative directory
            self.config_path = os.path.join(self.relative_root, self.config_path)
            if self.template_path:
                self.template_path = os.path.join(self.relative_root, self.template_path)

        if self.template_path:
            with open(template_path, 'r') as fh:
                self.template = fh.read()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, name):
        # we could do some logging or other validation here
        self._selected = name

    def validate_config(self):
        if not self.selected:
            raise ValueError('No config was selected')
        return self

    def apply_config(self, name=None):
        if name:
            self.selected = name

        templated = pystache.render(self.template, dict(
            template_blame=self.caused_by,
            config_module=self.config_module,
            config_name=self.selected,
            runtime_override_key=self.runtime_override_key,
            post_import_handler=self.post_import_handler,
            post_load_handler=self.post_load_handler,
        ))
        logger.info('writing config `%s` into %s', self.selected, self.config_path)
        self.validate_config()
        with open(self.config_path, 'w') as fh:
            fh.write(templated)

        return self


def init_from_command():
    parser = argparse.ArgumentParser()
    parser.add_argument('module_name')
    args = parser.parse_known_args()[0]
    my_module, my_package = args.module_name.rsplit(':', 1)
    module = importlib.import_module(my_module, my_package)
    project = getattr(module, my_package)
    if not isinstance(project, Project):
        raise TypeError('%r ought to be an instance of %r' % (project, Project))
    RuntimeUpdates().apply_all(project)
    project.apply_config()
