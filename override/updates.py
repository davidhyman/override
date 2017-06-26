import argparse
import ast
import os

from override.logs import logger


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
