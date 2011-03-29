import random
#import RLSARSA
import LinearSARSA
import gridDef
#import IPython #for debug
monsterType = gridDef.monsterType
coinType = gridDef.coinType
XType = gridDef.XType
YType = gridDef.YType
goalType = gridDef.goalType

#all, mario position, monster, coin,  coin+monster
#predict Q from lower order
#use the difference between the predicted and real one to update higher order relations
#conf: (2, 1) 2 monster, 1 coin
#conf: (0, 0) mario location
class RelationalQ:
    def __init__(self, alpha, epsilon, gamma, actionList):
        self.actionList = actionList
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.initialQ = 0
        self.dumpCount = 0 #dump is done by relationalQ
        self.isUpdate = True
        self.agent = {}
        self.addAgent(0)
        self.prob = LinearSARSA.LinearSARSA(self.alpha, self.epsilon, self.gamma, self.actionList, 0, self.dumpCount )
        self.realReward = LinearSARSA.LinearSARSA(self.alpha, self.epsilon, self.gamma, self.actionList, 0, self.dumpCount )

    def addAgent(self, conf):
        key = conf
        if not key in self.agent:
            self.agent[key] = LinearSARSA.LinearSARSA(self.alpha, self.epsilon, self.gamma, self.actionList, self.initialQ, self.dumpCount )

    def getLinkCost(self, observation, agent):
        key = self.getCurConf( observation)
        fea = Predicate.GetRelFeature(observation, key[0], key[1])
        cost = {}
        for action in self.actionList:
            assert(len(fea) == 1)
            cost[action] = agent.getQ(fea[0], action)

        maxCost = -100000 #TODO: tempoaray solution
        for v in cost:
            if cost[v] > maxCost:
               maxCost = cost[v]
        return maxCost


    def getMaxQ(self, observation):
        Q = self.getAllQ(observation)
        assert len(Q) > 0
        #print observation
        #print Q
        maxQ = -1000 #TODO: tempoaray solution
        for v in Q:
            if Q[v] > maxQ:
               maxQ = Q[v]
        return maxQ
        
    def getAllQ(self, observation):
        Q = {}
        for action in self.actionList:
            Q[action] = self.getQ(observation, action)
        return Q

    def getQ(self, observation, action):
        #marioLoc, objLoc = observation
        Q = 0

        key = self.getCurConf( observation)
        fea = Predicate.GetRelFeature(observation, key[0], key[1])
        assert(len(fea) == 1)
        Q = self.agent[0].getQ(fea[0], action)
        #for key in self.agent:
            #feaList = 
            #for fea in feaList:
                #Q = Q + self.agent[key].getQ(fea, action)
        return Q
    def getProb(self, observation, action):
        marioLoc, objLoc = observation
        key = self.getCurConf( observation)
        fea = Predicate.GetRelFeature(observation, key[0], key[1])
        assert(len(fea) == 1)
        return self.prob.getQ(fea[0], action)
        
    def getReward(self, observation, action):
        marioLoc, objLoc = observation
        key = self.getCurConf( observation)
        fea = Predicate.GetRelFeature(observation, key[0], key[1])
        assert(len(fea) == 1)
        return self.realReward.getQ(fea[0], action)

    def updateReward(self, observation, action, deltaQ):
        marioLoc, objLoc = observation
        #find current conf
        curConf = self.getCurConf(observation)
        relFea = Predicate.GetRelFeature(observation, curConf[0], curConf[1])
        assert (len(relFea) == 1) #there shall only one of it
        #self.addAgent(curConf)
        self.realReward.updateQ(relFea[0], action, deltaQ)

    def updateProb(self, observation, action, deltaQ):
        marioLoc, objLoc = observation
        #find current conf
        curConf = self.getCurConf(observation)
        relFea = Predicate.GetRelFeature(observation, curConf[0], curConf[1])
        assert (len(relFea) <= 1) #there shall only one of it
        self.prob.updateQ(relFea[0], action, deltaQ)

    def getCurConf(self, observation):
        marioLoc, objLoc = observation
        monNum = 0
        coinNum = 0
        for obj in objLoc:
            if obj[0] == coinType:
                coinNum = coinNum + 1
            elif obj[0] == monsterType:
                monNum = monNum + 1
        return (monNum, coinNum)     

    def selectAction(self, observation):
        Q = self.getAllQ(observation)

        #use epsilon-greedy
        if random.random() < self.epsilon:
            #select randomly
            action = self.actionList[int(random.random()*len(self.actionList))]
            return action
        else:
            #select the best action
            v = []
            for action in self.actionList:
                v.append(Q[action])
            assert len(v) > 0
            m = max(v)
            select = int(random.random()*v.count(m))

            i = 0
            maxCount = 0
            for value in v:
                if value == m:
                    if maxCount == select:
                        action = self.actionList[i]
                        break
                    maxCount = maxCount + 1
                i = i + 1
            return action

    def disableUpdate(self):
        self.isUpdate = False

    def start(self, observation):
        #print "-start-"
        #print "obj loc: ", self.getObjLoc(observation)
        self.lastObservation = observation
        self.lastAction = self.selectAction(observation)
        self.lastQ = self.getQ(observation, self.lastAction)
        return self.lastAction

    def getDeltaQ(self, lastQ, reward, newQVal):
        return (reward + self.gamma * newQVal - lastQ)

    def updateQ(self, observation, action, deltaQ):
        marioLoc, objLoc = observation
        #find current conf
        curConf = self.getCurConf(observation)
        relFea = Predicate.GetRelFeature(observation, curConf[0], curConf[1])
        assert (len(relFea) <= 1) #there shall only one of it
        if len(relFea) == 1:
            #self.addAgent(curConf)
            self.agent[0].updateQ(relFea[0], action, deltaQ)

    def step(self, reward, observation, realReward, isSuccess):
        newAction = self.selectAction(observation)
        
        newQ = self.getQ(observation, newAction)
        if self.isUpdate == True:
            deltaQ = self.getDeltaQ(self.lastQ, reward, newQ)
            self.updateQ( self.lastObservation, self.lastAction, deltaQ)

            #update probabilistic model
            oldProb = self.getProb(self.lastObservation, self.lastAction)
            if isSuccess:
               deltaProb = 0 - oldProb
            else:
               deltaProb = -10 - oldProb
            self.updateProb(self.lastObservation, self.lastAction, deltaProb)
            #update reward model
            oldRealReward = self.getReward(self.lastObservation, self.lastAction)
            deltaReward = realReward + oldRealReward
            self.updateReward(self.lastObservation, self.lastAction, deltaReward)


        self.lastObservation = observation
        self.lastAction = newAction
        self.lastQ = newQ
        return newAction

    def end(self, reward, realReward, isSuccess):
        if self.isUpdate == True:
            deltaQ = self.getDeltaQ(self.lastQ, reward, 0)
            self.updateQ( self.lastObservation, self.lastAction, deltaQ)

            #update probabilistic model
            oldProb = self.getProb(self.lastObservation, self.lastAction)
            if isSuccess:
               deltaProb = 0 - oldProb
            else:
               deltaProb = -10 - oldProb
            self.updateProb(self.lastObservation, self.lastAction, deltaProb)
            #update reward model
            oldRealReward = self.getReward(self.lastObservation, self.lastAction)
            deltaReward = realReward + oldRealReward
            self.updateReward(self.lastObservation, self.lastAction, deltaReward)

    def dumpObj(self):
        for conf in self.agent:
            print "Config:", conf
            for type in range(3, 5):
                    for X in range(-1, 2):
                        for Y in range(-1, 2):
                            keyX = (type, XType, X)
                            keyY = (type, YType, Y)
                            for action in self.actionList:
                                Q = self.agent[conf].getQ([keyX, keyY], action)
                                if Q != 0:
                                    print (type, X, Y), action, ": ", Q
        
    def dumpCoinAndGoalEx(self, agent):
        for cX in range(-1, 2):
            for cY in range(-1, 2):
                for gX in range(-1, 2):
                    for gY in range(-1, 2):
                        keyX = (coinType, (cX, cY), (gX, gY))
                        for action in self.actionList:
                            Q = agent.getQ([keyX], action)
                            if Q != 0:
                                print (keyX), action, ": ", Q
    def dumpCoinAndGoal(self):
        for conf in [0]:
            print "Config:", conf
            for cX in range(-1, 2):
                for cY in range(-1, 2):
                    for gX in range(-1, 2):
                        for gY in range(-1, 2):
                            keyX = (coinType, (cX, cY), (gX, gY))
                            for action in self.actionList:
                                Q = self.agent[conf].getQ([keyX], action)
                                if Q != 0:
                                    print (keyX), action, ": ", Q
        #for conf in [0]:
            #print "Config:", conf
            #for cX in range(-1, 2):
                #for cY in range(-1, 2):
                    #for gX in range(-1, 2):
                        #for gY in range(-1, 2):
                            #keyX = (coinType, XType, cX)
                            #keyY = (coinType, YType, cY)
                            #goalX = (goalType, XType, gX)
                            #goalY= (goalType, YType, gY)
                            #for action in self.actionList:
                                #Q = self.agent[conf].getQ([keyX, keyY, goalX, goalY], action)
                                #if Q != 0:
                                    #print (gX, gY, cX, cY), action, ": ", Q
        

    def dump(self):
        for conf in self.agent:
            print "Config:", conf
            for type in range(2, 4):
                for varType in range(1, 3):
                    for value in range(-2, 3):
                        key = (type, varType, value)
                        for action in self.actionList:
                            Q = self.agent[conf].getQ([key], action)
                            if Q != 0:
                                print key, action, ": ", Q

#def getMarioLoc(observation, size):
    #height, width = size
    #for y in range(0, height):
        #for x in range(0, width):
            #key = (y, x)
            #if(observation[key] == 1):
                #return key
    #return (-1, -1)

#def getObjLoc(observation, size):
    #res = []
    #height, width = size
    #for y in range(0, height):
        #for x in range(0, width):
            #key = (y, x)
            #if(observation[key] == 2):
                #res.append( (2, y, x))
            #elif (observation[key] == 3):
                #res.append( (3, y, x))
    #return res

import Predicate
if __name__ == "__main__":

    goalList = [(1, 0), (0, 1)]
    preList = [(0, 1), (1, 0), (1,1)]
    size = (5, 1)
    controller = RelationalQ(0.2, 0, 0.5, (-1, 1))
    trainingStage = 3
    world = {}
    world[(0, 0)] = 1
    world[(1, 0)] = 0
    world[(2, 0)] = 2
    world[(3, 0)] = 0
    world[(4, 0)] = 3

    objLoc = getObjLoc(world, size)
    marioLoc = getMarioLoc(world, size)
    goal = (0, 1)
    ob = (goal, marioLoc, objLoc)
    print controller.start(ob, (1, 1))

    #print "all"
    #print controller.agent[0].Q
    #print "world"
    #print controller.agent[1].Q
    #print "turtle"
    #print controller.agent[2].Q
    #print "coin"
    #print controller.agent[3].Q
    for i in range(0, 10):

        objLoc = getObjLoc(world, size)
        marioLoc = getMarioLoc(world, size)
        ob = (goal, marioLoc, objLoc)
        print controller.step(1, ob)
        #print controller.start(world)
        #print "all"
        #print controller.agent[0].Q
        #print "world"
        #print controller.agent[1].Q
        #print "turtle"
        #print controller.agent[2].Q
        #print "coin"
        #print controller.agent[3].Q

    #print controller.end(1, trainingStage)

    #print "world"
    #print controller.agent[1].Q

    #print "turtle"
    #print controller.agent[2].Q

    #print "coin"
    #print controller.agent[3].Q

    #import pickle
    #output = open('data.pkl', 'wb')
    #pickle.dump(controller, output)
    #output.close()
    #input = open('data.pkl', 'rb')
    #ctrl2 = pickle.load(input)
    #print "after load"
    #print ctrl2.Q
    #pickle.loads(xp)
    #y


