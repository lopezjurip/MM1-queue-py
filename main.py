from entities import *
import numpy
import simpy

__author__ = "Patricio Lopez Juri"


class Simulation:

    def __init__(self, env, capacity, LAMBDA, ALPHA, BETA, MU, GAMMA, p, q):
        self.env = env
        self.capacity = capacity
        self.LAMBDA = LAMBDA  # Clients/hour
        self.ALPHA = ALPHA  # Clients/hour
        self.BETA = BETA  # Clients/hour
        self.MU = MU  # Clients/hour
        self.GAMMA = GAMMA  # Clients/hour
        self.p = p  # Probability
        self.q = q  # Probability
        self.consultory = self.setup(env)

    def setup(self, env):
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

            # Client exits
            client.done = True

        return Consultory(
            env=env,
            arrival_rate=self.LAMBDA,
            doctors=[Doctor(env, self.MU), Doctor(env, self.GAMMA)],
            bond_sellers=[BondSeller(env, self.ALPHA)],
            receptionists=[Reception(env, self.BETA)],
            capacity=self.capacity,
            operation=operation
        )

    def start(self, env):
        '''
        Start simulation
        '''
        while True:
            client = Client(env)
            yield env.process(self.consultory.arrival(client))
            env.process(self.consultory.attend(client))



if __name__ == '__main__':

    env = simpy.Environment()

    TIMEOUT = 10
    simulation = Simulation(
        env=env,
        capacity=float('inf'),
        LAMBDA=10,
        ALPHA=10,
        BETA=12,
        MU=5,
        GAMMA=9,
        p=0.8,
        q=0.3
    )

    env.process(simulation.start(env))
    env.run(until=TIMEOUT)
    print("End of simulation.")