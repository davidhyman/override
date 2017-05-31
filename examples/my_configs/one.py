colour = 'red'
size = 5
quantity = 3
area = 0
sam = {
    'ham': 'green',
    'eggs': 'green'
}


class Box:
    donuts = 5


def post_import(config):
    config['area'] = config['size'] * config['quantity']
    print('area is being calculated')
