"""Run with: python -m unittest -v test_app.py"""
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from data_utils import load_inventory, decade_summary, scatter_records


class InventoryTests(unittest.TestCase):
    def test_source_and_denominators(self):
        data, audit = load_inventory()
        self.assertEqual(audit["source_rows"], 8862)
        self.assertEqual(audit["excluded_years"], 289)
        self.assertEqual(len(data), 8573)
        counts, agencies, selected = decade_summary(data, (1753, 2019), 100)
        self.assertEqual(int(counts.records.sum()), len(data))
        self.assertTrue(counts.groupby("agency").share.sum().round(10).eq(1).all())
        self.assertTrue(counts.records.ge(0).all())
        empty, _, _ = decade_summary(data, (1754, 1754), 8)
        self.assertTrue(empty.empty)

    def test_scatter_filters(self):
        data, _ = load_inventory()
        points = scatter_records(data, "University of Illinois", (1950, 2000), (1000, 10000))
        self.assertGreater(len(points), 0)
        self.assertTrue(points.agency.eq("University of Illinois").all())
        self.assertTrue(points.year.between(1950, 2000).all())
        self.assertTrue(points.area.between(1000, 10000).all())
        self.assertTrue(scatter_records(data, "University of Illinois", (1753, 2019), (0, 0)).empty)

    def test_app_and_interactions(self):
        at = AppTest.from_file(str(Path(__file__).parent / "streamlit_app.py"), default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.get("vega_lite_chart")), 2)
        at.radio(key="heat_metric").set_value("Record count")
        at.selectbox(key="top_n").set_value(5)
        at.selectbox(key="agency").set_value("Department of Natural Resources")
        at.toggle(key="log_scale").set_value(False)
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.get("vega_lite_chart")), 2)
        at.slider(key="heat_years").set_value((1754, 1754))
        at.slider(key="area_Department of Natural Resources").set_value((0, 0))
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.info), 2)
        self.assertEqual(len(at.get("vega_lite_chart")), 0)
        at.slider(key="heat_years").set_value((1900, 2019))
        at.selectbox(key="agency").set_value("University of Illinois")
        at.run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.get("vega_lite_chart")), 2)


if __name__ == "__main__":
    unittest.main()
