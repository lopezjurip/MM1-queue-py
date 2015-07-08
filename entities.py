from base_entities import SimObject, Server, Action

__author__ = "Patricio Lopez Juri"


class Consultory(Server):
    def __init__(self, env, arrival_rate, doctors, bond_sellers, receptionists,
                 capacity, operation):
        super().__init__(env, rate=arrival_rate, capacity=capacity)
        self.doctors = doctors
        self.bond_sellers = bond_sellers
        self.receptionists = receptionists
        self.operation = operation

    def arrival(self, client):
        return self.process(client)

    def attend(self, client):
        self.log(client, Action.arrive, self.env.now)
        with self.resource.request() as solicitude:
            yield solicitude
            self.log(client, Action.enter, self.env.now)
            yield self.env.process(self.operation(self, client))
            self.log(client, Action.exit, self.env.now)


class Client(SimObject):
    def __init__(self, env):
        super().__init__(env)
        self.done = False


class Reception(Server):
    pass


class BondSeller(Server):
    pass


class Doctor(Server):
    pass
