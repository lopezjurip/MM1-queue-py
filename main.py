import numpy
import simpy

from entities import *

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

    # ----------------------------------------------------------------------------

    REPETITIONS = 10
    TIMEOUT = 1000
    PARAMS = {
        'capacity': float('inf'),
        'LAMBDA': 10,
        'ALPHA': 10,
        'BETA': 12,
        'MU': 5,
        'GAMMA': 9,
        'p': 0.8,
        'q': 0.3
    }

    def simulate(duration, **params):
        env = simpy.Environment()
        simulation = Simulation(env=env, **params)
        env.process(simulation.start(env))
        env.run(until=duration)
        return simulation

    simulations = [simulate(TIMEOUT, **PARAMS) for n in range(REPETITIONS)]

    # ----------------------------------------------------------------------------

    average_clients_per_consultory = [
        s.consultory.average_unfinished_clients(frm=TIMEOUT - 1, to=TIMEOUT) for s in simulations
        ]
    average_clients_in_consultory = numpy.average(average_clients_per_consultory)
    print(
        "Average number of clients in consultory:",
        average_clients_in_consultory
    )

    # ----------------------------------------------------------------------------

    queued_waiting_times_per_bond_seller = [
        s.consultory.bond_sellers[0].average_queue_waiting_time(to=TIMEOUT) for s in simulations
        ]
    average_waiting_time_in_bond_seller = numpy.average(queued_waiting_times_per_bond_seller)
    print("Average queued waiting time in bond seller:", average_waiting_time_in_bond_seller)

    queued_waiting_times_per_receptionist = [
        s.consultory.receptionists[0].average_queue_waiting_time(to=TIMEOUT) for s in simulations
        ]
    average_waiting_time_in_receptionist = numpy.average(queued_waiting_times_per_receptionist)
    print("Average queued waiting time in receptionist:", average_waiting_time_in_receptionist)

    queued_waiting_times_per_doctor1 = [
        s.consultory.doctors[0].average_queue_waiting_time(to=TIMEOUT) for s in simulations
        ]
    average_waiting_time_in_doctor1 = numpy.average(queued_waiting_times_per_doctor1)
    print("Average queued waiting time in doctor1:", average_waiting_time_in_doctor1)

    queued_waiting_times_per_doctor2 = [
        s.consultory.doctors[1].average_queue_waiting_time(to=TIMEOUT) for s in simulations
        ]
    average_waiting_time_in_doctor2 = numpy.average(queued_waiting_times_per_doctor2)
    print("Average queued waiting time in doctor2:", average_waiting_time_in_doctor2)

    # ----------------------------------------------------------------------------

    queued_clients_per_bond_seller = [
        s.consultory.bond_sellers[0].average_queued_clients(to=TIMEOUT) for s in simulations
        ]
    average_clients_queued_bond_seller = numpy.average(queued_clients_per_bond_seller)
    print("Average clients queued in bond seller:", average_clients_queued_bond_seller)

    queued_clients_per_receptionist = [
        s.consultory.receptionists[0].average_queued_clients(to=TIMEOUT) for s in simulations
        ]
    average_clients_queued_receptionist = numpy.average(queued_clients_per_receptionist)
    print("Average clients queued in receptionist:", average_clients_queued_receptionist)

    queued_clients_per_doctor1 = [
        s.consultory.doctors[0].average_queued_clients(to=TIMEOUT) for s in simulations
        ]
    average_clients_queued_doctor1 = numpy.average(queued_clients_per_doctor1)
    print("Average clients queued in doctor1:", average_clients_queued_doctor1)

    queued_clients_per_doctor2 = [
        s.consultory.doctors[1].average_queued_clients(to=TIMEOUT) for s in simulations
        ]
    average_clients_queued_doctor2 = numpy.average(queued_clients_per_doctor2)
    print("Average clients queued in doctor2:", average_clients_queued_doctor2)

    # ----------------------------------------------------------------------------

    print("End of simulation.")
