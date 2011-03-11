import random
import sys,pygame

class Grid:
    def __init__(self, size, imgSize, actionList, monsterMoveProb):
        self.size = self.width, self.height = size
        self.imgSize = imgSize
        self.actionList = actionList
        self.monsterMoveProb = monsterMoveProb
        #Mario is 1
        #turtle is 2
        #coin is 3
        #empty tile is 0
        self.world = {}

    def getNewLoc(self, locList):
        while True:
            locX = min(int(random.random()*self.width), self.width -1);
            locY = min(int(random.random()*self.height), self.height -1);
            loc = (locX, locY)
            if locList.count(loc) == 0:
               locList.append(loc)
               return loc
               break

    def start(self, numOfTurtle, numOfCoin):
        self.stepNum = 0
        locList = []

        for y in range(0, self.width):
            for x in range(0, self.height):
                self.world[(x, y)] = 0

        #add turtle
        for i in range(0, numOfTurtle):
           self.world[self.getNewLoc(locList)] = 2

        #add coin
        for i in range(0, numOfCoin):
           self.world[self.getNewLoc(locList)] = 3

        #add mario
        self.world[self.getNewLoc(locList)] = 1
        #print self.getNewLoc(locList)

        self.mario = pygame.image.load("mario.bmp")
        self.coin = pygame.image.load("coin.bmp")
        self.turtle = pygame.image.load("turtle.bmp")
        self.screen = pygame.Surface(self.imgSize)

        return self.world

    def step(self, action, isTraining):
        self.stepNum = self.stepNum + 1
        reward = self.updateState(action)
        flag = self.isTerminal(reward, isTraining)
        #reward = calculate reward for newState
        #set observation equal to newState
        #state = newState
        return reward, self.world, flag

    def find(self, type):
        for y in range(0, self.width):
            for x in range(0, self.height):
                if self.world[(x, y)] == type:
                    return (x, y)
        return (-1, -1)

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
        if not isTraining:
            if self.count(3) == 0: #no coins available
                return True
        if self.stepNum > 2000:
            return True
        if reward == -30:
            return True
        return False

    def updateState(self, action):
        reward = -0.1
        marioOldLoc = self.find(1)
        self.world[marioOldLoc] = 0

        #move Monster
        if random.random() < self.monsterMoveProb:
            monLoc = self.find(2)

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
            self.world[monLoc] = 0
            self.world[monNewLoc] = 2

        #move Mario
        if random.random() < 0.1:
            #select randomly
            action = self.actionList[int(random.random()*len(self.actionList))]

        marioNewLoc = (marioOldLoc[0]+action[0], marioOldLoc[1]+action[1])

        #check Mario stays in the boundary
        if not marioNewLoc in self.world:
            reward = -1
            marioNewLoc = marioOldLoc
        #check if Mario eats coin
        if self.world[marioNewLoc] == 3:
            reward = 20
        elif self.world[marioNewLoc] == 2 or self.world[marioOldLoc] == 2:
            #meet turtle
            reward = -30
        self.world[marioNewLoc] = 1
        return reward

    #def getSarsaFeature(self):
        #marioLoc = (-1, -1)
        #coinLoc = (-1, -1)
        #monsterLoc = (-1, -1)
        #observation = self.world
        #for y in range(0, self.height):
            #for x in range(0, self.width):
                #key = (x, y)
                #if(observation[key] == 1):
                    #marioLoc = key
        #for y in range(0, self.height):
            #for x in range(0, self.width):
                #key = (x, y)
                #if(observation[key] == 2):
                    #monsterLoc = (key[0] - marioLoc[0], key[1] - marioLoc[1])
                #elif (observation[key] == 3):
                    #coinLoc = (key[0] - marioLoc[0], key[1] - marioLoc[1])
        #return (marioLoc[0], marioLoc[1], monsterLoc[0], monsterLoc[1], coinLoc[0], coinLoc[1])

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
