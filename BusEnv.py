import random
import sys,pygame
import gridDef

#import IPython
monsterType = gridDef.monsterType #monster is the wall here
coinType = gridDef.coinType
marioType = gridDef.marioType
XType = gridDef.XType
YType = gridDef.YType

school = (1, 1)
stop = [(1, 4), (4, 2), (4, 4)]
roadLoc = [(3, 1), (3, 2), (3, 4)]

        
class BusEnv:
    def __init__(self, size, imgSize, actionList):
        self.size = self.width, self.height = size
        self.imgSize = imgSize
        self.actionList = actionList
        self.wall = [
                (0, 1, 0, 2),
                (0, 3, 0, 4),

                (2, 0, 3, 0),
                (2, 1, 2, 2),
                (3, 1, 3, 2),
                (2, 3, 3, 3),
                (2, 3, 2, 4),
                (3, 3, 3, 4),
                (2, 5, 3, 5),

                (5, 1, 5, 2),
                (5, 3, 5, 4)
                ]
        self.randomList = {}
        self.randomList[(0, 1)] = [(1, 0), (-1, 0)]
        self.randomList[(0, -1)] = [(1, 0), (-1, 0)]
        self.randomList[(1, 0)] = [(0, 1), (0, -1)]
        self.randomList[(-1, 0)] = [(0, 1), (0, -1)]
        #Mario is 1
        #turtle is 2
        #coin is 3
        #goal is 4
        #empty tile is 0
        self.world = {}
        self.chanceToDie = 0.25

    def start(self, numOfTurtle, numOfCoin):
        self.stepNum = 0
        locList = []

        for y in range(0, self.width):
            for x in range(0, self.height):
                self.world[(x, y)] = 0

        #add turtle
        #for i in range(0, numOfTurtle):
           #self.world[self.getNewLoc(locList)] = 2

        #add coin (make sure there are at least one coin)
        for pas in stop:
           self.world[pas] = coinType

        #add mario
        self.world[school] = marioType
        #print self.getNewLoc(locList)
        #self.objective = (subgoal[0] + marioLoc[0], subgoal[1] + marioLoc[1])
        self.mario = pygame.image.load("mario.bmp")
        self.coin = pygame.image.load("coin.bmp")
        self.turtle = pygame.image.load("turtle.bmp")
        self.screen = pygame.Surface(self.imgSize)

        self.health = 1

        self.changeRoadStatus()
        #self.road = (1, 0, 1) #1 means the road is good, 0 means it is under construction
        #print "road status: ", self.road
        return self.world

    def changeRoadStatus(self):
        rand = random.random()
        if  rand < 0.33:
            self.road = (1, 1, 1) #1 means the road is good, 0 means it is under construction
        elif rand < 0.66:
            self.road = (1, 1, 0) #1 means the road is good, 0 means it is under construction
        else:
            self.road = (1, 0, 1) #1 means the road is good, 0 means it is under construction

    def step(self, action):
        self.stepNum = self.stepNum + 1
        realReward  = self.updateState(action)
        flag = self.isTerminal(realReward) #the order with updateState is important here
        return realReward, flag

    def getSarsaFeature(self):

        marioLoc = self.getMarioLoc()

        #check if the passenger is there or not
        pasInfo = []
        for pas in stop:
            if self.world[pas] != coinType:
                pasInfo.append(0)
            else:
                pasInfo.append(1)

        pasInfo.append(self.health)
        pasInfo.append(self.road)
        pasInfo.append(marioLoc)
        res = tuple(pasInfo)
        return res
    def find(self, type):
        res = []
        for y in range(0, self.width):
            for x in range(0, self.height):
                if self.world[(x, y)] == type:
                    res.append((x, y))
        return res
    def getNewLoc(self, locList):
        #WARNING! this function may not stop
        while True:
            locX = min(int(random.random()*self.width), self.width -1);
            locY = min(int(random.random()*self.height), self.height -1);
            loc = (locX, locY)
            if locList.count(loc) == 0:
               locList.append(loc)
               return loc

    def dump(self):
        for y in range(0, self.width):
            for x in range(0, self.height):
                print self.world[(x, y)]," ",
            print ""


    def count(self, type):
        counter = 0
        for y in range(0, self.width):
            for x in range(0, self.height):
                if self.world[(x, y)] == type:
                    counter += 1
        return counter
        
    def getMarioLoc(self):
        marioLocList = self.find(marioType) 
        if marioLocList !=  []:
            marioLoc = marioLocList[0]
        else:
            assert 0
        return marioLoc
    def isTerminal(self, reward):
        marioNewLoc = self.getMarioLoc()
        coinNum = self.count(coinType)
        if coinNum == 0 and marioNewLoc == school:
            return True
        if reward < -2:
            return True
        #if reward >= 10:
            #return True #return to the school
        #coinNum = self.count(coinType)
        #if coinNum == 0 and marioLoc == school
            #return True


        #if self.stepNum > 2000:
            #return True
        #print "reward", reward
        return False

    def isBlockedByWall(self, loc1, loc2):
        move1 = (loc1[0], loc1[1], loc2[0], loc2[1])
        move2 = (loc2[0], loc2[1], loc1[0], loc1[1])
        if (move1 in self.wall) or (move2 in self.wall):
            return True 
        return False
    def updateState(self, action):
        agentAction = action
        RandomAction = 0.1
        realReward = -1
        marioOldLoc = self.getMarioLoc()
        self.world[marioOldLoc] = 0

        #move Mario
        rand = random.random()
        if  rand < RandomAction:
            #select randomly
            if not action in self.randomList:
                assert(False)
            if rand < RandomAction/2:
                action = self.randomList[action][0]
            else:
                action = self.randomList[action][1]
            #print "random action!!!"
        marioNewLoc = (marioOldLoc[0]+action[0], marioOldLoc[1]+action[1])

        #check Mario stays in the boundary
        if not marioNewLoc in self.world:
            marioNewLoc = marioOldLoc

        #check Mario is blocked by the monster
        if self.world[marioNewLoc] == monsterType:
            marioNewLoc = marioOldLoc

        if self.isBlockedByWall(marioNewLoc, marioOldLoc):
            marioNewLoc = marioOldLoc

        #do the health check
        if self.health == 0:
            if random.random() < self.chanceToDie:
                realReward = realReward - 50 
        for i in range(0, len(self.road)):
            cond = self.road[i]
            if cond == 0 and marioNewLoc == roadLoc[i]:
                #the road is bad, so mario are in trouble
                self.health = 0
        self.world[marioNewLoc] = 1

        if random.random() < 0.05:
            #change road status
            #print "change status!!!"
            self.changeRoadStatus()

        
        coinNum = self.count(coinType)
        if coinNum == 0 and marioNewLoc == school:
            realReward = realReward + 100
        return realReward

    def getWallLine(self, wallLoc):
        if(wallLoc[0] == wallLoc[2]):
            return (wallLoc[0], wallLoc[3], wallLoc[0]+1, wallLoc[3])
        else:
            return (wallLoc[2], wallLoc[1], wallLoc[2], wallLoc[1]+1)

    def getScreen(self):
        white = 255,255,255
        black = 0, 0, 0
        red = 255, 0, 0
        self.screen.fill(black)

        #draw grid
        pygame.draw.rect(self.screen, white, pygame.Rect(0, 0, self.imgSize[0], self.imgSize[1]), 2)

        xLine = self.width*4;
        yLine = self.height*4;
        incX = self.imgSize[0]/xLine*4;
        incY = self.imgSize[0]/yLine*4;
        for x in range(0, self.imgSize[0], incX):
            pygame.draw.line(self.screen, white, (x, 0), (x, self.imgSize[1]), 2);
        for y in range(0, self.imgSize[1], incY):
            pygame.draw.line(self.screen, white, (0, y), (self.imgSize[0], y), 2);
        #draw wall
        for wallLoc in self.wall:
            lineLoc = self.getWallLine(wallLoc)
            pygame.draw.line(self.screen, red, (lineLoc[0]*incX, lineLoc[1]*incY), (lineLoc[2]*incX, lineLoc[3]*incY), 2);
            #pygame.draw.line(self.screen, red, (3, 0), (3, self.imgSize[1]), 2);
        #for x in range(0, self.imgSize[0], incX):
            #pygame.draw.line(self.screen, white, (x, 0), (x, self.imgSize[1]), 2);
        #for y in range(0, self.imgSize[1], incY):
            #pygame.draw.line(self.screen, white, (0, y), (self.imgSize[0], y), 2);

        #draw objects
        offsetX = incX /2
        offsetY = incY /2

        for y in range(0, self.width):
            for x in range(0, self.height):
                if self.world[(x, y)] == 1:
                    rect = self.mario.get_rect()
                    rect.center = (offsetX + x*incX, offsetY + y*incY)
                    self.screen.blit(self.mario, rect)
                if self.world[(x, y)] == 2:
                    rect = self.turtle.get_rect()
                    rect.center = (offsetX + x*incX, offsetY + y*incY)
                    self.screen.blit(self.turtle, rect)
                if self.world[(x, y)] == 3:
                    rect = self.coin.get_rect()
                    rect.center = (offsetX + x*incX, offsetY + y*incY)
                    self.screen.blit(self.coin, rect)

        return self.screen
import SARSA
import HORDQ
import RMax
import tool

def BusRun(type, punishment, maxStep, isRORDQ, isRandomPlanner, isShow, framRate, loadFile):
    discrete_size = 6
    objSet = (1, 1)
    monsterMoveProb = 0.3
    isEpisodeEnd = False
    #maxStep = 200000
    size = 800, 800
    gridSize = (discrete_size, discrete_size)
    delay = 100
    interval = 50
    pygame.init()
    pygame.key.set_repeat(delay, interval)
    clock=pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))
    #controller = RelationalQ.RelationalQ(0.05, 0.1, 0.9, actionList)
    alpha = 0.2
    probAlpha = 0.1
    gamma = 1
    if type == 'SARSA':
        epsilon = 0.1
        controller = SARSA.SARSA(alpha, epsilon, gamma, actionList)

    else:
        epsilon = 0.05
        #isRORDQ = True
        hordQ = HORDQ.HORDQ(alpha, epsilon, gamma, actionList, isRORDQ)
        probQ = SARSA.SARSA(probAlpha, epsilon, gamma, [0])
        if isRandomPlanner:
            epsilon = 1
        controller = RMax.RMax(epsilon, gamma, hordQ, probQ, punishment)
    if loadFile != '':
        print "load:", loadFile
        controller = tool.Load(loadFile)
    env = BusEnv((discrete_size, discrete_size), size, actionList)

    numOfTurtle = objSet[0]
    numOfCoin = objSet[1]

    print "# coin ", numOfCoin
    print "# Turtle ", numOfTurtle
    print "isEpisodeEnd ", isEpisodeEnd

    isTraining = not isEpisodeEnd

    count = 0

    totalReward = 0
    rewardList = []
    stepCount = 0
    while stepCount < maxStep:
        #randomly choose a sub goal at the beginning of the episode
        goalDiff =  actionList[int(random.random()*len(actionList))]
        world = env.start(numOfTurtle, numOfCoin)
        action = controller.start(env.getSarsaFeature())

        count += 1
        prevStepCount = stepCount
        episodeReward = 0
        while stepCount < maxStep:
            if stepCount % 1000 == 0:
                print "Time: ", stepCount / 1000
            stepCount = stepCount + 1
            clock.tick(frameRate)
            reward, flag = env.step(action)
            fea = env.getSarsaFeature()
            totalReward = totalReward + reward
            episodeReward = episodeReward + reward
            if flag:
                controller.end(reward)
                break
            action = controller.step(reward, fea)

            for event in pygame.event.get():
                #action = 0
               if event.type == pygame.QUIT: sys.exit()
            if isShow:
                screen.blit(env.getScreen(), (0, 0))
                pygame.display.flip()
        rewardList.append((prevStepCount, stepCount, episodeReward))
    print totalReward
    #for conf in controller.agent:
        #print controller.agent[conf].Q
    #controller.dumpObj()
    #controller.dumpCoinAndGoal()
    #controller.dumpCoinAndGoalEx(controller.prob)
    #controller.dumpCoinAndGoalEx(controller.realReward)
    tool.Save(controller, type)
    tool.Save(rewardList, 'reward_'+type)
    #tool.Save(controller, 'smart.db')
    #tool.Save(rewardList, 'reward_pun_10')
    #print controller.agent
def checkHordq():
    loadFile = 'pun20'
    controller = tool.Load(loadFile)
    inOb = ((1, 1, 1, 1, (1, 0, 1), (1, 2)))
    ob = ((2, 3), inOb)
    hordq = controller.hordq
    for action in hordq.actionList: 
        print action
        print hordq.getpQ((ob, action))
        
        


def checkProb():
    loadFile = 'pun20'
    controller = tool.Load(loadFile)
    inOb = ((1, 1, 1, 1, (1, 0, 1), (1, 2)))
    #adjOb = ((1, 1, 1, 1, (1, 0, 1), (3, 2)))
    #adjOb = ((1, 1, 1, 1, (1, 0, 1), (1, 1)))
    adjOb = ((0, 1, 1, 1, (1, 1, 1), (1, 4)))
    envVar = controller.getEnvVar(inOb)
    state = controller.getPlanVar(inOb)
    adj = controller.getPlanVar(adjOb)
    action = 3
    tmpKey = (state, adj)
    #print controller.probQ[envVar].touch(tmpKey, action)
    #print controller.probQ[envVar].Q
    #print controller.probQ[envVar].getQ(tmpKey, action)

    actionList = controller.getActionList(state)
    room = controller.getRoom(state)
    fullState = controller.mergeVar(state, envVar)
    controller.updateQModel(inOb)
    for action in actionList:
        actionR = (room, action) 
        controller.hordq.touchAll((actionR, fullState))
        r = controller.hordq.getVc((actionR, fullState))
        c = 0
        print '-------action: ', action, 'environment:', envVar
        print 'Vr:', r

        for adj in controller.adjState[state]:
            tmpKey = (state, adj)
            controller.probQ[envVar].touch(tmpKey, action)
            prob = controller.probQ[envVar].getQ(tmpKey, action)
            print tmpKey
            print prob
            #controller.touchAll(self.mergeVar(adj, envVar))
            v = controller.getV(controller.mergeVar(adj, envVar))
            print "v:", v
            #c = c + prob*v
    
    
if __name__ == "__main__":

    #checkHordq()
    #checkProb()
    #if False:
    if True:
        #compare with RORDQ with random plannar
        #compare with HORDQ with random plannar
        #maxStep = 2000000
        maxStep = 400000
        isShow = False
        frameRate = 50000
        if isShow == True:
            frameRate = 2
        isRORDQ = False
        isRandomPlanner = False
        loadFile = ''
        #loadFile = 'sarsa'
        #loadFile = 'pun5'
        #loadFile = 'pun25'
        #loadFile = 'RORDQ'
        #BusRun('SARSA', 0, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        BusRun('pun5', 5, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun_dec', 6, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun50', 50, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun60', 60, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        BusRun('pun0', 0, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun20', 20, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        BusRun('pun10', 10, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun30', 30, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('pun105', 105, maxStep, isRORDQ, isRandomPlanner, isShow, frameRate, loadFile)
        #BusRun('RORDQ', 5, maxStep, True, isRandomPlanner, isShow, frameRate, loadFile)
