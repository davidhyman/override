"""
for example, this represents a project that uses configuration settings.
As long as the system has been instantiated, you will have
code completion and inheritance working as expected in Python
"""

import pprint
from examples import built_config


def run():
    pprint.pprint({k: v for k, v in vars(built_config).items() if not k.startswith('__')})
    print('starting project. the colour is %s, the area is %s' % (built_config.colour, built_config.area))
    return built_config

if __name__ == '__main__':
    run()
