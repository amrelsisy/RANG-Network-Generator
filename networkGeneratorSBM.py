import csv
import operator
import random
import math
import sys
import dataPreparation as data_prep


manualAuto = sys.argv[1]
if manualAuto != "auto" and manualAuto != "manual":
	print("Please input \'auto\' or \'manual\'.")
	exit()

modelName = sys.argv[2]
if modelName != "BWRN" and modelName != "WRG":
	print("Please specify model name as \'BWRN\' or \'WRG\'.")
	exit()


probOfSuccess = sys.argv[3]
try:
	float(probOfSuccess)
	if float(probOfSuccess) > 1 or float(probOfSuccess) <= 0:
		print("Please enter a valid probability value between (0.0, 1.0].")
		exit()
except ValueError:
	print("Please enter a valid probability value between (0.0, 1.0].")
	exit()

randomizeIDs = sys.argv[4]
if randomizeIDs != "noRandomize" and randomizeIDs != "Randomize":
	print("Please pass in \'Randomize\', to randomize node ID's, otherwise please pass in \'noRandomize\'. ")
	exit()

if manualAuto == "auto":
	networkEdgesFile = sys.argv[5]
	try:
		open(networkEdgesFile,"r")
	except OSError as err:			
		print("Please enter a valid network edges file.")
		exit()		

	networkGroupsFile = sys.argv[6]
	try:
		open(networkGroupsFile,"r")
	except OSError as err:			
		print("Please enter a valid network groups file.")
		exit()		


	manualHierarchyFile = ''
elif manualAuto == "manual":
	networkEdgesFile = ''
	networkGroupsFile = sys.argv[5]
	try:
		open(networkGroupsFile,"r")
	except OSError as err:			
		print("Please enter a valid network groups file.")
		exit()		


	try:
		int(sys.argv[6])
		manualDegreeOfNetwork = sys.argv[6]
		if int(manualDegreeOfNetwork) <= 0:
			print("Please enter a valid total degree of the network.")
			exit()
	except ValueError:
		print("Please enter a valid total degree of the network.")
		exit()


	manualHierarchyFile = sys.argv[7] 
	try:
		open(manualHierarchyFile,"r")
	except OSError as err:			
		print("Please enter a valid hierarchy file.")
		exit()		


	manualEdgesFile = sys.argv[8] 
	try:
		open(manualEdgesFile,"r")
	except OSError as err:			
		print("Please enter a valid edges between groups file.")
		exit()		


	manualPreferencesFile = sys.argv[9]
	try:
		open(manualPreferencesFile,"r")
	except OSError as err:			
		print("Please enter a valid node preference file.")
		exit()		


if manualAuto == "auto":	
	if randomizeIDs == "Randomize":
		randomNodeIdsFile = sys.argv[7]
		try:
			open(randomNodeIdsFile,"r")
		except OSError as err:			
			print("Please enter a valid randomized node ids file.")
			exit()		


elif manualAuto == "manual":
	if randomizeIDs == "Randomize":
		randomNodeIdsFile = sys.argv[10]
		try:
			open(randomNodeIdsFile,"r")
		except OSError as err:			
			print("Please enter a valid randomized node ids file.")
			exit()		



if manualAuto == 'auto':
	nodes, totalDegree = data_prep.findNumberOfUniqueNodesAndTotalDegree(networkEdgesFile, networkGroupsFile)

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



numberOfCommunities, managementLevels, hierarchicalCommunities, networkGroups = data_prep.readGroundTruthCommunities(nodes, networkEdgesFile, networkGroupsFile, manualAuto, manualHierarchyFile)



if manualAuto == 'auto':				
	nodeEdges = data_prep.findEdgesToOtherNodes(networkEdgesFile, nodes)
elif manualAuto == 'manual':
	nodeEdges = data_prep.manualEdgesBetweenGroups(hierarchicalCommunities, nodes, manualEdgesFile, manualPreferencesFile)


w, h = 0, len(hierarchicalCommunities)*len(hierarchicalCommunities);
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

numberOfRuns = 0
outputFile = ""
if manualAuto == "auto":
	if randomizeIDs == "noRandomize":
		try:
			numberOfRuns = int(sys.argv[8])
			if numberOfRuns < 0:
				print("Please enter a valid value for number of runs.")
				exit()
		except ValueError:
			print("Please enter a valid value for number of runs.")
			exit()
	elif randomizeIDs == "Randomize":
		try:
			numberOfRuns = int(sys.argv[9])
			if numberOfRuns < 0:
				print("Please enter a valid value for number of runs.")
				exit()
		except ValueError:
			print("Please enter a valid value for number of runs.")
			exit()
			
elif manualAuto == "manual":
	if randomizeIDs == "noRandomize":
		try:
			numberOfRuns = int(sys.argv[11])
			if numberOfRuns < 0:
				print("Please enter a valid value for number of runs.")
				exit()
		except ValueError:
			print("Please enter a valid value for number of runs.")
			exit()
			
	elif randomizeIDs == "Randomize":
		try:
			numberOfRuns = int(sys.argv[12])
			if numberOfRuns < 0:
				print("Please enter a valid value for number of runs.")
				exit()
		except ValueError:
			print("Please enter a valid value for number of runs.")
			exit()
			
		
for runs in range(numberOfRuns):
	if manualAuto == "auto":
		if randomizeIDs == "noRandomize":
			try:
				outputFile = open(sys.argv[7] + str(runs+1) + ".txt", "w+")		
			except OSError as err:			
				print("Please enter a valid path to the output file.")
				exit()		


		elif randomizeIDs == "Randomize":
			try:
				outputFile = open(sys.argv[8] + str(runs+1) + ".txt", "w+")			
			except OSError as err:			
				print("Please enter a valid path to the output file.")
				exit()		

	elif manualAuto == "manual":
		if randomizeIDs == "noRandomize":
			try:
				outputFile = open(sys.argv[10] + str(runs+1) + ".txt", "w+")			
			except OSError as err:			
				print("Please enter a valid path to the output file.")
				exit()		
		elif randomizeIDs == "Randomize":
			try:
				outputFile = open(sys.argv[11] + str(runs+1) + ".txt", "w+")			
			except OSError as err:			
				print("Please enter a valid path to the output file.")
				exit()
				
	#bernoulli Model
	totalGeneratedEdges = []
	if modelName == 'BWRN':
		for i in range(combCnt):
			generatedEdges = data_prep.BWRN(nodeEdges, allGroupsCombinations[i], probOfSuccess)
				
			for edge in generatedEdges:
				totalGeneratedEdges.append(edge)


	elif modelName == 'WRG':
		for i in range(combCnt):
							
			generatedEdges = data_prep.WRG(nodeEdges, allGroupsCombinations[i])
	
			for edge in generatedEdges:
				totalGeneratedEdges.append(edge)

	if randomizeIDs == "Randomize":
		randomNodeIds = data_prep.randomizeNodeIds(totalGeneratedEdges, randomNodeIdsFile, len(nodes))

	sourceTargetTuples = set()
	totalW = 0
	finalGeneratedEdges = []
	for edge in totalGeneratedEdges:
		if (edge[0], edge[1]) not in sourceTargetTuples:
			sourceTargetTuples.add((edge[0], edge[1]))
			src = edge[0]
			trgt = edge[1]
			weight = edge[2]
			totalW += int(weight)

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

			if randomizeIDs == "Randomize":
				edgePair = newSourceId + ' ' + newTargetId + ' ' + str(weight) + '\n'
				outputFile.write(edgePair)	
			else:	
				edgePair = src + ' ' + trgt + ' ' + str(weight) + '\n'
				outputFile.write(edgePair)

				
