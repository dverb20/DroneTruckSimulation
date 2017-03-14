import math
import time
import random
import argparse
import json
from NetworkGraph import NetworkGraph
from helpers import minToHour, directDistance
from RouteMatrix import RouteMatrix, solve
from DroneRoute import DroneRoute
import networkx as nx


def start():
    start_time = time.time()
    dist_center = 3205 #distribution center node
    vehicles = 1 #input("Enter Number of Trucks(1-4): ")
    csv = 'testData.csv'
    routeSize = input("Enter Route Size(10-30): ")
    network = NetworkGraph()
    nodes, count = network.importData(csv)

    # print trial
    # print extra


    optimal = {}
    gate = False
    while gate is False:
        try:
            trial, extra = network.makeRoute(routeSize, dist_center, 5)
            truckMatrix = RouteMatrix(trial, network.graph, False)
            droneMatrix = RouteMatrix(trial, network.graph, True)
            optimal = {}
            optimal = solve(network.graph, trial, len(trial), truckMatrix)
        except nx.NetworkXNoPath:
            print "no node path"
        else:
            gate = True

    droneCenter = DroneRoute(dist_center, trial, droneMatrix)
    droneCenter.createTimeRoute(trial)
    #droneCenter.additions(extra)

    print "Drone - ", droneCenter.totalDistance(network.graph)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':

    start()
