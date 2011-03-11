from __future__ import generators
import copy
import gridDef
import IPython
monsterType = gridDef.monsterType
coinType = gridDef.coinType
XType = gridDef.XType
YType = gridDef.YType

def getObjLoc(observation):
    res = []
    for y in range(0, self.height):
        for x in range(0, self.width):
            key = (x, y)
            if(observation[key] == 2):
                res.append( (2, x, y))
            elif (observation[key] == 3):
                res.append( (3, x, y))
    return res
def pow2(key):
    return key[0]*key[0] + key[1]*key[1]
def getNearObj(observation, type):
    marioLoc, objLoc = observation
    objDist = []
    for obj in objLoc:
        if obj[0] == type:
            key = (obj[1] - marioLoc[0], obj[2] - marioLoc[1])
            objDist.append((pow2(key), key[0], key[1]))
    objDist.sort(key=lambda obj: obj[0])   

    res = []
    for obj in objDist:
        res.append(obj[1])
        res.append(obj[2]) 
    return tuple(res)

def getObjFeature(ob):
    marioLoc, monLoc, coinLoc = ob

    feaList = []
    #add mario Loc into it
    #feaList.append((1, XType, marioLoc[0]))
    #feaList.append((1, YType, marioLoc[1]))

    #separate it into individual faetures
    i = 0
    for loc in monLoc:
        if i % 2 == 0:
            fea = (monsterType, XType, loc)
        else:
            fea = (monsterType, YType, loc)
        i = i + 1
        feaList.append(fea)
    i = 0
    for loc in coinLoc:
        if i % 2 == 0:
            fea = (coinType, XType, loc)
        else:
            fea = (coinType, YType, loc)
        i = i + 1
        feaList.append(fea)
    return feaList

def getSarsaFeature(observation):
    marioLoc, objLoc = observation
    coinLoc = getNearObj(observation, coinType)
    monLoc = getNearObj(observation, monsterType)
    return getRelFeature((marioLoc, monLoc, coinLoc))
    
class RestPre:
    def __init__(self):
        self.order = -1
    def getFeature(self, observation):
        coinLoc = getNearObj(observation, coinType)
        monLoc = getNearObj(observation, monsterType)
        return (monLoc, coinLoc)

def xuniqueCombinations(items, n):

    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xuniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc
def getFeature(observation, order, type):
    goal, marioLoc, objLoc = observation
    coinList = []
    for obj in objLoc:
        if obj[0] == type:
            coinList.append((obj[1] - marioLoc[0], obj[2] - marioLoc[1]))
    coinList = sorted(coinList, key=lambda obj: obj[1]) 
    coinList = sorted(coinList, key=lambda obj: -(obj[0]*obj[0]+obj[1]*obj[1])) 
    
    feaList = []
    for i in xuniqueCombinations(coinList, order):
       feaList.append(i) 
    #if feaList == [[]]:
        #feaList = []  #a little ugly here, it comes when order is 0 or coinList is empty

    res = []
    while feaList != []:
        last = feaList.pop()
        last.reverse()
        listOfLoc = []
        for loc in last:
            listOfLoc.append(loc[0])
            listOfLoc.append(loc[1])
        res.append(tuple(listOfLoc))
    return res

def GetRelFeature( observation, monsterOrder, coinOrder):
    goal, marioLoc, objLoc = observation
    coinFea = getFeature(observation, coinOrder, coinType)
    monFea = getFeature(observation, monsterOrder, monsterType)
    res = []
    for coin in coinFea:
        for monster in monFea:
            res.append(getObjFeature((marioLoc, monster, coin)))
    if res == [[]]:
        res = []  #a little ugly here, it happens when monFea is empty or coinFea is empty
    return res


class CoinAndMonsterPre:
    def __init__(self, monsterOrder, coinOrder):
        self.coinOrder = coinOrder
        self.monsterOrder = monsterOrder

    def getFeature(self, observation):
        marioLoc, objLoc = observation
        coinFea = getFeature(observation, self.coinOrder, coinType)
        monFea = getFeature(observation, self.monsterOrder, monsterType)
        res = []
        for coin in coinFea:
            for monster in monFea:
                res.append(getRelFeature((marioLoc, monster, coin)))
        return res


if __name__ == "__main__":
    coinPre = CoinPre(1)
    marioLoc = (0,0)
    objList = [(3, 0, -1), (3, 0, 1), (2, 0, 3), (3, 0, 2)]
    ob = (marioLoc, objList)
    #print coinPre.getFeature()
    CMPre = CoinAndMonsterPre(0, 0)
    print CMPre.getFeature(ob)
    #pre = RestPre()
    #marioLoc = (0,0)
    #objList = [(2, 1,1), (3, 5, 1), (2, -1, 0), (3, 1, 2)]
    #print pre.getFeature((marioLoc, objList))

