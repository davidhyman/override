colour = 'red'
size = 5
quantity = 3
area = 0


def post_import(config):
    config['area'] = config['size'] * config['quantity']
    print('area is being calculated')
