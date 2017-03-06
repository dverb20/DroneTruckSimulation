import math
import time
import random
import argparse
import json
from NetworkGraph import NetworkGraph
from helpers import minToHour, directDistance
from RouteMatrix import RouteMatrix
from DroneRoute import DroneRoute


def start():
    start_time = time.time()
    dist_center = 3205 #distribution center node
    vehicles = 1 #input("Enter Number of Trucks(1-4): ")
    csv = 'testData.csv'
    routeSize = input("Enter Route Size(10-30): ")
    network = NetworkGraph()
    nodes, count = network.importData(csv)
    trial, extra = network.makeRoute(routeSize, dist_center, 5)
    print trial
    print extra
    matrix = RouteMatrix(trial, network.graph, True)
    droneCenter = DroneRoute(dist_center, trial, matrix)
    droneCenter.createTimeRoute(trial)

    print "Drone - ", droneCenter.totalDistance(network.graph)
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':

    start()
