import Predicate

def flatten(l):
    if isinstance(l,list):
        return (map(flatten,l))
    else:
        return l

if __name__ == "__main__":
    print Predicate.monsterType
    l = [(1,2), (3, 4)]
    l2 = [item for sublist in l for item in sublist]
    print l2

