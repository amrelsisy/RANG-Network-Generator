import sys
import csv
from operator import itemgetter
import community
from community import community_louvain
import networkx as nx
import matplotlib.pyplot as plt

#runs louvaine community detection algorithm


#initialize graph to use louvaine on
G = nx.Graph()
				
networkFile = sys.argv[1]
f = open(networkFile,"r")
lines = f.readlines()
nodes = []		
for l in lines:
	srcNode = l.split(' ')[0]
	trgtNode = l.split(' ')[1]
	if srcNode not in nodes:
		nodes.append(srcNode)
	if trgtNode not in nodes:
		nodes.append(trgtNode)
f.close()	
#print('nodes:', nodes)


#add nodes to this graph, based on nodes present in caviar6
for n in nodes:
	G.add_node(n)

#read the edge list
f = open(networkFile,"r")
lines = f.readlines()
csvEdgesSource = []
csvEdgesTarget = []
csvEdgesWeight = []
for l in lines:
	csvEdgesSource.append(l.split(' ')[0])
	csvEdgesTarget.append(l.split(' ')[1])
	csvEdgesWeight.append(l.split(' ')[2].rstrip()) #strips trailing \n
f.close()
	
	
	
totalEdges = 0
sourceN = []
targetN = []
frequency = []
visited = []#
#get the weight of the edges
for n1 in nodes:
	visited.append(n1)#
	for n2 in nodes:	
		if n2 in visited:#
			continue#
		freq = 0

		#check how many edges are formed between n1 and n2
		for i in range(len(csvEdgesSource)):
			source = csvEdgesSource[i]
			target = csvEdgesTarget[i]
			weight = int(csvEdgesWeight[i])	
			if source == n1 and target == n2:
				freq += weight
#				freq += 1
			elif source == n2 and target == n1: #since we treat graph as undirected#
#				freq += 1#
				freq += weight

		#create edge n1, n2, and give it a weight		
		if freq > 0:	
			sourceN.append(n1)
			targetN.append(n2)
			frequency.append(freq)
			totalEdges += freq
		
#for i in range(len(sourceN)):
#	print(sourceN[i], targetN[i], frequency[i])	
								
#print('totalEdges ' + str(totalEdges))				
#print(visited)

#add edges and weights to graph G
for i in range(len(sourceN)):
	G.add_edge(sourceN[i], targetN[i], weight = frequency[i])

#print(G.edges) #-> prints set of edges in graph
#print(G.get_edge_data('3','1')) # -> prints weight of edge between source, and target
#print(G.get_edge_data('1','3')) # -> prints weight of edge between source, and target


partitions = community_louvain.best_partition(G)
#print(partitions)

#print each partition memebrs on a single line
for comm in set(partitions.values()):
	for nodes in partitions.keys():
		if partitions[nodes] == comm:
			print(nodes, end=" ")
	print()



