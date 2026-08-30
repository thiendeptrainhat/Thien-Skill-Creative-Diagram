"""Regression tests for explicit owner-directed reuse, not renderer capability count."""
import json
import unittest
from unittest.mock import patch
from p19_scope import REUSED_TYPES, p18_references
from generate_p19b_gallery import specimen_sources, build_index, GALLERY
from verify_p19b import DocumentParser
from verify_p19b_review31 import verify


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
        self.assertEqual(len(sources), 30)
        self.assertFalse({identity for _, identity, _ in sources} & REUSED_TYPES)
        self.assertEqual(sum(fixture_id.startswith('type-') and fixture_id != 'type-layers' for fixture_id, _, _ in sources), 25)
        self.assertIn(('type-layers', 'layers'), {(fixture_id, identity) for fixture_id, identity, _ in sources})

    def test_capabilities_and_recent_fixes_retained(self):
        sources = {identity: ir for _, identity, ir in specimen_sources()}
        for name in ('gantt', 'loop-flywheel', 'fishbone', 'dp-integration', 'bar-chart', 'line-chart', 'medallion', 'polar-chart', 'CAP-V17', 'CAP-V18', 'CAP-V19', 'CAP-V20'):
            self.assertIn(name, sources)
        self.assertEqual(sources['CAP-V20']['diagram']['type'], 'scatter-plot')

    def test_index_has_no_duplicate_source_links(self):
        records = json.loads((GALLERY / 'P-19B-INVENTORY.json').read_bytes())['records']
        parser = DocumentParser()
        parser.feed(build_index(records))
        self.assertEqual(parser.tags['article'], 44)
        self.assertEqual(len(parser.hrefs), 104)
        self.assertEqual(len(set(parser.hrefs)), 104)
        self.assertEqual(sum(path.startswith('../../p18/') for path in parser.hrefs), 14)

    def test_exact_preservation_and_recoverable_withdrawal(self):
        report = verify()
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['global_policy_declarations'], 90)
        self.assertEqual(report['non_target_html_preserved_after_candidate_normalization'], 87)
        self.assertEqual(report['non_target_previews_byte_identical'], 29)
        self.assertEqual(report['sequence_measurement']['participants'], 4)
        self.assertEqual(report['sequence_measurement']['lifelines'], 4)
        self.assertEqual(report['sequence_measurement']['activations'], 2)
        self.assertEqual(report['sequence_measurement']['messages'], 6)
        self.assertEqual(report['sequence_measurement']['straight_messages'], 5)
        self.assertEqual(report['sequence_measurement']['self_messages'], 1)
        self.assertEqual(report['sequence_measurement']['centered_card_lifelines'], 4)


if __name__ == '__main__':
    unittest.main()
