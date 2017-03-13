
import math
import time
import random
import networkx as nx
import numpy as np
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from helpers import directDistance, minToHour, truckDistance
import csv
import time

class RouteMatrix(object): #ulimit -s 8192
  """Random matrix."""

  def __init__(self, V, graph, drone=False):
      # check if demands is empty, if not demands
      #V is a list of nodes to be visited, graph is the nx graph
        self.matrix = {}
        self.speed = 40
        for from_node in range(len(V)):
          self.matrix[from_node] = {}
          for to_node in range(len(V)):
            if from_node == to_node:
              self.matrix[from_node][to_node] = 0
            else:
                if drone is True:
                    self.matrix[from_node][to_node] = directDistance(graph.node[V[from_node]],graph.node[V[to_node]])
                else:
                    self.matrix[from_node][to_node] = self.getDistance(graph,V[from_node],V[to_node])
          #The line above creates a dictionary entry with the total distance between from_node to to_node

  def Distance(self, from_node, to_node):
        return self.matrix[from_node][to_node] #returns distance between nodes

  def getDistance(self, graph, from_node, to_node):
      #incorporates edge weights into total distance between nodes
        path = nx.dijkstra_path(graph,source=from_node,target=to_node)
        distance = 0
        for i in range(len(path)-1):
          #w = graph.get_edge_data(path[i],path[i+1])['weight']
            w = directDistance(graph.node[path[i]], graph.node[path[i+1]])
            distance += w
        return distance

  def Time(self, from_node, to_node):
        time = self.matrix[from_node][to_node] / self.speed
        return time




############################################################################
def solve(graph, V, size, matrix):
    #Google TSP algorithm
    routing = pywrapcp.RoutingModel(size, 1, 0)
    search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()
    # Setting first solution heuristic (cheapest addition).
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    #matrix = RandomMatrix(9,1)
    matrix_callback = matrix.Distance
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
      for vehicle in range(1):
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
              route += str(V[node_index]) + " -> "
              # Add the distance to the next node.
              route_dist += matrix_callback(node_index, node_index_next)
              # Add demand.
              index = index_next
              index_next = assignment.Value(routing.NextVar(index))

          node_index = routing.IndexToNode(index)
          node_index_next = routing.IndexToNode(index_next)
          route += str(V[node_index]) + " -> " + str(V[node_index_next])
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
      print(route)
      return collective
    else:
      print('No solution found.')
