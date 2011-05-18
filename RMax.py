import random

# observation format: (1, 0, 1, (x, y))
class RMax:
    def __init__(self, epsilon, gamma, hordQ, probQ):
        self.punishment = 10 #the punishment is Integer[0, inf)
        self.epsilon = epsilon
        self.gamma = gamma
        self.hordq = hordQ
        self.probQ = probQ
        self.adjState = {}
        self.adjRoom = [
                [1, 2],
                [0, 3],
                [0, 3, 4],
                [1, 2, 5],
                [2, 5],
                [3, 4]
                ]
        self.Q = {}
        
    def touchAll(self, observation):
        actionList = self.getActionList(observation)
        for action in actionList:
            self.touch(observation, action)
    def getLoc(self, ob):
        return ob[3] #!!!Assume observation format: (1, 0, 1, (x, y))
    def getRoom(self, ob):
        loc = self.getLoc(ob)
        y = loc[1]/2
        id = int(pow(2, y - 1))
        x = loc[0]/3
        id = id + x
        return id
         
    def touch(self, observation, action):
        key = (observation, action)
        if not key in self.Q:
            self.Q[key] = 0 #assign 0 as the initial value

    def getActionList(self, observation):
        room = self.getRoom(observation)
        actionList = self.adjRoom[room]
        return actionList
        
    def selectAction(self, observation):
        actionList = self.getActionList(observation)

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
        curRoom = self.getRoom(observation)
        self.lastAction = nextRoom = self.selectAction(observation)
        action = self.hordq.start(((curRoom, nextRoom), observation))
        return action

    def getQ(self, lastObservation, lastAction):
        key = (lastObservation, lastAction)
        return self.Q[key]
    def getV(self, ob):
        actionList = self.getActionList(ob)
        maxQ = self.getQ(ob, actionList[0])
        for action in actionList:
            Q = self.getQ(ob, action)
            if Q > maxQ:
                maxQ = Q
        return maxQ

            
    def updateModel(self, ob, lastOb, lastAction):
        #update probability model
        probKey = (ob, lastOb)
        self.probQ.touch(probKey, lastAction)
        self.probQ.updateQ(probKey, lastAction, 1, 0) #gamma for probQ is not useful here

        #add ob to lastOb's adjacency list
        if not lastOb in self.adjState:
            self.adjState[lastOb] = [ob]
        else:
            if not ob in self.adjState[lastOb]:
                self.adjState[lastOb].append(ob)

        for state in self.adjState[lastOb]:
            if state != ob:
                self.probQ.touch((state, lastOb), lastAction)
                self.probQ.updateQ((state, lastOb), lastAction, 0, 0) #gamma for probQ is not useful here

        #update Q value        
        for i in range(0, 2):
            for state in self.adjState:
                actionList = self.getActionList(state)
                room = self.getRoom(state)
                for action in actionList:
                    actionR = (room, action) 
                    r = self.hordq.getQc(state, actionR)
                    c = 0
                    for adj in self.adjState[state]:
                        self.probQ.touch((adj, state), actionR)
                        prob = self.probQ.getQ((adj, state), actionR)
                        self.touchAll(adj)
                        v = self.getV(adj)
                        c = c + prob*v
                    #the Bellman's equation
                    self.Q[(state, action)] = c + r

    def step(self, reward, observation):
        lastRoom = self.getRoom(self.lastObservation)
        curRoom = self.getRoom(observation)

        #check for termination of subtask
        if lastRoom == curRoom:
            #continue execute last action
            primitiveAction = self.hordq.step(reward, (self.lastAction, observation), reward)
        else:
            #update model
            self.updateModel(observation, self.lastObservation, self.lastAction)

            #choose the next action
            action = self.selectAction(observation)

            #room changed
            if curRoom == self.lastAction:
               #achieve the subgoal 
               internalReward = reward
            else:
               #mission failed. punish the agent
               internalReward = reward - self.punishment

            primitiveAction = self.hordq.step(reward, (action, observation), internalReward)

            self.lastObservation = observation
            self.lastAction = action
        return primitiveAction

    def end(self, reward):
        #assume bus ends at (0, 0) 
        self.hordq.end(reward, reward)

import EmptySARSA
import HORDQ
import SARSA
if __name__ == "__main__":

    alpha = 0.2
    epsilon = 0.1
    gamma = 0.99
    ob = (-1, -1, -1, (1, 2))
    ob2 = (-1, -1, -1, (5, 4))
    ob3 = (-1, -1, -1, (0, 0))
    hordQ = HORDQ.HORDQ(alpha, epsilon, gamma, [1, -1])
    probQ = SARSA.SARSA(alpha, epsilon, gamma, [1, -1])
    controller = RMax(epsilon, gamma, hordQ, probQ)
    controller.start(ob)
    for i in range(0, 10):
        
        controller.step(10, ob)
        controller.step(10, ob)
        #controller.step(10, ob3)
        controller.step(10, ob)
        controller.step(10, ob2)
    controller.end(10)

    print controller.Q
    #print probQ.Q