import random
import gridDef
monsterType = gridDef.monsterType
coinType = gridDef.coinType
XType = gridDef.XType
YType = gridDef.YType

class ProbSARSA:
    def __init__(self, actionList, initialCount, dumpCount ):
        self.actionList = actionList
        self.initialPosCount = initialCount #can be 1 or 0
        self.minimalCount = 5.0
        self.posCount = {}
        self.totalCount = {}
        self.dumpCount = dumpCount
        self.episodeNum = 0
    def touchAll(self, observation):
        for action in self.actionList:
            self.touch(observation, action)

    def touch(self, observation, action):
        for fea in observation:
            key = (fea, action)
            if not key in self.posCount:
                self.posCount[key] = self.initialPosCount
                self.totalCount[key] = 1.0

    def getFeaProb(self, key):
        if self.totalCount[key] > self.minimalCount:
            #print "pos: ", self.posCount[key]
            #print "total: ", self.totalCount[key]
            return self.posCount[key]/self.totalCount[key]
        else:
            return self.initialPosCount / 1.0
    def getProb(self, ob, action):
        self.touch(ob, action)
        prob = 1.0
        for fea in ob:
            feaProb = self.getFeaProb((fea, action))
            #print "feaProb: ", feaProb
            prob = min(prob, feaProb)
        return prob

    def updateProb(self, lastObservation, lastAction, isSuccess):
        self.touch(lastObservation, lastAction)
        numOfFeature = len(lastObservation)
        assert (numOfFeature >= 1)

        if isSuccess:
            delta = 1.0
        else:
            delta = 0.0
        deltaForPos = delta/numOfFeature
        deltaForTotal = 1.0/numOfFeature

        #print "delta: ", deltaPerFeature
        for fea in lastObservation:
            key = (fea, lastAction)
            self.posCount[key] = self.posCount[key] + deltaForPos
            self.totalCount[key] = self.totalCount[key] + deltaForTotal
            #print "update1: ", self.posCount[key] 
            #print "update2: ", self.totalCount[key] 
            #print "delta: ", deltaForTotal
        
    def dump(self):
        for varType in range(1,3):
            for varVal in range (-2, 3):
                ob = (3, varType, varVal)
                for action in self.actionList:
                    key = (ob, action)
                    self.touch([ob], action)
                    print key, " ", self.Q[key]

