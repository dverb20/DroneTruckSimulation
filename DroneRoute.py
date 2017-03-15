import numpy as np
import networkx as nx
import math
import time
import random
import argparse
import json
from helpers import minToHour, directDistance
from terminaltables import AsciiTable, SingleTable
from termcolor import colored

class DroneRoute(object):
    """Contains attributes about which drones go where"""

    def __init__(self, center, nodes, graph, timeDictionary = None):
        #If no times given, create times
        self.center = center
        self.nodes = nodes
        self.distances = {}#dictionary with distances from center to the node
        if timeDictionary is None:
            timeDictionary = {}
            for x in nodes:
                if x is not center:
                    timeDictionary[x] = random.randint(360,1260)
                    self.distances[x] = directDistance(graph.node[x],graph.node[center])
            sortedList = sorted(timeDictionary.items(), key=lambda x: x[1])
            #print sortedList
            #print json.dumps(sortedList, indent=4, sort_keys=True)
        else:
            sortedList = sorted(timeDictionary.items(), key=lambda x: x[1])
            #print json.dumps(sortedList, indent=4, sort_keys=True)
        self.times = sortedList
        for x in self.times:
            self.distances[x[0]] = directDistance(graph.node[x[0]],graph.node[center])

    def createTimeRoute(self, nodes = None):
        #Must incorporate battery charge time, and multiple drone take off
        speed = 35
        center = self.center
        distances = self.distances
        returnTime = []
        route, times = self.getRoute()
        if nodes:
            route = nodes
        returnTime.append(0)
        droneOrder = []
        #droneLimit = 1
        finalRoute = []
        tableRoute = []
        numDrones = 0
        tableRoute.append(['node', 'drone', 'distance', 'leave', 'return', 'time'])
        colors = ['red', 'blue', 'green', 'yellow', 'purple']

        #while attempt is True:
        for x in range(len(route)-1):
            dist = distances[route[x]]#Dont use node, use index of node in trial, aha
            time = (dist / speed) * 60
            leave = times[x] - time - 2
            j = 0
            enter = True
            #This is for using least used drone priority
            while enter is True:
                #
                if leave > min(returnTime):
                    enter = False
                    index = returnTime.index(min(returnTime))
                    returnTime[index] = times[x] + time + 2
                    finalRoute.append({'node': route[x],'travel': minToHour(time*2+4), 'drone': (index+1), 'leave': minToHour(leave), 'return': minToHour(returnTime[index]), 'distance': round(dist, 2)})
                    tableRoute.append([route[x], colored(str(index+1), colors[index%5]), round(dist,3), minToHour(leave), minToHour(returnTime[index]),minToHour(time*2+4)])
                    droneOrder.append(index+1)
                else:
                    returnTime.append(0)
                    numDrones += 1
                #j += 1
        table = SingleTable(tableRoute, "Drone Flight Schedule")
        #table.justify_columns[2] = 'right'
        table.inner_row_border = True
        table.inner_heading_row_border = True
        print(table.table)
        #for f in finalRoute:
            #print json.dumps(f, indent=4, sort_keys=True)
        #print ""
        print "Drone Order"
        print droneOrder
        print "length - ", len(droneOrder)
        return finalRoute

    def additions(self, additions):
        times = self.times
        for a in additions:
            times[a[0]] = a[1]
        sortedList = sorted(times.items(), key=lambda x: x[1])
        self.times = sortedList

    def getRoute(self):
        route = []
        times = []
        for x in self.times:
            route.append(x[0])
            times.append(x[1])
        return route, times
    def getDistances(self):
        return self.distances

    def totalDistance(self, alternate = None):
        if alternate is None:
            route, times = self.getRoute()
        else:
            route = alternate
        center = self.center
        distance = 0
        for x in route:
            distance += self.distances[x]*2
        return distance
