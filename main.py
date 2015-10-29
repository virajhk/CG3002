import os
import serial
ser = serial.Serial('/dev/ttyAMA0',9600,timeout=1)

import djikstra as dj
import re
import utils
import time
import whereAmI as wt
from math import sqrt
import json, requests
import sys
import pygame
import pyttsx
import statistics
from collections import deque
engine = pyttsx.init()

#Firmware global variables
first_ack = 0
handshake = 1
keypad = 1
start = ''
end = ''
heading = 0
steps = 0
alti = 0
#end


#Firmware Handshake
while handshake:
    if (first_ack == 0):
        ser.write("h")
        
    response = ser.readline()
    if (response != ''):
        print (response)
    if (first_ack == 1):
        ser.write("a")
        handshake = 0
        print ("Handshake established")
    if (first_ack == 0 and response == "a"):
        first_ack = 1
#end

def isIntOrFloat(x):
    try:
	   a = float(x)
	   b = int(a)
    except ValueError:
	   return False
    else:
	   return True

def textToSpeech(str):
    engine.say(str)
    engine.runAndWait()

textToSpeech("Handshake Established")

def getShortestPath(mapVar, initialNode, finalNode):
    table_location = utils.build_location_table(mapVar)
    print (table_location)
    print ("")
    print ("")
    table_neighbour = utils.build_neighbour_table(mapVar)
    print (table_neighbour)
    print ("")
    print ("")
    graph = utils.build_graph(table_location, table_neighbour)
    print (graph)
    print ("")
    print ("")
    return dj.shortestPath(graph,initialNode,finalNode)

mainUrl = "http://showmyway.comp.nus.edu.sg/getMapInfo.php"
inputMap1 = {'building' : "1", "level" : str(2)}
inputMap2 = {'building' : "1", "level" : str(3)}
inputMap3 = {'building' : "2", "level" : str(2)}
inputMap4 = {'building' : "2", "level" : str(3)}

params1 = dict(
    Building= "COM" + inputMap1['building'],
    Level= inputMap1['level']
)

params2 = dict(
    Building= "COM" + inputMap2['building'],
    Level= inputMap2['level']
)

params3 = dict(
    Building= "COM" + inputMap3['building'],
    Level= inputMap3['level']
)
params4 = dict(
    Building= "COM" + inputMap4['building'],
    Level= inputMap4['level']
)

#Firmware Keypad
while keypad:
    response = ser.readline()
    #print response
    if (response != ''):
        array = response.split(',')
        start = str(array[0].split('.')[0])
        end = str(array[1].split('.')[0])
        print ("Start:" + str(start))
        print ("End:" + str(end))
        keypad = 0
#end

dataArray = []
data = {}
finalData = {}

initialNode = start #input("Enter Initial Node: ")
finalNode = end #input("Enter final Node: ")
textToSpeech("Initial Node " + initialNode)
textToSpeech("Final Node " + finalNode)

try:
    params5 = dict(
        Building= utils.getBuildingFromNode(initialNode),
        Level= utils.getLevelFromNode(initialNode)
    )
    params6 = dict(
        Building= utils.getBuildingFromNode(finalNode),
        Level= utils.getLevelFromNode(finalNode)
    )
    #respX = 
    resp1 = requests.get(url=mainUrl, params=params5)
    #print resp1.text
    resp2 = requests.get(url=mainUrl, params=params6)
    dataArray.append({(utils.getBuildingFromNode(initialNode) + "#" + utils.getLevelFromNode(initialNode)) : utils.mapifyNodeIDs(json.loads(resp1.text), utils.getBuildingFromNode(initialNode), utils.getLevelFromNode(initialNode))})
    if(not utils.isFromSameMap(initialNode, finalNode)):
        dataArray.append({(utils.getBuildingFromNode(finalNode) + "#" + utils.getLevelFromNode(finalNode)) : utils.mapifyNodeIDs(json.loads(resp2.text), utils.getBuildingFromNode(finalNode), utils.getLevelFromNode(finalNode))})
    data = utils.getValueFromArrayOfDicts((utils.getBuildingFromNode(initialNode) + "#" + utils.getLevelFromNode(initialNode)), dataArray)
    finalData = utils.getValueFromArrayOfDicts((utils.getBuildingFromNode(finalNode) + "#" + utils.getLevelFromNode(finalNode)), dataArray)
    print "Wifi Works"
except:
    print "{0}Level{1}.json".format("COM" + inputMap1['building'], inputMap1['level'])
    with open("{0}Level{1}.json".format("COM" + inputMap1['building'], inputMap1['level'])) as data_file:
        dataArray.append({("COM" + inputMap1['building'] + "#" + inputMap1['level']) : utils.mapifyNodeIDs(json.load(data_file), inputMap1['building'], inputMap1['level'])})
    #with open("{0}Level{1}.json".format(inputMap2['building'], inputMap2['level'])) as data_file2:
        #dataArray.append((inputMap2['building'] + inputMap2['level']) : mapifyNodeIDs(json.load(data_file2), inputMap2['building'], inputMap2['level']))

    with open("{0}Level{1}.json".format("COM" + inputMap3['building'], inputMap3['level'])) as data_file3:
        dataArray.append({("COM" + inputMap3['building'] + "#" + inputMap3['level']) : utils.mapifyNodeIDs(json.load(data_file3), inputMap3['building'], inputMap3['level'])})

    with open("{0}Level{1}.json".format("COM" + inputMap4['building'], inputMap4['level'])) as data_file4:
        dataArray.append({("COM" + inputMap4['building'] + "#" + inputMap4['level']) : utils.mapifyNodeIDs(json.load(data_file4), inputMap4['building'], inputMap4['level'])})
    array = initialNode.split('#')
    initialNode = "1#2#" + str(array[2])
    array2 = finalNode.split('#')
    finalNode = "1#2#" + str(array2[2])

    data = utils.getValueFromArrayOfDicts((utils.getCOMBuildingFromNode(initialNode) + "#" + utils.getLevelFromNode(initialNode)), dataArray)
    finalData = utils.getValueFromArrayOfDicts((utils.getCOMBuildingFromNode(finalNode) + "#" + utils.getLevelFromNode(finalNode)), dataArray)

#result = dj.parse(data)
def PrintPathDictionary(path, Map):
    pathDictionary = {}
    for p in path:
        for m in Map:
            if p == m['nodeId']:
                print(str(p) + " : " + str(m['nodeName']))
path = []
if(not utils.isFromSameMap(initialNode, finalNode)):
    TONodeBuilding = utils.getCOMBuildingFromNode(finalNode)
    TONodeLevel = utils.getLevelFromNode(finalNode)
    TONode = utils.findTONodeFromMap(data['map'], TONodeBuilding, TONodeLevel)
    firstNodeNextMap = utils.getNextMapFirstNodeFromTONode(data['map'], TONode)
    #adds the com number and level before the node id
    print (firstNodeNextMap)
    #gives the number of the com building
    COMNumber = (re.findall('\d+', utils.getCOMBuildingFromNode(finalNode)))[0]
    mapifiedfirstNodeNextMap =  COMNumber + utils.getLevelFromNode(finalNode) + firstNodeNextMap
    print (mapifiedfirstNodeNextMap)
    path.append({(utils.getCOMBuildingFromNode(initialNode) + utils.getLevelFromNode(initialNode)) : getShortestPath(data['map'], initialNode, TONode)})
    path.append({(utils.getCOMBuildingFromNode(finalNode) + utils.getLevelFromNode(finalNode)) : getShortestPath(finalData['map'], mapifiedfirstNodeNextMap, finalNode)})
else:
    path.append({(utils.getCOMBuildingFromNode(initialNode) + utils.getLevelFromNode(initialNode)) : getShortestPath(data['map'], initialNode, finalNode)})

path = list(path[0].values())[0]
print (path)
PrintPathDictionary(path, data['map'])

#main algorithm
offset = 360 - wt.getMapNorthAt(data)
givenMagValue = 131;
magQueue = deque([], maxlen=5)
magQueue.append(givenMagValue)
print (offset)
print ("data")
print (data)
accArray = []
magArray = []
wt.magnetometerValues2 = [givenMagValue] + wt.magnetometerValues2 #adding the first mag value to the beginning of the array
accVal = 0
magVal = 1
currNodeCrossed = path[0]
currNodeCrossedX = wt.getNodeX(currNodeCrossed,data)
currNodeCrossedY = wt.getNodeY(currNodeCrossed,data)
currNodeCrossed = wt.findNearestNode(path, currNodeCrossedX, currNodeCrossedY, data)
totalDistance = 0
netDistanceInDir = 0
currPoint = {'x': currNodeCrossedX, 'y': currNodeCrossedY}
approachingCheck = False #checks whether close to checkpoint
#we always travel to the next node that comes after the closest node to the current position
start = time.time()
while(True):
    xChange = 0
    yChange = 0
    #Firmware Data Transfer
    response = ser.readline()
    print response
    if (response != ''):
        array = response.split(',')
        if (len(array) >= 3):
            tempArr = array[0].split('.')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    alti = int(tempArr[0])
            tempArr = array[1].split('.')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    heading = int(tempArr[0])
            tempArr = array[2].split('.')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    steps = int(tempArr[0])
            print ("Alti:" + str(alti))
            print ("Direction:" + str(heading))
            print ("Steps:" + str(steps))
    #end
    magQueue.append(heading)
    currNodeCrossedX = wt.getNodeX(currNodeCrossed,data)
    currNodeCrossedY = wt.getNodeY(currNodeCrossed,data)
    stepTaken = False
    nextCheckpoint = wt.getNextCheckpoint(path, currNodeCrossed)
    #print "nextCheckpoint" + str(nextCheckpoint)
    if(nextCheckpoint == wt.LAST_CONST):
        print ("You've reached your destination. You are a hero")
        break
    nextCheckpointX = wt.getNodeX(nextCheckpoint,data)
    if (currNodeCrossedX != nextCheckpointX):
        xChange = 1
    print ("nextCheckpointX : " + str(nextCheckpointX))
    nextCheckpointY = wt.getNodeY(nextCheckpoint, data)
    if (currNodeCrossedY != nextCheckpointY):
        yChange = 1
    print ("nextCheckpointY : " + str(nextCheckpointY))
    intendedMag = wt.getIntendedMagAngle(currNodeCrossed, nextCheckpoint, offset, data)
    #print "intendedMag" + str(intendedMag)
    #time.sleep(0.5)
    if(accVal < len(wt.accelerationX)):
        wt.addAccToArray(accArray, steps)
        #uncomment the next line to make distance calculation work on the first pass
        #wt.addAccToArray(accArray, wt.accelerationX[accVal])
        #print accArray
        #accVal += 1
    else:
        break
    if(magVal < len(wt.magnetometerValues2)):
        wt.addMagToArray(magArray, statistics.median(list(magQueue)))
        #magVal += 1
        #print magArray
    else:
        break
    if(len(accArray) > 1):
        if(abs(accArray[-1] - accArray[-2]) >= 1):
	    print ("Last value of steps : " + str(abs(accArray[-1])))
            stepTaken = True
    if(len(magArray) > 0):
        print ("Last value of magnetometer : " + str(abs(magArray[-1])))
        currPoint = wt.findCurrentPoint(currPoint['x'], currPoint['y'], magArray[-1], stepTaken, offset, xChange, yChange, intendedMag)
        print ("CurrentX : "  + str(currPoint['x']) + "CurrentY : " + str(currPoint['y']))
        print ("Distance from checkpoint : " +
        str(wt.distanceBetweenTwoCoordinates(currPoint['x'], currPoint['y'], nextCheckpointX, nextCheckpointY)))
        #netDistanceInDir = wt.netDistanceInIntendedDirection(intendedMag, magArray[-1],
            #netDistanceInDir, stepTaken) #checks net distance in intended direction
        #print netDistanceInDir
        #time.sleep(1000)
        if(approachingCheck == False):
            checkGoStraight = wt.provideDeviationAngleInfo(intendedMag, magArray[-1])
            if (checkGoStraight == 0):
                end = time.time()
                if (end - start >= 3 and stepTaken == True):
                    pygame.mixer.music.load("Move.wav")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue
                    start = end
        if(wt.aboutToReach(currPoint['x'], currPoint['y'], nextCheckpointX, nextCheckpointY)):
            print ("hello blah hello")
            print ("Checkpoint reached blah")
            approachingCheck = True
            os.system('espeak -ven+f3 "{0}"'.format("Checkpoint " + nextCheckpoint + " reached."))
	        #engine.say("Checkpoint " + nextCheckpoint + " reached.")
            wt.provideNavInstruction(path, currNodeCrossed, nextCheckpoint,
                currPoint['x'], currPoint['y'], data, offset)
            nextNextCheckpoint = wt.getNextCheckpoint(path, nextCheckpoint)
            if(nextNextCheckpoint == wt.LAST_CONST):
                print ("You are a hero")
                break
            nextNextCheckpointX = wt.getNodeX(nextNextCheckpoint, data)
            nextNextCheckpointY = wt.getNodeY(nextNextCheckpoint, data)
            currToNextNextDist = wt.distanceBetweenTwoCoordinates(currPoint['x'], currPoint['y'], nextNextCheckpointX, nextNextCheckpointY)
            nextToNextNextDist = wt.distanceBetweenTwoCoordinates(nextCheckpointX, nextCheckpointY, nextNextCheckpointX, nextNextCheckpointY)
            print ("currToNextNextDist : " + str(currToNextNextDist))
            print ("nextToNextNextDist : " + str(nextToNextNextDist))
            #if(currToNextNextDist < nextToNextNextDist):
                #netDistanceInDir = 0
            approachingCheck = False
            currPoint = {'x' : nextCheckpointX, 'y' : nextCheckpointY}
            currNodeCrossed = nextCheckpoint #currNode becomes the nextnode
            print ("New currNode : " + str(currNodeCrossed))
