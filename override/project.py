import os
import traceback

import pystache
from override.logs import logger

DEFAULT_TEMPLATE = '''# -*- coding: utf-8 -*-
# This file is auto-generated from settings in:
# {{template_blame}}

from {{config_module}}.{{config_name}} import *
{{#post_import_handler}}
{{post_import_handler}}(locals())
{{/post_import_handler}}

{{#runtime_override_key}}
from override import RuntimeUpdates as _RTU  # noqa
_RTU('{{runtime_override_key}}').apply_all(locals())
{{/runtime_override_key}}
{{#post_load_handler}}
{{post_load_handler}}(locals())
{{/post_load_handler}}
'''


class Project:
    """
    A project is an instance of a configuration system.

    Describes where config modules can be imported from
    and where the shim file is to be placed
    """

    def __init__(
            self,
            config_path='configs',
            config_module='config.py',
            relative_root=None,
            runtime_override_key='override',
            post_import_handler=None,
            post_load_handler=None,
            post_configure_callback=None,
            template=DEFAULT_TEMPLATE,
            template_path=None,
    ):
        """
        :param config_path: full name of the shim file to be generated (path can be relative)
        :param config_module: python module path to use when importing config variants
        :param relative_root: [opt] path from which others are relative
        :param runtime_override_key: [opt] the string used when overriding settings for cli and env
        :param post_import_handler: [opt] string name of function to invoke after hierarchy load
        :param post_load_handler: [opt] string name of function to invoke after hierarchy + overrides load
        :param post_configure_callback: [opt] function to be directly called whenever this config is written
        :param template: [opt] a string defining the shim
        :param template_path: [opt] a path to a file containing a shim template (path can be relative)
        """
        self.config_path = config_path
        self.config_module = config_module
        self.template_path = template_path
        self.template = template
        self.relative_root = os.path.abspath(os.path.dirname(relative_root)) if relative_root else None
        self.runtime_override_key = runtime_override_key
        self.post_import_handler = post_import_handler
        self.post_load_handler = post_load_handler
        self.post_configure_callback = post_configure_callback

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

        populated = pystache.render(self.template, dict(
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
            fh.write(populated)

        if self.post_configure_callback:
            logger.debug('invoking callback: %r', self.post_configure_callback)
            self.post_configure_callback()

        return self
