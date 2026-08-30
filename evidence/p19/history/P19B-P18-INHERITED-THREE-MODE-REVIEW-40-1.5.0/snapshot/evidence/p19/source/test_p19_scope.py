"""Regression tests for explicit owner-directed reuse, not renderer capability count."""
import json
import unittest
from unittest.mock import patch
from p19_scope import REUSED_TYPES, p18_references
from generate_p19b_gallery import specimen_sources, build_index, GALLERY
from verify_p19b import DocumentParser
from verify_p19b_review40 import verify


class ReuseScopeTests(unittest.TestCase):
    def test_exact_owner_list(self):
        self.assertEqual(len(REUSED_TYPES), 14)
        self.assertIn('sankey', REUSED_TYPES)
        self.assertNotIn('dp-integration', REUSED_TYPES)

    def test_p18_exact_binding(self):
        records = p18_references()
        self.assertEqual({r['identity'] for r in records}, REUSED_TYPES)
        self.assertTrue(all(r['mode'] == 'neutral-light' for r in records))

    def test_p18_manifest_mutation_rejected(self):
        with patch('p19_scope.P18_MANIFEST_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'manifest drift'):
                p18_references()

    def test_missing_owner_identity_rejected(self):
        with patch('p19_scope.REUSED_TYPES', REUSED_TYPES - {'sankey'}):
            with self.assertRaisesRegex(ValueError, 'owner reuse list'.capitalize()):
                p18_references()

    def test_generator_excludes_all_duplicates(self):
        sources = specimen_sources()
        self.assertEqual(len(sources), 31)
        self.assertFalse({identity for _, identity, _ in sources} & REUSED_TYPES)
        self.assertEqual(sum(fixture_id.startswith('type-') and fixture_id not in {'type-layers', 'type-scatter-chart'} for fixture_id, _, _ in sources), 25)
        self.assertIn(('type-layers', 'layers'), {(fixture_id, identity) for fixture_id, identity, _ in sources})
        self.assertIn(('type-scatter-chart', 'scatter-chart'), {(fixture_id, identity) for fixture_id, identity, _ in sources})

    def test_capabilities_and_recent_fixes_retained(self):
        sources = {identity: ir for _, identity, ir in specimen_sources()}
        for name in ('gantt', 'loop-flywheel', 'fishbone', 'dp-integration', 'bar-chart', 'line-chart', 'medallion', 'polar-chart', 'CAP-V17', 'CAP-V18', 'CAP-V19', 'bubble'):
            self.assertIn(name, sources)
        self.assertEqual(sources['bubble']['diagram']['type'], 'scatter-plot')
        self.assertEqual(sources['bubble']['diagram']['variant_ids'], ['CAP-V20'])

    def test_index_has_no_duplicate_source_links(self):
        records = json.loads((GALLERY / 'P-19B-INVENTORY.json').read_bytes())['records']
        parser = DocumentParser()
        parser.feed(build_index(records))
        self.assertEqual(parser.tags['article'], 45)
        self.assertEqual(len(parser.hrefs), 107)
        self.assertEqual(len(set(parser.hrefs)), 107)
        self.assertEqual(sum(path.startswith('../../p18/') for path in parser.hrefs), 14)

    def test_exact_preservation_and_recoverable_withdrawal(self):
        report = verify()
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['global_policy_declarations'], 93)
        self.assertEqual(report['target_html_count'], 3)
        self.assertEqual(report['non_target_html_preserved_after_candidate_normalization'], 90)
        self.assertEqual(report['non_target_previews_byte_identical'], 30)
        self.assertEqual(report['bubble_measurement']['bubbles'], 7)
        self.assertEqual(report['bubble_measurement']['focal'], 1)
        self.assertEqual(report['bubble_measurement']['axes'], 2)
        self.assertEqual(report['display_identity'], 'bubble')
        self.assertEqual(report['internal_capability_id'], 'CAP-V20')
        self.assertEqual(report['canonical_parent'], 'scatter-plot')
        self.assertEqual(report['three_mode_geometry'], 'PASS')


if __name__ == '__main__':
    unittest.main()
