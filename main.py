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
# new buttons
startStaircase_var = 0
endStaircase_var = 0
onePressed = 0 #extra variable to track the continuation of stairs
confirmationFlag = 0
systemReset = 0
#new buttons end
#end

#Staircase stuff
def shouldStartStaircase(node, startStaircase_var):
    if "2#2#16" in node:
        if startStaircase_var == 1:
            return 1
        else:
            return 0

def shouldEndStaircase(endStaircase_var, onePressed):
    if onePressed == 1:
        if endStaircase_var == 1:
            return 1
        else:
            return 0

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

#returns shortest path array given data['map'], initial node and final node from the same map.
def getShortestPath(mapVar, initialNode, finalNode):
    return dj.shortestPath(mapVar,initialNode,finalNode)

mainUrl = "http://showmyway.comp.nus.edu.sg/getMapInfo.php"
inputMap1 = {'building' : "1", "level" : str(2)}
#inputMap2 = {'building' : "1", "level" : str(3)}
inputMap3 = {'building' : "2", "level" : str(2)}
inputMap4 = {'building' : "2", "level" : str(3)}

params1 = dict(
    Building= "COM" + inputMap1['building'],
    Level= inputMap1['level']
)

#params2 = dict(
#    Building= "COM" + inputMap2['building'],
#    Level= inputMap2['level']
#)

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
        os.system('espeak -ven+f3 "{0}"'.format("Initial Node " + start))
        os.system('espeak -ven+f3 "{0}"'.format("Final Node " + end))
        #textToSpeech("Initial Node " + start)
        #textToSpeech("Final Node " + end)
        print ("Start:" + str(start))
        print ("End:" + str(end))
        confirm = 1
        while confirm:
            confirmKey = ser.readline()
            temp = confirmKey.split(',')[0]
            temp = int(temp.split('.')[0])
            if (confirmKey != ''):
                if (temp == 9):
                    print "entered here"
                    keypad = 0
                    confirm = 0
                    break
            if (confirmKey != ''):
                if (temp != 9):
                    confirm = 0
#end

initialNode = start #input("Enter Initial Node: ")
finalNode = end #input("Enter final Node: ")
#textToSpeech("Initial Node " + initialNode)
#textToSpeech("Final Node " + finalNode)

confirm = 0

dataArray = []
data = {}
data1 = {}
data2 = {}
finalData = {}

#Multiple maps code start
with open("{0}Level{1}.json".format("COM" + inputMap1['building'], inputMap1['level'])) as data_file:
    dataArray.append({("COM" + inputMap1['building'] + "#" + inputMap1['level']) : utils.mapifyNodeIDs(json.load(data_file), inputMap1['building'], inputMap1['level'])})

with open("{0}Level{1}.json".format("COM" + inputMap3['building'], inputMap3['level'])) as data_file3:
    dataArray.append({("COM" + inputMap3['building'] + "#" + inputMap3['level']) : utils.mapifyNodeIDs(json.load(data_file3), inputMap3['building'], inputMap3['level'])})

with open("{0}Level{1}.json".format("COM" + inputMap4['building'], inputMap4['level'])) as data_file4:
    dataArray.append({("COM" + inputMap4['building'] + "#" + inputMap4['level']) : utils.mapifyNodeIDs(json.load(data_file4), inputMap4['building'], inputMap4['level'])})

stitched_map = utils.stitchMaps(utils.getValueFromArrayOfDicts('COM1#2', dataArray)['map'], utils.getValueFromArrayOfDicts('COM2#2', dataArray)['map'], utils.getValueFromArrayOfDicts('COM2#3', dataArray)['map'])
data['map'] = utils.getValueFromArrayOfDicts('COM1#2', dataArray)['map']
data1['map'] = utils.getValueFromArrayOfDicts('COM2#2', dataArray)['map']
data2['map'] = utils.getValueFromArrayOfDicts('COM2#3', dataArray)['map']

for d in data1['map']:
    data['map'].append(d)

for d in data2['map']:
    data['map'].append(d)

data['COM1#2NorthAt'] = "315"
data['COM2#2NorthAt'] = "305"
data['COM2#3NorthAt'] = "305"
print data['map']
    
#Multiple maps code end

#result = dj.parse(data)
def PrintPathDictionary(path, Map):
    pathDictionary = {}
    for p in path:
        for m in Map:
            if p == m['nodeId']:
                print(str(p) + " : " + str(m['nodeName']))

path = []

path.append({(utils.getCOMBuildingFromNode(initialNode) + "#" + utils.getLevelFromNode(initialNode)) : getShortestPath(stitched_map, initialNode, finalNode)})

#Path was redefined to make it an array of integers rather than array of dictionaries for the first demo.
path = list(path[0].values())[0]

#main algorithm
#offset = 360 - wt.getMapNorthAt(data)
givenMagValue = 131;
magQueue = deque([], maxlen=4)
magQueue.append(givenMagValue)
#data initially is the initialNode map's data
# IMPORTANT: data needs to get updated everywhere in the while(true) if the node is from a new map.
# dataArray contains all the maps. just load the relevant map from the array on reaching a node in the next map.
accArray = []
magArray = []
wt.magnetometerValues2 = [givenMagValue] + wt.magnetometerValues2 #adding the first mag value to the beginning of the array
accVal = 0
magVal = 1
#Curr node initially is the first node in the shortest path array.
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
        if (len(array) >= 6):
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
            tempArr = array[3].split(',')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    startStaircase_var = int(tempArr[0])
            tempArr = array[4].split(',')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    endStaircase_var = int(tempArr[0])
            tempArr = array[5].split(',')
            if (len(tempArr) >= 2):
                if (isIntOrFloat(tempArr[0])):
                    systemReset = int(tempArr[0])
            #print ("Alti:" + str(alti))
            #print ("Direction:" + str(heading))
            #print ("Steps:" + str(steps))
    #end
    if(systemReset == 1):
        onePressed = 0
        currNodeCrossed = path[0]
        currPoint = {'x' : wt.getNodeX(currNodeCrossed,data), 'y': wt.getNodeX(currNodeCrossed,data)}
        wt.addAccToArray(accArray, 0)
        wt.addAccToArray(accArray, 0)
    
    magQueue.append(heading)
    currNodeCrossedX = wt.getNodeX(currNodeCrossed,data)
    currNodeCrossedY = wt.getNodeY(currNodeCrossed,data)
    stepTaken = False
    #Get next checkpoint with respect to currNodeCrossed
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
    offset = 360 - wt.getMapNorthAt(data, currNodeCrossed)
    intendedMag = wt.getIntendedMagAngle(currNodeCrossed, nextCheckpoint, offset, data)
    #print "intendedMag" + str(intendedMag)
    #time.sleep(0.5)
    if(accVal < len(wt.accelerationX)):
        if(shouldEndStaircase(endStaircase_var,onePressed) == 1):
            onePressed = 0
            currNodeCrossed = "2#3#11"
            currPoint = {'x' : wt.getNodeX(currNodeCrossed,data), 'y': wt.getNodeX(currNodeCrossed,data)}

        if shouldStartStaircase(currNodeCrossed, startStaircase_var) == 1:
            onePressed = 1

        if onePressed == 0:
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
        currPoint = wt.findCurrentPoint(currPoint['x'], currPoint['y'], magArray[-1], stepTaken, offset, xChange, yChange, intendedMag, nextCheckpointX, nextCheckpointY)
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
                if (end - start >= 1 and stepTaken == True):
                    pygame.mixer.music.load("Move.wav")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy() == True:
                        continue
                    start = end
        if(wt.aboutToReach(currPoint['x'], currPoint['y'], nextCheckpointX, nextCheckpointY, currNodeCrossed, nextCheckpoint)):
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
