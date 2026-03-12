import math

def distance(thumb, index):
    x1,y1 = thumb
    x2,y2 = index
    length = math.hypot(x2-x1,y2-y1)
    return length

def fingers_pos(lmList):
    tipIDs = [4,8,12,16,20]
    fingers = []
    if lmList[tipIDs[0]][1] > lmList[tipIDs[0]-1][1]:
        fingers.append(1)
    else:
        fingers.append(0)
    for id in range(1,5):
        if lmList[tipIDs[id]][2] < lmList[tipIDs[id]-2][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers