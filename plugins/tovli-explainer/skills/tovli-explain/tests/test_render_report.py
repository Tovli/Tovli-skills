"""Regression checks for report separation and diagram integrity."""
import copy
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_report", ROOT / "scripts" / "render_report.py")
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


class PanelParser(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.stack = []
        self.panels = {}
        self.text = {"business": [], "technical": []}
        self.scripts = []
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        view = attrs.get("data-view") or (self.stack[-1][1] if self.stack else None)
        if attrs.get("data-view"):
            self.panels[view] = attrs
        if tag == "script":
            self.scripts.append(attrs)
        if tag not in {"meta", "link", "br", "hr", "img", "input"}:
            self.stack.append((tag, view))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        view = self.stack[-1][1] if self.stack else None
        if view:
            self.text[view].append(text)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples" / "report-data.example.json").read_text(encoding="utf-8"))

    def test_business_and_technical_content_are_separate(self):
        report = PanelParser(RENDERER.build_html(self.data))
        business = " ".join(report.text["business"])
        technical = " ".join(report.text["technical"])
        self.assertEqual(set(report.panels), {"business", "technical"})
        self.assertNotIn("hidden", report.panels["business"])
        self.assertIn("hidden", report.panels["technical"])
        self.assertIn("Show no matches", business)
        self.assertNotIn("HTTP", business)
        self.assertNotIn("InvoiceLookup", business)
        self.assertNotIn("src/Invoices", business)
        self.assertNotIn(self.data["meta"]["head"], business)
        self.assertIn("HTTP 404", technical)
        self.assertIn("InvoiceLookup", technical)
        self.assertIn("src/Invoices", technical)
        self.assertNotIn("all invoice search workflows", technical)
        self.assertIn("all invoice search workflows", business)
        self.assertFalse(any("src" in attrs for attrs in report.scripts))

    def test_technical_visuals_cannot_be_put_in_business_view(self):
        scene = copy.deepcopy(self.data["scenes"][2])
        scene["category"] = "business"
        with self.assertRaises(ValueError):
            RENDERER.render_visual(scene)

    def test_activity_has_valid_svg_and_complete_branch_connections(self):
        graph = self.data["scenes"][1]["visual"]["after"]
        svg = RENDERER.graph_svg(graph, "activity")
        # Strip the HTML figure wrapper and parse the SVG itself.
        tree = ET.fromstring(svg[svg.index("<svg"):svg.index("</svg>") + len("</svg>")])
        namespace = {"s": "http://www.w3.org/2000/svg"}
        self.assertEqual(len(tree.findall("s:g", namespace)), len(graph["nodes"]))
        self.assertEqual(len(tree.findall("s:path", namespace)), len(graph["edges"]))
        self.assertEqual(tree.attrib["role"], "img")
        self.assertTrue(tree.attrib["aria-label"])

    def test_invalid_diagram_edges_and_unlabeled_decisions_are_rejected(self):
        graph = copy.deepcopy(self.data["scenes"][1]["visual"]["after"])
        graph["edges"][0]["to"] = "does-not-exist"
        with self.assertRaises(ValueError):
            RENDERER.graph_svg(graph, "activity")
        graph = copy.deepcopy(self.data["scenes"][1]["visual"]["after"])
        del graph["edges"][1]["label"]
        with self.assertRaises(ValueError):
            RENDERER.graph_svg(graph, "activity")

    def test_duplicate_node_and_grid_positions_are_rejected(self):
        graph = copy.deepcopy(self.data["scenes"][1]["visual"]["after"])
        graph["nodes"].append(copy.deepcopy(graph["nodes"][0]))
        with self.assertRaises(ValueError):
            RENDERER.graph_svg(graph, "activity")
        graph["nodes"][-1]["id"] = "different-id"
        with self.assertRaises(ValueError):
            RENDERER.graph_svg(graph, "activity")

    def test_diagram_comparison_and_content_escaping(self):
        graph = self.data["scenes"][1]["visual"]["after"]
        scene = {"category": "business", "visual": {"type": "activity", "before": graph, "after": graph}}
        comparison = RENDERER.render_visual(scene)
        self.assertEqual(comparison.count("<svg "), 2)
        escaped = copy.deepcopy(graph)
        escaped["nodes"][0]["label"] = '<script>alert("test")</script>'
        result = RENDERER.graph_svg(escaped, "activity")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_legacy_categories_stay_in_technical_view(self):
        data = {"scenes": [{"id": "legacy", "title": "Legacy detail", "narrative": ["Legacy response"],
                           "visual": {"type": "before-after", "before": ["Old"], "after": ["New"]}}],
                "summary": {"purpose": "HTTP 404 legacy summary"}, "unknowns": ["Legacy unknown"]}
        report = PanelParser(RENDERER.build_html(data))
        self.assertIn("hidden", report.panels["business"])
        self.assertNotIn("hidden", report.panels["technical"])
        self.assertIn("Legacy response", " ".join(report.text["technical"]))
        self.assertNotIn("Legacy response", " ".join(report.text["business"]))
        self.assertIn("Legacy unknown", " ".join(report.text["technical"]))
        self.assertIn("HTTP 404 legacy summary", " ".join(report.text["technical"]))
        self.assertNotIn("HTTP 404 legacy summary", " ".join(report.text["business"]))

    def test_invalid_categories_are_rejected(self):
        self.data["scenes"][0]["category"] = "mixed"
        with self.assertRaises(ValueError):
            RENDERER.build_html(self.data)


if __name__ == "__main__":
    unittest.main()
