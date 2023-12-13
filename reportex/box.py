from dataclasses import dataclass

import math

from reportlab.pdfgen.canvas import Canvas
from reportex.core import (
    BoxConstraints,
    Position,
    SingleChildWidget,
    Size,
    Widget,
    Border,
    Rect,
    INFINITY,
)


@dataclass
class Line:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def length(self) -> float:
        return math.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)


class Box(SingleChildWidget):
    def __init__(
        self,
        *,
        child: Widget = None,
        width=None,
        height=None,
        border: Border = Border.zero()
    ):
        super().__init__(child, width, height)
        self.border = border

    @property
    def client_width(self):
        if self.width is not None:
            return self.width - self.border.left.width - self.border.right.width

    @property
    def client_height(self):
        if self.height is not None:
            return self.height - self.border.top.width - self.border.bottom.width

    @property
    def client_origin(self):
        return Position(self.border.left.width, self.border.top.width)

    def layout(self, constraints: BoxConstraints) -> Size:
        if self.width is not None and self.height is not None:
            size = self._layout_with_size(constraints)
        elif self.width is not None and self.height is None:
            size = self._layout_with_width(constraints)
        elif self.width is None and self.height is not None:
            size = self._layout_with_height(constraints)
        else:
            size = self._layout_with_nosize(constraints)

        self.set_size(size)
        # breakpoint()
        if self.child:
            self.child.offset = Position(
                (self.client_width - self.child.width) / 2 + self.border.left.width,
                (self.client_height - self.child.height) / 2 + self.border.top.width,
            )
        return size

    def _layout_with_width(self, constraints: BoxConstraints):
        border_width = self.border.left.width + self.border.right.width
        border_width_vert = self.border.top.width + self.border.bottom.width
        width = (
            constraints.max_width
            if (self.width == INFINITY or self.width > constraints.max_width)
            else self.width
        )

        if not self.child:
            return Size(self.width, 0)

        child_size = self.child.layout(
            BoxConstraints(
                0,
                0,
                width - border_width,
                constraints.max_height - border_width_vert,
            )
        )
        size = Size(width, child_size.height + border_width_vert)
        return size

    def _layout_with_height(self, constraints: BoxConstraints):
        border_width = self.border.left.width + self.border.right.width
        border_width_vert = self.border.top.width + self.border.bottom.width
        height = (
            constraints.max_height
            if (self.height == INFINITY or self.height > constraints.max_height)
            else self.height
        )
        if not self.child:
            return Size(0, self.height)

        child_size = self.child.layout(
            BoxConstraints(
                0,
                0,
                constraints.max_width - border_width,
                height - border_width_vert,
            )
        )

        self.child.offset = Position(
            self.border.left.width,
            (height - child_size.height) / 2 + self.border.top.width,
        )
        size = Size(child_size.width + border_width, height)
        return size

    def _layout_with_size(self, constraints: BoxConstraints):
        # breakpoint()
        border_width = self.border.left.width + self.border.right.width
        border_width_vert = self.border.top.width + self.border.bottom.width
        width = (
            constraints.max_width
            if (self.width == INFINITY or self.width > constraints.max_width)
            else self.width
        )
        height = (
            constraints.max_height
            if (self.height == INFINITY or self.height > constraints.max_height)
            else self.height
        )
        if not self.child:
            return Size(width, height)

        self.child.layout(
            BoxConstraints(
                0,
                0,
                width - border_width,
                height - border_width_vert,
            )
        )
        size = Size(width, height)
        return size

    def _layout_with_nosize(self, constraints: BoxConstraints):
        border_width = self.border.left.width + self.border.right.width
        border_width_vert = self.border.top.width + self.border.bottom.width

        if not self.child:
            return Size(0, 0)

        child_size = self.child.layout(
            BoxConstraints(
                0,
                0,
                constraints.max_width - border_width,
                constraints.max_height - border_width_vert,
            )
        )

        size = Size(
            child_size.width + border_width, child_size.height + border_width_vert
        )
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        # self.draw_borders(canvas, pos)
        self._draw_sided_borders(canvas, pos)
        if self.child:
            self.child.draw(canvas, pos)

    def draw_borders(self, canvas: Canvas, pos: Position):
        lines = self.get_border_lines(pos)
        top = lines["top"]
        left = lines["left"]
        Rect(
            canvas,
            top.x1,
            top.y1,
            top.length,  # or client_width
            left.length,  # or client_height
        )

    def get_border_lines(self, pos: Position) -> dict:
        """return lines in resolved coordinates"""
        x2 = pos.x + self.width
        return {
            "top": Line(
                pos.x,
                pos.y - self.border.top.width / 2,
                x2,
                pos.y - self.border.top.width / 2,
            ),
            "right": Line(
                x2 - self.border.right.width / 2,
                pos.y,
                x2 - self.border.right.width / 2,
                pos.y - self.height,
            ),
            "bottom": Line(
                pos.x,
                pos.y - self.height + self.border.bottom.width / 2,
                x2,
                pos.y - self.height + self.border.bottom.width / 2,
            ),
            "left": Line(
                pos.x + self.border.left.width / 2,
                pos.y,
                pos.x + self.border.left.width / 2,
                pos.y - self.height,
            ),
        }

    def _draw_sided_borders(self, canvas: Canvas, pos: Position):
        lines = self.get_border_lines(pos)
        border_data = {
            "top": self.border.top,
            "right": self.border.right,
            "bottom": self.border.bottom,
            "left": self.border.left,
        }

        for name, side in border_data.items():
            if side.width > 0:
                line: Line = lines[name]
                canvas.setLineWidth(side.width)
                color = side.color.normalize()
                canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
                canvas.line(line.x1, line.y1, line.x2, line.y2)
