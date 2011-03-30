import random
import sys,pygame
import gridDef

#import IPython
monsterType = gridDef.monsterType
coinType = gridDef.coinType
marioType = gridDef.marioType
XType = gridDef.XType
YType = gridDef.YType

class Grid:
    def __init__(self, size, imgSize, actionList, monsterMoveProb):
        self.size = self.width, self.height = size
        self.imgSize = imgSize
        self.actionList = actionList
        self.monsterMoveProb = monsterMoveProb

        #Mario is 1
        #turtle is 2
        #coin is 3
        #goal is 4
        #empty tile is 0
        self.world = {}


    def start(self, numOfTurtle, numOfCoin, subgoal):
        self.stepNum = 0
        locList = []


        for y in range(0, self.width):
            for x in range(0, self.height):
                self.world[(x, y)] = 0

        #put mario in the middle of the world
        marioLoc = (self.width/2, self.height/2)
        self.world[marioLoc] = marioType
        locList.append(marioLoc)

        #add turtle
        for i in range(0, numOfTurtle):
            self.world[self.getNewLoc(locList)] = monsterType

        #add coin
        for i in range(0, numOfCoin):
            self.world[self.getNewLoc(locList)] = coinType


        self.objective = (subgoal[0] + marioLoc[0], subgoal[1] + marioLoc[1])
        #print self.getNewLoc(locList)

        self.mario = pygame.image.load("mario.bmp")
        self.coin = pygame.image.load("coin.bmp")
        self.turtle = pygame.image.load("turtle.bmp")
        self.screen = pygame.Surface(self.imgSize)

        return self.world

    def step(self, action, isTraining):
        self.stepNum = self.stepNum + 1
        reward, realReward, isSuccess = self.updateState(action)
        flag = self.isTerminal(realReward, isTraining)
        return reward, self.world, flag, realReward, isSuccess

    #def find(self, type):
        #for y in range(0, self.width):
            #for x in range(0, self.height):
                #if self.world[(x, y)] == type:
                    #return (x, y)
        #return (-1, -1)

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

    def isTerminal(self, reward, isTraining):
        marioLocList = self.find(marioType) 
        if marioLocList !=  []:
            marioLoc = marioLocList[0]
        else:
            assert 0
        monsterLoc = self.find(monsterType)
        if not isTraining:
            if self.count(coinType) == 0: #no coins available
                return True
        if marioLoc[0] == self.objective[0] and marioLoc[1] == self.objective[1]:
            #print "goal reached"
            return True 
        if self.stepNum == 1: #mario needs to acheive its goal in a very short time
            #print "Too long"
            return True
        if reward <= -30:
            return True

        return False

    def updateState(self, action):
        realReward = -0.5
        internalReward = -0.5
        marioLocList = self.find(marioType) 
        if marioLocList !=  []:
            marioOldLoc = marioLocList[0]
        else:
            IPython.Shell.IPShellEmbed()()
            assert 0
        self.world[marioOldLoc] = 0

        #move Monster
        monLocList = self.find(monsterType)
        if monLocList != []:
            for monLoc in monLocList:
                if random.random() < self.monsterMoveProb:
                    diffMon = (marioOldLoc[0] - monLoc[0], marioOldLoc[1] - monLoc[1])
                    monAction = (0, 0)
                    if diffMon[0] > 0:
                        monAction = (1, 0)
                    elif diffMon[1] > 0:
                        monAction = (0, 1)
                    elif diffMon[0] < 0:
                        monAction = (-1, 0)
                    elif diffMon[1] < 0:
                        monAction = (0, -1)
                    monNewLoc =(monLoc[0]+monAction[0], monLoc[1]+monAction[1]) 
                    
                    #check if monster goes to the boundary
                    if monNewLoc in self.world and self.world[monNewLoc] != coinType and self.world[monNewLoc] != monsterType :
                        self.world[monLoc] = 0
                        self.world[monNewLoc] = monsterType

        #move Mario
        if random.random() < 0.1:
            #select randomly
            action = self.actionList[int(random.random()*len(self.actionList))]

        marioNewLoc = (marioOldLoc[0]+action[0], marioOldLoc[1]+action[1])

        #check Mario stays in the boundary
        if not marioNewLoc in self.world:
            #reward = 0 #don't punish it
            marioNewLoc = marioOldLoc
        #check if Mario eats coin
        if self.world[marioNewLoc] == coinType:
            realReward = realReward + 20

        #meet turtle
        isMarioAlive = True
        if self.world[marioNewLoc] == monsterType or self.world[marioOldLoc] == monsterType:
            realReward = realReward - 60
            internalReward = internalReward - 60
            isMarioAlive = False

        isSuccess = False
        if marioNewLoc[0] == self.objective[0] and marioNewLoc[1] == self.objective[1]:
            if isMarioAlive:
                isSuccess = True
                #add a small reward to reward the agent who reaches the subgoal
                internalReward = internalReward + 20
        self.world[marioNewLoc] = 1
        return internalReward, realReward, isSuccess

    def getScreen(self):
        white = 255,255,255
        black = 0, 0, 0
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

def Save(agent, filename): 
    import pickle
    output = open(filename, 'wb')
    pickle.dump(agent, output)
    output.close()

def Load(filename):
    import pickle
    input = open(filename, 'rb')
    return pickle.load(input)
import RelationalQ
import tool
if __name__ == "__main__":
    #confList = [(0, 1)]
    discrete_size = 8
    objSet = (1, 1)
    monsterMoveProb = 0.3
    isEpisodeEnd = False
    maxStep = 10000
    frameRate = 5000
    isShow = False
    size = 800, 800
    gridSize = (discrete_size, discrete_size)
    delay = 100
    interval = 50
    pygame.init()
    pygame.key.set_repeat(delay, interval)
    clock=pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))
    controller = RelationalQ.RelationalQ(0.05, 0.1, 0.9, actionList)
    env = Grid((discrete_size, discrete_size), size, actionList, monsterMoveProb)

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
        world = env.start(numOfTurtle, numOfCoin, goalDiff)
        objLoc = tool.getObjLoc(world, gridSize)
        marioLoc = tool.getMarioLoc(world, gridSize)
        goal = (marioLoc[0]+goalDiff[0], marioLoc[1]+goalDiff[1])
        objLocWithGoal = tool.addGoalLoc(objLoc, goal)
        ob = (marioLoc, objLocWithGoal)
        action = controller.start(ob)

        count += 1
        prevStepCount = stepCount
        episodeReward = 0
        while stepCount < maxStep:
            stepCount = stepCount + 1
            clock.tick(frameRate)
            reward, world, flag, realReward, isSuccess = env.step(action, isTraining)
            totalReward = totalReward + reward
            episodeReward = episodeReward + reward
            if flag:
                #print "episodeEnd: ", reward
                controller.end(reward, realReward, isSuccess)
                break
            assert(False)
            objLoc = tool.getObjLoc(world, gridSize)
            marioLoc = tool.getMarioLoc(world, gridSize)
            objLocWithGoal = tool.addGoalLoc(objLoc, goal)
            #goalDiff = (goal[0]-marioLoc[0], goal[1]-marioLoc[1])
            ob = (marioLoc, objLocWithGoal)
            action = controller.step(reward, ob, realReward, isSuccess)

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
    Save(controller, 'smart.db')
    #print controller.agent
