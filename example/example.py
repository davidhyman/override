"""
for example, you would execute this code as part of a build or initial setup step
"""

from override.tools import Project


def run():
    Project(
        config_module='my_configs',
        config_path='built_config.py',
        relative_root=__file__,
        runtime_override_key='fizz',
    ).apply_config('two')

if __name__ == '__main__':
    run()
