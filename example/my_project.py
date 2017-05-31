"""
for example, this represents a project that uses configuration settings.
As long as the system has been instantiated, you will have
code completion and inheritance working as expected in Python
"""

import built_config


def run():
    print(dir(built_config))
    print('starting project. the colour is %s, the area is %s' % (built_config.colour, built_config.area))
    return built_config

if __name__ == '__main__':
    run()
