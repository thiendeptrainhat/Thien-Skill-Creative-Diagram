import unittest

from sequence_layout_v15 import layout_sequence, render_sequence, validate_sequence_svg
from sequence_review31_fixture import sequence_fixture
from visual_adapters_v15 import adapt_visual


class DetailedSequenceTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(sequence_fixture())

    def test_semantic_and_layout_contract(self):
        layout = layout_sequence(self.plan)
        self.assertEqual(len(layout["nodes"]), 4)
        self.assertEqual(len(layout["edges"]), 6)
        self.assertEqual(list(layout["participant_x"].values()), [300, 760, 1220, 1680])
        self.assertEqual(len(layout["activations"]), 2)

    def test_serialized_contract(self):
        measurement = validate_sequence_svg(f"<svg>{render_sequence(self.plan)}</svg>")
        self.assertEqual(measurement["participants"], 4)
        self.assertEqual(measurement["messages"], 6)
        self.assertEqual(measurement["straight_messages"], 5)
        self.assertEqual(measurement["self_messages"], 1)
        self.assertEqual(measurement["centered_card_lifelines"], 4)

    def test_self_call_is_only_orthogonal_exception(self):
        svg = render_sequence(self.plan)
        self.assertEqual(svg.count('data-route-kind="rounded-orthogonal"'), 1)
        self.assertEqual(svg.count('data-route-kind="straight"'), 5)
        self.assertIn('data-route-exception="self-call-requires-return-to-same-lifeline"', svg)


if __name__ == "__main__":
    unittest.main()
