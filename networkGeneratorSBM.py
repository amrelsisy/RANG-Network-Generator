import csv
import operator
import random
import math
import sys
import dataPreparation as data_prep

if sys.argv[1] == '-h' or sys.argv[1] == '--help':
	print('Expected command line argument to use the \033[1mauto\033[0m version of the RANG network generator.')
	print('\033[1m\'python3 networkGeneratorSBM.py version model p Randomization network_file network_groups random_node_ids output_file number_of_networks\'\033[0m')
	print()
	print('\033[1mversion:\033[0m  Indicates the usage of the auto/manual version of the RANG generator. Expects: \'auto\' or \'manual\'')
	print()
	print('\033[1mmodel:\033[0m Indicates the usage of the BWRN/WRG model. Expects: \'BWRN\' or \'WRG\'')
	print()
	print('\033[1mp:\033[0m Probability of creating an edge using the specified model.')
	print()
	print('\033[1mRandomization:\033[0m If a user wants to randomize node IDs for increased anonymity, the user must pass in \'Randomize\', otherwise the user passes in \'noRandomize\'.')
	print()
	print('\033[1mnetwork_file:\033[0m Network file with an edge list of the format: source_node target_node edge_weight. Note: edgelist is space separated and must have weights provided.')
	print()
	print('\033[1mnetwork_groups:\033[0m Original groups of the provided network. These groups can be found using either ground truth data, or a community detection method.')
	print()
	print('\033[1mrandom_node_ids:\033[0m File with a mapping of the original node IDs to the new randomized node IDs. This file should NOT be provided if the user chooses \'noRandomize\' for the randomization command line argument. Expected format: originalNodeId RandomNodeId (space separated).')
	print()
	print('\033[1moutput_file:\033[0m Name of the file that the generated network will be printed to. If more than one network will be generated, the file names will automatically be numbered')
	print()
	print('\033[1mnumber_of_networks:\033[0m The number of networks that the user wants to generate.')
	print()

#start bold = \033[1m
#end bold = \033[0m


	print()
	print('Expected command line argument to use the \033[1mmanual\033[0m version of the RANG network generator.')
	print('\033[1m\'python3 networkGeneratorSBM.py version model p Randomization network_groups network_degree hierarchy_network edges_between_groups node_preference random_node_ids output_file number_of_networks\'\033[0m')

	print()
	print('\033[1mversion:\033[0m Indicates the usage of the auto/manual version of the RANG generator. Expects: \'auto\' or \'manual\'')
	print()
	print('\033[1mmodel: Indicates the usage of the BWRN/WRG model. Expects: \'BWRN\' or \'WRG\'')
	print()
	print('\033[1mp:\033[0m Probability of creating an edge using the specified model.')
	print()
	print('\033[1mRandomization:\033[0m If a user wants to randomize node IDs for increased anonymity, the user must pass in \'Randomize\', otherwise the user passes in \'noRandomize\'.')
	print()
	print('\033[1mnetwork_groups:\033[0m Original groups of the provided network. These groups can be found using either ground truth data, or a community detection method.')
	print()
	print('\033[1mnetwork_degree:\033[0m Integer value representing the total degree of the network.')
	print()
	print('\033[1mhierarchy_network:\033[0m This file will indicate the leader, and the managers of the network. See readme for more info on expected format.')
	print()
	print('\033[1medges_between_groups:\033[0m This file will list out the edges between the hierarchical groups in our network. See readme for more info on the expected format.')
	print()
	print('\033[1mnode_preference:\033[0m This file will be composed of each group’s node preference. See readme for more info on the expected format.')
	print()
	print('\033[1mrandom_node_ids:\033[0m File with a mapping of the original node IDs to the new randomized node IDs. This file should NOT be provided if the user chooses “noRandomize” for the randomization command line argument. Expected format: originalNodeId RandomNodeId (space separated)')
	print()
	print('\033[1moutput_file:\033[0m Name of the file that the generated network will be printed to. If more than one network will be generated, the file names will automatically be numbered')
	print()
	print('\033[1mnumber_of_networks:\033[0m The number of networks that the user wants to generate.')
	print()
	exit()



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

				
