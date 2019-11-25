import snap
import random
import time
import threading
import pandas
import matplotlib.pyplot as plt

def manage_graphs(out_degree, nodes=50):
    rnd = snap.TRnd(1, 0)
    graph = snap.GenSmallWorld(nodes, out_degree, 0.7, rnd)
    print(f"Starting Graph for #{nodes} Nodes.")
    print(40*"#")

    # Save the graph in order to reload it after manipulation
    output_filename = f"temporary_graphs/{nodes}_ws_graph.graph"
    f_out = snap.TFOut(output_filename)
    graph.Save(f_out)
    f_out.Flush()

    # Highest rank Node
    max_degree_node = graph.GetNI(snap.GetMxDegNId(graph))
    print(f"Highest Degree Node ID#{max_degree_node.GetId()}"
          f" with Degree={max_degree_node.GetDeg()}")

    # Gets Hubs and Authorities of all the nodes
    hubs_per_node = snap.TIntFltH()
    auths_per_node = snap.TIntFltH()
    snap.GetHits(graph, hubs_per_node, auths_per_node)

    max_hub_node = graph.GetNI(max(hubs_per_node, key=lambda h: hubs_per_node[h]))
    print(f"Highest Hub Score Node ID#{max_hub_node.GetId()}"
          f" with Score={hubs_per_node[max_hub_node.GetId()]}")

    max_authority_node = graph.GetNI(max(auths_per_node, key=lambda a: auths_per_node[a]))
    print(f"Highest Authority Score Node ID#{max_authority_node.GetId()}"
          f" with Score={hubs_per_node[max_authority_node.GetId()]}")

    exceed = False
    # CNM Community Detector
    cnm_community = snap.TCnComV()
    cnm_thread = threading.Thread(target=snap.CommunityCNM, args=(graph, cnm_community))
    cnm_start_time = time.time()

    try:
        cnm_thread.start()

        cnm_thread.join(10*60)

        cnm_stop_time = time.time()
    except MemoryError:
        cnm_stop_time = time.time()
        exceed = True

    cnm_community_exec_time = cnm_stop_time - cnm_start_time

    # GN Community Detector
    if cnm_community_exec_time < 10*60 and not exceed:
        gn_community = snap.TCnComV()
        gn_thread = threading.Thread(target=snap.CommunityGirvanNewman, args=(graph, gn_community))
        gn_start_time = time.time()

        try:
            gn_thread.start()

            gn_thread.join((10 * 60) - cnm_community_exec_time)

            gn_stop_time = time.time()
        except MemoryError:
            gn_stop_time = time.time()
            exceed = True

        gn_community_exec_time = gn_stop_time - gn_start_time
        exceed &= not gn_community_exec_time >= (10 * 60) - cnm_community_exec_time
    else:
        gn_community_exec_time = 0.00

    print(f"Execution Time for CNM Communities Detector is {round(cnm_community_exec_time, 2):.2f}")
    print(f"Execution Time for GN Communities Detector is {round(gn_community_exec_time, 2):.2f}")
    print(40*"#")

    # load graph in it's initial State
    f_in = snap.TFIn(output_filename)
    graph = snap.TUNGraph.Load(f_in)

    return graph, cnm_community_exec_time, gn_community_exec_time, exceed


if __name__ == "__main__":
    # Generate the Watts-Strogatz graph

    # Start with nodes = 50
    out_degree = random.randint(5, 20)
    graph, cnm_exec_time, gn_exec_time, exceed = manage_graphs(out_degree, 50)
    # nodes_num = 100
    # while not exceed:
    #     largest_graph = graph
    #     graph, cnm_exec_time, gn_exec_time, exceed = manage_graphs(nodes_num)
    #     if not exceed:
    #         nodes_num += 50

    # Find Top-30 nodes og PageRank
    page_rank_scores = snap.TIntFltH()
    snap.GetPageRank(graph, page_rank_scores)
    top_thirty_nodes_ids = sorted(page_rank_scores, key=lambda n: page_rank_scores[n])[:30]
    top_thirty_nodes_ids.sort()
    top_thirty_nodes_page_rank = [page_rank_scores[node_id] for node_id in top_thirty_nodes_ids]

    # Gets Hubs and Authorities of all the nodes
    hubs_per_node = snap.TIntFltH()
    auths_per_node = snap.TIntFltH()
    snap.GetHits(graph, hubs_per_node, auths_per_node)
    top_thirty_hubs = [hubs_per_node[node_id] for node_id in top_thirty_nodes_ids]
    top_thirty_authorities = [auths_per_node[node_id] for node_id in top_thirty_nodes_ids]
    #
    # Find betweenness
    nodes_betweenness = snap.TIntFltH()
    edge_betweenness = snap.TIntPrFltH()
    betweenness_centrality = snap.GetBetweennessCentr(graph, nodes_betweenness, edge_betweenness,  1.0)
    top_thirty_betweenness = [nodes_betweenness[node_id] for node_id in top_thirty_nodes_ids]

    # Find closeness
    top_thirty_closeness = [snap.GetClosenessCentr(graph, node_id) for node_id in top_thirty_nodes_ids]

    measures_df = pandas.DataFrame().from_dict({
        "PageRank": top_thirty_nodes_page_rank,
        "Hubs": top_thirty_hubs,
        "Authorities":  top_thirty_authorities,
        "Betweenness": top_thirty_betweenness,
        "Closeness": top_thirty_closeness,
        "NodeIds": top_thirty_nodes_ids
    })

    measures_df = measures_df.set_index("NodeIds")

    print(measures_df.head(5))

    plot_1 = measures_df.plot.bar(y=["Betweenness", "Closeness", "PageRank"])
    plt.show()

    plot_2 = measures_df.plot.barh(y=["PageRank", "Hubs", "Authorities"])
    plt.show()
