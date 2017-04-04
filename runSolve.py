import math
import time
import random
import argparse
import json
from NetworkGraph import NetworkGraph
from helpers import minToHour, directDistance
from RouteMatrix import RouteMatrix, solve
from DroneRoute import DroneRoute
from xlutils.copy import copy
import xlwt
import xlrd
import networkx as nx


def start():
    start_time = time.time()
    dist_center = 3205 #distribution center node
    vehicles = 1 #input("Enter Number of Trucks(1-4): ")
    csv = 'testData.csv'
    routeSize = input("Enter Route Size(10-30): ")
    network = NetworkGraph()
    nodes, count = network.importData(csv)
    workbook1 = xlrd.open_workbook('TruckData.xls', on_demand = True, formatting_info=True)
    wb1 = copy(workbook1)
    ws1 = wb1.get_sheet(0)
    workbook2 = xlrd.open_workbook('DroneData.xls', on_demand = True, formatting_info=True)
    wb2 = copy(workbook2)
    ws2 = wb2.get_sheet(0)
    ws1.write(2, 1, routeSize)
    ws2.write(2, 1, routeSize)

    # print trial
    # print extra

    for index in range(0,10):
        optimal = {}
        gate = False
        print "Full Truck Route"
        while gate is False:
            try:
                trial, timeDictionary = network.makeRoute(routeSize, dist_center)
                truckMatrix = RouteMatrix(trial, network.graph, False)
                #droneMatrix = RouteMatrix(trial, network.graph, True)
                optimal = {}
                optimal, truckDist, longest, shortest = solve(network.graph, trial, len(trial), truckMatrix)
            except nx.NetworkXNoPath:
                print "no node path"
            else:
                gate = True

        ws1.write((index+5), 1, truckDist)
        ws1.write((index+5), 2, shortest)
        ws1.write((index+5), 3, longest)


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
            optimal, truckDist, longest, shortest = solve(network.graph, morning, len(morning), truckMatrix)
            ws1.write((index+5), 4, truckDist)
            ws1.write((index+5), 5, shortest)
            ws1.write((index+5), 6, longest)
        print "\nNoon Truck Route"
        if len(noon) > 1:
            optimal, truckDist, longest, shortest = solve(network.graph, noon, len(noon), truckMatrix)
            ws1.write((index+5), 7, truckDist)
            ws1.write((index+5), 8, shortest)
            ws1.write((index+5), 9, longest)
        print "\nNight Truck Route"
        if len(night) > 1:
            optimal, truckDist, longest, shortest = solve(network.graph, night, len(night), truckMatrix)
            ws1.write((index+5), 10, truckDist)
            ws1.write((index+5), 11, shortest)
            ws1.write((index+5), 12, longest)

        droneCenter = DroneRoute(dist_center, trial, network.graph, timeDictionary)
        finalRoute, avg, numDrones, shortest, longest  = droneCenter.createTimeRoute()
    #for x in finalRoute:
        #print x
    #droneCenter.additions(extra)
        droneDistance = droneCenter.totalDistance()
        # print "Drone Distance - ", droneDistance
        # print "Average Distance", droneDistance/routeSize
        # print "Number of Drones", numDrones

        ws2.write((index+5), 1, droneDistance)
        ws2.write((index+5), 2, shortest)
        ws2.write((index+5), 3, longest)
        ws2.write((index+5), 4, avg)
        ws2.write((index+5), 5, numDrones)
    wb1.save('TruckData.xls')
    wb2.save('DroneData.xls')
    # print ""
    # print "Hybrid Method"
    # maxDist = input("What is the max distance for drones: " )
    # distancesDrone = droneCenter.getDistances()
    # droneTrial = []
    # truckTrial = []
    # truckTrial.append(dist_center)
    # for key, val in distancesDrone.iteritems():
    #     if val < maxDist:
    #         droneTrial.append(key)
    #     else:
    #         truckTrial.append(key)
    # #truckTrial.append(dist_center)
    # hybridOptimal = solve(network.graph, truckTrial, len(truckTrial), truckMatrix)
    # print droneTrial
    # droneCenter.createTimeRoute(droneTrial)
    # print "Drone - ", droneCenter.totalDistance(droneTrial)
    print("--- %s minutes ---" % ((time.time() - start_time)/60))

if __name__ == '__main__':

    start()
