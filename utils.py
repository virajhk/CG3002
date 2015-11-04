from math import sqrt
import re
import json

#---------------------------------------testing purpose----------------------------------------
# from priodict import priorityDictionary
# import json, requests
# url = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?Building=COM1&Level=2'
#
# params = dict(
#     Building='COM1',
# Level='2'
# )
#
# resp = requests.get(url=url, params=params)
# data = json.loads(resp.text)
#print data
#-----------------------------------------------------------------------------------------------
# sqrt((y2-y1)^2+(x2-x1)^2)
# need to do int() otherwise the data type will unicode(undesirable)
# the parameters end , start are tuples
def distanceOfTwoPoints(start, end):
    distance = sqrt(abs((int(end[1]) - int(start[1]))**2 + (int(end[0]) - int(start[0]))**2))
    return distance

# This example is for com1 level 2:
# Constructing the following table
#   node id | x  | y   |
#    1      | 0  |2436 |
#    2      |2152|2436 |
# in a form of dictionary : {'1':(0,2436),'2':(2152,2436)} <--- this dictionary is returned
def build_location_table(map):
    location_table = {}
    for m in map:
        location_table[str(m['nodeId'])] = (int(m['x']), int(m['y']))  # need to put str otherwise the data type will be in unicode (undesirable)
    return location_table

# This example is for com1 level 2:
# Constructing the following table
#   node id | neighbour nodes |
#    1      |        2        |
#    2      |      1, 3, 4    |
# in a form of dictionary : {'1':['2'],'2':['1','3','4']} <--- this dictionary is returned
# Note: Split function stores everything in an array
def build_neighbour_table(map):
    neighbour_table = {}
    for m in map:
        neighbour_table[str(m['nodeId'])] = ([x.strip() for x in str(m['linkTo']).split(',')])  # need to put str otherwise the data type will be in unicode (undesirable)
    return neighbour_table

# This example is for com1 level 2:
# Constructing the following table
#   node id | neighbour nodes/distance from nodeId  |
#     1     |               2/2152.0                |
#     2     |      1/2152.0 ,3/1705.0 ,4/731.0      |
# in a form of dictionary : {'1':{'2':2152.0},'2':{'1':2152.0, '3':1705.0, '4':731.0}} <--- this dictionary is returned
def build_graph(location, neighbour):
    graph = {}
    for k,v in neighbour.items():
        d = {}
        for i in v:
            d[i] = distanceOfTwoPoints(location[k], location[i])
        graph[k] = d

    return graph

# This example is for com1 level 2:
# keyToCheck: 1#2
# arrayToCheck: [{"1#2": {jsondata1}}, {"2#2" : {jsondata2}}]
# returns jsondata1
def getValueFromArrayOfDicts(keyToCheck, arrayToCheck):
    for m in arrayToCheck:
        for i in m:
            if(i == keyToCheck):
                return m[i]

# renames all the nodeIds in the following format: #buildingNum#levelNum#nodeId
# This example is for com1 level 2: nodeId 1 is rename as 1#2#1
def mapifyNodeIDs(data, building, level):
    mapVar = data['map']
    buildingNumberList = (re.findall('\d+', building))
    idPrepend = str(buildingNumberList[0]) + "#" + str(level)
    for m in mapVar:
        m['nodeId'] = idPrepend + "#"  + m['nodeId']
        linkNumbers = str(m['linkTo']).strip().split(',')
        idPrependedLinkTo = [idPrepend + "#" + s.strip() for s in linkNumbers]
        m['linkTo'] = ",".join(map(str, idPrependedLinkTo))
    data['map'] = mapVar
    return data

# given a nodeId and a map, get the node name.
# This example is for com1 level 2:
# if nodeId = 7, nodeName returned will be "Lobby"
def getNodeNameFromMap(mapVar, nodeId):
    for m in mapVar:
        if nodeId == int(m['nodeId']):
            return str(m['nodeName'])

# COM1Level2Node3 represented as 1#2#3#
# 1#2#3# is stored in an array as [1,2,3]. Split function stores everything in an array
# 0th element from array is returned. 1 is returned in this example
def getBuildingFromNode(node):
    nodeArray = node.split('#')
    return nodeArray[0]

# COM1Level2Node3 represented as 1#2#3#
# 1#2#3# is stored in an array as [1,2,3]. Split function stores everything in an array
# "COM" is appended with the 0th element and returned
def getCOMBuildingFromNode(node):
    nodeArray = node.split('#')
    return "COM" + nodeArray[0]

# COM1Level2Node3 represented as 1#2#3#
# 1#2#3# is stored in an array as [1,2,3]. Split function stores everything in an array
# 1st element from array is returned. 2 is returned in this example
def getLevelFromNode(node):
    nodeArray = node.split('#')
    return nodeArray[1]

# find the relevant "TO" node of the current map and returns the nodeId for that "TO" node
# This example is for com1 level 2:
# if the node name is TO COM2-2-1, then we return 31 (its nodeID)
def findTONodeFromMap(mapVar, nextMapBuilding, nextMapLevel):
    for m in mapVar:
        if m['nodeName'].startswith("TO") and ((nextMapBuilding + "-" + nextMapLevel) in m['nodeName']):
            print (m['nodeName'])
            return str(m["nodeId"])

# get the next map's first nodeId from the TO Node of the previous map
# Example:
# for com1 level 2 --> if the "TO" node is "TO COM2-2-1", the array integersInNodeList will be: ['TO COM2','2','1']
# the last element in the array is returned. 1 is returned in this case. 1 is the first nodeId for com2 level 2
def getNextMapFirstNodeFromTONode(mapVar, node):
    integersInNodeList = str(getNodeNameFromMap(mapVar, node)).strip().split('-')
    return str(integersInNodeList[-1])

# check whether two nodes are from the same map
# Example:
# 2 nodes of the format: #1#2#3 (Building 1 level 2 node 3) & #1#2#4 (Building 1 level 2 node 4) will return true
# 2 nodes of the format: #1#2#3 (Building 1 level 2 node 3) & #1#3#4 (Building 1 level 3 node 4) will return false
def isFromSameMap(initialNode, finalNode):
    initialNodeArray = initialNode.split('#')
    finalNodeArray = finalNode.split('#')
    return (initialNodeArray[0] == finalNodeArray[0] and initialNodeArray[1] == finalNodeArray[1])

def stitchMaps(map1, map2, map3):
    map1_location = build_location_table(map1)
    map2_location = build_location_table(map2)
    map3_location = build_location_table(map3)

    map1_neighbor = build_neighbour_table(map1)
    map2_neighbor = build_neighbour_table(map2)
    map3_neighbor = build_neighbour_table(map3)

    map1_graph = build_graph(map1_location, map1_neighbor)
    map2_graph = build_graph(map2_location, map2_neighbor)
    map3_graph = build_graph(map3_location, map3_neighbor)

    #map1_dict = map1_graph['1#2#31']
    map1_graph['1#2#31']['2#2#1'] = 0.1
    map2_graph['2#2#1']['1#2#31'] = 0.1
    map2_graph['2#2#16']['2#3#11'] = 0.1
    map3_graph['2#3#11']['2#2#16'] = 0.1    

    stitched_graph = map1_graph.copy()
    stitched_graph.update(map2_graph)
    stitched_graph.update(map3_graph)

    return stitched_graph

# inputMap1 = {'building' : "1", "level" : str(2)}
# #inputMap2 = {'building' : "1", "level" : str(3)}
# inputMap3 = {'building' : "2", "level" : str(2)}
# inputMap4 = {'building' : "2", "level" : str(3)}
# dataArray = []

# initialNode = "1#2#29"
# finalNode = "2#3#10"

# with open("{0}Level{1}.json".format("COM" + inputMap1['building'], inputMap1['level'])) as data_file:
#     dataArray.append({("COM" + inputMap1['building'] + "#" + inputMap1['level']) : mapifyNodeIDs(json.load(data_file), inputMap1['building'], inputMap1['level'])})

# with open("{0}Level{1}.json".format("COM" + inputMap3['building'], inputMap3['level'])) as data_file3:
#     dataArray.append({("COM" + inputMap3['building'] + "#" + inputMap3['level']) : mapifyNodeIDs(json.load(data_file3), inputMap3['building'], inputMap3['level'])})

# with open("{0}Level{1}.json".format("COM" + inputMap4['building'], inputMap4['level'])) as data_file4:
#     dataArray.append({("COM" + inputMap4['building'] + "#" + inputMap4['level']) : mapifyNodeIDs(json.load(data_file4), inputMap4['building'], inputMap4['level'])})

# array = initialNode.split('#')
# initialNode = str(array[0]) + str(array[1]) + str(array[2])
# array2 = finalNode.split('#')
# finalNode = str(array2[0]) + str(array2[1]) + str(array2[2])

# stitched_map = stitchMaps(getValueFromArrayOfDicts("COM1#2", dataArray)['map'], getValueFromArrayOfDicts("COM2#2", dataArray)['map'], getValueFromArrayOfDicts("COM2#3", dataArray)['map'])
# print stitched_map

#---------------------------------------testing purpose----------------------------------------
# location = build_location_table(data['map'])
# neighbour =  build_neighbour_table(data['map'])
# print build_graph(location, neighbour)
#print findTONodeFromMap(data['map'],"COM2","2")
#print getNextMapFirstNodeFromTONode(data['map'],16)
#print isFromSameMap("1#2#3","1#3#4")
#print getNodeNameFromMap(data['map'],7)
#print getValueFromArrayOfDicts("1#2",[{"1#2": 10}, {"2#2" : 2}])
#print mapifyNodeIDs(data, getBuildingFromNode("1#2#3#"), getLevelFromNode("1#2#3#"))
#-----------------------------------------------------------------------------------------------
