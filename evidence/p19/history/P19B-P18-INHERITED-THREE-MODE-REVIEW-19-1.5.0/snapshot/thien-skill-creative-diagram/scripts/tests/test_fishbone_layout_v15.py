"""Focused D-086 tests for detailed Fishbone layout and rendering."""
import copy
import re
import unittest
import xml.etree.ElementTree as ET

from fishbone_layout_v15 import layout_fishbone, render_fishbone, fishbone_table
from fishbone_review06_fixture import fishbone_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual
from diagram_core import CoreError


class FishboneLayoutTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fishbone_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_detailed_material(self):
        layout = layout_fishbone(self.plan)
        self.assertEqual(len(layout['categories']), 5)
        self.assertEqual(sum(len(c['members']) for c in layout['categories']), 10)
        self.assertEqual(layout['effect']['label'], 'Hồ sơ xử lý trễ')
        self.assertEqual([c['side'] for c in layout['categories']], ['top','bottom','top','bottom','top'])

    def test_every_tick_meets_owning_bone_and_label_has_gap(self):
        layout = layout_fishbone(self.plan)
        for category in layout['categories']:
            sx,sy=category['start']; ex,ey=category['attach']
            for cause in category['members']:
                (tx,ty),(ux,uy)=cause['tick']
                cross=(ux-sx)*(ey-sy)-(uy-sy)*(ex-sx)
                self.assertAlmostEqual(cross, 0, places=5)
                self.assertEqual(ty,uy)
                self.assertGreater(tx-cause['label_position'][0], 0)
                estimated_left=cause['label_position'][0]-len(cause['label'])*7.8
                self.assertGreaterEqual(estimated_left, 30)

    def test_serialized_semantic_bindings(self):
        svg='<svg>'+render_fishbone(self.plan)+'</svg>'; root=ET.fromstring(svg)
        self.assertEqual(len(root.findall('.//*[@data-fishbone-category]')),5)
        self.assertEqual(len(root.findall('.//*[@data-fishbone-cause]')),10)
        self.assertEqual(len(root.findall('.//*[@data-fishbone-effect]')),1)
        self.assertEqual(len(root.findall('.//*[@data-fishbone-spine]')),1)
        self.assertNotIn('bridge',svg)

    def test_table_exposes_every_cause_and_effect(self):
        value=fishbone_table(self.plan)
        for item in self.fixture['nodes']+self.fixture['groups']:
            self.assertIn(item['id'],value)
        self.assertEqual(value.count('<tr>'),11)

    def test_three_modes_share_geometry(self):
        values=[]
        for mode in MODES:
            page=render_gallery_html(self.fixture,mode,'type-fishbone')
            svg=re.search(r'<svg .*?</svg>',page,re.S).group()
            values.append(svg.replace(mode,'MODE'))
            self.assertIn('viewBox="0 0 1750 900"',svg)
            self.assertIn('HỆ QUẢ QUAN SÁT',svg)
        self.assertEqual(len(set(values)),1)

    def test_orphan_cause_rejected(self):
        fixture=copy.deepcopy(self.fixture); fixture['groups'][0]['member_ids'].pop()
        with self.assertRaises((CoreError, ValueError)):
            layout_fishbone(adapt_visual(fixture))

    def test_relation_to_wrong_effect_rejected(self):
        fixture=copy.deepcopy(self.fixture); fixture['edges'][0]['target']=fixture['nodes'][0]['id']
        with self.assertRaises((CoreError, ValueError)):
            layout_fishbone(adapt_visual(fixture))

    def test_unsupported_annotations_rejected(self):
        plan=copy.deepcopy(self.plan)
        plan['semantic_projection']['annotations']=[{'id':'x','text':'x','target_ids':['effect-delay']}]
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            layout_fishbone(plan)


if __name__ == '__main__': unittest.main()
