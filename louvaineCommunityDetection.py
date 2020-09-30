##code by Aamir Mandviwalla
import sys
from community import community_louvain
import networkx as nx

G = nx.Graph()
#set to the input file
filename = sys.argv[1]
    
#here i assumed that you were using spaces to separate values and with weights included
with open(filename) as f:
	for line in f:
		values = line.split(" ")
		source = values[0]
		target = values[1]
		weighty = float(values[2].strip("\n"))
		if G.has_edge(target, source):
			G[target][source]["weight"] += weighty
		else:	
			G.add_edge(source,target, weight=weighty)

#output 
partitions = community_louvain.best_partition(G)
for comm in set(partitions.values()):
	for node in partitions.keys():
		if partitions[node] == comm:
			print(node, end=" ")
	print()     

			
