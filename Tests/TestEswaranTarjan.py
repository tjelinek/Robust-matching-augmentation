from nose.tools import assert_set_equal, assert_raises, assert_false, assert_true
import networkx as nx
from Algo.EswaranTarjan import eswaran_tarjan
from Algo.Util import get_sources_sinks_isolated


def edgesForAugment(G) -> int:
    """ Bounds the number of arcs needed to make G strongly connected

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    Returns
    -------
    ints
        A lower and an upper bound on the number of arcs needed to add to G
        to make G strongly connected
    Notes
    -----
    For upper and lower bound on augmenting arcs see
    Theorem 2 in Eswaran and Tarjan's algorithm https://epubs.siam.org/doi/abs/10.1137/0205044
    """
    G = nx.algorithms.condensation(G)

    sourcesSinksIsolated = get_sources_sinks_isolated(G)
    s: int = len(sourcesSinksIsolated['sources'])
    t: int = len(sourcesSinksIsolated['sinks'])
    q: int = len(sourcesSinksIsolated['isolated'])

    if s + t + q > 1:
        return max(s, t) + q
    else:  # obviously s > 0 iff t > 0, thus s == t == 0
        if q <= 1:
            return 0
        else:
            return q


def is_correctly_augmented(G: nx.DiGraph()) -> bool:
    """Returns if eswaran_tarjan augments G and the augmenting set is minimal

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    Returns
    -------
    correct : bool
       True if eswaran_tarjan augments eswaran_tarjan and is a minimal such set
       according to the lower bound by Eswaran and Tarjan

    Notes
    -----
    For upper and lower bound see
    Theorem 2 in Eswaran and Tarjan's algorithm https://epubs.siam.org/doi/abs/10.1137/0205044
    """

    G = G.copy()
    A = eswaran_tarjan(G)
    n = edgesForAugment(G)
    G.add_edges_from(A)
    return nx.algorithms.is_strongly_connected(G) and (len(A) == n)


class TestEswaranTarjan:

    def test_directed(self):
        # Testing on directed graph, no exception expected
        exception = False
        try:
            eswaran_tarjan(nx.DiGraph())
        except:
            exception = True
        assert_false(exception, "eswaran_tarjan should be implemented for networkx.DiGraph")

    def test_wrong_graph_type(self):
        # Testing on unsupported graph types, exception networkx.NetworkXNotImplemented expected
        assert_raises(nx.NetworkXNotImplemented, eswaran_tarjan, nx.Graph())
        assert_raises(nx.NetworkXNotImplemented, eswaran_tarjan, nx.MultiGraph())
        assert_raises(nx.NetworkXNotImplemented, eswaran_tarjan, nx.MultiDiGraph())

    def test_non_condensation(self):
        # Testing non condensed graph with is_condensation=True, exception networkx.HasACycle expected
        G: nx.DiGraph = nx.cycle_graph(range(1, 4), nx.DiGraph())
        assert_raises(nx.HasACycle, eswaran_tarjan, G, True)
        G.add_node(0)
        assert_raises(nx.HasACycle, eswaran_tarjan, G, True)
        G.clear()
        G.add_edges_from({(0, 1), (1, 0)})
        assert_raises(nx.HasACycle, eswaran_tarjan, G, True)

    def test_empty(self):
        # Testing on empty digraph, empty set expected.
        assert_set_equal(eswaran_tarjan(nx.DiGraph()), set(), "Expected empty set")

    def test_trivial(self):
        # Testing digraph with one vertex, empty set expected.
        assert_set_equal(eswaran_tarjan(nx.complete_graph(1, nx.DiGraph())), set(), "Expected empty set")

    def test_directed_path_joins_ends(self):
        # Testing if called on directed path,
        # expected
        for i in range(2, 11):
            assert_set_equal(eswaran_tarjan(nx.path_graph(i, nx.DiGraph())), {(i - 1, 0)})

    def test_tree(self):
        # Testing correct behaviour on trees, expecting to connect all leaves and one
        # leaf with root.
        for i in range(0, 5):
            G: nx.DiGraph = nx.generators.classic.balanced_tree(2, i, create_using=nx.DiGraph)
            assert_true(is_correctly_augmented(G))
            G = G.reverse()
            assert_true(is_correctly_augmented(G))

    def test_isolated(self):
        # Tests correct behaviour on graph consisting of isolated trivial vertices
        n = 0
        for i in range(5):
            G: nx.DiGraph = nx.DiGraph()
            G.add_nodes_from({j for j in range(2**i + n)})
            n = n + 1
            assert_true(is_correctly_augmented(G))

    def test_several_disjoint_strongly_connected_components(self):
        # Tests a correct behaviour of connecting isolated vertices when
        # there are more mutually disjoint strongly connected components,
        # this tests correct choice of representative and connecting only
        # isolated vertices.
        n = 0
        for i in range(0, 5):
            G: nx.DiGraph = nx.DiGraph()
            for j in range(2 ** i + n):
                C = nx.cycle_graph(i+2, create_using=nx.DiGraph())
                G = nx.disjoint_union(G, C)
            n = n + 1
            assert_true(is_correctly_augmented(G))

    """
    --------------------
    The following tests test the correct behaviour on marginal conditions
    in regard to s, t, p, q as defined in eswaran_tarjan
    --------------------
    """
    def test_A_critical_q_null_p_eq_st(self):
        # Tests correct behaviour if q = 0 and p = s = t
        G = nx.DiGraph()
        for i in range(0, 5):
            G.add_edge(2*i, 2*i+1)
        assert_true(is_correctly_augmented(G))

    def test_A_critical_q_null_p_lower_s_eq_t(self):
        # Tests correct behaviour if q = 0 and p < s = t
        # To test this, we test in on a "crossroad" graph G
        # E(G) = {(a, m), (m, b), (c, m), (d, m)}
        # We test both if p + 1 = s = t and if the difference if bigger
        # and also if the underlying undirected graph is not connected
        G = nx.DiGraph()
        G.add_edges_from({('a', 'm'), ('m', 'b'), ('c', 'm'), ('d', 'm')})
        assert_true(is_correctly_augmented(G))

        for i in range(0, 5):
            G.add_edge(2 * i, 2 * i + 1)
        assert_true(is_correctly_augmented(G))

    def test_A_critical_q_null_p_lower_s_lower_t(self):
        pass

    def test_A_critical_q_notnull_stp_null(self):
        pass

    def test_A_critical_q_notnull_p_eq_st(self):
        pass

    def test_A_critical_q_notnull_p_lower_s_eq_t(self):
        pass

    def test_A_critical_q_notnull_p_lower_s_lower_t(self):
        pass
    """
    --------------------
    End of testing marginal conditions regarding s, t, p, q
    --------------------
    """


    def test_random_graphs(self):
        # Tests behaviour on (small) random graphs of different density.
        # Used to catch graph instances not caught in previous tests,
        # for which special tests should be created afterwards.
        for i in range(1, 100):
            p = 0.199
            while p < 1:
                G = nx.fast_gnp_random_graph(i, p, directed=True)
                assert_true(is_correctly_augmented(G))
                p += 0.2
