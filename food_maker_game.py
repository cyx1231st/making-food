import eventlet
eventlet.monkey_patch()
import random


def make_food(food):
    # Note(Yingxin): Making food requires 2.5 seconds...
    eventlet.sleep(2.5)
    return food + 1


class FoodMaker(object):
    def __init__(self):
        self.food = 0
        self.events = []
        eventlet.spawn(self._make_food)
        self.p_event = eventlet.event.Event()

    def _make_food(self):
        while(True):
            consumer = self.p_event.wait()
            print "maker: got request from %s, making food..." % consumer

            self.food = make_food(self.food)

            events = self.events
            self.events = []
            consumers = []
            for evt, consumer in events:
                evt.send(self.food)
                consumers.append(consumer)
            self.p_event.reset()
            print "maker: ok, food %s delivered to %s" % (self.food, consumers)

    def get_food(self, consumer):
        if not self.p_event.ready():
            self.p_event.send(consumer)
        evt = eventlet.event.Event()
        self.events.append((evt, consumer))
        return evt.wait()


def eat_and_get_hungry(food):
    eventlet.sleep(random.randint(3, 10))


class FoodConsumer(object):
    def __init__(self, name, maker):
        self.name = name
        self.maker = maker
        eventlet.spawn(self._consume_food)

    def _consume_food(self):
        while(True):
            print "consumer %s want food" % self.name
            food = self.maker.get_food(self.name)
            print "consumer %s got food %s and eat..." % (self.name, food)
            eat_and_get_hungry(food)


def main():
    maker = FoodMaker()
    for i in range(0, 10):
        FoodConsumer(i, maker)

    eventlet.hubs.get_hub().switch()


if __name__ == "__main__":
    main()
