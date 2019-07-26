from multiprocessing import Process, Queue


class Person:
    name = 'Person'

    def __init__(self):
        self.fname = 'person'

    def say(self):
        print(self.name, self.fname)


class Boy(Person):
    name = 'Boy'

    def __init__(self):
        self.fname = 'boy'

    def say(self):
        print('boy say')
        super().say()


if __name__ == '__main__':
    b = Boy()
    b.say()
