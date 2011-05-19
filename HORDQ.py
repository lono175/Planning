import random

class HORDQ:
    def __init__(self, alpha, epsilon, gamma, actionList):
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.actionList = actionList
        self.Qc = {}
        self.Qe = {}
        self.pQc = {}

    def touch(self, observation, action):
        key = (observation, action)
        if not key in self.Qc:
            self.Qc[key] = 0 #assign 0 as the initial value
        if not key in self.Qe:
            self.Qe[key] = 0 #assign 0 as the initial value
        if not key in self.pQc:
            self.pQc[key] = 0 #assign 0 as the initial value

    #def getQc(self, ob, action):
        #key = (ob, action)
        #if not key in self.Qc:
            #return 0 #optimistic exploration?
        #return self.Qc[key] 
    def getVc(self, ob):
        maxV = self.Qc[(ob, self.actionList[0])]
        for action in self.actionList:
            key = (ob, action)
            if self.Qc[key] > maxV:
                maxV = self.Qc[key]
        return maxV

    def getpQ(self, key):
        return self.pQc[key] + self.Qe[key]

    def touchAll(self, observation):
        for action in self.actionList:
            self.touch(observation, action)

    def selectAction(self, observation):
        self.touchAll(observation)
        #use epsilon-greedy
        if random.random() < self.epsilon:
            #select randomly
            action = self.actionList[int(random.random()*len(self.actionList))]
            return action
        else:
            #select the best action
            v = []
            for action in self.actionList:
                v.append(self.getpQ((observation, action)))
            assert len(v) > 0
            m = max(v)
            #print "v: ", v
            #print "a:", self.actionList
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

    def update(self, lastObservation, lastAction, reward, observation, action, internalReward):
        #you need to update Qc and Qe individually
        oldTask, oldState = lastObservation
        newTask, newState = observation
        newQe = self.Qe[(observation, action)]
        newQc = self.Qc[(observation, action)]
        newpQc = self.pQc[(observation, action)]
        newQ = newQe + newQc

        key = (lastObservation, lastAction)
        if oldTask != newTask:
            #the taks has finished
            #print "newpQc", newpQc
            #print "newQe", newQe
            newQe = newQ
            newpQc = 0
            newQc = 0
            #print "Qe", self.Qe[key], " delta", self.gamma * newQe

        self.pQc[key] = (1 - self.alpha)*self.pQc[key] + self.alpha*(internalReward + self.gamma * newpQc)
        self.Qc[key] = (1 - self.alpha)*self.Qc[key] + self.alpha*(reward + self.gamma * newQc)
        self.Qe[key] = (1 - self.alpha)*self.Qe[key] + self.alpha*(self.gamma * newQe)
        
        #print "newpQc", newpQc
        #print "newQe", newQe
        #print "pQc", self.pQc[key], " delta",internalReward + self.gamma * newpQc 
        #print "Qe", self.Qe[key], " delta", self.gamma * newQe

    def updateQ(self, lastObservation, lastAction, reward, internalReward):
        newQe = 0
        newQc = 0
        newpQc = 0
        key = (lastObservation, lastAction)
        self.pQc[key] = (1 - self.alpha)*self.pQc[key] + self.alpha*(internalReward + self.gamma * newpQc)
        self.Qc[key] = (1 - self.alpha)*self.Qc[key] + self.alpha*(reward + self.gamma * newQc)
        self.Qe[key] = (1 - self.alpha)*self.Qe[key] + self.alpha*(self.gamma * newQe)

    def start(self, observation):
        self.lastObservation = observation
        self.lastAction = self.selectAction(observation)
        return self.lastAction

    def step(self, reward, observation, internalReward):
        isUpdate = True
        newAction = self.selectAction(observation)
        if isUpdate:
            self.update(self.lastObservation, self.lastAction, reward, observation, newAction, internalReward)
        self.lastObservation = observation
        self.lastAction = newAction
        return newAction
    def end(self, reward, internalReward):
        isUpdate = True
        if isUpdate:
            self.updateQ(self.lastObservation, self.lastAction, reward, internalReward)

if __name__ == "__main__":
    
    ob = ((1, 1), 0)
    controller = HORDQ(0.5, 0.1, 0.8, (-1, 1))
    print controller.start(ob)
    print controller.step(-1, ob, -1)
    print controller.step(-1, ob, -1)
    print controller.step(-1, ob, -1)
    print controller.step(-1, ob, -1)
    print controller.step(-1, ob, -1)
    print controller.end(1, -1)
    print controller.Qe
    print controller.Qc
    print controller.pQc
    #import pickle
    #output = open('data.pkl', 'wb')
    #pickle.dump(controller, output)
    #output.close()
    #input = open('data.pkl', 'rb')
    #ctrl2 = pickle.load(input)
    #print "after load"
    #pickle.loads(xp)
    #y
    
