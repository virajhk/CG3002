import pygame
pygame.mixer.init()

STEP_LENGTH = 45 #we can change this later
NAV_THRESHOLD = 70 # we can change this later
LAST_CONST = "last"
import djikstra as dj
import utils
from math import sqrt
import math
import json
dontGoStraight = 0
# For acceleration, if the x value changes by more than 0.3 g, a step has been taken
with open("xyz.json") as data_file:
    dummydata = json.load(data_file)
# dummy array values
accelerationX = [1.9, 2.1] * 85
#magnetometerValues = [150, 54, 78, 67, 98, 56, 90, 100, 315, 340, 12, 315, 90, 90]
magnetometerValues2 = [180, 104, 100] + [135, 132, 139] * 120
for i in range(25):
    magnetometerValues2.append(225)

# return acceleration values
# obtained at regular intervals, possibly every second, timer can be in main.py
# rupali
def addAccToArray(accArray, accX=None):
    if accX is not None:
        return accArray.append(accX)
    else:
        return accArray

# return the magnetic north angle, one angle returned in degrees
# rupali
def addMagToArray(magArray, mag=None):
    if mag is not None:
        return magArray.append(mag)
    else:
        return magArray

# obtained from map json and used as an offset
# rupali
def getMapNorthAt(data):
    northAtValue = data["info"]["northAt"]
    return int(northAtValue)

offestTest = 360 - getMapNorthAt(dummydata)

def getNodeX(node, data):
    mapVar = data['map']
    table_location = utils.build_location_table(mapVar)
    return table_location[str(node)][0]

def getNodeY(node, data):
    mapVar = data['map']
    table_location = utils.build_location_table(mapVar)
    return table_location[str(node)][1]

def calculateAngleBetweenTwoPoints(firstX, firstY, secondX, secondY):
    if (secondY == firstY): 
        if (secondX > firstX): return 90
        else: return 270
    if (secondX == firstX):
        if(secondY < firstY): return 180
        else: return 0
    if(secondX > firstX and secondY < firstY):
        radianVal = (math.atan((secondX - firstX)/(secondY - firstY)))
        print ("radian Val 1")
        print (radianVal)
        print (90 + abs(180.0 * radianVal)/3.1412)
        return 90 + abs(180.0 * radianVal)/3.1412
    if(secondX > firstX and secondY > firstY):
        radianVal = (math.atan((secondX - firstX)/(secondY - firstY)))
        print ("radian Val 2")
        print (radianVal)
        print (abs(180.0 * radianVal)/3.1412)
        return abs(180.0 * radianVal)/3.1412
    if(secondX < firstX and secondY < firstY):
        radianVal = (math.atan((secondX - firstX)/(secondY - firstY)))
        print ("radian Val 3")
        print (radianVal)
        print (180 + (180.0 * radianVal)/3.1412)
        return 180 + abs(180.0 * radianVal)/3.1412
    if(secondX < firstX and secondY > firstY):
        radianVal = (math.atan((secondX - firstX)/(secondY - firstY)))
        print ("radian Val 4")
        print (radianVal)
        print (270 + abs(180.0 * radianVal)/3.1412)
        return 270 + abs(180.0 * radianVal)/3.1412

#current mag angle that the user is in
#intended mag angle that the user needs to be in
def provideDeviationAngleInfo(IntendedMagAngle, currentMagAngle):
    dontGoStraight = 0
    angleDiff = IntendedMagAngle - currentMagAngle
    if(angleDiff >= 0):
        if(angleDiff >= 170 and angleDiff <= 190):
            dontGoStraight = 1
            print ("Make a UTurn")
            pygame.mixer.music.load("Uturn.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
        elif(angleDiff > 180 and abs(360 - angleDiff) >= 45):
            if(abs(360 - angleDiff) >= 45 and abs(360 - angleDiff) <= 60):
                dontGoStraight = 1
                print("Turn left by 45 degree")
                pygame.mixer.music.load("Left45.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(360 - angleDiff)> 60 and abs(360 - angleDiff) <= 120):
                dontGoStraight = 1
                print("Turn left by 90 degree")
                pygame.mixer.music.load("Left90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(360 - angleDiff) > 120 and abs(360 - angleDiff) <= 165):
                dontGoStraight = 1
                print("Turn left by 45 and then left by 90")
                pygame.mixer.music.load("Left45left90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(360 - angleDiff) > 165 and abs(360 - angleDiff) < 180):
                dontGoStraight = 1
                print("Take a U-Turn")
                pygame.mixer.music.load("Uturn.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
        elif(angleDiff < 180 and angleDiff >= 45):
            if(angleDiff >= 45 and angleDiff <= 60):
                dontGoStraight = 1
                print("Turn right by 45 degree")
                pygame.mixer.music.load("Right45.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff > 60 and angleDiff <= 120):
                dontGoStraight = 1
                print("Turn right by 90 degree")
                pygame.mixer.music.load("Right90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff > 120 and angleDiff <= 165):
                dontGoStraight = 1
                print("Turn right by 45 and then right by 90")
                pygame.mixer.music.load("Right45right90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff > 165 and angleDiff < 180):
                dontGoStraight = 1
                print("Take a U-Turn")
                pygame.mixer.music.load("Uturn.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
    else:
        if(angleDiff <= -170 and angleDiff >= -190):
            dontGoStraight = 1
            print ("Make UTurn")
            pygame.mixer.music.load("Uturn.wav")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
        elif(angleDiff > -180 and abs(angleDiff) >= 45):
            if(abs(angleDiff) >= 45 and abs(angleDiff) <= 60):
                dontGoStraight = 1
                print("Turn left by 45 degree")
                pygame.mixer.music.load("Left45.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(angleDiff) > 60 and abs(angleDiff) <= 120):
                dontGoStraight = 1
                print("Turn left by 90 degree")
                pygame.mixer.music.load("Left90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(angleDiff) > 120 and abs(angleDiff) <= 165):
                dontGoStraight = 1
                print("Turn left by 45 and then left by 90")
                pygame.mixer.music.load("Left45left90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(abs(angleDiff) > 165 and abs(angleDiff) < 180):
                dontGoStraight = 1
                print("Take a U-Turn")
                pygame.mixer.music.load("Uturn.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
        elif(angleDiff < -180 and 360-abs(angleDiff) >= 45):
             if((360-abs(angleDiff)) >= 45 and (360-abs(angleDiff)) <= 60):
                dontGoStraight = 1
                print("Turn right by 45 degree")
                pygame.mixer.music.load("Right45.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
             elif((360-abs(angleDiff)) > 60 and (360-abs(angleDiff)) <= 120):
                dontGoStraight = 1
                print("Turn right by 90 degree")
                pygame.mixer.music.load("Right90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
             elif((360-abs(angleDiff)) > 120 and (360-abs(angleDiff)) <= 165):
                dontGoStraight = 1
                print("Turn right by 45 and then right by 90")
                pygame.mixer.music.load("Right45right90.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
             elif((360-abs(angleDiff)) > 165 and (360-abs(angleDiff)) < 180):
                dontGoStraight = 1
                print("Take a U-Turn")
                pygame.mixer.music.load("Uturn.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue

    temp = dontGoStraight
    dontGoStraight = 0
    return temp

# calculate distannce from curr point to next checkpoint
# rupali
def distanceBetweenTwoCoordinates(currX, currY, nextX, nextY):
    distance = sqrt((int(nextY) - int(currY))**2 + (int(nextX) - int(currX))**2)
    return distance

def findCurrentPoint(currX, currY, nextMag, stepTaken, offset, xChange, yChange, intendedMag):
    mapAngle = nextMag - offset
    if(mapAngle < 0):
        mapAngle += 360
    if(stepTaken == True):
        if(mapAngle >= 0 and mapAngle <= 90):
            mapAngle  = mapAngle * 3.1412/180.0
            if (xChange == 1 and yChange == 0):
                return {'x' : currX + STEP_LENGTH, 'y' : currY}
            elif (yChange == 1 and xChange == 0):
                return {'x' : currX, 'y' : currY + STEP_LENGTH}
            else:
                return {'x' : currX + STEP_LENGTH * math.sin(intendedMag), 'y' : currY + STEP_LENGTH * math.cos(intendedMag)}
        elif(mapAngle > 90 and mapAngle <= 180):
            tempAngle = mapAngle - 90
            tempAngle  = tempAngle * 3.1412/180.0
            if (xChange == 1 and yChange == 0):
                return {'x' : currX + STEP_LENGTH, 'y' : currY}
            elif (yChange == 1 and xChange == 0):
                return {'x': currX, 'y': currY - STEP_LENGTH}
            else:
                return {'x': currX + STEP_LENGTH * math.cos(intendedMag), 'y': currY - STEP_LENGTH * abs(math.sin(intendedMag))}
        elif(mapAngle > 180 and mapAngle <= 270):
            tempAngle = mapAngle - 180
            tempAngle  = tempAngle * 3.1412/180.0
            if (xChange == 1 and yChange == 0):
                return {'x' : currX - STEP_LENGTH, 'y' : currY}
            elif (yChange == 1 and xChange == 0):
                return {'x': currX, 'y': currY - STEP_LENGTH}
            else:
                return {'x': currX - STEP_LENGTH * math.sin(intendedMag), 'y' : currY - STEP_LENGTH * math.cos(intendedMag)}
        elif(mapAngle > 270 and mapAngle <=360):
            tempAngle = mapAngle - 270
            tempAngle  = tempAngle * 3.1412/180.0
            if (xChange == 1 and yChange == 0):
                return {'x' : currX - STEP_LENGTH, 'y' : currY}
            elif (yChange == 1 and xChange == 0):
                return {'x': currX, 'y': currY + STEP_LENGTH}
            else:
                return {'x' : currX - STEP_LENGTH * math.cos(intendedMag), 'y' : currY + STEP_LENGTH * math.sin(intendedMag)}
    else:
        return {'x' : currX, 'y': currY}

def netDistanceInIntendedDirection(IntendedMagAngle, currMagAngle, currDistance, stepTaken):
    angleDiff = currMagAngle - IntendedMagAngle
    angleDiff = angleDiff * 3.1412/180.0
    if(stepTaken == True):
        return currDistance + STEP_LENGTH * math.cos(angleDiff)
    else:
        return currDistance

def getNextCheckpoint(DjikstraArray, Checkpoint):
    if Checkpoint in DjikstraArray:
        currentIndex = DjikstraArray.index(Checkpoint)
        if(currentIndex + 1 >= len(DjikstraArray)):
            print("This is the last index")
            return LAST_CONST
        else:
            return DjikstraArray[currentIndex + 1]
    else:
        print("Next checkpoint is the first point")
        return DjikstraArray[0]

def getIntendedMagAngle(node1, node2, offset, data):
    node1X = getNodeX(node1, data)
    node1Y = getNodeY(node1, data)
    node2X = getNodeX(node2, data)
    node2Y = getNodeY(node2, data)
    intendedMagAngle = offset + calculateAngleBetweenTwoPoints(node1X, node1Y, node2X, node2Y)
    if(intendedMagAngle >= 360):
        return intendedMagAngle - 360
    else:
        return intendedMagAngle

#returns true or false if the destination is about to be reached
def aboutToReach(locationX, locationY, nextNodeX, nextNodeY):
    return abs(distanceBetweenTwoCoordinates(locationX, locationY, nextNodeX, nextNodeY)) <= NAV_THRESHOLD


    # get x and y of the upcoming checkpoint, dictionary to be used
# include the name of the checkpoint in the dictionary too.
# tell user to turn left, right or go straight. also blurt out
# which checkpoint
def provideNavInstruction(DjikstraArray, prevNode, nextNode, locationX, locationY, data, offset): #manmeet
    nextNextNode = getNextCheckpoint(DjikstraArray, nextNode)
    if(nextNextNode == LAST_CONST):  #if nextNode is the last node
        print ("You are a hero")
        pygame.mixer.music.load("JourneyCompleted.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
        return ("You are a hero")
    print (nextNextNode)
    magAngleNextToNextNext = getIntendedMagAngle(nextNode, nextNextNode, offset, data) #mag angle from next to next node
    magAnglePrevToNext = getIntendedMagAngle(prevNode, nextNode, offset, data) #mag angle from curr node crossed to next node
    #print "magAngleNextToNextNext"
    #print magAngleNextToNextNext
    #print "magAnglePrevToNext "
    #print magAnglePrevToNext
    # if(magAngleNextToNextNext < magAnglePrevToNext): #need to add this otherwise this test fails: provideNavInstruction([6,11,12,13,14,15,16],14,15,3800,2700,dummydata,55)
    #     print "Turn Left"
    #     return None
    #angleDiff = getIntendedMagAngle(nextNode, nextNextNode) - getIntendedMagAngle(prevNode, nextNode)
    angleDiff = magAngleNextToNextNext - magAnglePrevToNext
    # print "magAngleNextToNextNext"
    # print magAngleNextToNextNext
    # print "magAnglePrevToNext "
    # print magAnglePrevToNext
    print ("angleDiff")
    print (angleDiff)
    nextNodeX = getNodeX(nextNode, data)
    nextNodeY = getNodeY(nextNode, data)

    if(aboutToReach(locationX, locationY, nextNodeX, nextNodeY)):
        print ("checkpoint reached")
        pygame.mixer.music.load("Checkpointreached.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
        if (abs(angleDiff) < 180):
            if(angleDiff > 0):
                print ("Turn right")
                pygame.mixer.music.load("Right.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff < 0):
                print ("Turn left")
                pygame.mixer.music.load("Left.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff == 0):
                print ("Go straight")
                pygame.mixer.music.load("straight.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
        else:
            if(angleDiff < 0):
                print ("Turn right")
                pygame.mixer.music.load("Right.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff > 0):
                print ("Turn left")
                pygame.mixer.music.load("Left.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
            elif(angleDiff == 0):
                print ("Go straight")
                pygame.mixer.music.load("straight.wav")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy() == True:
                    continue
        return True
    else:
        print ("Not within 150cm of your next checkpoint")
        return False

def findNearestNode(DjikstraArray, locationX, locationY, data):
    min = distanceBetweenTwoCoordinates(getNodeX(DjikstraArray[0], data), getNodeY(DjikstraArray[0], data), locationX, locationY)
    minIndex = 0
    for index, m in enumerate(DjikstraArray):
        distance = distanceBetweenTwoCoordinates(getNodeX(m, data), getNodeY(m, data), locationX, locationY)
        if(distance <= min):
            min = distance
            minIndex = index
    return DjikstraArray[minIndex]

def provideNavigationWrtNode(nodePrev, nodeNext, currentMag,offestTest, dummydata, locationX,locationY):
    intendedMagAngle = getIntendedMagAngle(nodePrev,nodeNext,offestTest,dummydata)
    distance = distanceBetweenTwoCoordinates(getNodeX(nodeNext,dummydata),getNodeY(nodeNext,dummydata),locationX,locationY)
    print (distance)
    print ("intendedMagAngle = " + str(intendedMagAngle))
    provideDeviationAngleInfo(intendedMagAngle,currentMag)
#testing purpose
#provideNavigationWrtNode(5,3,310,180,dummydata,500,400)
#provideNavigationWrtNode(5,3,0,180,dummydata,600,400)
#provideNavigationWrtNode(5,3,50,180,dummydata)
#provideNavigationWrtNode(5,3,90,180,dummydata)
#provideNavigationWrtNode(5,3,270,180,dummydata)
#print findNearestNode([5,3,1],1,2,dummydata)
# print addAccToArray(accelerationX,3)
#print accelerationX
#print addMagToArray(magnetometerValues,90)
#print magnetometerValues
# print getMapNorthAt(data)
#print distanceBetweenTwoCoordinates(2131,2780, 2152, 2436)
# print offset
#print getIntendedMagAngle(4,5,0,data)
# print calculateAngleBetweenTwoPoints(0, 5, 1, 5.5777)
#print (provideDeviationAngleInfo(180, 110))
#print (provideDeviationAngleInfo(90,40))
#print (provideDeviationAngleInfo(90,270))
# print (provideDeviationAngleInfo(270,20)) # left by 90
#print (provideDeviationAngleInfo(270,0))  #left by 90
#print (provideDeviationAngleInfo(270,310))  #left by 45
# print (provideDeviationAngleInfo(270,280)) #st
#print (provideDeviationAngleInfo(270,45)) # left by 45 n left by 90
#print (provideDeviationAngleInfo(270,75)) # u turn
# print (provideDeviationAngleInfo(270,95)) #u turn
#print (provideDeviationAngleInfo(270,119)) # u turn
# print (provideDeviationAngleInfo(270,123)) # right by 45 n right by 90
# print (provideDeviationAngleInfo(270,145)) # right by 45 n right by 90
# print (provideDeviationAngleInfo(270,175)) # right by 90
# print (provideDeviationAngleInfo(270,225)) #  right by 45
# print (provideDeviationAngleInfo(270,245)) #  st
# print (provideDeviationAngleInfo(270,270)) #  st
# print (provideDeviationAngleInfo(270,275)) #  st
#print (provideDeviationAngleInfo(270,301)) #  left by 45
# print (provideDeviationAngleInfo(270,355)) #  left by 90
# print (provideDeviationAngleInfo(270,360)) #  left by 45
#print (provideDeviationAngleInfo(90,20)) # right by 90
# print (provideDeviationAngleInfo(90,0))  # right by 90
#print (provideDeviationAngleInfo(90,310))  # right by 45 and right by 90
# print (provideDeviationAngleInfo(90,280)) # uturn
#print (provideDeviationAngleInfo(90,45)) # right by 45
# print (provideDeviationAngleInfo(90,75)) # st
# print (provideDeviationAngleInfo(90,95)) # st
# print (provideDeviationAngleInfo(90,119)) # st
#print (provideDeviationAngleInfo(90,123)) # left 45
#print (provideDeviationAngleInfo(90,145)) # left 45
# print (provideDeviationAngleInfo(90,175)) # left 90
# print (provideDeviationAngleInfo(90,225)) #  left by 45 n left 90
# print (provideDeviationAngleInfo(90,245)) # uteun
# print (provideDeviationAngleInfo(90,270)) # uturn
# print (provideDeviationAngleInfo(90,275)) # uturn
# print (provideDeviationAngleInfo(90,355)) # right 90
# print (provideDeviationAngleInfo(90,360)) # right 90
#print getNextCheckpoint([1, 2, 3], 3)
#print findCurrentPoint(400, 300, 225, True, 180)  #x=330,y=430
#print findCurrentPoint(400, 300, 10, True, 180) #x=393, y=260
#print getNodeX(2, dummydata)
#print getNodeY(2, dummydata)
#provideNavInstruction([1,2,3],1,2,4,2436,dummydata,45)  #havent reached
#provideNavInstruction([1,2,3],1,2,2150,2436,dummydata,45) #right
#provideNavInstruction([1,2,4,7,10],2,4,2153,2436,dummydata,45) #havent reached
#provideNavInstruction([1,2,4,7,10],2,4,2873,2436,dummydata,45) #st
#provideNavInstruction([1,2,4,7,10],4,7,3628,2436,dummydata,45) #right
#provideNavInstruction([1,2,4,6],1,2,2150,2436,dummydata,45) #st
#provideNavInstruction([1,2,4,6],2,4,2873,2436,dummydata,45) #left
#provideNavInstruction([1,2,4,6],4,6,2883,2914,dummydata,45) #st last
#provideNavInstruction([18,22,34,26,29,31],18,22,9744,731,dummydata,45) #st
#provideNavInstruction([18,22,34,26,29,31],22,34,10270,731,dummydata,45) #right
#provideNavInstruction([34,26,28,30],34,26,10278,700,dummydata,45) #not within range
#provideNavInstruction([34,26,28,30],34,26,11000,690,dummydata,45) #left
#provideNavInstruction([34,26,28,30],26,28,11003,1200,dummydata,45) #right
#-----2nd level com 2--------
#provideNavInstruction([1,17,18],1,17,1100,2900,dummydata,55)  #right
#provideNavInstruction([6,11,12,13,14,15,16],11,12,3700,1800,dummydata,55) #right
#provideNavInstruction([6,11,12,13,14,15,16],12,13,4100,2010,dummydata,55) #left
#provideNavInstruction([6,11,12,13,14,15,16],13,14,4300,2300,dummydata,55)  #left
#provideNavInstruction([6,11,12,13,14,15,16],14,15,3800,2700,dummydata,55) #left
#provideNavInstruction([6,11,12,13,14,15,16],15,16,3700,2600,dummydata,55) #straight
#------xyz----------
# provideNavInstruction([5,3],5,3,500,300,dummydata,180) #st
# provideNavInstruction([5,3,2],5,3,500,300,dummydata,180) #left
# provideNavInstruction([5,2,3],5,2,500,400,dummydata,180) #
