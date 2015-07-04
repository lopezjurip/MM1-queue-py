from entities import *
import numpy
import simpy

__author__ = "Patricio Lopez Juri"


class Simulation:

    def __init__(self, capacity, LAMBDA, ALPHA, BETA, MU, GAMMA, p, q):
        self.capacity = capacity
        self.LAMBDA = LAMBDA  # Clients/hour
        self.ALPHA = ALPHA  # Clients/hour
        self.BETA = BETA  # Clients/hour
        self.MU = MU  # Clients/hour
        self.GAMMA = GAMMA  # Clients/hour
        self.p = p  # Probability
        self.q = q  # Probability

    def start(self, env):
        p, q = self.p, self.q

        def operation(consultory, client):
            '''
            This is how the consultory treats each client.
            '''
            if numpy.random.uniform() <= p:
                # Go to the bond seller
                yield consultory.env.process(
                    consultory.bond_sellers[0].attend(client)
                )

            # Everyone must go to the receptionist.
            yield consultory.env.process(
                consultory.receptionists[0].attend(client)
            )

            # Chose doctor.
            doctor = consultory.doctors[
                0 if numpy.random.uniform() <= q else 1
            ]
            yield consultory.env.process(doctor.attend(client))

            # Client exists
            client.done = True

        consultory = Consultory(
            env=env,
            arrival_rate=self.LAMBDA,
            doctors=[Doctor(env, self.MU), Doctor(env, self.GAMMA)],
            bond_sellers=[BondSeller(env, self.ALPHA)],
            receptionists=[Reception(env, self.BETA)],
            capacity=self.capacity,
            operation=operation
        )

        # Start simulation
        while True:
            client = Client(env)
            yield env.process(consultory.arrival(client))
            env.process(consultory.attend(client))


if __name__ == '__main__':

    TIMEOUT = 2
    simulation = Simulation(
        capacity=10000000000,
        LAMBDA=10,
        ALPHA=10,
        BETA=12,
        MU=5,
        GAMMA=9,
        p=0.8,
        q=0.3
    )

    env = simpy.Environment()
    env.process(simulation.start(env))
    env.run(until=TIMEOUT)
