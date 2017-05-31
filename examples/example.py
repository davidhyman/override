"""
for example, you would execute this code as part of a build or initial setup step
"""

from project import Project


def after_configuration_write():
    print('this code could output a subset of the config for other purposes')


def run():
    Project(
        config_module='examples.my_configs',
        config_path='built_config.py',
        relative_root=__file__,
        runtime_override_key='fizz',
        post_configure_callback=after_configuration_write
    ).apply_config('two')

if __name__ == '__main__':
    run()
