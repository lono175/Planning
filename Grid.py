#how to deal with poison?? -> give you small reward but make you die after 100 steps or when you shoot something --> it takes time for the bullet to reach its target

import sys,pygame
import copy #for copy objects
import RelationalQ
import SARSA
import LinearSARSA
import Predicate
import LinearSARSA
import GridEnv

def Save(agent, filename): 
    import pickle
    output = open(filename, 'wb')
    pickle.dump(agent, output)
    output.close()

def Load(filename):
    import pickle
    input = open(filename, 'rb')
    return pickle.load(input)

def SubgoalTraining(controller, discrete_size, monsterMoveProb, trainingStage, objSet, maxStep, isEpisodeEnd, isShow, frameRate):
    size = 800, 800
    gridSize = (discrete_size, discrete_size)
    delay = 100
    interval = 50
    pygame.init()
    pygame.key.set_repeat(delay, interval)
    clock=pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))
    env = GridEnvSim.Grid((discrete_size, discrete_size), size, actionList, monsterMoveProb)

    isTraining = not isEpisodeEnd

    numOfTurtle = objSet[0]
    numOfCoin = objSet[1]

    print "# coin ", numOfCoin
    print "# Turtle ", numOfTurtle
    print "training stage ", trainingStage
    print "isEpisodeEnd ", isEpisodeEnd

    count = 0
    
    totalReward = 0
    rewardList = []
    stepCount = 0
    while stepCount < maxStep:
        #randomly choose a sub goal at the beginning of the episode
        subgoal =  self.actionList[int(random.random()*len(actionList))]
        world = env.start(numOfTurtle, numOfCoin, subgoal)
        objLoc = getObjLoc(world, gridSize)
        marioLoc = getMarioLoc(world, gridSize)
        ob = (subgoal, marioLoc, objLoc)
        action = controller.start(ob)
            
        count += 1
        prevStepCount = stepCount
        episodeReward = 0
        while stepCount < maxStep:
            stepCount = stepCount + 1
            clock.tick(frameRate)
            reward, world, flag = env.step(action, isTraining)
            totalReward = totalReward + reward
            episodeReward = episodeReward + reward
            if flag:
                controller.end(reward, trainingStage)
                break
            objLoc = getObjLoc(world, gridSize)
            marioLoc = getMarioLoc(world, gridSize)
            ob = (subgoal, marioLoc, objLoc)
            action = controller.step(reward, ob, trainingStage)

            for event in pygame.event.get():
               #action = 0
               if event.type == pygame.QUIT: sys.exit()
            if isShow:
                screen.blit(env.getScreen(), (0, 0))
                pygame.display.flip()
        rewardList.append((prevStepCount, stepCount, episodeReward))
    print totalReward
    return rewardList, controller

def TestRun(controller, type, discrete_size, monsterMoveProb, isUpdate, trainingStage, objSet, maxStep, isEpisodeEnd, isShow, frameRate):

    print "MaxStep: ", maxStep
    size = 800, 800
    gridSize = (discrete_size, discrete_size)
    delay = 100
    interval = 50
    pygame.init()
    pygame.key.set_repeat(delay, interval)
    clock=pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))
    env = GridEnv.Grid((discrete_size, discrete_size), size, actionList, monsterMoveProb)

    isTraining = not isEpisodeEnd
    #maxStep = 200

    numOfTurtle = objSet[0]
    numOfCoin = objSet[1]

    print "# coin ", numOfCoin
    print "# Turtle ", numOfTurtle
    print "training stage ", trainingStage
    print "isEpisodeEnd ", isEpisodeEnd

    count = 0
    
    totalReward = 0
    rewardList = []
    stepCount = 0
    while stepCount < maxStep:
    #for i in range(0, maxEpisode):
        #print totalReward
        #rewardList[i] = totalReward

        world = env.start(numOfTurtle, numOfCoin)
        objLoc = getObjLoc(world, gridSize)
        marioLoc = getMarioLoc(world, gridSize)
        ob = (marioLoc, objLoc)
        if type == 'RRL':
            action = controller.start(ob)
        elif type == 'SARSA':
            action = controller.start(Predicate.getSarsaFeature(ob))
            #print Predicate.getSarsaFeature(ob)
        elif type == 'LinearSARSA':
            action = controller.start(Predicate.getSarsaFeature(ob))
            
        count += 1
        prevStepCount = stepCount
        episodeReward = 0
        while stepCount < maxStep:
            stepCount = stepCount + 1
            clock.tick(frameRate)
            reward, world, flag = env.step(action, isTraining)
            totalReward = totalReward + reward
            episodeReward = episodeReward + reward
            if flag:
                if type == 'RRL':
                    controller.end(reward, trainingStage)
                elif type == 'SARSA' or type == 'LinearSARSA':
                    controller.end(reward, isUpdate)
                else:
                    assert False
                break
            objLoc = getObjLoc(world, gridSize)
            marioLoc = getMarioLoc(world, gridSize)
            ob = (marioLoc, objLoc)
            if type == 'RRL':
                action = controller.step(reward, ob, trainingStage)
            elif type == 'SARSA' or 'LinearSARSA':
                action = controller.step(reward, Predicate.getSarsaFeature(ob), isUpdate)
            else:
                assert False
            for event in pygame.event.get():
               #action = 0
               if event.type == pygame.QUIT: sys.exit()
            if isShow:
                screen.blit(env.getScreen(), (0, 0))
                pygame.display.flip()
        rewardList.append((prevStepCount, stepCount, episodeReward))
    print totalReward
    return rewardList, controller

    
def DumpSARSA(controller):
    #print controller.Q
    #print controller.agent[2].Q
    for y in range(-1, 2):
        for x in range(-1, 2):
            for action in controller.actionList:
                fea = ((0, 0), (1, 0), (x, y))
                controller.touch(fea, action)
                key = (fea, action)
                print key, " ", action, " ", controller.Q[key]
def DumpRRL(controller):
    actionList = controller.actionList
    print "monster------------------"
    #print controller.agent[2].Q
    for y in range(-2, 3):
        for x in range(-2, 3):
            for action in actionList:
                controller.agent[2].touch((x, y), action)
                print (x, y), " ", action, " ", controller.agent[2].Q[((x, y), action)]
    print "coin------------------"
    #print controller.agent[2].Q
    for y in range(-2, 3):
        for x in range(-2, 3):
            for action in actionList:
                controller.agent[3].touch((x, y), action)
                print (x, y), " ", action, " ", controller.agent[3].Q[((x, y), action)]
    print "world------------------"
    for y in range(0, 3):
        for x in range(0, 3):
            for action in actionList:
                controller.agent[1].touch((x, y), action)
                print (x, y), " ", action, " ", controller.agent[1].Q[((x, y), action)]
    print "coin and monster------------------"
    for y in range(0, 3):
        for x in range(0, 3):
            for action in actionList:
                controller.agent[4].touch(((x, y), (1, 0)), action)
                print (x, y), " ", action, " ", controller.agent[4].Q[(((x, y), (1, 0)), action)]
def SmallWorldTest(isShow, frameRate, discrete_size, worldConf, agentConf, maxTrainEpisode, maxTestEpisode):

    #isShow = True
    #frameRate = 10
    #discrete_size = 16
    monsterMoveProb = 0.3
    isUpdate = True
    #worldConf = (3, 5)

    actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))

    #if False:
    dumpCount = 10000000000
    initialQ = 0
    #controller = LinearSARSA.LinearSARSA(0.1, 0.2, 0.9, actionList, initialQ, dumpCount)
    #controller = SARSA.SARSA(0.1, 0.2, 0.9, actionList)
    #reward, controller = TestRun(controller, 'LinearSARSA', discrete_size, monsterMoveProb, isUpdate, 4, worldConf, maxTrainEpisode, True, isShow, frameRate)
    #SaveToCSV(reward, 'LinearSarsaTrainX'+ str(discrete_size) + 'X' + str(worldConf[0]) +'_' + str(worldConf[1])+ 'X' + str(maxTrainEpisode)+'.csv')
    #reward, controller = TestRun(controller, 'LinearSARSA', discrete_size, monsterMoveProb, isUpdate, 4, worldConf, maxTestEpisode, True, isShow, frameRate)
    #SaveToCSV(reward, 'LinearSarsaTestX'+ str(discrete_size) + 'X'+ str(worldConf[0]) +'_'+ str(worldConf[1])+'X' +str(maxTestEpisode)+'.csv')

    #Save(controller, 'SarsaCompController'+'.txt')
    #print controller.Q
    #DumpSARSA(controller)



    #preList = [Predicate.MarioPre(), Predicate.MonsterPre(), Predicate.CoinPre(), Predicate.CoinAndMonsterPre(), Predicate.RestPre()]
    preList = []
    for conf in agentConf:
        preList.append(Predicate.CoinAndMonsterPre(conf[0], conf[1]))
    preList.append(Predicate.RestPre())
    controller = RelationalQ.RelationalQ(0.1, 0.2, 0.9, actionList, preList)
    

    #trainEpisodeList = [0, 50, 100, 150]
    trainEpisode = maxTrainEpisode / len(agentConf)

    trainingStage = 1
    lastConf = agentConf[len(agentConf)-1]
    print "Prepare training--------------"
    for conf in agentConf: #don't run 2-order in the training stage
        #print "stage: ", trainingStage 
        #print "monster: ", conf[0]
        #print "coin: ", conf[1]

        coinNum = conf[1]

        isEpisodeEnd  = False
        if coinNum > 0:
            isEpisodeEnd = True

        reward, controller = TestRun(controller, 'RRL', discrete_size, monsterMoveProb, isUpdate, trainingStage, conf, trainEpisode, isEpisodeEnd, isShow, frameRate)
        #Save(controller, 'RRL_controller_train_'+str(trainEpisode)+ '_'+str(lastConf)+'_'+str(len(agentConf)) + '.txt')
        #DumpRRL(controller)
        trainingStage = trainingStage + 1

    #DumpRRL(controller)
    #raw_input("Press Enter to continue...")

    #DumpRRL(controller)

    isEpisodeEnd = True
    reward, controller = TestRun(controller, 'RRL', discrete_size, monsterMoveProb, isUpdate, trainingStage, worldConf, maxTestEpisode, isEpisodeEnd, isShow, frameRate)
    SaveToCSV(reward, 'RRLXtestX'+ str(discrete_size) + 'X'+ str(worldConf[0])+'_'+str(worldConf[1]) + 'X' +str(maxTrainEpisode)+'X'+str(lastConf[0])+'_'+str(lastConf[1])+'X'+str(len(agentConf))+'.csv')
    #Save(controller, 'RRL_test_controller_'+str(trainEpisode)+'_'+str(lastConf)+'_'+str(len(agentConf))+'.txt')

        
def SaveToCSV(list, filename):
    FILE = open(filename,"w")
    for line in list:
        for item in line:
            FILE.write(str(item))
            FILE.write(', ')
        FILE.write('\n')
    FILE.close()
if __name__ == "__main__":
    #reward = Load('convergence.txt')
    #SaveToCSV(r]ward, 'conv.csv')
    #trainEpisodeList = [0, 400, 800, 1200, 1600, 2000, 2400, 2800]
    multipler = 1000
    #trainEpisodeList = [1, 5, 10, 20, 40, 60, 80, 100]
    trainEpisodeList = [1, 5, 10, 20, 40, 60, 80, 100]
    #trainEpisodeList = [10]
    testEpisode = 100

    i = 0
    for item in trainEpisodeList:
        trainEpisodeList[i] = item*multipler
        i = i + 1
    
    print trainEpisodeList
    testEpisode = testEpisode*multipler

    discreteSizeList = [8, 16, 24, 32]
    confList = [(3, 5), (6, 10), (12, 20)]
    agentList =                      \
    [                                \
    #[(1, 1), (2, 5)],                 \
    #[(5, 3)]                         \
    [(1, 1)],                        \
    [(1, 2)],                        \
    [(2, 1)],                        \
    [(0, 1)],                        \
    [(0, 2)],                        \
    [(1, 0)],                        \
    [(2, 0)],                        \
    #[(0, 3)],                        \
    [(0, 1), (0, 2)],                \
    [(1, 0), (0, 1)],                 \
    [(1, 0), (0, 1), (1, 1)],                 \
    [(1, 1), (1, 2)],                \
    [(1, 0), (0, 1), (1, 1), (0, 2), (1, 2)], \
    #[(0, 1), (0, 2), (0, 3)],        \
    #[(0, 1), (0, 2), (0, 3), (0, 4)],\
    [(1, 1), (2, 1)],                \
    [(1, 0), (0, 1), (1, 1), (2, 0), (2, 1)], \
    #[(1, 0), (2, 0)],                \
    #[(1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (2, 1), (1, 2), (2, 2)], \
    #[(3, 0)],                        \
    #[(1, 0), (2, 0), (3, 0)],        \
    #[(1, 0), (2, 0), (3, 0), (4, 0)]\
    ]
    isShow = False
    frameRate = 5000
    #discrete_size = 16
    #worldConf = (3, 5)
    for discreteSize in discreteSizeList:
        for worldConf in confList:
            for trainEpisode in trainEpisodeList:
                for agentConf in agentList:
                    SmallWorldTest(isShow, frameRate, discreteSize, worldConf, agentConf, trainEpisode, testEpisode)
    #for maxEpisode in range(100, 1000, 100):
        #controller = train(maxEpisode, 'SARSA')
        #Save(controller, 'SARSA-Agent' + str(maxEpisode) + '.txt')

    #for maxEpisode in range(100, 1000, 100):
        #controller = train(maxEpisode, 'RRL')
        #Save(controller, 'RL-Agent' + str(maxEpisode) + '.txt')


    #for maxEpisode in range(100, 1000, 100):
        #controller = Load('SARSA-Agent' + str(maxEpisode) + '.txt')
        #reward = TestRun(controller, 'SARSA')
        #Save(reward, 'SARSA-Reward'+str(maxEpisode)+'.txt')

    #for maxEpisode in range(100, 1000, 100):
        #controller = Load('RL-Agent' + str(maxEpisode) + '.txt')
        #reward = TestRun(controller, 'RRL')
        #Save(reward, 'RRL'+str(maxEpisode)+'.txt')

    #controller = Load('RL-Agent' + str(900) + '.txt')
    #reward = TestRun(controller, 'RRL')
    #Save(reward, 'RRL-Reward-learning-900'+'.txt')

    #controller = Load('SARSA-Agent' + str(900) + '.txt')
    #reward = TestRun(controller, 'SARSA')
    #Save(reward, 'SARSA-Reward-learning-900'+'.txt')

    #reward = Load('SARSA-Reward-learning-900.txt')
    #FILE = open('SARSA_Reward_Diff',"w")
    #for index in reward:
        #FILE.write(str(reward[index]))
        #FILE.write(', ')
        #
    #FILE.close()

    #reward = Load('RRL-Reward-learning-900.txt')
    #FILE = open('RRL_Reward_Diff',"w")
    #for index in reward:
        #FILE.write(str(reward[index]))
        #FILE.write(', ')
        #
    #FILE.close()
