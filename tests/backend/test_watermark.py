"""The vector watermark: the SVG logos of backend/media/watermarks are drawn as shapes, not as a bitmap."""
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib  # noqa: E402

matplotlib.use('Agg')

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

from PIL import Image  # noqa: E402

from backend.plot_renderer import RequestDataSource, render_plot_image  # noqa: E402
from backend.plotting.formatting import watermark  # noqa: E402
from backend.plotting.svg_logo import parse_path, read_shapes  # noqa: E402
from backend.security import MAX_LOGO_BYTES, check_logo_bytes  # noqa: E402

LOGO_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect fill="#123456" width="10" height="10"/></svg>'


def _png(size=(40, 20)) -> bytes:
    buffer = io.BytesIO()
    Image.new('RGBA', size, (255, 0, 0, 255)).save(buffer, format='PNG')
    return buffer.getvalue()


class SvgPathTest(unittest.TestCase):
    def test_relative_and_absolute_commands(self) -> None:
        path = parse_path('M10,10h5v5H10Z')
        self.assertEqual(path.vertices.tolist(), [[10, 10], [15, 10], [15, 15], [10, 15], [10, 10]])
        self.assertEqual(list(path.codes), [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO, MplPath.CLOSEPOLY])

    def test_smooth_curve_mirrors_the_previous_control_point(self) -> None:
        path = parse_path('M0,0C0,10,10,10,10,0S20,-10,20,0')
        self.assertEqual(path.vertices[4].tolist(), [10, -10])      # 2 × (10,0) − (10,10)

    def test_arcs_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            parse_path('M0,0A5,5,0,0,1,10,0')


class WatermarkTest(unittest.TestCase):
    def test_the_default_logos_are_drawn_as_vector_shapes(self) -> None:
        for dark_mode in (False, True):
            fig = plt.figure()
            try:
                watermark(fig, True, alpha=0.6, dark_mode=dark_mode, pos=[0.7, 0.1], size=0.13)
                logo_ax = fig.axes[-1]
                self.assertEqual(len(logo_ax.images), 0)
                self.assertGreater(len(logo_ax.patches), 0)
            finally:
                plt.close(fig)


SVG_HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50">'


class SvgShapesTest(unittest.TestCase):
    def shapes(self, body: str):
        return read_shapes(io.BytesIO((SVG_HEAD + body + '</svg>').encode()))[0]

    def test_circle_and_ellipse(self) -> None:
        (circle, _), (ellipse, _) = self.shapes('<circle cx="10" cy="20" r="5"/><ellipse cx="50" cy="20" rx="8" ry="4"/>')
        extent = circle.get_extents()
        self.assertEqual((extent.x0, extent.x1, extent.y0, extent.y1), (5, 15, 15, 25))
        extent = ellipse.get_extents()
        self.assertEqual((extent.x0, extent.x1, extent.y0, extent.y1), (42, 58, 16, 24))

    def test_text_is_outlined_at_its_position_with_y_down(self) -> None:
        (outline, color), = self.shapes('<text x="10" y="40" font-size="20" fill="#abcdef">Hi</text>')
        extent = outline.get_extents()
        self.assertEqual(color, '#abcdef')
        self.assertAlmostEqual(extent.x0, 10, delta=3)
        self.assertLess(extent.y0, 40)      # the letters stand above the baseline: smaller y in SVG
        self.assertAlmostEqual(extent.y1, 40, delta=1)

    def test_text_anchor_middle_centres_on_x(self) -> None:
        (outline, _), = self.shapes('<text x="50" y="30" text-anchor="middle" font-size="20">Mid</text>')
        extent = outline.get_extents()
        self.assertAlmostEqual((extent.x0 + extent.x1) / 2, 50, delta=1)

    def test_fills_from_classes_groups_and_style_attributes(self) -> None:
        shapes = self.shapes('<style>.a{fill:#111111}.b,.c{fill:#222222;}</style>'
                             '<g fill="#333333"><rect class="a" width="1" height="1"/><rect width="1" height="1"/>'
                             '<rect class="b" width="1" height="1"/><rect style="fill: #444444" width="1" height="1"/></g>'
                             '<rect class="c" width="1" height="1"/><rect fill="none" width="1" height="1"/>')
        self.assertEqual([color for _, color in shapes], ['#111111', '#333333', '#222222', '#444444', '#222222'])

    def test_text_limits(self) -> None:
        with self.assertRaises(ValueError):
            self.shapes('<text x="0" y="0">' + 'x' * 501 + '</text>')


class CustomLogoTest(unittest.TestCase):
    def test_uploads_are_checked_before_decoding(self) -> None:
        check_logo_bytes(_png())
        check_logo_bytes(LOGO_SVG)
        for bad in (b'GIF89a', b'<html></html>', b'x' * (MAX_LOGO_BYTES + 1)):
            with self.assertRaises(ValueError):
                check_logo_bytes(bad)

    def test_png_and_svg_logos_are_drawn(self) -> None:
        for logo, drawn in ((_png(), 'images'), (LOGO_SVG, 'patches')):
            fig = plt.figure()
            try:
                watermark(fig, True, alpha=0.6, dark_mode=False, pos=[0.7, 0.1], size=0.13, logo_bytes=logo)
                self.assertGreater(len(getattr(fig.axes[-1], drawn)), 0)
            finally:
                plt.close(fig)

    def test_unsupported_svg_features_are_named(self) -> None:
        for svg, word in ((b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><line x2="1"/></svg>', 'line'),
                          (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><path transform="scale(2)" d="M0,0h1v1Z"/></svg>', 'transform')):
            fig = plt.figure()
            try:
                with self.assertRaisesRegex(ValueError, word):
                    watermark(fig, True, alpha=0.6, dark_mode=False, pos=[0.7, 0.1], size=0.13, logo_bytes=svg)
            finally:
                plt.close(fig)

    def test_only_the_key_holder_gets_the_own_logo(self) -> None:
        config = json.loads((Path(__file__).resolve().parents[1] / 'fixtures' / 'render-config.json').read_text(encoding='utf-8'))['config']
        config['dataframes'][0]['watermark'] = True
        source = {0: RequestDataSource('xlsx', (Path(__file__).resolve().parents[1] / 'dataset_1.xlsx').read_bytes(), 'dataset_1.xlsx')}
        unlocked = render_plot_image(config, data_sources=source, attribution_unlocked=True, watermark_logo=LOGO_SVG).content
        locked = render_plot_image(config, data_sources=source, attribution_unlocked=False, watermark_logo=LOGO_SVG).content
        self.assertIn(b'#123456', unlocked)
        self.assertNotIn(b'#123456', locked)


if __name__ == '__main__':
    unittest.main()
