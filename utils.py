from math import sqrt
import re

def distanceOfTwoPoints(start, end):
    distance = sqrt(abs((int(end[1]) - int(start[1]))**2 + (int(end[0]) - int(start[0]))**2))
    return distance

def build_location_table(map):
    location_table = {}
    for m in map:
        location_table[str(m['nodeId'])] = (int(m['x']), int(m['y']))
    return location_table


def build_neighbour_table(map):
    neighbour_table = {}
    for m in map:
        neighbour_table[str(m['nodeId'])] = ([x.strip() for x in str(m['linkTo']).split(',')])
    return neighbour_table

def build_graph(location, neighbour):
    graph = {}
    for k,v in neighbour.items():
        d = {}
        for i in v:
            d[i] = distanceOfTwoPoints(location[k], location[i])
        graph[k] = d

    return graph

def getValueFromArrayOfDicts(keyToCheck, arrayToCheck):
    for m in arrayToCheck:
        for i in m:
            if(i == keyToCheck):
                return m[i]

#change map names like COM1Level2Node3 to 123, COM2Level3Node21 to 2321 etc.
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

#given a node and a map, get the node name.
def getNodeNameFromMap(mapVar, node):
    for m in mapVar:
        if node == m['nodeId']:
            return str(m['nodeName'])

def getBuildingFromNode(node):
    nodeArray = node.split('#')
    return nodeArray[0]

def getCOMBuildingFromNode(node):
    nodeArray = node.split('#')
    return "COM" + nodeArray[0]

#get the relevant level of building from node number
def getLevelFromNode(node):
    nodeArray = node.split('#')
    return nodeArray[1]

#find the relevant to node of the map
def findTONodeFromMap(mapVar, nextMapBuilding, nextMapLevel):
    for m in mapVar:
        if m['nodeName'].startswith("TO") and ((nextMapBuilding + "-" + nextMapLevel) in m['nodeName']):
            print (m['nodeName'])
            return str(m["nodeId"])

# get the next map's first node from the TO Node of the previous map
def getNextMapFirstNodeFromTONode(mapVar, node):
    integersInNodeList = str(getNodeNameFromMap(mapVar, node)).strip().split('-')
    return str(integersInNodeList[-1])

#check whether two nodes are from the same map
def isFromSameMap(initialNode, finalNode):
    initialNodeArray = initialNode.split('#')
    finalNodeArray = finalNode.split('#')
    return (initialNodeArray[0] == finalNodeArray[0] and initialNodeArray[1] == finalNodeArray[1])
