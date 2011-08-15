import random
import copy

#!!!observation format: (1, 0, 1, hp, (1, 1, 1), (x, y))
class RMax:
    def __init__(self, epsilon, gamma, hordQ, probQ, punishment):
        self.punishment = punishment #the punishment is Integer[0, inf)
        self.epsilon = epsilon
        self.gamma = gamma
        self.hordq = hordQ
        self.oriProbQ = probQ
        self.probQ = {}
        self.adjState = {}
        self.adjRoom = [
                [1, 2],
                [0, 3],
                [0, 3, 4],
                [1, 2, 5],
                [2, 5],
                [3, 4]
                ]
        self.Qmodel = {}
        self.stepNum = 0
        
    def touchAll(self, observation):
        actionList = self.getActionList(self.getPlanVar(observation))
        for action in actionList:
            self.touch(observation, action)

    def touch(self, observation, action):
        ob = self.getPlanVar(observation)
        key = (ob, action)
        envVar = self.getEnvVar(observation)
        if not envVar in self.Qmodel:
            self.Qmodel[envVar] = {}
            self.probQ[envVar] = copy.deepcopy(self.oriProbQ)
        if not key in self.Qmodel[envVar]:
            self.Qmodel[envVar][key] = 0 #assign 0 as the initial value

    def getPlanVar(self, ob):
        assert(len(ob) == 6)
        return (ob[0], ob[1], ob[2], ob[5])
    def getEnvVar(self, ob):
        assert(len(ob) == 6)
        return (ob[3], ob[4])
    def mergeVar(self, planVar, envVar):
        return (planVar[0], planVar[1], planVar[2], envVar[0], envVar[1], planVar[3])

    def getLoc(self, ob):
        assert(len(ob)==4) #observation format: (1, 1, 1, (x, y))
        return ob[3] 
    #observation in reduced format
    def getRoom(self, ob):
        loc = self.getLoc(ob)
        y = int(loc[1]/2)
        x = int(loc[0]/3)
        id = 2*y + x
        return id
         

    #observation in reduced format
    def getActionList(self, observation):
        room = self.getRoom(observation)
        actionList = self.adjRoom[room]
        return actionList
        
    def selectAction(self, observation):
        actionList = self.getActionList(self.getPlanVar(observation))

        #use epsilon-greedy
        if random.random() < self.epsilon:
            #select randomly
            action = actionList[int(random.random()*len(actionList))]
            self.touch(observation, action)
            return action
        else:
            #select the best action
            v = []
            for action in actionList:
                self.touch(observation, action)
                v.append(self.getQ(observation, action))
            assert len(v) > 0
            m = max(v)
            select = int(random.random()*v.count(m))

            i = 0
            maxCount = 0
            for value in v:
                if value == m:
                    if maxCount == select:
                        action = actionList[i]
                        break
                    maxCount = maxCount + 1
                i = i + 1
            return action

    def start(self, observation):
        self.lastObservation = observation
        curRoom = self.getRoom(self.getPlanVar(observation))
        self.lastAction = nextRoom = self.selectAction(observation)
        action = self.hordq.start(((curRoom, nextRoom), observation))
        self.lastPrimitiveAction = action #debug only
        return action

    def getQ(self, inOb, action):
        ob = self.getPlanVar(inOb)
        envVar = self.getEnvVar(inOb)
        key = (ob, action)
        return self.Qmodel[envVar][key]

    def getV(self, ob):
        actionList = self.getActionList(self.getPlanVar(ob))
        maxQ = self.getQ(ob, actionList[0])
        for action in actionList:
            Q = self.getQ(ob, action)
            if Q > maxQ:
                maxQ = Q
        return maxQ

    def dumpProb():
        #status = [0, 0, 0]

        print "1->2:", self.probQ.getQ(((0, 0, 0, (1, 1)), (0, 0, 0, (1, 2))), 2)
            
    def updateProbModel(self, inOb, inLastOb, lastAction):
        self.touch(inLastOb, lastAction)

        #use the old value to update
        envVar = self.getEnvVar(inLastOb)
        lastOb = self.getPlanVar(inLastOb)
        ob = self.getPlanVar(inOb)

        #check if the environment variable exists or not
        if not envVar in self.Qmodel:
            self.Qmodel[envVar] = {}
            self.probQ[envVar] = copy.deepcopy(self.oriProbQ)

        #update probability model
        probKey = (lastOb, ob)
        self.probQ[envVar].touch(probKey, lastAction)
        self.probQ[envVar].updateQ(probKey, lastAction, 1, 0) #gamma for probQ is not useful here

        #add ob to lastOb's adjacency list
        if not lastOb in self.adjState:
            self.adjState[lastOb] = [ob]
        else:
            if not ob in self.adjState[lastOb]:
                self.adjState[lastOb].append(ob)

        for state in self.adjState[lastOb]:
            if state != ob:
                tmpProbKey = (lastOb, state)
                self.probQ[envVar].touch(tmpProbKey, lastAction)
                self.probQ[envVar].updateQ(tmpProbKey, lastAction, 0, 0) #gamma for probQ is not useful here

    def updateQModel(self, inOb):
        self.touchAll(inOb)
        #use the old value to update
        envVar = self.getEnvVar(inOb)
        

        #use the new value to update
        #update Q value        
        for i in range(0, 3):
            for state in self.adjState:
                actionList = self.getActionList(state)
                room = self.getRoom(state)
                fullState = self.mergeVar(state, envVar)
                for action in actionList:
                    actionR = (room, action) 
                    self.hordq.touchAll((actionR, fullState))
                    r = self.hordq.getVc((actionR, fullState))
                    c = 0
                    for adj in self.adjState[state]:
                        tmpKey = (state, adj)
                        self.probQ[envVar].touch(tmpKey, action)

                        prob = self.probQ[envVar].getQ(tmpKey, action)
                        
                        fullAdjState = self.mergeVar(adj, envVar)
                        self.touchAll(fullAdjState)
                        v = self.getV(fullAdjState)
                        c = c + prob*v

                    #the Bellman's equation
                    self.Qmodel[envVar][(state, action)] = self.gamma*c + r


    #observation is original format
    def step(self, reward, observation):
        lastRoom = self.getRoom(self.getPlanVar(self.lastObservation))
        curRoom = self.getRoom(self.getPlanVar(observation))

        #check for termination of subtask
        if lastRoom == curRoom:
            #continue execute last action
            primitiveAction = self.hordq.step(reward, ((curRoom, self.lastAction), observation), reward)
        else:
            #update model
            if self.epsilon != 1:
                self.updateProbModel(observation, self.lastObservation, self.lastAction)
                self.updateQModel(observation)

            #choose the next action
            action = self.selectAction(observation)

            #room changed
            if curRoom == self.lastAction:
               #achieve the subgoal 
               internalReward = reward + self.punishment
               #internalReward = reward 
            else:
               internalReward = reward
               #mission failed. punish the agent
               #internalReward = reward - self.punishment

            #debugging
            #curLoc = self.getLoc(self.getPlanVar(observation))
            #prevLoc = self.getLoc(self.getPlanVar(self.lastObservation))
            #print "lastOb:", self.lastObservation
            #print "ob:", observation
            #print "move: ",prevLoc, "->", curLoc, " ", self.lastPrimitiveAction, " reward ", internalReward
            #print "move: ",lastRoom, "->", curRoom, " ", self.lastAction, " next action:", action, " reward ", internalReward

            primitiveAction = self.hordq.step(reward, ((curRoom, action), observation), internalReward)

            self.lastObservation = observation
            self.lastAction = action
        self.lastPrimitiveAction = primitiveAction #debug only
        self.stepNum = self.stepNum + 1
        #if self.stepNum % 100000 == 0:
        self.punishment = self.punishment - 5.0/100000.0
        #if self.punishment < 0:
            #self.punishment = 0
         
        return primitiveAction

    def end(self, reward):
        #assume bus ends at (0, 0) 
        #update prob model
        inLastOb = self.lastObservation
        lastAction = self.lastAction
        lastOb = self.getPlanVar(inLastOb)
        envVar = self.getEnvVar(inLastOb)
        if lastOb in self.adjState:
            for state in self.adjState[lastOb]:
                tmpProbKey = (lastOb, state)
                self.probQ[envVar].touch(tmpProbKey, lastAction)
                self.probQ[envVar].updateQ(tmpProbKey, lastAction, 0, 0) #gamma for probQ is not useful here
        self.hordq.end(reward, reward)

#add comparison to random planner
import EmptySARSA
import HORDQ
import SARSA
if __name__ == "__main__":

    alpha = 0.2
    epsilon = 0.1
    gamma = 0.9
    #ob = (-1, -1, -1, (1, 2))
    #ob2 = (-1, -1, -1, (5, 4))
    #ob3 = (-1, -1, -1, (0, 0))
    ob4 = (-1, -1, -1, (1, 1))
    punishment = 10
    isRORDQ = False
    hordQ = HORDQ.HORDQ(alpha, epsilon, gamma, [1, -1], isRORDQ)
    probQ = SARSA.SARSA(alpha, epsilon, gamma, [1, -1])
    controller = RMax(epsilon, gamma, hordQ, probQ, punishment)

    #unit test for get room
    val = controller.getRoom(ob4)
    print "value: ", val
    assert( val == 0)
    #controller.start(ob)
    #for i in range(0, 1000):
        #
        #controller.step(1, ob)
        #controller.step(1, ob)
        #controller.step(1, ob)
        #controller.step(1, ob2)
    #controller.end(10)

    #print controller.Q
    #print hordQ.Qc
    #print probQ.Q
