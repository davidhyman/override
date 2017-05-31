from override.tools import Project


def run():
    Project(
        config_module='example.my_configs',
        config_path='configuration/config.py',
        relative_root=__file__,
        runtime_override_key='fizz',
    ).select_config('two').apply_config()

if __name__ == '__main__':
    run()
