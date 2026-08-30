"""Regression tests for explicit owner-directed reuse, not renderer capability count."""
import json
import unittest
from unittest.mock import patch
from p19_scope import REUSED_TYPES, p18_references
from generate_p19b_gallery import specimen_sources, build_index, GALLERY
from verify_p19b import DocumentParser
from verify_p19b_review16 import verify


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
        for name in ('gantt', 'loop-flywheel', 'fishbone', 'dp-integration', 'bar-chart', 'CAP-V17', 'CAP-V18', 'CAP-V19', 'CAP-V20'):
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
        self.assertEqual(report['line_chart_html_changed'], 3)
        self.assertEqual(report['prior_html_artwork_preserved'], 87)


if __name__ == '__main__':
    unittest.main()
