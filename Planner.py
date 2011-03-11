import networkx as nx

def GetPlan(gridSize, marioLoc, objLoc, Q):
    #compute the link cost
    return

if __name__ == "__main__":
    DG=nx.DiGraph()
    DG.add_weighted_edges_from([(2,1,0.5), (3,1,0.1), (2, 3, 0.1)])
    #G=nx.path_graph(5)
    #print G.nodes()
    
    print nx.shortest_path(DG,source=2,target=1)
    print nx.shortest_path(DG,source=2,target=1, weighted=True)
    
    
    #G=nx.Graph()
    #G.add_nodes_from([2,3])
    #G.add_edge(1,2)
    #print G.nodes()
    #print G.edges()
    
    
    
