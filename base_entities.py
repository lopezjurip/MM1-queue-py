from logger import Log, Action
import numpy
import simpy

__author__ = "Patricio Lopez Juri"


class SimObject:
    id_counter = 0

    def __init__(self, env):
        self.env = env
        self.__class__.id_counter += 1
        self.id = self.__class__.id_counter

    def __str__(self):
        return "{} #{}".format(self.__class__.__name__, self.id)


class Server(SimObject):

    def __init__(self, env, rate, capacity=1):
        super().__init__(env)
        self.rate = rate
        self.resource = simpy.Resource(env, capacity=capacity)

    def log(self, client, action):
        Log.d(time=self.env.now, user=client, action=action, target=self)

    def process(self, client):
        yield self.env.timeout(numpy.random.exponential(1 / self.rate))

    def attend(self, client):
        self.log(client, Action.arrive)
        with self.resource.request() as solicitude:
            yield solicitude
            self.log(client, Action.enter)
            yield self.env.process(self.process(client))
            self.log(client, Action.exit)
