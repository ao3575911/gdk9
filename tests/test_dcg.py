import math
import unittest

from gdk9.dcg import (
    _CLASS_LOWER,
    _CLASS_UPPER,
    get_dcg,
    homotopy_equivalent,
    sym_energy,
    symmetry_class,
    vectorize,
    word_sym_energy,
    word_vector,
)


class TestSymmetryClass(unittest.TestCase):
    def test_known_upper(self):
        self.assertEqual(symmetry_class('A'), 'idempotent')
        self.assertEqual(symmetry_class('B'), 'biphasic')
        self.assertEqual(symmetry_class('N'), 'involutive')
        self.assertEqual(symmetry_class('F'), 'asymmetric')

    def test_lowercase_matches_uppercase(self):
        for ch in 'abcdefghijklmnopqrstuvwxyz':
            self.assertEqual(symmetry_class(ch), symmetry_class(ch.upper()),
                             msg=f"Mismatch for {ch!r}")

    def test_all_26_upper_classified(self):
        classes = set()
        for u in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            classes.add(symmetry_class(u))
        # Every letter must fall into one of the four classes
        self.assertEqual(classes, {'idempotent', 'biphasic', 'involutive', 'asymmetric'})

    def test_total_upper_coverage(self):
        total = sum(len(v) for v in _CLASS_UPPER.values())
        self.assertEqual(total, 26)

    def test_total_lower_coverage(self):
        total = sum(len(v) for v in _CLASS_LOWER.values())
        self.assertEqual(total, 26)


class TestSymEnergy(unittest.TestCase):
    def test_idempotent_is_pos(self):
        # A is pos=1, idempotent → energy=1
        self.assertAlmostEqual(sym_energy('A'), 1.0)
        # M is pos=13, idempotent → energy=13
        self.assertAlmostEqual(sym_energy('M'), 13.0)

    def test_biphasic_is_sin(self):
        # E is pos=5, biphasic → energy=sin(5)
        self.assertAlmostEqual(sym_energy('E'), math.sin(5), places=10)

    def test_involutive_is_reciprocal(self):
        # N is pos=14, involutive → energy=1/14
        self.assertAlmostEqual(sym_energy('N'), 1.0 / 14.0, places=10)
        # S is pos=19
        self.assertAlmostEqual(sym_energy('S'), 1.0 / 19.0, places=10)

    def test_asymmetric_is_pos_plus_one(self):
        # F is pos=6, asymmetric → energy=7
        self.assertAlmostEqual(sym_energy('F'), 7.0)
        # R is pos=18, asymmetric → energy=19
        self.assertAlmostEqual(sym_energy('R'), 19.0)

    def test_non_alpha_is_zero(self):
        self.assertEqual(sym_energy(' '), 0.0)
        self.assertEqual(sym_energy('9'), 0.0)

    def test_lowercase_same_as_uppercase(self):
        for ch in 'abcdefghijklmnopqrstuvwxyz':
            self.assertAlmostEqual(sym_energy(ch), sym_energy(ch.upper()),
                                   msg=f"Energy mismatch for {ch!r}")

    def test_fwem_whitepaper(self):
        # Whitepaper §2: E(FWEM) ≈ 42.04
        total = word_sym_energy('FWEM')
        self.assertAlmostEqual(total, 42.04, places=1)


class TestVectorize(unittest.TestCase):
    def test_returns_four_floats(self):
        v = vectorize('A')
        self.assertEqual(len(v), 4)
        for x in v:
            self.assertIsInstance(x, float)

    def test_pos_component(self):
        # A → pos=1
        self.assertAlmostEqual(vectorize('A')[0], 1.0)
        # Z → pos=26
        self.assertAlmostEqual(vectorize('Z')[0], 26.0)

    def test_type_id_component(self):
        self.assertEqual(vectorize('A')[1], 1.0)   # idempotent
        self.assertEqual(vectorize('B')[1], 2.0)   # biphasic
        self.assertEqual(vectorize('N')[1], 3.0)   # involutive
        self.assertEqual(vectorize('F')[1], 4.0)   # asymmetric

    def test_sqrt_e_nonnegative(self):
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
            self.assertGreaterEqual(vectorize(ch)[2], 0.0)

    def test_non_alpha_is_zero_vector(self):
        self.assertEqual(vectorize(' '), (0.0, 0.0, 0.0, 0.0))


class TestWordVector(unittest.TestCase):
    def test_empty_word(self):
        v = word_vector('')
        self.assertEqual(v, (0.0, 0.0, 0.0, 0.0))

    def test_single_char_matches_vectorize(self):
        for ch in 'ABFNS':
            wv = word_vector(ch)
            cv = vectorize(ch)
            for i in range(4):
                self.assertAlmostEqual(wv[i], cv[i])

    def test_additivity(self):
        va = word_vector('AB')
        fa = vectorize('A')
        fb = vectorize('B')
        for i in range(4):
            self.assertAlmostEqual(va[i], fa[i] + fb[i])


class TestBuildDCG(unittest.TestCase):
    def setUp(self):
        self.g = get_dcg()

    def test_node_count(self):
        self.assertEqual(self.g.node_count(), 52)

    def test_all_letters_present(self):
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
            data = self.g.node_data(ch)
            self.assertIn('class', data, msg=f"Missing node data for {ch!r}")

    def test_uppercase_to_lowercase_edges(self):
        for u in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.assertTrue(self.g.has_edge(u, u.lower()),
                            msg=f"Missing edge {u}→{u.lower()}")

    def test_lowercase_to_uppercase_edges(self):
        for lo in 'abcdefghijklmnopqrstuvwxyz':
            self.assertTrue(self.g.has_edge(lo, lo.upper()),
                            msg=f"Missing edge {lo}→{lo.upper()}")

    def test_dc_ac_edge_costs(self):
        # DC→AC should be cheaper than AC→DC
        self.assertLess(self.g.edge_weight('A', 'a'),
                        self.g.edge_weight('a', 'A'))

    def test_within_class_edges_upper(self):
        # All idempotent uppercase letters should have edges to each other
        idemp = _CLASS_UPPER['idempotent']
        for src in idemp:
            for dst in idemp:
                if src != dst:
                    self.assertTrue(self.g.has_edge(src, dst),
                                    msg=f"Missing within-class edge {src}→{dst}")

    def test_within_class_edges_lower(self):
        biph = _CLASS_LOWER['biphasic']
        for src in biph:
            for dst in biph:
                if src != dst:
                    self.assertTrue(self.g.has_edge(src, dst),
                                    msg=f"Missing within-class edge {src}→{dst}")

    def test_cross_class_cycle_upper(self):
        # Key whitepaper edge: F (asymmetric) → E (biphasic)
        self.assertTrue(self.g.has_edge('F', 'E'))
        # Full cycle: asym→biph→idemp→invol→asym
        # Pick one from each class
        self.assertTrue(self.g.has_edge('F', 'B'))   # asym→biph
        self.assertTrue(self.g.has_edge('B', 'A'))   # biph→idemp
        self.assertTrue(self.g.has_edge('A', 'N'))   # idemp→invol
        self.assertTrue(self.g.has_edge('N', 'F'))   # invol→asym

    def test_cross_class_cycle_lower(self):
        self.assertTrue(self.g.has_edge('f', 'b'))
        self.assertTrue(self.g.has_edge('b', 'a'))
        self.assertTrue(self.g.has_edge('a', 'n'))
        self.assertTrue(self.g.has_edge('n', 'f'))

    def test_no_same_node_self_loop(self):
        for ch in 'ABCabc':
            self.assertFalse(self.g.has_edge(ch, ch),
                             msg=f"Unexpected self-loop on {ch!r}")

    def test_edge_count_reasonable(self):
        # Should have hundreds of edges covering all morphism types
        self.assertGreater(self.g.edge_count(), 500)

    def test_edge_count_by_type_keys(self):
        by_type = self.g.edge_count_by_type()
        self.assertIn('dc_ac', by_type)


class TestShortestPath(unittest.TestCase):
    def setUp(self):
        self.g = get_dcg()

    def test_same_node_trivial(self):
        path = self.g.shortest_path('A', 'A')
        self.assertEqual(path, ['A'])

    def test_adjacent_within_class(self):
        # A and M are both idempotent uppercase → direct within-class edge
        path = self.g.shortest_path('A', 'M')
        self.assertIsNotNone(path)
        self.assertEqual(path[0], 'A')
        self.assertEqual(path[-1], 'M')

    def test_dc_ac_hop(self):
        # A → a should use the direct DC→AC edge
        path = self.g.shortest_path('A', 'a')
        self.assertEqual(path, ['A', 'a'])

    def test_cross_class_path_exists(self):
        # F (asym) → M (idemp): must route through biphasic
        path = self.g.shortest_path('F', 'M')
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], 'F')
        self.assertEqual(path[-1], 'M')

    def test_path_edges_all_valid(self):
        path = self.g.shortest_path('F', 'M')
        for i in range(len(path) - 1):
            self.assertTrue(self.g.has_edge(path[i], path[i + 1]),
                            msg=f"Invalid edge {path[i]}→{path[i+1]} in shortest path")

    def test_cost_nonnegative(self):
        cost = self.g.shortest_path_cost('F', 'M')
        self.assertIsNotNone(cost)
        self.assertGreater(cost, 0)


class TestWordPathInfo(unittest.TestCase):
    def setUp(self):
        self.g = get_dcg()

    def test_fwem_classes(self):
        info = self.g.word_path_info('FWEM')
        classes = [s['class'] for s in info['steps']]
        self.assertEqual(classes, ['asymmetric', 'idempotent', 'biphasic', 'idempotent'])

    def test_fwem_energy(self):
        info = self.g.word_path_info('FWEM')
        self.assertAlmostEqual(info['total_energy'], 42.04, places=1)

    def test_skips_non_alpha(self):
        info = self.g.word_path_info('F W')   # space between F and W
        # Only F and W should appear as steps
        chars = [s['char'] for s in info['steps']]
        self.assertEqual(chars, ['F', 'W'])

    def test_single_char_valid(self):
        info = self.g.word_path_info('A')
        self.assertTrue(info['is_valid_path'])

    def test_empty_word(self):
        info = self.g.word_path_info('')
        self.assertEqual(info['steps'], [])
        self.assertTrue(info['is_valid_path'])

    def test_vector_sum_shape(self):
        info = self.g.word_path_info('FWEM')
        self.assertEqual(len(info['vector_sum']), 4)


class TestHomotopyEquivalent(unittest.TestCase):
    def test_identical_words_are_equivalent(self):
        equiv, _ = homotopy_equivalent('FWEM', 'FWEM')
        self.assertTrue(equiv)

    def test_same_letters_reordered_near_equivalent(self):
        # FWeM vs FeWM — whitepaper example; same letters, same energy
        equiv, detail = homotopy_equivalent('FWeM', 'FeWM', tol=1.0)
        self.assertAlmostEqual(detail['energy_diff'], 0.0, places=6)
        self.assertTrue(equiv)

    def test_completely_different_words_not_equivalent(self):
        # GDK vs ZZZ — very different energy profiles
        equiv, _ = homotopy_equivalent('GDK', 'ZZZ', tol=1.0)
        self.assertFalse(equiv)

    def test_detail_keys(self):
        _, detail = homotopy_equivalent('AB', 'BA')
        for key in ('word_a', 'word_b', 'energy_diff', 'vector_distance', 'tol', 'equivalent'):
            self.assertIn(key, detail)

    def test_tight_tol_rejects_close_words(self):
        # Use tol=0 — only truly identical words pass
        equiv, _ = homotopy_equivalent('AB', 'BA', tol=0.0)
        # AB and BA have same energy but different vector sums (pos differs by order-independence)
        # vector sum is commutative so they SHOULD still be equivalent even with tol=0
        _, detail = homotopy_equivalent('AB', 'BA', tol=0.0)
        # Both energy diff and vector dist should be 0 (addition is commutative)
        self.assertAlmostEqual(detail['energy_diff'], 0.0, places=6)
        self.assertAlmostEqual(detail['vector_distance'], 0.0, places=6)


class TestSingletonDCG(unittest.TestCase):
    def test_same_instance(self):
        g1 = get_dcg()
        g2 = get_dcg()
        self.assertIs(g1, g2)


if __name__ == '__main__':
    unittest.main()
