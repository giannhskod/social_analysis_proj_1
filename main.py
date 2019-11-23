from snap import *
import unittest


def has_euler_path(graph):
    vertices = set()
    ## FILL HERE
    return False, vertices


def has_euler_circuit(graph):
    ## FILL HERE
    return False


class TestEulerMethods(unittest.TestCase):

    def test_has_euler_path_but_not_circuit(self):
        graph = None
        # FILL HERE
        result, vertices = has_euler_path(graph)
        self.assertTrue(result)
        self.assertEqual(len(vertices), 2)

    def test_does_not_have_euler_path(self):
        graph = None
        # FILL HERE
        result, vertices = has_euler_path(graph)
        self.assertFalse(result)
        self.assertEqual(len(vertices), 0)

    def test_has_euler_circuit(self):
        graph = None
        # FILL HERE
        result = has_euler_circuit(graph)
        self.assertTrue(result)
        self.assertTrue(graph.GetNodes()>=1000)

    def test_does_not_have_euler_circuit(self):
        graph = None
        # FILL HERE
        result = has_euler_circuit(graph)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
