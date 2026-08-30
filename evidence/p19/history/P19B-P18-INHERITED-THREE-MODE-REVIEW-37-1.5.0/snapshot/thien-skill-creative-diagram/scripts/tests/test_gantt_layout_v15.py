"""Calendar correctness and fail-closed layout checks, independent of QA fixture."""
import copy
from datetime import datetime
import re
import unittest
import xml.etree.ElementTree as ET

from gantt_layout_v15 import layout_gantt, render_gantt, gantt_table
from gallery_renderer_v15 import MODES, render_gallery_html
from semantic_fixtures import finalize, n, g, fixtures
from visual_adapters_v15 import adapt_visual


def schedule():
    nodes = [n(f'task-{i}', 'task', f'Công việc {i}', state='gate' if i==4 else 'task',
               start=f'2026-{9+i//3:02d}-{1+i%3*8:02d}T00:00:00+07:00',
               end=f'2026-{9+i//3:02d}-{7+i%3*8:02d}T00:00:00+07:00') for i in range(7)]
    return finalize('gantt', nodes=nodes, groups=[
        g('phase-a','Giai đoạn A',['task-0','task-1']),
        g('phase-b','Giai đoạn B',['task-2','task-3','task-4']),
        g('phase-c','Giai đoạn C',['task-5','task-6'])])


class GanttLayoutTests(unittest.TestCase):
    def plan(self):
        return adapt_visual(schedule())

    def test_all_rows_and_groups_render_once(self):
        root = ET.fromstring('<svg>'+render_gantt(self.plan())+'</svg>')
        self.assertEqual(len(root.findall('.//*[@data-task-id]')),7)
        self.assertEqual(len(root.findall('.//rect[@class="gantt-phase"][@data-phase-id]')),3)
        self.assertEqual(len(root.findall('.//rect[@class="gantt-gate"][@data-task-id]')),1)

    def test_month_widths_follow_calendar_not_equal_slots(self):
        result=layout_gantt(self.plan())
        x=result['x']
        a,b,c=result['months']
        self.assertAlmostEqual((x(c)-x(b))/(x(b)-x(a)),31/30)
        self.assertEqual(result['limit'].isoformat(),'2026-12-01T00:00:00+07:00')

    def test_dates_share_one_scale(self):
        result=layout_gantt(self.plan())
        for row in result['rows']:
            self.assertEqual(row['x'],result['x'](row['start_time']))
            self.assertAlmostEqual(row['end_x']-row['x'],6/91*(result['right']-result['left']))

    def test_phase_encloses_owned_bars_with_vertical_clearance(self):
        result=layout_gantt(self.plan())
        for row in result['rows']:
            band=next(b for b in result['bands'] if b['id']==row['group_id'])
            self.assertGreaterEqual(row['y']-20-band['y'],12)
            self.assertGreaterEqual(band['y']+band['height']-row['y']-20,12)
            self.assertGreaterEqual(row['x'],22+12)
            self.assertLessEqual(row['end_x'],result['width']-22-12)

    def test_three_modes_identical_geometry(self):
        svgs=[]
        for mode in MODES:
            page=render_gallery_html(schedule(),mode,'type-gantt')
            svgs.append(re.search(r'<svg .*?</svg>',page,re.S).group().replace(mode,'MODE'))
        self.assertEqual(len(set(svgs)),1)

    def test_exact_table_preserves_all_dates_and_ids(self):
        ir=schedule()
        table=gantt_table(adapt_visual(ir))
        for node in ir['nodes']:
            for key in ('start','end','id','label'):
                self.assertIn(node[key],table)
        self.assertIn('Cửa sổ duyệt',table)

    def test_zero_duration_is_marker_not_fake_duration(self):
        plan=self.plan()
        item=plan['semantic_projection']['time_contract']['items'][0]
        item['end']=item['start']
        root=ET.fromstring('<svg>'+render_gantt(plan)+'</svg>')
        self.assertEqual(root.find('.//*[@data-task-id="task-0"]').tag,'path')

    def test_short_gate_does_not_inflate_bar(self):
        plan=self.plan()
        item=plan['semantic_projection']['time_contract']['items'][4]
        item['end']=item['start'].replace('T00:', 'T01:')
        result=layout_gantt(plan)
        row=next(r for r in result['rows'] if r['id']=='task-4')
        self.assertLess(row['end_x']-row['x'],1)
        self.assertIn('text-anchor="start">GATE',render_gantt(plan))

    def test_duplicate_or_missing_membership_rejected(self):
        for change in ('duplicate','missing'):
            plan=self.plan()
            groups=plan['semantic_projection']['groups']
            if change=='duplicate': groups[1]['member_ids'].append('task-0')
            else: groups[0]['member_ids'].pop()
            with self.assertRaises(ValueError): layout_gantt(plan)

    def test_invalid_time_rejected(self):
        for end in ('2025-01-01T00:00:00+07:00','2026-09-07T00:00:00'):
            plan=self.plan()
            plan['semantic_projection']['time_contract']['items'][0]['end']=end
            with self.assertRaises(ValueError): layout_gantt(plan)

    def test_long_labels_grow_rows_not_shrink_text(self):
        plan=self.plan()
        before=layout_gantt(plan)
        plan['semantic_projection']['time_contract']['items'][0]['label']='Nội dung mở rộng ' * 15
        after=layout_gantt(plan)
        self.assertGreater(after['height'],before['height'])
        self.assertGreater(len(after['rows'][0]['lines']),2)

    def test_original_two_task_fixture_keeps_dependency(self):
        ir=fixtures()['gantt']
        svg=render_gantt(adapt_visual(ir))
        self.assertIn('data-dependency-id="dependency-build"',svg)
        self.assertEqual(svg.count('data-task-id='),2)

    def test_unsafe_labels_are_escaped(self):
        plan=self.plan()
        plan['semantic_projection']['time_contract']['items'][0]['label']='<script>x</script>'
        self.assertNotIn('<script>',render_gantt(plan))
        self.assertIn('&lt;script&gt;',gantt_table(plan))

    def test_cross_year_calendar(self):
        plan=self.plan()
        for item in plan['semantic_projection']['time_contract']['items']:
            item['start']='2026-12-25T00:00:00+07:00'
            item['end']='2027-01-05T00:00:00+07:00'
        result=layout_gantt(plan)
        self.assertEqual([(m.year,m.month) for m in result['months']],[(2026,12),(2027,1)])

if __name__=='__main__':
    unittest.main()
