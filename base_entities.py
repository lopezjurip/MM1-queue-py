from logger import Log, Action, Stat
from collections import defaultdict
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
        self.stats = defaultdict((lambda : Stat()))

    def log(self, client, action):
        time = self.env.now
        self.stats[client][action] = time
        Log.d(time=time, user=client, action=action, target=self)

    def waiting_times(self, start=Action.arrive, end=Action.exit):
        return [stat[start:end] for stat in self.stats.values()]

    def mean_waiting_times(self, start=Action.arrive, end=Action.exit):
        return numpy.mean(self.waiting_times(start, end))

    def process(self, client):
        yield self.env.timeout(numpy.random.exponential(1 / self.rate))

    def attend(self, client):
        self.log(client, Action.arrive)
        with self.resource.request() as solicitude:
            yield solicitude
            self.log(client, Action.enter)
            yield self.env.process(self.process(client))
            self.log(client, Action.exit)
