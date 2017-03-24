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
    print "Full Truck Route"
    while gate is False:
        try:
            trial, timeDictionary = network.makeRoute(routeSize, dist_center)
            truckMatrix = RouteMatrix(trial, network.graph, False)
            #droneMatrix = RouteMatrix(trial, network.graph, True)
            optimal = {}
            optimal = solve(network.graph, trial, len(trial), truckMatrix)
        except nx.NetworkXNoPath:
            print "no node path"
        else:
            gate = True

    morning = []#360 - 660
    morning.append(dist_center)
    noon = []#660 - 960
    noon.append(dist_center)
    night = []#960-1260
    night.append(dist_center)

    for key, val in timeDictionary.iteritems():
        if val <661:
            morning.append(key)
        elif val > 660 and val < 961:
            noon.append(key)
        elif val > 960:
            night.append(key)

    print "\nMorning Truck Route"
    if len(morning) > 1:
        solve(network.graph, morning, len(morning), truckMatrix)
    print "\nNoon Truck Route"
    if len(noon) > 1:
        solve(network.graph, noon, len(noon), truckMatrix)
    print "\nNight Truck Route"
    if len(night) > 1:
        solve(network.graph, night, len(night), truckMatrix)

    droneCenter = DroneRoute(dist_center, trial, network.graph, timeDictionary)
    droneCenter.createTimeRoute()
    #droneCenter.additions(extra)

    print "Drone Distance - ", droneCenter.totalDistance()
    print ""
    print "Hybrid Method"
    maxDist = input("What is the max distance for drones: " )
    distancesDrone = droneCenter.getDistances()
    droneTrial = []
    truckTrial = []
    truckTrial.append(dist_center)
    for key, val in distancesDrone.iteritems():
        if val < maxDist:
            droneTrial.append(key)
        else:
            truckTrial.append(key)
    truckTrial.append(dist_center)
    hybridOptimal = solve(network.graph, truckTrial, len(truckTrial), truckMatrix)
    print droneTrial
    droneCenter.createTimeRoute(droneTrial)
    print "Drone - ", droneCenter.totalDistance(droneTrial)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':

    start()
