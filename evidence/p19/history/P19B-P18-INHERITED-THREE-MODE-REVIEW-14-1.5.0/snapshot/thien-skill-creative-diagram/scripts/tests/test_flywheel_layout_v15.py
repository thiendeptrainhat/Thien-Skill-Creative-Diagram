"""Independent cycle/shared-state/layout regressions; no QA fixture dependency."""
import copy
import math
import re
import unittest
import xml.etree.ElementTree as ET

from semantic_fixtures import finalize, n, e, annotation, fixtures
from visual_adapters_v15 import adapt_visual
from gallery_renderer_v15 import MODES, render_gallery_html
from flywheel_layout_v15 import layout_flywheel, render_flywheel, flywheel_table, validate_flywheel_layout, _point

def sample(count=6, hub=True):
    nodes=[n(f's{i}','station',f'Bước {i}',state='decision' if i==2 else 'normal') for i in range(count)]
    edges=[e(f'c{i}',f's{i}',f's{(i+1)%count}','cycle') for i in range(count)]
    notes=[annotation(f'd{i}',f'Nội dung bước {i}',[f's{i}']) for i in range(count)]
    if hub:
        nodes.append(n('memory','shared-state','Tri thức chung'))
        notes.extend(annotation(f'a{i}','Góp vào Tri thức chung: kết quả',[f's{i}','memory']) for i in range(count))
    return finalize('loop-flywheel',nodes=nodes,edges=edges,annotations=notes)

class FlywheelTests(unittest.TestCase):
    def plan(self,count=6,hub=True): return adapt_visual(sample(count,hub))

    def test_six_stations_shared_state_and_spokes(self):
        value=layout_flywheel(self.plan())
        self.assertEqual(len(value['order']),6)
        self.assertNotIn('memory',value['order'])
        self.assertEqual(len(value['arcs']),6)
        self.assertEqual(len(value['spokes']),6)
        self.assertEqual({s['target'] for s in value['spokes']},{'memory'})

    def test_order_follows_edges_not_node_array(self):
        p=self.plan(); p['semantic_projection']['nodes'][1:6]=reversed(p['semantic_projection']['nodes'][1:6])
        self.assertEqual(layout_flywheel(p)['order'],[f's{i}' for i in range(6)])

    def test_three_mode_geometry_and_full_table(self):
        svgs=[]; ir=sample()
        for mode in MODES:
            page=render_gallery_html(ir,mode,'type-loop-flywheel')
            svgs.append(re.search(r'<svg .*?</svg>',page,re.S).group().replace(mode,'MODE'))
            for collection in ('nodes','edges','annotations'):
                for item in ir[collection]: self.assertIn(item['id'],page[page.index('<details'):])
        self.assertEqual(len(set(svgs)),1)

    def test_arcs_are_clockwise_and_stay_on_one_circle(self):
        value=layout_flywheel(self.plan())
        for arc in value['arcs']:
            self.assertLess(arc['start_angle'],arc['end_angle'])
            for point in (arc['start'],arc['end']):
                self.assertAlmostEqual(math.dist(value['center'],point),value['radius'])
        root=ET.fromstring('<svg>'+render_flywheel(self.plan())+'</svg>')
        for path in root.findall('.//*[@data-cycle-edge]'):
            self.assertIn(' 0 0 1 ',path.get('d'))
            self.assertEqual(path.get('d').count('M'),1)
            self.assertEqual(path.get('d').count('A'),1)
            self.assertEqual(path.get('marker-end'),'url(#arrow)')

    def test_shared_state_is_optional_not_fabricated(self):
        p=adapt_visual(fixtures()['loop-flywheel'])
        value=layout_flywheel(p)
        self.assertEqual(len(value['order']),3)
        self.assertIsNone(value['shared_id'])
        self.assertEqual(value['spokes'],[])

    def test_contributions_are_not_fabricated(self):
        p=self.plan(); p['semantic_projection']['annotations']=[]
        self.assertEqual(layout_flywheel(p)['spokes'],[])

    def test_disconnected_cycles_rejected(self):
        p=self.plan()
        for edge in p['semantic_projection']['edges']:
            i=int(edge['source'][1:]); edge['target']=f's{(i//3)*3+(i+1)%3}'
        with self.assertRaises(ValueError): layout_flywheel(p)

    def test_shared_state_cannot_become_cycle_station(self):
        p=self.plan(); p['semantic_projection']['edges'][0]['target']='memory'
        with self.assertRaises(ValueError): layout_flywheel(p)

    def test_ambiguous_annotation_rejected(self):
        p=self.plan(); p['semantic_projection']['annotations'][-1]['text']='Unspecified relationship'
        with self.assertRaises(ValueError): layout_flywheel(p)

    def test_duplicate_contribution_rejected(self):
        p=self.plan(); p['semantic_projection']['annotations'].append(copy.deepcopy(p['semantic_projection']['annotations'][-1]))
        with self.assertRaises(ValueError): layout_flywheel(p)

    def test_long_text_grows_canvas_and_cards(self):
        p=self.plan(); before=layout_flywheel(p)
        p['semantic_projection']['nodes'][0]['label']='Nội dung mở rộng ' * 15
        after=layout_flywheel(p)
        self.assertGreater(after['height'],before['height'])
        self.assertGreater(after['nodes']['s0']['box'][3],before['nodes']['s0']['box'][3])

    def test_supports_three_through_twelve_stations(self):
        for count in range(3,13):
            value=layout_flywheel(self.plan(count))
            self.assertEqual(len(value['arcs']),count)

    def test_overlap_and_arc_intrusion_mutations_rejected(self):
        value=layout_flywheel(self.plan())
        value['nodes']['s0']['box']=value['nodes']['memory']['box']
        with self.assertRaises(ValueError): validate_flywheel_layout(value)
        value=layout_flywheel(self.plan())
        arc=value['arcs'][0]; arc['start_angle']=value['nodes']['s0']['angle']
        with self.assertRaises(ValueError): validate_flywheel_layout(value)

    def test_script_like_text_is_escaped(self):
        p=self.plan(); p['semantic_projection']['nodes'][0]['label']='<script>x</script>'
        self.assertNotIn('<script>',render_flywheel(p))
        self.assertIn('&lt;script&gt;',flywheel_table(p))

if __name__=='__main__': unittest.main()
