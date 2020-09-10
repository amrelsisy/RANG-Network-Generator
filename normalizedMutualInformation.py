import sys
import csv
import sklearn.metrics
import math

originalNodes = ['1', '2', '3', '5', '6', '4', '7', '24', '25', '27', '9', '26', '29', '15', '16', '19', '21', '23', '30', '31', '32', '10', '14', '20', '28', '33', '8', '11', '12', '13', '17', '18', '22', '34']
#originalNodes.sort()
#print(originalNodes)

w, h = 2, len(originalNodes);
randomNodeIds = [[0 for x in range(w)] for y in range(h)]
#read random node id's from file
f = open("/Users/AmrElsisy/Desktop/criminalNetworksStatistics/KARATE/randomNodeIds.txt","r")
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

#ground truth communities
origComm1 = ['1', '2', '3', '4', '14', '20', '8', '12', '13', '18', '22']
origComm2 = ['5', '6', '7', '11', '17'] 
origComm3 = ['24', '27', '9', '15', '16', '19', '21', '23', '30', '31', '10', '28', '33', '34'] 
origComm4 = ['25', '26', '29', '32']
for i in range(len(origComm1)):
	for j in range(len(randomNodeIds)):
		if origComm1[i] == randomNodeIds[j][0]:			
			origComm1[i] = randomNodeIds[j][1]			
for i in range(len(origComm2)):
	for j in range(len(randomNodeIds)):
		if origComm2[i] == randomNodeIds[j][0]:			
			origComm2[i] = randomNodeIds[j][1]			
for i in range(len(origComm3)):
	for j in range(len(randomNodeIds)):
		if origComm3[i] == randomNodeIds[j][0]:			
			origComm3[i] = randomNodeIds[j][1]			
for i in range(len(origComm4)):
	for j in range(len(randomNodeIds)):
		if origComm4[i] == randomNodeIds[j][0]:			
			origComm4[i] = randomNodeIds[j][1]			
#print(origComm1)



speakEasy = 0
louvaine = 0
natural = 0
if speakEasy == 1: #speakeasy communities are used
	origComm1 = ['1','20','11','82','83','87','4','2','77','6']
	origComm2 = ['12','25','9','14','13','31','18','17']
	origComm3 = ['76','3','19','15','78']
	origComm4 = ['85','8','84','5']
elif louvaine == 1: #louvaine detected communities are used
	origComm1 = ['12','9','14','13','18','25','17','31','3','77']
	origComm2 = ['2','83','87','1','4','82','6','20','11','85','84','5','8','19']
	origComm3 = ['76','78','15']
	origComm4 = []
elif natural == 1:
	origComm1 = ['83','1','19','5','3','76','11','85','2','8','78','20','77','6','15','87','84','9','82','4']
	origComm2 = ['17','12','18','13','14','25','31']
	origComm3 = []
	origComm4 = []


#at most there are 6 generated communities for CAVIAR6	
genComm1 = []
genComm2 = []
genComm3 = []
genComm4 = []
genComm5 = []
genComm6 = []

f = open(sys.argv[1],"r")
contents = f.readlines()
commCnt = 0
for line in contents:		
	nodes = line.split(" ")
	for n in nodes:
		if n != '\n':
			if commCnt == 0:
				genComm1.append(n.rstrip())
			elif commCnt == 1:
				genComm2.append(n.rstrip())
			elif commCnt == 2:
				genComm3.append(n.rstrip())
			elif commCnt == 3:
				genComm4.append(n.rstrip())
			elif commCnt == 4:
				genComm5.append(n.rstrip())
			elif commCnt == 5:
				genComm6.append(n.rstrip())
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
for oc in range(4): #go through original communities
	if oc == 0:
		origComm = origComm1
	elif oc == 1:
		origComm = origComm2
	elif oc == 2:
		origComm = origComm3
	elif oc == 3:
		origComm = origComm4
										 
	n_r = len(origComm) #nodes in community r in partition C
	
	for gc in range(6): #go through generated communities
		if gc == 0:
			genComm = genComm1
		elif gc == 1:
			genComm = genComm2
		elif gc == 2:
			genComm = genComm3
		elif gc == 3:
			genComm = genComm4
		elif gc == 4:
			genComm = genComm5
		elif gc == 5:
			genComm = genComm6
						
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

for oc in range(4):
	if oc == 0:
		origComm = origComm1
	elif oc == 1:
		origComm = origComm2
	elif oc == 2:
		origComm = origComm3
	elif oc == 3:
		origComm = origComm4
	
	n_c	= len(origComm)		
	if n_c > 0:			
		summation_HC -= (n_c / n) * math.log2(n_c / n) 
		#print('H(C): ', summation_HC, n_c, n, math.log2(n_c/n), n_c, n)
H_C = summation_HC

for gc in range(6):				
	if gc == 0:
		genComm = genComm1
	elif gc == 1:
		genComm = genComm2
	elif gc == 2:
		genComm = genComm3
	elif gc == 3:
		genComm = genComm4
	elif gc == 4:
		genComm = genComm5
	elif gc == 5:
		genComm = genComm6
	
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


'''
#built in NMI
labels_true = []
labels_pred = []
ownCluster = 100
for n in originalNodes:
	if n in origComm1:
		labels_true.append(0)
	elif n in origComm2:
		labels_true.append(1)
	elif n in origComm3:
		labels_true.append(2)
	elif n in origComm4:
		labels_true.append(3)

	if n in genComm1:
		labels_pred.append(0)
	elif n in genComm2:
		labels_pred.append(1)
	elif n in genComm3:
		labels_pred.append(2)
	elif n in genComm4:
		labels_pred.append(3)
	elif n in genComm5:
		labels_pred.append(4)
	elif n in genComm6:
		labels_pred.append(5)
	else:
		labels_pred.append(ownCluster) #node is its own cluster, (isolated node)
		ownCluster += 100


#print(labels_true)
#print(labels_pred)


nmi = sklearn.metrics.normalized_mutual_info_score(labels_true, labels_pred, average_method='arithmetic')


print('sklearn NMI: ', nmi)
print()
#if nmi > 0:
#	print(nmi)
#else:
#	print(0)

'''
