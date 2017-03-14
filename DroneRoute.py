import numpy as np
import networkx as nx
import math
import time
import random
import argparse
import json
from helpers import minToHour, directDistance

class DroneRoute(object):
    """Contains attributes about which drones go where"""

    def __init__(self, center, nodes, matrix, timeDictionary = None):
        #If no times given, create times
        self.center = center
        self.matrix = matrix
        self.nodes = nodes
        self.numDrones = 1
        if timeDictionary is None:
            timeDictionary = {}
            for x in nodes:
                if x is not center:
                    timeDictionary[x] = random.randint(360,1260)
            sortedList = sorted(timeDictionary.items(), key=lambda x: x[1])
            #print sortedList
            #print json.dumps(sortedList, indent=4, sort_keys=True)
        else:
            sortedList = sorted(timeDictionary.items(), key=lambda x: x[1])
            #print json.dumps(sortedList, indent=4, sort_keys=True)
        self.times = sortedList

    def createTimeRoute(self, nodes):
        #Must incorporate battery charge time, and multiple drone take off
        speed = 35
        center = self.center
        returnTime = []
        route, times = self.getRoute()
        returnTime.append(0)
        droneOrder = []
        #droneLimit = 1
        finalRoute = []
        callback = self.matrix.Distance
        #while attempt is True:
        for x in range(len(route)-1):
            dist = callback(nodes.index(route[x]),nodes.index(center))#Dont use node, use index of node in trial, aha
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
                    droneOrder.append(index+1)
                else:
                    returnTime.append(0)
                    self.numDrones += 1
                #j += 1
        for f in finalRoute:
            print json.dumps(f, indent=4, sort_keys=True)
        print ""
        print "Drone Order"
        print droneOrder
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

    def totalDistance(self, graph):
        route, times = self.getRoute()
        center = self.center
        distance = 0
        for x in route:
            distance += directDistance(graph.node[x],graph.node[center])*2
        return distance
