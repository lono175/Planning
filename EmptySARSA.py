import random

class EmptySARSA:
    def __init__(self, actionList ):
        self.actionList = actionList
    def getQ(self, lastObservation, lastAction):
        return 0
    def start(self, observation):
        self.lastObservation = observation
        return self.actionList[0]
        #for action in actionList:
        #for each action a
        #if highest valued action valueFunction(observation,a)
        #then store a as lastAction
        #return self.lastAction
    def step(self, reward, observation, internalReward):
        return self.actionList[0]
    def end(self, reward, internalReward):
        pass
    
