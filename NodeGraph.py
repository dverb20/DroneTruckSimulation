import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from xlutils.copy import copy
import xlwt
import xlrd
import math
import time
import random
import argparse
import json

#from math import radians, cos, sin, asin, sqrt
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
import csv
import time

class RouteMatrix(object): #ulimit -s 8192
  """Random matrix."""

  def __init__(self, V, graph, demands, drone=False):
      # check if demands is empty, if not demands
      #V is a list of nodes to be visited, graph is the nx graph
    self.demands = demands
    self.matrix = {}
    self.speed = 40
    for from_node in range(len(V)):
      self.matrix[from_node] = {}
      for to_node in range(len(V)):
        if from_node == to_node:
          self.matrix[from_node][to_node] = 0
        else:
            if drone is True:
                self.matrix[from_node][to_node] = euDistance(graph.node[V[from_node]],graph.node[V[to_node]])
            else:
                self.matrix[from_node][to_node] = getDistance(graph,V[from_node],V[to_node])
          #The line above creates a dictionary entry with the total distance between from_node to to_node

  def Distance(self, from_node, to_node):
    return self.matrix[from_node][to_node] #returns distance between nodes

  def Demand(self, from_node, to_node):
      return self.demands[from_node]

  def Time(self, from_node, to_node):
      time = self.matrix[from_node][to_node] / self.speed
      return time

def solve(graph, V, size, demands, num_vehicles, load_max):
    #Google TSP algorithm
    routing = pywrapcp.RoutingModel(size, num_vehicles, 0)
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    if load_max < 2:
        matrix = RouteMatrix(V, graph, demands, True)
    else:
        matrix = RouteMatrix(V, graph, demands)
    #matrix = RandomMatrix(9,1)
    matrix_callback = matrix.Distance
    demand_callback = matrix.Demand
    travel_time_callback = matrix.Time
    vehicle_capacity = load_max
    null_capacity_slack = 0
    fix_start_cumul_to_zero = True
    capacity = "Capacity"
    time_per_demand_unit = 300
    horizon = 24 * 3600
    time = "Time"
    routing.SetArcCostEvaluatorOfAllVehicles(matrix_callback)
    # routing.AddDimension(demand_callback, null_capacity_slack, vehicle_capacity,
    #                      fix_start_cumul_to_zero, capacity)
    # routing.AddDimension(travel_time_callback,  # total time function callback
    #                      horizon,
    #                      horizon,
    #                      fix_start_cumul_to_zero,
    #                      time)
    assignment = routing.SolveWithParameters(search_parameters)
    if assignment:
      # Solution cost.
      #print(assignment.ObjectiveValue())
      # Inspect solution.
      # Only one route here; otherwise iterate from 0 to routing.vehicles() - 1
      collective = {}
      for vehicle in range(num_vehicles):
          index = routing.Start(vehicle)
          index_next = assignment.Value(routing.NextVar(index))
          route = ''
          route_dist = 0
          route_demand = 0
          collective[vehicle] = []
          collective[vehicle].append(routing.IndexToNode(index))

          while not routing.IsEnd(index_next):
              collective[vehicle].append(index_next)
              node_index = routing.IndexToNode(index)
              node_index_next = routing.IndexToNode(index_next)
              route += str(node_index) + " -> "
              # Add the distance to the next node.
              route_dist += matrix_callback(node_index, node_index_next)
              # Add demand.
              route_demand += demands[node_index_next]
              index = index_next
              index_next = assignment.Value(routing.NextVar(index))

          node_index = routing.IndexToNode(index)
          node_index_next = routing.IndexToNode(index_next)
          route += str(node_index) + " -> " + str(node_index_next)
          route_dist += matrix_callback(node_index, node_index_next)
          collective[vehicle].append(0)

    #   route_number = 0
    #   node = routing.Start(route_number)

    #   route = ''
    #   r = []
    #   while not routing.IsEnd(node):
    #     r.append(node)
    #     route += str(node) + ' -> '
    #     node = assignment.Value(routing.NextVar(node))
    #   route += '0'
      #print(route)
      return collective, matrix
    else:
      print('No solution found.')

def makeRoute(graph,size,center):
    #creates list of n active nodes
    #Used to test various cases
    r = []
    r.append(center)
    for n in range(size):
        j = True
        while j is True:
            ran = random.randint(0,3205)
            if ran not in r:
                if int(graph.node[ran]['active']) is 0:
                    r.append(ran)
                    j = False
    return r

def getDistance(graph, from_node, to_node):
    #incorporates edge weights into total distance between nodes
    path = nx.dijkstra_path(graph,source=from_node,target=to_node)
    distance = 0
    for i in range(len(path)-1):
        #w = graph.get_edge_data(path[i],path[i+1])['weight']
        w = euDistance(graph.node[path[i]], graph.node[path[i+1]])
        distance += w
    return distance

def combine(routes, nodes, graph):
    #Creates a comprehensive list creating the total path the truck will take
    collective = {}
    lengths = []
    for veh in routes:
        route = routes[veh]
        final = []
        length = 0
        for i in range(len(route)-1):
            final.extend(nx.dijkstra_path(graph,source=nodes[route[i]],target=nodes[route[i+1]]))
            length += getDistance(graph,nodes[route[i]],nodes[route[i+1]])
        collective[veh] = final
        lengths.append(length)
    #print length
    #print collective
    return collective, lengths

def euDistance(node1,node2):
    #Used for drones, finds distance between two nodes
    a = [node1['x'],node1['y']]
    b = [node2['x'],node2['y']]
    dist = [(m - n)**2 for m, n in zip(a, b)]
    dist = math.sqrt(sum(dist))*100
    R = 6371  # radius of the earth in km
    mile = 0.621371
    x = (node2['x'] - node1['x']) * math.cos( 0.5*(node2['y']+node2['y']) )
    y = node2['y'] - node1['y']
    d = (R * math.sqrt( x*x + y*y ) * mile)/50
    return d

def euclideanDistance(graph,route):
    totalDistance = 0
    for i in range(len(route)-1):
        a = [graph.node[route[i]]['x'],graph.node[route[i]]['y']]
        b = [graph.node[route[i+1]]['x'],graph.node[route[i+1]]['y']]
        dist = [(m - n)**2 for m, n in zip(a, b)]
        dist = math.sqrt(sum(dist))*100
        totalDistance += dist
    print "Euclidean"
    print totalDistance

def droneNodeEdge(oldGraph,newGraph,nodes):
    #Creates graph for drones
    totalDistance = 0
    newGraph.add_node(nodes[0],pos=oldGraph.node[nodes[0]]['pos'],x=oldGraph.node[nodes[0]]['x'],y=oldGraph.node[nodes[0]]['y'])
    for n in range(1,len(nodes)-1):
        newGraph.add_node(nodes[n],pos=oldGraph.node[nodes[n]]['pos'],x=oldGraph.node[nodes[n]]['x'],y=oldGraph.node[nodes[n]]['y'])
        weight = euDistance(oldGraph.node[nodes[n-1]],oldGraph.node[nodes[n]])
        totalDistance += weight
        newGraph.add_edge(nodes[n-1],nodes[n],weight=weight)
    #print "Euclidean"
    #print totalDistance
    return newGraph, totalDistance

def minToHour(minutes):
    h, m = divmod(minutes, 60)
    return "%d:%02d" % (h,m)


def makeDroneRoute(nodes):
    #Makes route drone will fly, has drone always return to center
    #all times are in minutes, each day is 1440
    #minutes given create median time, window is created by taking 15 minutes before and 15 after
    newRoute = []
    timeList = {}
    center = nodes[0]
    for x in nodes:
        if x is not center:
            timeList[x] = random.randint(360,1260)
    #print timeList
    sortedList = sorted(timeList.items(), key=lambda x: x[1])
    route = []
    times = []
    for x in sortedList:
        print x
        route.append(x[0])
        times.append(x[1])
    print route
    print times
    flip = 0
    newRoute.append(center)
    i = 1
    while i < len(route):
        if flip is 0:
            newRoute.append(route[i])
            flip = 1
        if flip is 1:
            newRoute.append(center)
            flip = 0
            i += 1
    #odd indecies are the destinations
    return newRoute, route, times


def droneRouteTest(route, nodes, times, center, matrix):
    #Must incorporate battery charge time, and multiple drone take off
    speed = 35
    returnTime = []
    returnTime.append(0)
    droneOrder = []
    #droneLimit = 1
    finalRoute = []
    callback = matrix.Distance
    #while attempt is True:
    for x in range(len(route)-1):
        dist = callback(nodes.index(route[x]),nodes.index(center))#Dont use node, use index of node in trial, aha
        time = (dist / 40) * 60
        leave = times[x] - time + 2
        j = 0
        enter = True

        #This is for using first index priority
        # while enter is True:
        #     try:
        #         returnTime[j]
        #     except IndexError:
        #         returnTime.append(0)
        #     if leave > returnTime[j]:
        #         enter = False
        #         returnTime[j] = times[x] + time
        #         finalRoute.append({'node': route[x],'travel': minToHour(time), 'drone': (j+1), 'leave': minToHour(leave), 'return': minToHour(returnTime[j]), 'distance': round(dist, 2)})
        #     j += 1

        #This is for using least used drone priority
        while enter is True:
            #
            if leave > min(returnTime):
                enter = False
                index = returnTime.index(min(returnTime))
                returnTime[index] = times[x] + time
                finalRoute.append({'node': route[x],'travel': minToHour(time), 'drone': (index+1), 'leave': minToHour(leave), 'return': minToHour(returnTime[index]), 'distance': round(dist, 2)})
                droneOrder.append(index+1)
            else:
                returnTime.append(0)
            #j += 1
    for f in finalRoute:
        print json.dumps(f, indent=4, sort_keys=True)
    print ""
    print "Drone Order"
    print droneOrder
    return finalRoute

def timeAdjust(fullRoute, newNodes, center, matrix):
    speed = 35
    finalRoute = []
#newNodes give nodes and times in dictionary, screw all this, let's make a new folder with legit classes

def drawRoutes(tG, dG, finalRoutes, trial, dist_center):

    #Drawing Trucks
    for rou in finalRoutes:
        size = []
        node_colors = []
        finalRoute = finalRoutes[rou]
        for n in tG.nodes():
            if n in finalRoute:
                if n in trial:
                    # if n == dist_center:
                    #     print "inside"
                    if n == dist_center:
                        node_colors.append("green")
                    else:
                        node_colors.append("red")
                    size.append(50)
                else:
                    node_colors.append("blue")
                    size.append(19)
            else:
                node_colors.append("black")
                size.append(0.8)

        pos=nx.get_node_attributes(G,'pos')
        nx.draw(G,pos, node_size=size, node_color=node_colors, width=0.1)
        plt.show()
    #Drawing Drones
    drone_colors = []
    droneSize = []
    for n in Gd.nodes():
        if n is dist_center:
            drone_colors.append("blue")
            droneSize.append(50)
        else:
            drone_colors.append("green")
            droneSize.append(40)

    dronePos=nx.get_node_attributes(Gd,'pos')
    nx.draw(Gd,dronePos, node_size=droneSize, node_color=drone_colors, width=0.1)
    plt.show()

def openFile(name, G):
    edge, node, count = -1, -1, 0
    nodes, cost, demands = {}, {}, []
    with open(name) as csvfile:
        #Reads in nodes and edges from csv file
        reader = csv.DictReader(csvfile)

        for row in reader:
            if edge == row['edge']:
                edge = row['edge']
                if row['nodeid'] not in nodes:
                    G.add_node(float(row['nodeid']),pos=(float(row['x']),float(row['y'])),active=row['active'],x=float(row['x']),y=float(row['y']))
                    demands.append(float(row['demand']))
                G.add_edge(node,float(row['nodeid']),weight=weight)
                cost[node,float(row['nodeid'])] = weight
            else:
                edge = row['edge']
                if row['nodeid'] not in nodes:
                    G.add_node(float(row['nodeid']),pos=(float(row['x']),float(row['y'])),active=row['active'],x=float(row['x']),y=float(row['y']))
                    demands.append(float(row['demand']))
            node = float(row['nodeid'])
            weight = float(row['weight'])
            nodes[count] = node
            count += 1
        return G, nodes, demands, count, cost

def solverGate(G, routeSize, dist_center, vehicles, demands):
    gate = False
    while gate is False:
        try:
            trial = makeRoute(G,routeSize,dist_center)
            #V = [3205,56,198,1007,308,245]
            optimal = {}
            optimal, matrix = solve(G, trial, len(trial), demands, vehicles, 30)
        except nx.NetworkXNoPath:
            print "no node path"
        else:
            if vehicles == 4:
                gate = True
            if optimal is None:
                vehicles += 1
            else:
                gate = True
    return vehicles, trial, optimal, matrix

# workbook = xlrd.open_workbook('importNumbers.xls', on_demand = True, formatting_info=True)
# wb = copy(workbook)
# wb = xlwt.Workbook()
# ws = wb.get_sheet(0)
# ws.write(2, 0, 1)
# ws.write(2, 1, 1)
# wb.save('importNumbers.xls')

#########################################
#########################################

#Initializing variables
start_time = time.time()
G = nx.Graph()
Gd = nx.Graph()
dist_center = 3205 #distribution center node
vehicles = input("Enter Number of Trucks(1-4): ")
routeSize = input("Enter Route Size(10-30): ")

#Reads nodes and edges, creating the graph
G, nodes, demands, count, cost = openFile('testData.csv', G)

#Runs the google solver to create random destinations with the best route
vehicles, trial, optimal, droneMatrix = solverGate(G, routeSize, dist_center, vehicles, demands)
print optimal

#Makes comprehensive list of all nodes the truck will pass through
finalRoutes, truckDistances = combine(optimal,trial,G)

#creates full route list for drone
droneRoute, destinations, times = makeDroneRoute(trial)
#drone distance matrix
print ""
# temp = [dist_center] + destinations
# print temp
# droneMatrix = RouteMatrix(temp, G, demands, True)
droneRouteTest(destinations, trial, times, dist_center, droneMatrix)
#Creates graph of drone nodes for visual aids
Gd, droneDistance = droneNodeEdge(G,Gd,droneRoute)

#prints relevant data
print "Route Size - ", routeSize
print "Number of Trucks - ", vehicles
print "Truck - ", truckDistances,
print "Total - ", sum(truckDistances)
print "Drone - ", droneDistance

#Draws routes and prints total runtime of program
print("--- %s seconds ---" % (time.time() - start_time))
drawRoutes(G,Gd,finalRoutes,trial,dist_center)
