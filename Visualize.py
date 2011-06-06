import tool
#def Load(objectList, filename):
    #import pickle
    #input = open(filename, 'rb')
    #objectList[0] = pickle.load(input)
#def Save(object, filename): 
    #import pickle
    #output = open(filename, 'wb')
    #pickle.dump(object, output)
    #output.close()


def SaveToCSV(list, filename):
    FILE = open(filename,"w")
    for line in list:
        for item in line:
            FILE.write(str(item))
            FILE.write(', ')
        FILE.write('\n')
    FILE.close()
def FileSaveToCSV(filename):
    listT = tool.Load(filename)
    controller = listT[0]
    SaveToCSV(listT, filename+'.csv')
if __name__ == "__main__":
    fileList = [
            'reward_sarsa',
            'reward_pun0',
            #'reward_pun2',
            'reward_pun5',
            'reward_pun10',
            'reward_pun20',
            'reward_pun50',
            #'reward_pun30',
            'reward_pun60',
            'reward_RORDQ',
            #'reward_pun105'
            ]
    for file in fileList:
        FileSaveToCSV(file)

