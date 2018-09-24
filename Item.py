class Item(object):
    def __init__(self):
        self.generate_random()
        
    def generate_random(self):
        cost = 5 * random.randint(0, 4)
