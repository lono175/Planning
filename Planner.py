import networkx as nx
import tool
import math #for exp
import gridDef
#import IPython #for debug
monsterType = gridDef.monsterType
coinType = gridDef.coinType
XType = gridDef.XType
YType = gridDef.YType
goalType = gridDef.goalType
def GetPlanCost(inPath, objLoc, controller, isDump):
    Q = 0
    accProb = 1
    path = inPath[:]
    prev = path.pop(0) #remove the first one
    #print "--------------path: ", path
    step = 1
    for node in path:
        #print "goal: ", node
        objLocWithGoal = tool.addGoalLoc(objLoc, node)
        ob = (prev, objLocWithGoal)
        #print "observation: ", ob
        prob = controller.getLinkProb(ob, controller.prob)

        #temporary solution
        #if prob > 0:
            #prob = 0
        #prob = prob/2

        reward = controller.getLinkReward(ob, controller.realReward)
        failedReward = controller.getLinkReward(ob, controller.failedReward)

        newQ = pow(0.95, step)*accProb*(reward*prob + failedReward*(1-prob))

        accProb = accProb * prob
        if isDump:
            print "newQ: ", newQ
            print "failedReward: ",  failedReward
            print "reward: ",  reward
            print "prob", prob
        Q = Q + newQ
        prev = node
        step = step + 1
    return Q


def GetPlan(gridSize, marioLoc, objLoc, controller):

    diffGoal = ((0, 1), (0, -1), (1, 0), (-1, 0))
    DG=nx.DiGraph()
    #G=nx.path_graph(5)
    #add each node into the graph
    for x in range(0, gridSize):
        for y in range(0, gridSize):
            loc = (x, y)

            for diff in diffGoal:
                goal = (diff[0]+loc[0], diff[1]+loc[1])
                if not goal[0]  in range(0, gridSize) or not goal[1] in range(0, gridSize):
                    continue
                objLocWithGoal = tool.addGoalLoc(objLoc, goal)
                ob = (loc, objLocWithGoal)
                #compute the link cost
                #linkCost = controller.getLinkCost(ob, controller.prob)

                #temporary solution, log prob is max at 0
                #if linkCost > 0:
                    #linkCost = 0
                #linkCost = -linkCost #need to be positive

                #print maxQ
                #assert(maxQ > -10) #don't handle monster
                linkCost = controller.getLinkCost(ob, controller.agent[0])
                linkCost = 1 / pow(2, (linkCost))
                DG.add_weighted_edges_from([(loc, goal, linkCost)])

    #for x in range(0, gridSize):
        #for y in range(0, gridSize):
            #goal = (x, y)
    pathList = nx.single_source_dijkstra_path(DG, source = marioLoc)
    #print nx.single_source_dijkstra_path(DG, source = marioLoc)
    #print nx.single_source_dijkstra_path_length(DG,source=marioLoc)
    #print '------------------'
    #print nx.shortest_path(DG, source = marioLoc, target = (4, 4), weighted=True)
    #print nx.shortest_path_length(DG, source = marioLoc, target = (4, 4), weighted=True)

    #follow the path and find the one with maximum reward

    maxQ = -1000000
    bestPath = []
    for goal in pathList:
        
        #cannot stay in the current state
        if goal[0] == marioLoc[0] and goal[1] == marioLoc[1]:
            continue
        Q = GetPlanCost(pathList[goal], objLoc, controller, False)
        if Q > maxQ:
            maxQ = Q
            bestPath = pathList[goal]
    #just reture the next node in the best path
    #print "path cost: ", maxQ
    return bestPath[0], bestPath
#print bestPath
    #print maxQ

    #maxQ = -10000
    #for goal in {(7, 7):[(1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7), (5, 7), (6, 7), (7, 7)]}:
        #Q = 0
        #path = pathList[goal]
        #prev = path.pop(0) #remove the first one
        #for node in path:
            ##diff = (node[0] - prev[0], node[1] - prev[1])
            #objLocWithGoal = tool.addGoalLoc(objLoc, node)
            #ob = (prev, objLocWithGoal)
            #nodeQ = controller.getMaxQ(ob)
            #Q = Q + nodeQ
            #print "nodeQ: ", nodeQ
            #prev = node
        #if Q > maxQ:
            #maxQ = Q
            #bestPath = path
    #print bestPath
    #print maxQ

    #maxQ = -10000
    #for goal in {(7, 1):[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (7, 1)]}:
        #Q = 0
        #path = pathList[goal]
        #prev = path.pop(0) #remove the first one
        #for node in pathList:
            ##diff = (node[0] - prev[0], node[1] - prev[1])
            #objLocWithGoal = tool.addGoalLoc(objLoc, node)
            #ob = (prev, objLocWithGoal)
            #nodeQ = controller.getMaxQ(ob)
            #Q = Q + nodeQ
            #prev = node
        #if Q > maxQ:
            #maxQ = Q
            #bestPath = path
    #print bestPath
    #print maxQ
    return

def Load(filename):
    import pickle
    input = open(filename, 'rb')
    return pickle.load(input)
def Save(agent, filename): 
    import pickle
    output = open(filename, 'wb')
    pickle.dump(agent, output)
    output.close()
import GridEnv
import sys,pygame
import copy #for copy objects
def TestRun(controller, discrete_size, monsterMoveProb, objSet, maxStep, isEpisodeEnd, isShow, frameRate):
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
    print "isEpisodeEnd ", isEpisodeEnd

    count = 0

    totalReward = 0
    rewardList = []
    stepCount = 0
    while stepCount < maxStep:
        #for i in range(0, maxEpisode):
        #print totalReward
        #rewardList[i] = totalReward

        Save(controller, 'smart.db')
        world = env.start(numOfTurtle, numOfCoin)
        objLoc = tool.getObjLoc(world, gridSize)
        marioLoc = tool.getMarioLoc(world, gridSize)
        goal, bestPath = GetPlan(discrete_size, marioLoc, objLoc, controller)
        #print "plan: ", bestPath

        dummy = bestPath.pop(0)
        prevPath = bestPath[:]
        goal = bestPath.pop(0)
        #curPlanCounter = 3
        #print "goal: ", goal
        objLocWithGoal = tool.addGoalLoc(objLoc, goal)
        ob = (marioLoc, objLocWithGoal)
        action = controller.start(ob)

        count += 1
        prevStepCount = stepCount
        while stepCount < maxStep:
            stepCount = stepCount + 1
            clock.tick(frameRate)
            reward, world, flag, realReward, isSuccess = env.step(action, isTraining, goal)
            totalReward = totalReward + reward

            if flag:
                controller.end(reward, realReward, isSuccess)
                break
            objLoc = tool.getObjLoc(world, gridSize)
            marioLoc = tool.getMarioLoc(world, gridSize)
            print "-------------mario: ", marioLoc
            #if len(bestPath) == 0 or curPlanCounter == 0:
            dummy, bestPath = GetPlan(discrete_size, marioLoc, objLoc, controller)
            print "plan: ", bestPath
            #curPlanCounter = curPlanCounter - 1

            if isSuccess: #if not, just use the old plan
                curPathCost = GetPlanCost(bestPath, objLoc, controller, True)
                prevPathCost = GetPlanCost(prevPath, objLoc, controller, True)
                print "cur plan Cost: ", curPathCost
                print "prev plan Cost: ", prevPathCost
                if prevPathCost > 0.9*curPathCost and len(prevPath) > 1:
                    #stay with old plan
                    print "stay with old plan"
                    bestPath = prevPath
                
            dummy = bestPath.pop(0)
            prevPath = bestPath[:]
            goal = bestPath.pop(0)
                    
            #print "goal: ", goal
            objLocWithGoal = tool.addGoalLoc(objLoc, goal)
            ob = (marioLoc, objLocWithGoal)
            allQ = controller.getAllQ(ob)
            print "allQ: ", allQ
            #print "internalReward: ", reward
            action = controller.step(reward, ob, realReward, isSuccess)
            print "action: ", action
            for event in pygame.event.get():
                #action = 0
               if event.type == pygame.QUIT: sys.exit()
            if isShow:
                screen.blit(env.getScreen(), (0, 0))
                pygame.display.flip()
        #rewardList.append((prevStepCount, stepCount, episodeReward))
    #print totalReward
    return rewardList, controller
if __name__ == "__main__":
    controller = Load('smart.db')
    #controller.dumpObjAndGoalAndProb(controller.prob, coinType)
    #controller.dumpObjAndGoalAndProb(controller.prob, monsterType)
    #controller.dumpObjAndGoalEx(controller.prob, coinType)
    #controller.dumpObjAndGoalEx(controller.prob, monsterType)
    #controller.dumpObjAndGoalEx(controller.realReward, coinType)
    #controller.dumpObjAndGoalEx(controller.realReward, monsterType)
    #print ""
    #controller.dumpObjAndGoalEx(controller.failedReward, monsterType)

    discrete_size = 8
    objSet = (2, 5)
    monsterMoveProb = 0.3
    isEpisodeEnd = True
    maxStep = 5000
    frameRate = 5
    isShow = True
    TestRun(controller, discrete_size, monsterMoveProb, objSet, maxStep, isEpisodeEnd, isShow, frameRate)

    #Save(controller, 'smart.db')
    #DG=nx.DiGraph()
    #DG.add_weighted_edges_from([(2,1,0.5), (3,1,0.1), (2, 3, 0.1)])
    #G=nx.path_graph(5)
    #print G.nodes()

    #print nx.shortest_path(DG,source=2,target=1)
    #print nx.shortest_path(DG,source=2,target=1, weighted=True)


    #G=nx.Graph()
    #G.add_nodes_from([2,3])
    #G.add_edge(1,2)
    #print G.nodes()
    #print G.edges()



