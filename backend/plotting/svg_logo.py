"""Simple SVG logos as matplotlib shapes (the watermark).

matplotlib cannot draw an SVG, and the libraries for it either only convert path data (svgpath2mpl) or
render a bitmap (cairosvg, svglib). The logos here are flat shapes, so they are read directly:
path (M L H V C S Q T Z, no arcs), polygon, rect, circle, ellipse and text, with fills from presentation
attributes, style attributes or CSS classes (inherited from groups). Text becomes outlines, so a logo
is vector shapes in SVG exports and sharp at any dpi. Everything else (transforms, arcs, strokes,
gradients, images, ...) is refused with a message instead of being drawn wrongly.
"""
from __future__ import annotations

import io
import re

from defusedxml import ElementTree
from matplotlib import patches
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D

_NS = '{http://www.w3.org/2000/svg}'
_TOKEN = re.compile(r'[A-Za-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
_ARGUMENTS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'Z': 0}


def parse_path(d:str) -> Path:
    '''SVG path data (M L H V C S Q T Z, absolute and relative; no arcs) as a matplotlib Path'''
    tokens = _TOKEN.findall(d)
    verts, codes = [], []
    x = y = start_x = start_y = 0.0
    last_ctrl = None    # second control point of the previous C/S (or Q/T), for the smooth variants
    command, i = None, 0
    while i < len(tokens):
        if tokens[i].isalpha():
            command, i = tokens[i], i + 1
        elif command in (None, 'Z', 'z'):
            raise ValueError(f'Unexpected number in SVG path: {tokens[i]}')
        upper, relative = command.upper(), command.islower()
        if upper not in _ARGUMENTS:
            raise ValueError(f"Unsupported SVG path command '{command}' (arcs are not supported).")
        count = _ARGUMENTS[upper]
        args = [float(t) for t in tokens[i:i + count]]
        if len(args) < count:
            raise ValueError('Incomplete SVG path.')
        i += count
        ox, oy = (x, y) if relative else (0.0, 0.0)
        if upper == 'Z':
            verts.append((start_x, start_y)); codes.append(Path.CLOSEPOLY)
            x, y, last_ctrl = start_x, start_y, None
            continue
        if upper == 'H':
            args = [args[0] + (x if relative else 0.0), y]
        elif upper == 'V':
            args = [x, args[0] + (y if relative else 0.0)]
        else:
            args = [value + (ox if k % 2 == 0 else oy) for k, value in enumerate(args)]
        if upper == 'M':
            verts.append((args[0], args[1])); codes.append(Path.MOVETO)
            start_x, start_y = args[0], args[1]
            command = 'l' if relative else 'L'      # further pairs after a moveto are linetos
            last_ctrl = None
        elif upper in 'LHV':
            verts.append((args[-2], args[-1])); codes.append(Path.LINETO)
            last_ctrl = None
        elif upper in 'CS':
            if upper == 'S':
                c1 = (2 * x - last_ctrl[0], 2 * y - last_ctrl[1]) if last_ctrl else (x, y)
                c2, end = (args[0], args[1]), (args[2], args[3])
            else:
                c1, c2, end = (args[0], args[1]), (args[2], args[3]), (args[4], args[5])
            verts += [c1, c2, end]; codes += [Path.CURVE4] * 3
            last_ctrl = c2
        else:   # Q, T
            if upper == 'T':
                c1 = (2 * x - last_ctrl[0], 2 * y - last_ctrl[1]) if last_ctrl else (x, y)
                end = (args[0], args[1])
            else:
                c1, end = (args[0], args[1]), (args[2], args[3])
            verts += [c1, end]; codes += [Path.CURVE3] * 2
            last_ctrl = c1
        x, y = verts[-1]
    return Path(verts, codes)


_IGNORED = {'g', 'defs', 'style', 'title', 'desc', 'metadata', 'svg'}
_INHERITED = ('fill', 'font-size', 'font-family', 'font-weight', 'font-style', 'text-anchor')
MAX_TEXT_CHARACTERS = 500       # a logo, not a document: bounds the work of laying out text


def _declarations(text:str) -> dict[str, str]:
    '''"fill: red; font-size: 12px" as a dict, for CSS rules and style attributes'''
    pairs = (declaration.split(':', 1) for declaration in text.split(';') if ':' in declaration)
    return {name.strip(): value.strip() for name, value in pairs}


def _class_rules(root) -> dict[str, dict[str, str]]:
    '''declarations of the simple class selectors (".cls-1, .cls-2 { ... }") of the <style> elements'''
    css = ' '.join(style.text or '' for style in root.iter(_NS + 'style'))
    rules: dict[str, dict[str, str]] = {}
    for selectors, declarations in re.findall(r'([^{}]+)\{([^}]*)\}', css):
        for selector in selectors.split(','):
            if re.fullmatch(r'\.[\w-]+', selector.strip()):
                rules.setdefault(selector.strip()[1:], {}).update(_declarations(declarations))
    return rules


def _number(value:str|None, default:float=0.0) -> float:
    if value is None:
        return default
    try:
        return float(re.sub(r'px$', '', value.strip()))
    except ValueError as error:
        raise ValueError(f"unsupported number '{value}' (only plain numbers or px)") from error


def _text_path(element, style:dict[str, str]) -> Path | None:
    '''the outlines of a <text> element at its position, y pointing down like the rest of the SVG'''
    content = re.sub(r'\s+', ' ', ''.join(element.itertext())).strip()
    if not content:
        return None
    if len(content) > MAX_TEXT_CHARACTERS:
        raise ValueError(f'text longer than {MAX_TEXT_CHARACTERS} characters')
    for child in element:
        if any(attribute in child.attrib for attribute in ('x', 'y', 'dx', 'dy', 'rotate')):
            raise ValueError('positions inside <text> (on <tspan>) are not supported')
    if any(attribute in element.attrib for attribute in ('dx', 'dy', 'rotate')):
        raise ValueError('dx, dy and rotate on <text> are not supported')
    families = [family.strip(' \'"') for family in style.get('font-family', 'sans-serif').split(',')]
    properties = FontProperties(family=families, weight=style.get('font-weight', 'normal'), style=style.get('font-style', 'normal'))
    outline = TextPath((0, 0), content.replace('$', r'\$'), size=_number(style.get('font-size'), 16.0), prop=properties)
    extent = outline.get_extents()
    shift = {'middle': (extent.x0 + extent.x1) / 2, 'end': extent.x1}.get(style.get('text-anchor', 'start'), 0.0)
    return outline.transformed(Affine2D().scale(1, -1).translate(_number(element.attrib.get('x')) - shift, _number(element.attrib.get('y'))))


def _shape_path(tag:str, element, style:dict[str, str]) -> Path | None:
    attributes = element.attrib
    if tag == 'path':
        return parse_path(attributes['d'])
    if tag == 'polygon':
        numbers = [float(v) for v in _TOKEN.findall(attributes['points'])]
        points = list(zip(numbers[0::2], numbers[1::2]))
        return Path(points + [points[0]], [Path.MOVETO] + [Path.LINETO] * (len(points) - 1) + [Path.CLOSEPOLY])
    if tag == 'rect':
        x, y, width, height = (_number(attributes.get(name)) for name in ('x', 'y', 'width', 'height'))      # x and y default to 0
        return Path.unit_rectangle().transformed(Affine2D().scale(width, height).translate(x, y))
    if tag in ('circle', 'ellipse'):
        rx, ry = (_number(attributes.get('r')),) * 2 if tag == 'circle' else (_number(attributes.get('rx')), _number(attributes.get('ry')))
        return Path.unit_circle().transformed(Affine2D().scale(rx, ry).translate(_number(attributes.get('cx')), _number(attributes.get('cy'))))
    if tag == 'text':
        return _text_path(element, style)
    raise ValueError(f'SVG element <{tag}> is not supported; convert it to a path')


def read_shapes(source:Path|io.BytesIO) -> tuple[list[tuple[Path, str]], list[float]]:
    '''(outline, fill colour) of every shape of the logo in drawing order, and its viewBox [x, y, width, height]'''
    root = ElementTree.parse(source).getroot()
    viewbox = [float(v) for v in root.attrib['viewBox'].replace(',', ' ').split()]
    rules = _class_rules(root)
    shapes: list[tuple[Path, str]] = []

    def visit(element, inherited:dict[str, str]) -> None:
        tag = element.tag.replace(_NS, '')
        if 'transform' in element.attrib:
            raise ValueError('SVG transforms are not supported (Inkscape: Preferences → Behavior → Transforms → Store transformation: optimized)')
        style = dict(inherited)
        for name in element.attrib.get('class', '').split():
            style.update(rules.get(name, {}))
        style.update({name: element.attrib[name] for name in _INHERITED if name in element.attrib})
        style.update(_declarations(element.attrib.get('style', '')))
        if tag not in _IGNORED:
            path = _shape_path(tag, element, style)
            fill = style.get('fill', 'black')
            if path is not None and fill != 'none':
                shapes.append((path, fill))
        if tag != 'text':       # the content of a text is part of it
            for child in element:
                visit(child, {name: value for name, value in style.items() if name in _INHERITED})

    visit(root, {})
    return shapes, viewbox


def draw(ax, source:Path|io.BytesIO, alpha:float) -> None:
    '''the logo in `ax`, scaled to fit and anchored bottom right'''
    try:
        shapes, (x0, y0, width, height) = read_shapes(source)
    except (ValueError, KeyError, ElementTree.ParseError) as error:
        raise ValueError(f'Logo: {error}') from error
    by_color: dict[str, list[Path]] = {}
    for path, color in shapes:
        by_color.setdefault(color, []).append(path)
    for color, paths in by_color.items():       # one patch per colour: overlapping shapes must not apply the alpha twice
        ax.add_patch(patches.PathPatch(Path.make_compound_path(*paths), facecolor=color, edgecolor='none', alpha=alpha))
    ax.set_xlim(x0, x0 + width)
    ax.set_ylim(y0 + height, y0)       # SVG's y axis points down
    ax.set_aspect('equal', anchor='SE')
