#!/usr/bin/python

import sys
import getopt
import snap
import random
import time
import threading
import pandas
import matplotlib.pyplot as plt


def manage_graphs(out_degree, nodes, max_minutes):
    rnd = snap.TRnd(1, 0)
    graph = snap.GenSmallWorld(nodes, out_degree, 0.7, rnd)
    print(40 * "#")
    print(f"Starting Graph for #{nodes} Nodes.")

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
        cnm_thread.join(max_minutes)

    except MemoryError:
        exceed = True

    finally:
        cnm_stop_time = time.time()
        cnm_community_exec_time = cnm_stop_time - cnm_start_time
        exceed |= max_minutes <= cnm_community_exec_time

    # GN Community Detector
    if max_minutes > cnm_community_exec_time and not exceed:
        gn_community = snap.TCnComV()
        gn_thread = threading.Thread(target=snap.CommunityGirvanNewman, args=(graph, gn_community))
        gn_start_time = time.time()

        try:
            gn_thread.start()
            gn_thread.join(max_minutes - cnm_community_exec_time)

        except MemoryError:
            exceed = True

        finally:
            gn_stop_time = time.time()
            gn_community_exec_time = gn_stop_time - gn_start_time
            exceed |= gn_community_exec_time >= max_minutes - cnm_community_exec_time
    else:
        gn_community_exec_time = 0.00
    if not exceed:
        print(f"Execution Time for CNM Communities Detector is {round(cnm_community_exec_time, 4):.4f}")
        print(f"Execution Time for GN Communities Detector is {round(gn_community_exec_time, 4):.4f}")
    else:
        print(f"Graph with Nodes#{nodes_num} exceeded the valid calculation limits.")
    print(40*"#")

    # load graph in it's initial State
    f_in = snap.TFIn(output_filename)
    graph = snap.TUNGraph.Load(f_in)

    return graph, cnm_community_exec_time, gn_community_exec_time, exceed


if __name__ == "__main__":
    # Set up default values
    if sys.argv[1:] in ("python", "python3"):
        myopts, args = getopt.getopt(sys.argv[2:], "n:m:r:i:v:h")
    else:
        myopts, args = getopt.getopt(sys.argv[1:], "n:m:r:i:v:h")

    nodes = 50
    max_iters = 50
    rate = 50
    verbose = False
    max_minutes = 10 * 60

    for o, a in myopts:
        print(o)
        num_a = int(a)
        if o in '-n':
            nodes = num_a
        elif o == '-i':
            if int(num_a) < 1 or int(num_a) > 100:
                print("Invalid value for parameter 'i'. Values should be 1 <= i <= 100.")
                sys.exit(2)
            max_iters = int(num_a)
        elif o == "-r":
            if num_a < 10 or num_a > 100:
                print("Invalid value for parameter 'r'. Values should be 10 <= r <= 1000.")
                sys.exit(2)
            rate = num_a
        elif o == "-m":
            max_minutes = num_a
        elif o == "-v":
            verbose = True
        else:
            print(f"Usage: {sys.argv[0]}"
                  f"\n\t -n initial number of the nodes(default: 50) "
                  f"\n\t -i max number of iterations (1 <= i <= 100, default: 50)"
                  f"\n\t -r The rate of the nodes that will be added per iteration (10 <= i <= 1000, default: 50)"
                  f"\n\t -m The maximum seconds of the centralities calculations (default: 600s - 10min)"
                  f"\n\t -v If given then show the graphs despite the saving in as images."
                  f"(Needs to be in environment that the graphs can be loaded)")
            sys.exit(1)
    print(f"Nodes: {nodes}, MaxIterations: {max_iters}, Rate: {rate}, MaxMinutes:{max_minutes}")

    out_degree = random.randint(5, 20)
    exceed = False
    largest_graph = None
    graphs_execution_info = []
    for nodes_num in range(nodes, (max_iters*rate) + nodes, rate):
        graph, cnm_exec_time, gn_exec_time, exceed = manage_graphs(out_degree, nodes_num, max_minutes)
        if not exceed:
            graphs_execution_info.append({
                "Nodes": nodes_num,
                "OutDegree": out_degree,
                "CNMExecutionTIme": round(cnm_exec_time, 4),
                "GNExecutionTime": round(gn_exec_time, 4)
            })
            out_degree = random.randint(5, 20)
            largest_graph = graph
        else:
            break

    if largest_graph:
        reports_df = pandas.DataFrame(graphs_execution_info)
        print(reports_df)
        print("The selected graph for the Centrality Metrics is:",
              "\n",
              reports_df.sort_values(by=["GNExecutionTime"], ascending=False).head(1))

        # Find Top-30 nodes of PageRank
        page_rank_scores = snap.TIntFltH()
        snap.GetPageRank(largest_graph, page_rank_scores)
        top_thirty_nodes_ids = sorted(page_rank_scores, key=lambda n: page_rank_scores[n], reverse=True)[:30]
        top_thirty_nodes_ids.sort()
        top_thirty_nodes_page_rank = [page_rank_scores[node_id] for node_id in top_thirty_nodes_ids]

        # Gets Hubs and Authorities of all the nodes
        hubs_per_node = snap.TIntFltH()
        auths_per_node = snap.TIntFltH()
        snap.GetHits(largest_graph, hubs_per_node, auths_per_node)
        top_thirty_hubs = [hubs_per_node[node_id] for node_id in top_thirty_nodes_ids]
        top_thirty_authorities = [auths_per_node[node_id] for node_id in top_thirty_nodes_ids]
        #
        # Find betweenness
        nodes_betweenness = snap.TIntFltH()
        edge_betweenness = snap.TIntPrFltH()
        betweenness_centrality = snap.GetBetweennessCentr(largest_graph, nodes_betweenness, edge_betweenness,  1.0)
        top_thirty_betweenness = [nodes_betweenness[node_id] for node_id in top_thirty_nodes_ids]

        # Find closeness
        top_thirty_closeness = [snap.GetClosenessCentr(largest_graph, node_id) for node_id in top_thirty_nodes_ids]

        measures_df = pandas.DataFrame().from_dict({
            "PageRank": top_thirty_nodes_page_rank,
            "Hubs": top_thirty_hubs,
            "Authorities":  top_thirty_authorities,
            "Betweenness": top_thirty_betweenness,
            "Closeness": top_thirty_closeness,
            "NodeIds": top_thirty_nodes_ids
        })

        measures_df = measures_df.set_index("NodeIds").sort_values(by=["PageRank"], ascending=False)
        # Standardize Betweenness centrality in order to be easier visualized with Closeness Node Centrality
        # based on a type found in https://www.sciencedirect.com/topics/psychology/degree-centrality.
        # The multiplication with 100 after the standarization helps for the visualization of
        # the Betweenness Centrality & Closeness Centrality

        graph_nodes = largest_graph.GetNodes()
        measures_df["BetweennessStd"] = measures_df["Betweenness"] / (graph_nodes ** 2 - 3 * graph_nodes + 2) * 100
        print(measures_df)

        plot_1 = measures_df.plot.line(y=["BetweennessStd", "Closeness"], x="PageRank")
        plt.savefig("plots/group_a.png")
        if verbose:
            plt.show()

        # Uncomment if you want to add it as a plot
        # plot_2 = measures_df.plot.line(y=["Betweenness", "Closeness"], x="PageRank")
        # plt.savefig("plots/group_a_2.png")
        # if verbose:
        #   plt.show()

        plot_3 = measures_df.plot.line(y=["Authorities", "Hubs"], x="PageRank")
        plt.savefig("plots/group_b.png")
        if verbose:
            plt.show()
