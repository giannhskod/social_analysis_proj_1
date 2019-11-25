import snap
import unittest


def is_uniquely_connected(graph):

    def is_unique(components):
        return len(list(filter(lambda comp: comp.Len() > 1, components))) == 1

    # First identify if there are strongly connected components in the graph
    s_components = snap.TCnComV()
    snap.GetSccs(graph, s_components)
    unique = is_unique(s_components)

    # if there is unique strongly connected component then we don't need to search
    # for the weakly because the graph is connected, otherwise implement the same search
    # on the weakly components.
    if not is_unique:
        w_components = snap.TCnComV()
        snap.GetWccs(graph, w_components)
        unique = is_unique(w_components)

    return unique


def has_euler_path(graph):
    odd_vertices = set()
    if is_uniquely_connected(graph):
        odd_vertices = list(filter(lambda node: node.GetDeg() % 2 == 1, graph.Nodes()))

    return len(odd_vertices) == 2, odd_vertices


def has_euler_circuit(graph):
    contains_euler_path, odd_vertices = has_euler_path(graph)
    return len(odd_vertices) == 0


class TestEulerMethods(unittest.TestCase):
    def setUp(self):
        super(TestEulerMethods, self).setUp()
        self.graph = snap.TNGraph.New()
        # set up 5 nodes
        for i in range(1, 6):
            self.graph.AddNode(i)

        # set up the graph in order to contain an euler path
        self.graph.AddEdge(2, 1)
        self.graph.AddEdge(1, 3)
        self.graph.AddEdge(3, 2)
        self.graph.AddEdge(1, 4)
        self.graph.AddEdge(4, 5)

    def test_has_euler_path_but_not_circuit(self):
        result, vertices = has_euler_path(self.graph)
        self.assertTrue(result)
        self.assertEqual(len(vertices), 2)

    def test_does_not_have_euler_path(self):
        # reformat it to an euler circuit
        self.graph.AddEdge(5, 1)
        result, vertices = has_euler_path(self.graph)
        self.assertFalse(result)
        self.assertEqual(len(vertices), 0)

    def test_has_euler_circuit(self):
        graph = snap.GenCircle(snap.PNGraph, 10000, 10)
        # FILL HERE
        result = has_euler_circuit(graph)
        self.assertTrue(result)
        self.assertTrue(graph.GetNodes() >= 1000)

    def test_does_not_have_euler_circuit(self):
        self.graph.AddNode(6)
        self.graph.AddNode(7)
        self.graph.AddEdge(5, 6)
        self.graph.AddEdge(6, 7)
        result = has_euler_circuit(self.graph)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
