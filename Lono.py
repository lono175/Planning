import random
import SARSA
class FactoredQ:
    def __init__(self, alpha, epsilon, gamma, actionList, size ):
        self.size = self.width, self.height = size
        self.actionList = actionList
        self.epsilon = epsilon
        self.agent = [ SARSA.SARSA(alpha, epsilon, gamma, actionList), #all
                SARSA.SARSA(alpha, epsilon, gamma, actionList), #world
                SARSA.SARSA(alpha, epsilon, gamma, actionList), #turtle
                SARSA.SARSA(alpha, epsilon, gamma, actionList), #coin
                ]

    def updateAllQ(self, objectLoc):
        #print "objLoc: ", objectLoc
        for y in range(0, self.height):
            for x in range(0, self.width):
                key = (x, y)
                for obj in objectLoc:
                    type, objX, objY = obj
                    diff = (x-objX, y-objY)

                    #touch the location
                    for action in self.actionList:
                        self.agent[type].touch(diff, action)
                        self.agent[0].touch(key, action)
                        self.agent[1].touch(key, action)
                        #print "type: ", type
                        #print "diff: ", diff
                        self.agent[0].Q[(key, action)] = self.agent[1].Q[(key, action)] + self.agent[type].Q[(diff, action)]
    def getMarioLoc(self, observation):
        for y in range(0, self.height):
            for x in range(0, self.width):
                key = (x, y)
                if(observation[key] == 1):
                    return key
        return (-1, -1)
         
    def getObjLoc(self, observation):
        res = []
        for y in range(0, self.height):
            for x in range(0, self.width):
                key = (x, y)
                if(observation[key] == 2):
                    res.append( (2, x, y))
                elif (observation[key] == 3):
                    res.append( (3, x, y))
        return res
         
    def selectAction(self, observation):
        objLoc = self.getObjLoc(observation)
        self.updateAllQ(objLoc)
        marioLoc = self.getMarioLoc(observation)

        #use epsilon-greedy
        if random.random() < self.epsilon:
            #select randomly
            action = self.actionList[int(random.random()*len(self.actionList))]
            return action
        else:
            #select the best action
            v = []
            for action in self.actionList:
                v.append(self.agent[0].Q[(marioLoc, action)])
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

    def start(self, observation):
        #print "-start-"
        #print "obj loc: ", self.getObjLoc(observation)
        self.lastObservation = observation
        self.lastMarioLoc = self.getMarioLoc(observation)
        self.lastAction = self.selectAction(observation)
        return self.lastAction
        #for action in actionList:
        #for each action a
        #if highest valued action valueFunction(observation,a)
        #then store a as lastAction
        #return self.lastAction
    def step(self, reward, observation):
        objLoc = self.getObjLoc(self.lastObservation)
        newAction = self.selectAction(observation)
        marioLoc = self.getMarioLoc(observation)
        self.agent[1].lastObservation = self.lastMarioLoc
        self.agent[1].lastAction = self.lastAction
        self.agent[1].step(reward, marioLoc, newAction) 
        #if reward == 100000:
            #print "mario last loc: ", self.lastMarioLoc
            #print "mario loc: ", marioLoc
            #print "last obj loc: ", objLoc
            #print "obj loc: ", self.getObjLoc(observation)
        for obj in objLoc:
            type, objX, objY = obj
            diff = (marioLoc[0]-objX, marioLoc[1]-objY)
            diffOld = (self.lastMarioLoc[0] - objX, self.lastMarioLoc[1] - objY)
            self.agent[type].lastObservation = diffOld
            self.agent[type].lastAction = self.lastAction
            self.agent[type].step(reward, diff, newAction)
        self.lastMarioLoc = marioLoc
        self.lastAction = newAction
        self.lastObservation = observation
        return newAction
    def end(self, reward):
        self.agent[1].lastObservation = self.lastMarioLoc
        self.agent[1].lastAction = self.lastAction
        self.agent[1].end(reward) 
        objLoc = self.getObjLoc(self.lastObservation)
        for obj in objLoc:
            type, objX, objY = obj
            diffOld = (self.lastMarioLoc[0] - objX, self.lastMarioLoc[1] - objY)
            self.agent[type].lastObservation = diffOld
            self.agent[type].lastAction = self.lastAction
            self.agent[type].end(reward)
    
if __name__ == "__main__":
    
    controller = FactoredQ(0.5, 0, 0.8, (-1, 1), (5, 1))
    world = {}
    world[(0, 0)] = 1
    world[(1, 0)] = 0
    world[(2, 0)] = 2
    world[(3, 0)] = 3
    world[(4, 0)] = 3
    print controller.start(world)
    print "all"
    print controller.agent[0].Q
    print "world"
    print controller.agent[1].Q
    print "turtle"
    print controller.agent[2].Q
    print "coin"
    print controller.agent[3].Q
    for i in range(0, 20):
        
        print controller.step(1, world)
        #print controller.start(world)
        #print "all"
        #print controller.agent[0].Q
        #print "world"
        #print controller.agent[1].Q
        #print "turtle"
        #print controller.agent[2].Q
        print "coin"
        print controller.agent[3].Q

    print controller.end(-100)
    print "coin"
    print controller.agent[3].Q
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
    
