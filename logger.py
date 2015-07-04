from enum import Enum

__author__ = "Patricio Lopez Juri"


class Action(Enum):
    arrive = 0
    enter = 1
    exit = 2


class Log:
    enabled = True
    start_hour = 9
    start_minute = 0

    @staticmethod
    def timerize(number):
        return str(number).zfill(2)

    @staticmethod
    def d(time, user, action, target):
        if Log.enabled:
            hour = Log.timerize(Log.start_hour + int(time))
            minutes = Log.timerize(Log.start_minute + round(60 * (time % 1.0)))
            line = "Time: {}:{} | \t{} \t-> \t{} \t-> \t{}".format(
                hour,
                minutes,
                user,
                action,
                target
            )
            print(line)
