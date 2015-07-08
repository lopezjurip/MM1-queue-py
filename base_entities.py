from collections import defaultdict

import numpy
import simpy

from logger import Log, Action, Stat

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
        self.stats = defaultdict((lambda: Stat()))

    def __getitem__(self, client):
        return self.stats[client]

    def log(self, client, action, time):
        self.stats[client][action] = time
        Log.d(time=time, user=client, action=action, target=self)

    def waiting_times(self, start=Action.arrive, end=Action.exit, frm=0, to=float('inf')):
        def condition(client, stat):
            valid_start = frm <= stat[start] <= to
            valid_end = stat[end] <= to or stat[end] == Stat.DEFAULT_TIME
            return valid_start and valid_end

        def get_time(self, stat):
            start_time = stat[start]
            end_time = stat[end] if stat[end] != Stat.DEFAULT_TIME else to
            return end_time - start_time

        return [
            get_time(self, stat) for client, stat in self.stats.items() if condition(client, stat)
            ]

    def queued_waiting_times(self, frm=0, to=float('inf')):
        return self.waiting_times(start=Action.arrive, end=Action.enter, frm=frm, to=to)

    def attention_waiting_times(self, frm=0, to=float('inf')):
        return self.waiting_times(start=Action.enter, end=Action.exit, frm=frm, to=to)

    def average_waiting_time(self, frm=0, to=float('inf')):
        return numpy.average(self.waiting_times(frm=frm, to=to))

    def average_queue_waiting_time(self, frm=0, to=float('inf')):
        return numpy.average(self.queued_waiting_times(frm, to))

    def average_attention_waiting_time(self, frm=0, to=float('inf')):
        return numpy.average(self.attention_waiting_times(frm, to))

    def clients(self, at=float('inf'), condition=None):
        def final_condition(client, stat):
            in_time = stat.arrival <= at and stat.arrival != Stat.DEFAULT_TIME
            if condition:
                return in_time and condition(client, stat)
            return in_time

        return [
            client for client, stat in self.stats.items() if final_condition(client, stat)
            ]

    def finished_clients(self, at=float('inf')):
        """
        Clients who entered and completed their process at given time.
        :param to: Time to check.
        :return: Client list
        """

        def condition(client, stat):
            return stat.exit <= at and stat.exit != Stat.DEFAULT_TIME

        return self.clients(at, condition)

    def unfinished_clients(self, at=float('inf')):
        """
        Clients who entered but has not leave the server at given time.
        :param to: Time to check.
        :return: Client list
        """

        def condition(client, stat):
            return stat.exit > at or stat.exit == Stat.DEFAULT_TIME

        return self.clients(at, condition)

    def queued_clients(self, at=float('inf')):
        """
        Clients who entered and still in queue at given time.
        :param to: Time to check.
        :return: Client list
        """

        def condition(client, stat):
            return stat.attention > at or stat.attention == Stat.DEFAULT_TIME

        return self.clients(at, condition)

    def __calculate_average_clients(self, method, frm=1, to=None):
        to = to or round(max([s.exit for c, s in self.stats.items()]))
        return numpy.average([len(method(at=t)) for t in range(frm, to)])

    def average_clients(self, frm=1, to=None):
        return self.__calculate_average_clients(self.clients, frm, to)

    def average_finished_clients(self, frm=1, to=None):
        return self.__calculate_average_clients(self.finished_clients, frm, to)

    def average_unfinished_clients(self, frm=1, to=None):
        return self.__calculate_average_clients(self.unfinished_clients, frm, to)

    def average_queued_clients(self, frm=1, to=None):
        return self.__calculate_average_clients(self.queued_clients, frm, to)

    def process(self, client):
        """
        This is the main operation of the server.
        It takes a random exponential time based on the instance 'rate' variable.
        :param client: Client to attend
        :return:
        """
        yield self.env.timeout(numpy.random.exponential(1 / self.rate))
        # yield self.env.timeout(random.expovariate(1 / self.rate))

    def attend(self, client):
        """
        The client enters to the server and waits to be attended.
        Goes to the queue if the server is busy.
        :param client: Arrived client
        :return:
        """
        self.log(client, Action.arrive, self.env.now)
        with self.resource.request() as solicitude:
            yield solicitude
            self.log(client, Action.enter, self.env.now)
            yield self.env.process(self.process(client))
            self.log(client, Action.exit, self.env.now)
