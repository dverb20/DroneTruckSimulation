import numpy as np
import networkx as nx
import math
import time
import random
import argparse
import json
import csv

class NetworkGraph(object):
    """Collection of Nodes and Edges for pathing"""

    def __init__(self):

        self.graph = nx.Graph()


    def importData(self, csvfile):
        G = self.graph
        edge, node, count = -1, -1, 0
        nodes = {}
        with open(csvfile) as csvfile:
            #Reads in nodes and edges from csv file
            reader = csv.DictReader(csvfile)

            for row in reader:
                if edge == row['edge']:
                    edge = row['edge']
                    if row['nodeid'] not in nodes:
                        G.add_node(float(row['nodeid']),pos=(float(row['x']),float(row['y'])),active=row['active'],x=float(row['x']),y=float(row['y']))
                    G.add_edge(node,float(row['nodeid']),weight=weight)
                else:
                    edge = row['edge']
                    if row['nodeid'] not in nodes:
                        G.add_node(float(row['nodeid']),pos=(float(row['x']),float(row['y'])),active=row['active'],x=float(row['x']),y=float(row['y']))
                node = float(row['nodeid'])
                weight = float(row['weight'])
                nodes[count] = node
                count += 1
            return nodes, count

    def makeRoute(self, routeSize, center):
        #creates list of n active nodes
        #Used to test various cases
        graph = self.graph
        r = []
        r.append(center)
        for n in range(routeSize):
            j = True
            while j is True:
                ran = random.randint(0,3205)
                if ran not in r:
                    if int(graph.node[ran]['active']) is 0:
                        r.append(ran)
                        j = False

        timeDictionary = {}
        x = []
        for node in r:
            if node is not center:
                timeDictionary[node] = random.randint(360,1260)
        return r, timeDictionary
