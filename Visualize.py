import Lono
def Load(objectList, filename):
    import pickle
    input = open(filename, 'rb')
    objectList[0] = pickle.load(input)
def Save(object, filename): 
    import pickle
    output = open(filename, 'wb')
    pickle.dump(object, output)
    output.close()
actionList = ((0, 1), (0, -1), (1, 0), (-1, 0))
discrete_size = 8
trainedControl = Lono.FactoredQ(0.2, 0.2, 0.9, actionList, (discrete_size, discrete_size))
listT = [trainedControl];
Load(listT, 'controller.txt')
controller = listT[0]
#print "coin------------------"
##print controller.agent[2].Q
#print "turtle------------------"
#for y in range(-2, 3):
    #for x in range(-2, 3):
        #for action in actionList:
            #print (x, y), " ", action, " ", controller.agent[2].Q[((x, y), action)]
#print "coin------------------"
#for y in range(-4, 4):
    #for x in range(-4, 4):
        #for action in actionList:
            #print (x, y), " ", action, " ", controller.agent[3].Q[((x, y), action)]
#print "world------------------"
#for y in range(0, 3):
    #for x in range(0, 3):
        #for action in actionList:
            #print (x, y), " ", action, " ", controller.agent[1].Q[((x, y), action)]
#print "all------------------"
#for y in range(0, 3):
    #for x in range(0, 3):
        #for action in actionList:
            #print (x, y), " ", action, " ", controller.agent[0].Q[((x, y), action)]

#listR = [[]]
#Load(listR, 'avgReward.txt')
#print listR

outputX = open('rewardx.csv', 'wb')
outputY = open('rewardy.csv', 'wb')
Agent = controller.agent[2]
for y in range(-4, 5):
    for x in range(-4, 5):
        maxAction = actionList[0]
        maxReward = Agent.Q[(x, y), maxAction]
        for action in actionList:
            #print (x, y), " ", action, " ", Agent.Q[((x, y), action)]
            reward = Agent.Q[(x, y), action]
            if reward > maxReward:
                maxAction = action
                maxReward = reward

        
        print (x, y), " ", maxAction, " ", Agent.Q[((x, y), maxAction)]
        outputX.write(str(maxAction[0]) + ',')
        outputY.write(str(maxAction[1]) + ',')
       
outputX.close()
outputY.close()
