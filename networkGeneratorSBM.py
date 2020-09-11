import csv
import operator
import random
import math
import sys
import dataPreparation as data_prep

#command to run:
#clear; python3 networkGeneratorSBM.py auto BWRN 0.875 noRandomize CAVIAR6edges_weighted.txt networkGroups.txt manualHierarchy.txt manualEdgesBetweenGroups.txt manualPreferences.txt randomNodeIds.txt

manualAuto = sys.argv[1]
modelName = sys.argv[2]
probOfSuccess = sys.argv[3]
randomizeIDs = sys.argv[4]
if manualAuto == "auto":
	networkEdgesFile = sys.argv[5]	
	networkGroupsFile = sys.argv[6]
	manualHierarchyFile = ''
elif manualAuto == "manual":
	networkEdgesFile = ''
	networkGroupsFile = sys.argv[5]
	manualDegreeOfNetwork = sys.argv[6]
	manualHierarchyFile = sys.argv[7] 
	manualEdgesFile = sys.argv[8] 
	manualPreferencesFile = sys.argv[9]

if manualAuto == "auto":	
	if randomizeIDs == "Randomize":
		randomNodeIdsFile = sys.argv[7]
elif manualAuto == "manual":
	if randomizeIDs == "Randomize":
		randomNodeIdsFile = sys.argv[10]

if manualAuto == 'auto':
	nodes, totalDegree = data_prep.findNumberOfUniqueNodesAndTotalDegree(networkEdgesFile, networkGroupsFile)
#	print('auto nodes:', nodes)
#	print('auto totalDegree:', totalDegree)

elif manualAuto == 'manual':
	nodes = []				
	f = open(networkGroupsFile,"r")
	lines = f.readlines()
	communityCnt = 0 
	for l in lines:
		communityNodesCnt = 0 
		nodesInCommunity = l.split(' ')
		for n in nodesInCommunity:
			if n.rstrip() not in nodes:
				nodes.append(n.rstrip())
		communityCnt += 1
	f.close()	
				
	totalDegree = int(manualDegreeOfNetwork)
#	print('manual nodes:', nodes)
#	print('manual totalDegree:', totalDegree)



numberOfCommunities, managementLevels, hierarchicalCommunities, networkGroups = data_prep.readGroundTruthCommunities(nodes, networkEdgesFile, networkGroupsFile, manualAuto, manualHierarchyFile)

#print('numberOfCommunities:', numberOfCommunities)		
				
#print('managementLevels:', managementLevels)		
#print()				
#print('hierarchicalCommunities:', hierarchicalCommunities)		
#print()				
#print('networkGroups:', networkGroups)		

#use to calculate preferences of each node, for manual input				
#auxiliary function
#to help find preferences of nodes for manual input
#data_prep.calculatePereference(hierarchicalCommunities, networkEdgesFile)
				
#find edges between communities (weighted edges)
#auxiliary function
#to help find edges between groups for manual input
#edgesBetweenGroups = data_prep.findEdgesBetweenGroups(hierarchicalCommunities, nodes, networkEdgesFile)
#print('edgesBetweenGroups:', edgesBetweenGroups)				
#print()

if manualAuto == 'auto':				
	nodeEdges = data_prep.findEdgesToOtherNodes(networkEdgesFile, nodes)
#	print('auto nodeEdges:', nodeEdges)				
elif manualAuto == 'manual':
	nodeEdges = data_prep.manualEdgesBetweenGroups(hierarchicalCommunities, nodes, manualEdgesFile, manualPreferencesFile)
#	print('manual nodeEdges:', nodeEdges)			

#print()

w, h = 0, 1000;
allGroupsCombinations = [[0 for x in range(w)] for y in range(h)]
combCnt = 0
iterationCnt = len(networkGroups) + len(managementLevels)
for i in range(iterationCnt):
	if i == 0: #leader <-> managers
		allGroupsCombinations[combCnt].append(managementLevels[0])		
		allGroupsCombinations[combCnt].append(managementLevels[1])	
		allGroupsCombinations[combCnt].append('noRandom')	
		combCnt += 1	

	elif i < len(networkGroups)+1: # managers <-> corresponding low-level nodes
		managerPos = managementLevels[1][i-1]
		lowLevelPos = len(managementLevels[0]) + len(managementLevels[1]) + i - 1
		manager = []
		manager.append(managementLevels[1][i-1])
		allGroupsCombinations[combCnt].append(manager)
		allGroupsCombinations[combCnt].append(hierarchicalCommunities[lowLevelPos])	
		allGroupsCombinations[combCnt].append('noRandom')	
		combCnt += 1	

	elif i == len(networkGroups) + 1: #find probability between groups
		sz = len(networkGroups) + 1
		for j in range(sz):
			for k in range(sz):
				if k >= j:			
					if j == 0 and k == 0:
						allGroupsCombinations[combCnt].append(managementLevels[1])
						allGroupsCombinations[combCnt].append(managementLevels[1])
						allGroupsCombinations[combCnt].append('noRandom')	
						combCnt += 1
					elif j == 0 and k != 0:
						allGroupsCombinations[combCnt].append(managementLevels[1])
						allGroupsCombinations[combCnt].append(hierarchicalCommunities[k+sz-1])
						allGroupsCombinations[combCnt].append('noRandom')	
						combCnt += 1	
					elif j != 0 and k == 0:
						allGroupsCombinations[combCnt].append(hierarchicalCommunities[j+sz-1])
						allGroupsCombinations[combCnt].append(managementLevels[1])
						allGroupsCombinations[combCnt].append('noRandom')	
						combCnt += 1	
					else:
						allGroupsCombinations[combCnt].append(hierarchicalCommunities[j+sz-1])
						allGroupsCombinations[combCnt].append(hierarchicalCommunities[k+sz-1])
						
						#to only allow randomization of edges between level 1 groups
						#within each group in level1, there is no randomization
						#within -> src group = trgt groups -> (in group edge generation)
						if hierarchicalCommunities[j+sz-1] == hierarchicalCommunities[k+sz-1]:
							allGroupsCombinations[combCnt].append('noRandom')	
						else:
							allGroupsCombinations[combCnt].append('random')	
#							allGroupsCombinations[combCnt].append('random')	

						combCnt += 1	

	elif i > len(networkGroups)+1: 
		#find probabilities between leaders and NOT their low-level groups
		sz = len(networkGroups) + 1	
		for j in range(sz):
			if j == 0: #leader node
				g = []
				for n in nodes:
					if n not in managementLevels[1] and n not in managementLevels[0]:
						g.append(n)
				allGroupsCombinations[combCnt].append(managementLevels[0])
				allGroupsCombinations[combCnt].append(g)
				allGroupsCombinations[combCnt].append('random')	
				combCnt += 1	
	
			else:
				manager = []
				manager.append(managementLevels[1][j-1])
				g = []
				for community in networkGroups:
					if manager[0] not in community:
						for n in nodes:
							if n in community and n not in managementLevels[0] and n not in managementLevels[1]:
								g.append(n)
		
				
				allGroupsCombinations[combCnt].append(manager)
				allGroupsCombinations[combCnt].append(g)
				allGroupsCombinations[combCnt].append('random')	
				combCnt += 1	

'''				
for entry in allGroupsCombinations:
	if entry != []:
		print(entry)
'''

#bernoulli Model
totalGeneratedEdges = []
if modelName == 'BWRN':
	#print('bernoulli_WRG')
	for i in range(combCnt):
		#print(i, allGroupsCombinations[i])			
		generatedEdges = data_prep.BWRN(nodeEdges, allGroupsCombinations[i], probOfSuccess)
				
		for edge in generatedEdges:
			totalGeneratedEdges.append(edge)


elif modelName == 'WRG':
	#print('regular_WRG')
	for i in range(combCnt):
						
		#print(i, allGroupsCombinations[i])				
		generatedEdges = data_prep.WRG(nodeEdges, allGroupsCombinations[i])

		for edge in generatedEdges:
			totalGeneratedEdges.append(edge)

if randomizeIDs == "Randomize":
	randomNodeIds = data_prep.randomizeNodeIds(totalGeneratedEdges, randomNodeIdsFile, len(nodes))
	#print(randomNodeIds)

#print generated edges:
sourceTargetTuples = []
totalW = 0
finalGeneratedEdges = []
for edge in totalGeneratedEdges:
	#to make sure to only print every directed unique edge only once
	if (edge[0], edge[1]) not in sourceTargetTuples:
		sourceTargetTuples.append((edge[0], edge[1]))
		src = edge[0]
		trgt = edge[1]
		weight = edge[2]
		totalW += int(weight)
		#print(src, trgt, weight)

		#change node ids to the new random node ids
		if randomizeIDs == "Randomize":		
			newSourceId = ''
			newTargetId = ''
			for rnids in randomNodeIds:
				if src == rnids[0]:
					newSourceId = rnids[1]
				if trgt == rnids[0]:
					newTargetId = rnids[1]
			finalGeneratedEdges.append((newSourceId, newTargetId, weight))
		else:		
			finalGeneratedEdges.append((src, trgt, weight))

		'''		
		for k in range(int(weight)):		
			if randomizeIDs == "Randomize":
				print(newSourceId, newTargetId)	
			else:	
				print(src, trgt)		
		'''	
		if randomizeIDs == "Randomize":				
			print(newSourceId, newTargetId, weight)	
		else:	
			print(src, trgt, weight)

#find breakdown of generated edges between hierarchical groups
#data_prep.findBreakDownOfGeneratedEdgesBetweenGroups(hierarchicalCommunities, finalGeneratedEdges)				
