from example.configuration import config


def run():
    print(dir(config))
    print('starting project. the colour is %s' % config.colour)
    return config

if __name__ == '__main__':
    run()
