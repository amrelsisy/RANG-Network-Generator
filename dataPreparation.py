import csv
import operator
import random
import math
from operator import itemgetter

#step 1
#a) find number of unique nodes in network
def findNumberOfUniqueNodesAndTotalDegree(networkEdgesFile, networkGroups):
	f = open(networkEdgesFile,"r")
	lines = f.readlines()
	csvEdgesSource = []
	csvEdgesTarget = []
	csvEdgesWeights = []	
	for l in lines:
		csvEdgesSource.append(l.split(' ')[0])
		csvEdgesTarget.append(l.split(' ')[1]) #strips trailing \n
		csvEdgesWeights.append(l.split(' ')[2].rstrip()) #strips trailing \n
	f.close()

	totalWeights = 0	
	for w in csvEdgesWeights:
		totalWeights += int(w)

	totalDegree = totalWeights*2
	nodes = []
	for n in csvEdgesSource:
		if n not in nodes:
			nodes.append(n)

	for n in csvEdgesTarget:
		if n not in nodes:
			nodes.append(n)


	#in case a node is not present in the edges list	
	#append nodes in communities that are isolated			
	f = open(networkGroups,"r")
	lines = f.readlines()
	communityCnt = 0
	for l in lines:
		communityNodesCnt = 0
		nodesInCommunity = l.split(' ')
		for n in nodesInCommunity:
			if n.rstrip() not in nodes:
				nodes.append(n.rstrip())
		communityCnt += 1


				
	return nodes, totalDegree




#b) read ground truth communities from input file
def readGroundTruthCommunities(nodes, networkEdgesFile, networkGroups, manual_auto, manualHierarchyFile):	
	
	f = open(networkGroups,"r")
	lines = f.readlines()

	w, h = 0, len(lines);
	groundTruthCommunities = [[0 for x in range(w)] for y in range(h)]
	communityCnt = 0
	for l in lines:
		communityNodesCnt = 0
		nodesInCommunity = l.split(' ')
		for n in nodesInCommunity:
			groundTruthCommunities[communityCnt].append(n.rstrip())
			communityNodesCnt += 1
	
		communityCnt += 1
	#print(groundTruthCommunities)
	
		
	#nodeID, degree
	w, h = 2, len(nodes);
	nodeDegrees = [[0 for x in range(w)] for y in range(h)]
	
	for i in range(len(nodes)):
		nodeDegrees[i][0] = nodes[i]				

	
	if manual_auto == 'auto':
		#find degree of the nodes in the network

		f = open(networkEdgesFile,"r")
		lines = f.readlines()
		edgeCnt = 0
		for l in lines:
			srcNode = l.split(' ')[0]
			trgNode = l.split(' ')[1]
			weight = l.split(' ')[2].rstrip() #strips trailing \n
			for n in nodeDegrees:
				if n[0] == srcNode:
					n[1] += int(weight)
				if n[0] == trgNode:
					n[1] += int(weight)
		#print('auto  nodeDegrees:', nodeDegrees)
		f.close()			
	
		#find leader of the whole network
		sorted_nodeDegrees = sorted(nodeDegrees, key=lambda x: x[1], reverse=True)
	#	print(sorted_nodeDegrees)			

		w, h = 0, 3; #only three levels of hierarchy
		managementLevels = [[0 for x in range(w)] for y in range(h)]

		#leader of the network
		managementLevels[0].append(sorted_nodeDegrees[0][0])

		#find manager nodes		
		#find leader of each community (managers of groups)
		#once leader is found, no need to check the remaining nodes in the community			
		#group manager can't be the same as the leader of the whole networks
		for community in groundTruthCommunities:
			for sortedNodes in sorted_nodeDegrees:
				if sortedNodes[0] in community and sortedNodes[0] not in managementLevels[0]:
					managementLevels[1].append(sortedNodes[0])
					break
					
		#find soldier nodes		
		#all nodes that are not in management level 0 or 1			
		for sortedNodes in sorted_nodeDegrees:
			if sortedNodes[0] not in managementLevels[0]:
				if sortedNodes[0] not in managementLevels[1]:	
					managementLevels[2].append(sortedNodes[0])
	
	
	elif manual_auto == 'manual':
		w, h = 0, 3; #only three levels of hierarchy
		managementLevels = [[0 for x in range(w)] for y in range(h)]

		f = open(manualHierarchyFile,"r")
		lines = f.readlines()
		for l in lines:
			managementType = l.split(' ')[0]
			if managementType == "boss:":
				nodeID = l.split(' ')[1].rstrip()
				managementLevels[0].append(nodeID)				
			elif managementType == "managers:":
				managerNodes = l.split(' ')
				for mn in managerNodes:
					if mn != "managers:":
						managementLevels[1].append(mn.rstrip())

		lowLevelNodes = []		
		for community in groundTruthCommunities:		
			for node in community:
				if node not in managementLevels[0] and node not in managementLevels[1]:
						managementLevels[2].append(node)
		
	#find hierarchical groups (cocaine managers, cocaine soldiers, hashish ....)		
	#for each management group, we will have a low-level group		
	numberOfHierarchicalGroups = len(managementLevels[0]) + len(managementLevels[1]) * 2
		
	w, h = 0, numberOfHierarchicalGroups;
	hierarchicalCommunities = [[0 for x in range(w)] for y in range(h)]
	cnt = 0
	for managementLevel in managementLevels:
		for community in groundTruthCommunities:
			done = 0

			#for the case of community with only one node
			#it will have no low-level nodes
			if managementLevel == managementLevels[2] and len(community) == 1:
				cnt += 1
				continue
			for node in nodes:
				if node in managementLevel and node in community:
					hierarchicalCommunities[cnt].append(node)
					done = 1
			if done == 1:
				cnt += 1
	
	return numberOfHierarchicalGroups, managementLevels, hierarchicalCommunities, groundTruthCommunities


#treat edges as if they were weighted
#find edges between communities (weighted edges)
def findEdgesBetweenGroups(communities, nodes, networkEdgesFile):

	edgesBetweenGroups = {}
	for i in range(len(communities)):
		for j in range(len(communities)):
			edgesBetweenGroups[(i,j)] = []

#	print(edgesBetweenGroups)			
	f = open(networkEdgesFile,"r")
	lines = f.readlines()
	for l in lines:
		src = l.split(' ')[0]
		trgt = l.split(' ')[1].rstrip() #strips trailing \n
		weight = l.split(' ')[2].rstrip()
		
		communityCnt = 0
		srcCommunity = -1
		trgtCommunity = -1
		for community in communities:
			if src in community:
				srcCommunity = communityCnt
			if trgt in community:
				trgtCommunity = communityCnt
			communityCnt += 1
		edgesBetweenGroups[(srcCommunity, trgtCommunity)].append(weight)

	f.close()

	return edgesBetweenGroups

#auxiliary function
#to help find preferences of nodes for manual input
#used just for testing the manual side of the generator	
def calculatePereference(hierarchicalCommunities, networkEdgesFile):
	for comm in hierarchicalCommunities:
		totalCommWeight = 0
		f = open(networkEdgesFile,"r")
		lines = f.readlines()
		src = ''
		trgt = ''
		weight = ''
		for l in lines:
			src = l.split(' ')[0]
			trgt = l.split(' ')[1] 
			weight = int(l.split(' ')[2].rstrip()) #strips trailing \n
			if src in comm:
				totalCommWeight += weight
			if trgt in comm:
				totalCommWeight += weight
		print(comm, totalCommWeight)

		for n in comm:
			nodeWeight = 0
			for l in lines:
				src = l.split(' ')[0]
				trgt = l.split(' ')[1]
				weight = int(l.split(' ')[2].rstrip()) #strips trailing \n
				if src == n:
					nodeWeight += weight
				elif trgt == n:
					nodeWeight += weight
#			print(n, nodeWeight, nodeWeight/totalCommWeight)
			print(n, nodeWeight/totalCommWeight)

		f.close()


def manualEdgesBetweenGroups(communities, nodes, manualEdgesFile, manualPreferencesFile):

	#read manual weight of edges between groups			
	weightedEdgesBetweenGroups = {}
	for i in range(len(communities)):
		for j in range(len(communities)):
			weightedEdgesBetweenGroups[(i,j)] = []


	f = open(manualEdgesFile,"r")
	lines = f.readlines()
	srcCommunityCnt = 0
	for l in lines:
		trgCommunityCnt = 0
		edges = l.split(';')
		for edgeWeights in edges:
			weights = edgeWeights.split(' ')
			for weight in weights:
				w = weight.rstrip()
				if w != '':
					weightedEdgesBetweenGroups[(srcCommunityCnt, trgCommunityCnt)].append(int(w))
				
			trgCommunityCnt += 1
		srcCommunityCnt += 1
	f.close()

	#find total degree of each community
	#will be used to find preference (degree) of each node compared to other nodes in its community			
	degreeOfCommunity = []
	for commCnt in range(len(communities)):
		totalDegree = 0			
		for i in range(len(communities)):
			for j in range(len(communities)):
				if i == commCnt or j == commCnt:			
					edges = weightedEdgesBetweenGroups[i,j]
					for edge in edges:	
						totalDegree += edge
		degreeOfCommunity.append(totalDegree)		

#	print('communities degree:', degreeOfCommunity)

	nodePref = {}
	for n in nodes:
		nodePref[n] = 1
			
	#find preference of nodes within group
	#this is read from an input file
	#preference of each node is relative to its hierarchical group members
	#boss and managers automatically have preference 1, since they are the only nodes in their hierarchical groups	
	f = open(manualPreferencesFile, "r")
	lines = f.readlines()
	for l in lines:
		preferences = l.split(' ')
		for entry in preferences:
			node = entry.split(':')[0].rstrip()
			pref = entry.split(':')[1].rstrip()
			nodePref[node] = float(pref)
			#print(node, pref) 

#	print('nodePref', nodePref)
#	for entry, value in nodePref.items():
#		print(entry, value)

	#node id, node degree, total community degree			
	w, h = 3, len(nodes);
	estimatedNodeDegree = [[-1 for x in range(w)] for y in range(h)]
	commCnt = 0
	nodeCnt = 0
	#find estimated node degree, by multiplying a nodes preference score with the total degree of its community
	for comm in communities:
		commDegree = degreeOfCommunity[commCnt]
		for n in nodes:
			if n in comm:
				for nid, pref in nodePref.items():
					if nid == n:
						estimatedNodeDegree[nodeCnt][0] = nid
						estimatedNodeDegree[nodeCnt][1] = int(pref*commDegree)
						estimatedNodeDegree[nodeCnt][2] = commDegree
						nodeCnt += 1
		commCnt += 1

#	print('estimated node degree:', estimatedNodeDegree)			

	nodeEdges = {}
	for n in nodes:
		nodeEdges[n] = []

#	print('communities:', communities)			
	#assign edges randomly to node with highest preference	
	for i in range(len(communities)):
		uniqueEdges = set()			
		for j in range(len(communities)):
			edges = sorted(weightedEdgesBetweenGroups[i,j], reverse=True)
#			print(communities[i], communities[j])		
			#node preference per community
			#nID, node preference	
			w, h = 2, len(communities[i]);
			srcCommPref = [[-1 for x in range(w)] for y in range(h)]
			
			cnt = 0
			for node in communities[i]:
				srcCommPref[cnt][0] = node
				for entry in estimatedNodeDegree:
					if node == entry[0]:
						if entry[2] == 0:
							srcCommPref[cnt][1] = 0
						else:
							srcCommPref[cnt][1] = entry[1]/entry[2]
				cnt += 1	

			w, h = 2, len(communities[j]);
			trgtCommPref = [[-1 for x in range(w)] for y in range(h)]
			cnt = 0
			for node in communities[j]:
				trgtCommPref[cnt][0] = node
				for entry in estimatedNodeDegree:
					if node == entry[0]:
						if entry[2] == 0:
							trgtCommPref[cnt][1] = 0
						else:	
							trgtCommPref[cnt][1] = entry[1]/entry[2]
				cnt += 1

			sorted_srcCommPref = sorted(srcCommPref, key=lambda x: x[1], reverse=True)
			sorted_trgtCommPref = sorted(trgtCommPref, key=lambda x: x[1], reverse=True)
#			if edges != [0]:	
#				print('p1:', communities[i], communities[j], edges)
#				print('p2:', sorted_srcCommPref, sorted_trgtCommPref, edges)
#			print(communities[i], srcCommPref)
			nodePosCnt = 0
			for edge in edges:
				edgePass = -1
				while edgePass == -1:
					edgePass = 1
					if edge != 0:
						edgePass = -1

						#if source or target groups have only 1 node
						#then assign edge weights sequentially based on preference order
						if len(sorted_srcCommPref) == 1 or len(sorted_trgtCommPref) == 1:
#							print('here', communities[i], communities[j], edges)
							if len(sorted_srcCommPref) == 1:
								src = sorted_srcCommPref[0][0]
							else:	
								src = sorted_srcCommPref[nodePosCnt][0]
								nodePosCnt += 1

							if len(sorted_trgtCommPref) == 1:
								trg = sorted_trgtCommPref[0][0]
							else:	
								trg = sorted_trgtCommPref[nodePosCnt][0]
								nodePosCnt += 1

						else:
							#pick source and target nodes randomly 
							#but taking preference into consideration
							r_src = random.uniform(0,1)
							threshold = 0
							for entry in sorted_srcCommPref:
								threshold += entry[1]
								if r_src <= threshold:
									src = entry[0]
									break

							r_trgt = random.uniform(0,1)
							threshold = 0
							for entry in sorted_trgtCommPref:
								threshold += entry[1]
								if r_trgt <= threshold:
									trg = entry[0]
									break
#							print("rrrrr", r_src, r_trgt)
#						print(communities[i], communities[j], edges)
#						print(src, trg, edge)
						#cant have a self loop edge
						if src != trg:
							#cant assign an edge between the same pair of nodes more than once
							if (src, trg) not in uniqueEdges and (trg, src) not in uniqueEdges:
								edgePass = 1
#								print(src, trg, edge)
								nodeEdges[src].append((trg, int(edge)))
								uniqueEdges.add((src, trg))
								uniqueEdges.add((trg, src))

								'''
								for entry in estimatedNodeDegree:
									if entry[0] == src or entry[0] == trg:
										entry[1] = entry[1] - edge
								srcComm = ''
								trgComm = ''

								for comm in communities:
									if src in comm:
										srcComm = comm
									if trg in comm:
										trgComm = comm
#								print('srcTrgComm:', srcComm, trgComm)	
								for entry in estimatedNodeDegree:
									#check so we don't double subtract
									if srcComm == trgComm:
										if entry[0] in srcComm:
											entry[2] = entry[2] - edge
									else:	
										if entry[0] in srcComm:
											entry[2] = entry[2] - edge
										if entry[0] in trgComm:
											entry[2] = entry[2] - edge
											
#								print('estimated:', estimatedNodeDegree)
#								print()
								'''			


#	print('estimatedNodedegree:', estimatedNodeDegree)
	return nodeEdges


#for each node we will create a list with the weighted directed edges it has to all other nodes
#ex: '3': [('1', 62), ('83', 1), ('85', 1), ('8', 2), ('76', 9), ('9', 3)...
def findEdgesToOtherNodes(networkEdgesFile, nodes):

	#dictionary will hold the following
	#key = node ID		
	nodeEdges = {}

	for n in nodes:
		nodeEdges[n] = []

	f = open(networkEdgesFile,"r")
	lines = f.readlines()
	
	
	#from leader to managers						
	edgeWeightToSubordinates = 0
	edgeWeightFromSubordinates = 0
	for l in lines:
		srcNode = l.split(' ')[0]
		trgNode = l.split(' ')[1]
		w = l.split(' ')[2].rstrip() #strips trailing \n
		nodeEdges[srcNode].append((trgNode, int(w)))
	
				
	#print(nodeEdges)
	#print(nodeEdges['3'], nodeEdges['3'][0], nodeEdges['3'][0][1])			

	return nodeEdges




def BWRN(nodeEdges, hierarchicalCommunities, probabilityOfSuccess):
	p = float(probabilityOfSuccess)
	generatedEdges = []			
	
	#different groups			
	if hierarchicalCommunities[0] != hierarchicalCommunities[1]:
		for loop in range(2):
			if loop == 0:
				srcGroup = hierarchicalCommunities[0]
				trgtGroup = hierarchicalCommunities[1]
			elif loop	== 1:
				srcGroup = hierarchicalCommunities[1]
				trgtGroup = hierarchicalCommunities[0]

			w, h = 2, len(srcGroup);
			srcNodePriority = [[0 for x in range(w)] for y in range(h)]
			
			w, h = 2, len(trgtGroup);
			trgtNodePriority = [[0 for x in range(w)] for y in range(h)]
				
			edgeWeights = []


			cnt = 0
			for node in srcGroup:
				srcNodePriority[cnt][0] = node
				cnt += 1

			cnt = 0	
			for node in trgtGroup:
				trgtNodePriority[cnt][0] = node
				cnt += 1


			e_0 = 0 #number of edges with 0 weights
			e_1 = 0 #number of edges with 1 weights
			W = 0 #sum of all weights
			for srcNode in srcGroup:
				edgesFromSrcNode = nodeEdges[srcNode]
				for trgtNode in trgtGroup:
					if srcNode == trgtNode:
						continue
					weight = 0
					for entry in edgesFromSrcNode:
						#find if there is an edge from the source node to the target node
						if trgtNode == entry[0]:
							weight = entry[1]
							for srcEntry in srcNodePriority:
								if srcEntry[0] == srcNode:
									tempWeight = srcEntry[1]
									tempWeight += weight
									srcEntry[1] = tempWeight
								
							for trgtEntry	in trgtNodePriority:
								if trgtEntry[0] == trgtNode:
									trgtEntry[1] = trgtEntry[1] + weight
										
										
							edgeWeights.append(weight)		
						
					if weight == 0:
						e_0 += 1
					elif weight == 1:
						e_1 += 1
					W += int(weight)	



			sorted_srcNodePriority = sorted(srcNodePriority, key=lambda x: x[1], reverse=True)
			sorted_trgtNodePriority = sorted(trgtNodePriority, key=lambda x: x[1], reverse=True)
			edgeWeights.sort(reverse=True)
			sorted_edgeWeights = edgeWeights	
				
			#print(srcGroup,trgtGroup,sorted_srcNodePriority, sorted_trgtNodePriority, sorted_edgeWeights)
			#print(srcGroup,trgtGroup)
					
			#actual generating of edges
			#will mark pairs that have an edge generated between them
			#this pair becomes no longer eligible for pair assignment
			connectedPairs = []
			#start with heaviest edge
			for w in sorted_edgeWeights:
#				#print()
				#select top pair, which is eligible
				#this list is dynamic, top nodes may change after assignment
				#node degree is decreased by the weight of the edge that the node is assigned
				topSrc = sorted_srcNodePriority[0][0]
				topTrgt = sorted_trgtNodePriority[0][0]
				#print(topSrc, topTrgt, w)
				

				#make sure pair is eligible
				topSrcCnt = 0
				topTrgtCnt = 0
				
				'''
				#new code for randomization
				#code for randomly picking source and target nodes
				#between groups where we allow for randomization
				if hierarchicalCommunities[2] == 'random':
					#print(len(hierarchicalCommunities[0]), len(hierarchicalCommunities[1]), hierarchicalCommunities)
					randSrc = random.randint(0, len(srcGroup) - 1)
					topSrc = sorted_srcNodePriority[randSrc][0]
					randTrg = random.randint(0, len(trgtGroup) - 1)
					topTrgt = sorted_trgtNodePriority[randTrg][0]

					#make sure pair is eligible
					while (topSrc, topTrgt) in connectedPairs:
						randSrc = random.randint(0, len(srcGroup) - 1)
						topSrc = sorted_srcNodePriority[randSrc][0]
						randTrg = random.randint(0, len(trgtGroup) - 1)
						topTrgt = sorted_trgtNodePriority[randTrg][0]
					else:	
						connectedPairs.append((topSrc, topTrgt))
				else:								
					topSrc = sorted_srcNodePriority[0][0]
					topTrgt = sorted_trgtNodePriority[0][0]	

					#make sure pair is eligible
					while (topSrc, topTrgt) in connectedPairs:
						topSrc = sorted_srcNodePriority[topSrcCnt][0]
						topTrgt = sorted_trgtNodePriority[topTrgtCnt][0]
						if len(srcGroup) > topSrcCnt + 1:
							topSrcCnt += 1
						elif len(trgtGroup) > topTrgtCnt + 1:
							topTrgtCnt += 1
					else:
						connectedPairs.append((topSrc, topTrgt))
					
				#end of new code with randomization			
				'''
				#old code with no randomization
				topSrc = sorted_srcNodePriority[0][0]
				topTrgt = sorted_trgtNodePriority[0][0]	

				#make sure pair is eligible
				while (topSrc, topTrgt) in connectedPairs:
					topSrc = sorted_srcNodePriority[topSrcCnt][0]
					topTrgt = sorted_trgtNodePriority[topTrgtCnt][0]
					if len(srcGroup) > topSrcCnt + 1:
						topSrcCnt += 1
					elif len(trgtGroup) > topTrgtCnt + 1:
						topTrgtCnt += 1
				else:
					connectedPairs.append((topSrc, topTrgt))
				#end of old code with no randomization	

				numOfIterations = int(w/p)
				assignedWeight = 0
				for iter in range(numOfIterations):
					rnd = random.uniform(0,1)
					if rnd <= p:
						assignedWeight += 1		
				oneMoreIteration = -1
				a = w/p - int(w/p)
				p_l = a*p
				if a > 0:
					rnd = random.uniform(0,1)
					if rnd <= p_l:
						assignedWeight += 1
					
					
#				print(topSrc, topTrgt, assignedWeight)	
				if assignedWeight > 0:	
					generatedEdges.append((topSrc, topTrgt, assignedWeight))	
#				print(topSrc, topTrgt, assignedWeight, connectedPairs)	
				for srcEntry in srcNodePriority:
					if srcEntry[0] == topSrc:
						tempWeight = srcEntry[1]
						tempWeight -= assignedWeight
						srcEntry[1] = tempWeight
	
				for trgtEntry in trgtNodePriority:
					if trgtEntry[0] == topTrgt:
						tempWeight = trgtEntry[1]
						tempWeight -= assignedWeight
						trgtEntry[1] = tempWeight
											
				sorted_srcNodePriority = sorted(srcNodePriority, key=lambda x: x[1], reverse=True)
				sorted_trgtNodePriority = sorted(trgtNodePriority, key=lambda x: x[1], reverse=True)
#				print(sorted_srcNodePriority, sorted_trgtNodePriority)
	


	elif hierarchicalCommunities[0] == hierarchicalCommunities[1]:
		srcGroup = hierarchicalCommunities[0]
		trgtGroup = hierarchicalCommunities[1]
		#print('same:', srcGroup, trgtGroup)

		w, h = 2, len(srcGroup);
		srcNodePriority = [[0 for x in range(w)] for y in range(h)]
			
		w, h = 2, len(trgtGroup);
		trgtNodePriority = [[0 for x in range(w)] for y in range(h)]
			
		edgeWeights = []


		cnt = 0
		for node in srcGroup:
			srcNodePriority[cnt][0] = node
			cnt += 1

		cnt = 0	
		for node in trgtGroup:
			trgtNodePriority[cnt][0] = node
			cnt += 1


		e_0 = 0 #number of edges with 0 weights
		e_1 = 0 #number of edges with 1 weights
		W = 0 #sum of all weights
		for srcNode in srcGroup:
			edgesFromSrcNode = nodeEdges[srcNode]
			for trgtNode in trgtGroup:
				if srcNode == trgtNode:
					continue
				weight = 0
				for entry in edgesFromSrcNode:
					#find if there is an edge from the source node to the target node
					if trgtNode == entry[0]:
						weight = entry[1]
						for srcEntry in srcNodePriority:
							if srcEntry[0] == srcNode:
								tempWeight = srcEntry[1]
								tempWeight += weight
								srcEntry[1] = tempWeight
							
						for trgtEntry	in trgtNodePriority:
							if trgtEntry[0] == trgtNode:
								trgtEntry[1] = trgtEntry[1] + weight
									
									
						edgeWeights.append(weight)		
					
				if weight == 0:
					e_0 += 1
				elif weight == 1:
					e_1 += 1
				W += int(weight)	



		sorted_srcNodePriority = sorted(srcNodePriority, key=lambda x: x[1], reverse=True)
		sorted_trgtNodePriority = sorted(trgtNodePriority, key=lambda x: x[1], reverse=True)
		edgeWeights.sort(reverse=True)
		sorted_edgeWeights = edgeWeights	
			
		#print(srcGroup,trgtGroup,sorted_srcNodePriority, sorted_trgtNodePriority, sorted_edgeWeights)
		#print(srcGroup,trgtGroup)
				
		#actual generating of edges
		#will mark pairs that have an edge generated between them
		#this pair becomes no longer eligible for pair assignment
		connectedPairs = []
		#start with heaviest edge
		for w in sorted_edgeWeights:
#			#print()
			#select top pair, which is eligible
			#this list is dynamic, top nodes may change after assignment
			#node degree is decreased by the weight of the edge that the node is assigned
			topSrc = sorted_srcNodePriority[0][0]
			topTrgt = sorted_trgtNodePriority[0][0]
			#print(topSrc, topTrgt, w)
				

			#make sure pair is eligible
			topSrcCnt = 0
			topTrgtCnt = 0
			while (topSrc, topTrgt) in connectedPairs or topSrc == topTrgt:
				topSrc = sorted_srcNodePriority[topSrcCnt][0]
				topTrgt = sorted_trgtNodePriority[topTrgtCnt][0]
				if len(srcGroup) > topSrcCnt + 1:
					topSrcCnt += 1
				elif len(trgtGroup) > topTrgtCnt + 1:
					topTrgtCnt += 1
			else:
				connectedPairs.append((topSrc, topTrgt))
				
			numOfIterations = int(w/p)
			assignedWeight = 0
			for iter in range(numOfIterations):
				rnd = random.uniform(0,1)
				if rnd <= p:
					assignedWeight += 1		
			oneMoreIteration = -1
			a = w/p - int(w/p)
			p_l = a*p
			if a > 0:
				rnd = random.uniform(0,1)
				if rnd <= p_l:
					assignedWeight += 1
				
					
#			print(topSrc, topTrgt, assignedWeight)	
			if assignedWeight > 0:	
				generatedEdges.append((topSrc, topTrgt, assignedWeight))	
#			print(topSrc, topTrgt, assignedWeight, connectedPairs)	
			for srcEntry in srcNodePriority:
				if srcEntry[0] == topSrc:
					tempWeight = srcEntry[1]
					tempWeight -= assignedWeight
					srcEntry[1] = tempWeight
	
			for trgtEntry in trgtNodePriority:
				if trgtEntry[0] == topTrgt:
					tempWeight = trgtEntry[1]
					tempWeight -= assignedWeight
					trgtEntry[1] = tempWeight
											
			sorted_srcNodePriority = sorted(srcNodePriority, key=lambda x: x[1], reverse=True)
			sorted_trgtNodePriority = sorted(trgtNodePriority, key=lambda x: x[1], reverse=True)
#			print(sorted_srcNodePriority, sorted_trgtNodePriority)
	
		
		
	return generatedEdges


#generate edges that will be between communities
#each two communities have their own probability of forming edges between them
#iterate through communities
def WRG(nodeEdges, hierarchicalCommunities):

	generatedEdges = []			
	#different groups			
	if hierarchicalCommunities[0] != hierarchicalCommunities[1]:
		for loop in range(2):
			if loop == 0:
				srcGroup = hierarchicalCommunities[0]
				trgtGroup = hierarchicalCommunities[1]
			elif loop	== 1:
				srcGroup = hierarchicalCommunities[1]
				trgtGroup = hierarchicalCommunities[0]


			#print('diff:', srcGroup, trgtGroup)
			W = 0 #sum of weights of all heavy weights
			for srcNode in srcGroup:
				edgesFromSrcNode = nodeEdges[srcNode]
				for trgtNode in trgtGroup:
					weight = 0
					for entry in edgesFromSrcNode:
						
						#find if there is an edge from the source node to the target node
						if trgtNode == entry[0]:
							weight = entry[1]
			
					W += int(weight)
			#print(srcGroup, trgtGroup, 'e_0:', e_0, 'e_1:', e_1, 'W:', W)

			p = W / (W + len(srcGroup)*len(trgtGroup))					
			#actual generating of edges
			for srcNode in srcGroup:
				for trgtNode in trgtGroup:
					rnd = random.uniform(0,1)
					rw = -1
					prob = 1 - p
					sprob = prob
					while sprob < rnd:
						prob = prob * p
						sprob = sprob + prob
						rw = rw + 1
					if rw > 0:
						generatedEdges.append((srcNode, trgtNode, rw))
				
	elif hierarchicalCommunities[0] == hierarchicalCommunities[1]:
		srcGroup = hierarchicalCommunities[0]
		trgtGroup = hierarchicalCommunities[1]
		#print('same:', srcGroup, trgtGroup)

		W = 0 #sum of weights of all heavy weights
		for srcNode in srcGroup:
			edgesFromSrcNode = nodeEdges[srcNode]
			for trgtNode in trgtGroup:
				if srcNode == trgtNode:
					continue
	
				weight = 0
				for entry in edgesFromSrcNode:
					
					#find if there is an edge from the source node to the target node
					if trgtNode == entry[0]:
						weight = entry[1]
			
				W += int(weight)
		#print(srcGroup, trgtGroup, 'e_0:', e_0, 'e_1:', e_1, 'W:', W)
		
		p = W / (W + len(srcGroup)*(len(trgtGroup)-1))					
		#actual generating of edges
		for srcNode in srcGroup:
			for trgtNode in trgtGroup:
				if srcNode == trgtNode:
					continue
			
				rnd = random.uniform(0,1)
				rw = -1
				prob = 1 - p
				sprob = prob
				while sprob < rnd:
					prob = prob * p
					sprob = sprob + prob
					rw = rw + 1
				if rw > 0:
					generatedEdges.append((srcNode, trgtNode, rw))
	
								

	return generatedEdges


def randomizeNodeIds(totalGeneratedEdges, randomNodeIdsFile, numNodes):
	
	w, h = 2, numNodes;
	randomNodeIds = [[0 for x in range(w)] for y in range(h)]
		
	#read random node id's from file
	f = open(randomNodeIdsFile,"r")
	lines = f.readlines()
	lineCnt = 0			
	nodeCnt = 0
	for l in lines:
		if lineCnt == 0:
			lineCnt += 1
			continue
		
		randomNodeIds[nodeCnt][0] = l.split(' ')[0]	
		randomNodeIds[nodeCnt][1] = l.split(' ')[1].rstrip()
		nodeCnt += 1
	
	'''
	#to create random node ids from scratch
	#randomize node id's
	uniqueNodes = []
	for entry in totalGeneratedEdges:
		src = entry[0]
		trgt = entry[1]
		weight = entry[2]
		#find unique nodes
		if src not in uniqueNodes:
			uniqueNodes.append(src)
		if trgt not in uniqueNodes:
			uniqueNodes.append(trgt)

	print(uniqueNodes, len(uniqueNodes))	
	w, h = 1, numNodes;
	randomNodeIds = [[0 for x in range(w)] for y in range(h)]
	cnt = 0
	for node in uniqueNodes:
		r_nid = str(random.randint(1,100))
		while r_nid in uniqueNodes or r_nid in randomNodeIds:
			r_nid = str(random.randint(1,100))
		randomNodeIds[cnt] = r_nid
		cnt += 1

	#print('uniqueNodes', uniqueNodes, len(uniqueNodes))
	print('randomNodeIds', randomNodeIds, len(randomNodeIds))
	for i in range(len(uniqueNodes)):
		print(uniqueNodes[i], randomNodeIds[i])
	print()	
	'''
	return randomNodeIds



def findBreakDownOfGeneratedEdgesBetweenGroups(communities, totalGeneratedEdges):
	#find breakdown of generated edges between hierarchical groups
	for i in range(len(communities)):
		for j in range(len(communities)):
			for edge in totalGeneratedEdges:
				src = edge[0]
				trgt = edge[1]
				weight = edge[2]
				if src in communities[i] and trgt in communities[j]:
					print(i,j,'(', src, trgt, weight,')')
					
	
