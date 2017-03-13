import time
import math
import time
import random
import argparse
import json
import networkx as nx

def minToHour(minutes):
    h, m = divmod(minutes, 60)
    return "%d:%02d" % (h,m)

def directDistance(node1,node2):
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

def truckDistance(graph, from_node, to_node):
    #incorporates edge weights into total distance between nodes
    path = nx.dijkstra_path(graph,source=from_node,target=to_node)
    distance = 0
    for i in range(len(path)-1):
        #w = graph.get_edge_data(path[i],path[i+1])['weight']
        w = directDistance(graph.node[path[i]], graph.node[path[i+1]])
        distance += w
    return distance
