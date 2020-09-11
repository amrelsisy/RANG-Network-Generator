import sys
import csv
import sklearn.metrics
import math


networkGroups = sys.argv[1]
f = open(networkGroups,"r")
lines = f.readlines()
originalNodes = []		
for l in lines:
	members = l.split(' ')
	for m in members:
		if m.rstrip() not in originalNodes:
			originalNodes.append(m.rstrip())
f.close()	
#print('nodes:', originalNodes)

if sys.argv[2] == 'Randomize':
	w, h = 2, len(originalNodes);
	randomNodeIds = [[0 for x in range(w)] for y in range(h)]
	#read random node id's from file
	f = open(sys.argv[3],"r")
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
																					 
	for i in range(len(originalNodes)):
		for j in range(len(randomNodeIds)):
			if originalNodes[i] == randomNodeIds[j][0]:
				originalNodes[i] = randomNodeIds[j][1]
	originalNodes.sort()
	#print(originalNodes)
	f.close()
 
f = open(networkGroups, "r")
lines = f.readlines()
w, h = 0, len(lines);
originalCommunities = [[0 for x in range(w)] for y in range(h)]
communityCnt = 0
for l in lines:
	communityNodesCnt = 0
	nodesInCommunity = l.split(' ')
	for n in nodesInCommunity:
		originalCommunities[communityCnt].append(n.rstrip())
		communityNodesCnt += 1
		
	communityCnt += 1

#for entry in originalCommunities:
#	print(entry)
				
if sys.argv[2] == 'Randomize':
	for i in range(len(originalCommunities)):
		for j in range(len(originalCommunities[i])):		
			for k in range(len(randomNodeIds)):			
				if originalCommunities[i][j] == randomNodeIds[k][0]:			
					originalCommunities[i][j] = randomNodeIds[k][1]			

#print(originalCommunities)


				
w, h = 0, len(originalNodes);
generatedCommunities = [[0 for x in range(w)] for y in range(h)]

generatedGroups = ''
if sys.argv[2] == 'Randomize':
	generatedGroups = sys.argv[4]
else:
	generatedGroups = sys.argv[3]

f = open(generatedGroups,"r")
contents = f.readlines()
commCnt = 0
for line in contents:		
	nodes = line.split(" ")
	for n in nodes:
		if n != '\n':
			generatedCommunities[commCnt].append(n.rstrip())
	commCnt += 1	
f.close()
	


#given two different partitions C and D, mutual information I(C,D) is
I_C_D = 0
H_C = 0 #entropy of partition C
H_D = 0 #entropy of partition D
summation = 0
n = len(originalNodes) #total nodes
origComm = []
genComm = []
for oc in range(len(originalCommunities)): #go through original communities
	origComm = originalCommunities[oc]
	n_r = len(origComm) #nodes in community r in partition C
	
	for gc in range(len(generatedCommunities)): #go through generated communities
		genComm = generatedCommunities[gc]
		n_s = len(genComm) #nodes in community s in partition D
	
		#node that are both in community r in C, and in community s in D
		n_r_s = len(set(origComm) & set(genComm))

		if n_r_s > 0:
			x = (n * n_r_s) / (n_r * n_s)	
			summation += (n_r_s / n) * math.log2(x) 
			#print('I(C): ', summation, n, n_r_s, n_r, n_s, x)	

I_C_D = summation

#calculate H(C) and H(D)
origComm = []
genComm = []
summation_HC = 0
summation_HD = 0

for oc in range(len(originalCommunities)):
	origComm = originalCommunities[oc]			
	n_c	= len(origComm)		
	if n_c > 0:			
		summation_HC -= (n_c / n) * math.log2(n_c / n) 
		#print('H(C): ', summation_HC, n_c, n, math.log2(n_c/n), n_c, n)
H_C = summation_HC

for gc in range(len(generatedCommunities)):				
	genComm = generatedCommunities[gc]			
	
	n_d	= len(genComm)		
	if n_d > 0:
		summation_HD -= (n_d / n) * math.log2(n_d / n) 
		#print('H(D): ', summation_HD, n_d, n, math.log2(n_d/n), n_d, n)

H_D = summation_HD
NMI = (2*I_C_D) / (H_C + H_D)
#print('I_C_D: ', I_C_D, 'H_C: ', H_C, 'H_D: ', H_D)
#error with NMI, gives negative values
#need to check documentation, and fix this
#print('calculated NMI: ', NMI)
print(NMI)


