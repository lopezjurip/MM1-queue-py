from enum import Enum
from collections import defaultdict

__author__ = "Patricio Lopez Juri"


class Action(Enum):
    arrive = 0
    enter = 1
    exit = 2


class Log:
    enabled = False
    start_hour = 0
    start_minute = 0

    @staticmethod
    def timerize(number):
        return str(number).zfill(2)

    @staticmethod
    def d(time, user, action, target):
        if Log.enabled:
            hour = Log.timerize(Log.start_hour + int(time))
            minutes = Log.timerize(Log.start_minute + round(60 * (time % 1.0)))
            line = "Time: {}:{} ({})| \t{} \t-> \t{} \t-> \t{}".format(
                hour,
                minutes,
                time,
                user,
                action,
                target
            )
            print(line)


class Stat:
    DEFAULT_TIME = -1

    def __init__(self, client=None):
        self.client = client
        self.stats = defaultdict(lambda: Stat.DEFAULT_TIME)

    def __getitem__(self, key):
        if isinstance(key, Action):
            return self.stats[key]
        elif isinstance(key, slice):
            start = self.stats[key.start]
            end = self.stats[key.stop]
            return end - start

    def __setitem__(self, key, value):
        self.stats[key] = value

    @property
    def arrival(self):
        return self.stats[Action.arrive]

    @property
    def attention(self):
        return self.stats[Action.enter]

    @property
    def exit(self):
        return self.stats[Action.exit]
