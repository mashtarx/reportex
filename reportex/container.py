from reportex.core import (
    SingleChildWidget,
    Color,
    Colors,
    BoxConstraints,
    Size,
    Position,
    Widget,
    INFINITY,
    Border,
    Rect,
)

from reportex.box import Box, Line
from reportlab.pdfgen.canvas import Canvas


class Container(Box):
    def __init__(
        self,
        *,
        child: Widget = None,
        width: float | None = None,
        height: float | None = None,
        border: Border = Border.zero(),
        border_radius=0,
        color: Color = Colors.white,
        shadow: bool = False
    ):
        super().__init__(child=child, width=width, height=height)
        self.width = width
        self.height = height
        self.border: Border = border
        self.border_radius = border_radius
        self.color = color
        self.shadow = shadow

    def layout(self, constraints: BoxConstraints) -> Size:
        return super().layout(constraints)

    def draw(self, canvas: Canvas, parent_pos: Position):
        # breakpoint()
        pos = parent_pos.resolve(self.offset)
        origin = self.client_origin
        canvas.saveState()
        c = self.color.normalize()
        canvas.setFillColorRGB(c.r, c.g, c.b, c.a)
        canvas.rect(
            pos.resolvex(origin.x),
            pos.resolvey(origin.y) - self.client_height,
            self.client_width,
            self.client_height,
            fill=True,
            stroke=False,
        )
        canvas.restoreState()
        super().draw(canvas, parent_pos)

    def _draw_shadow(self, canvas: Canvas, pos: Position):
        canvas.saveState()
        if self.shadow:
            canvas.setFillGray(0.89, 0.99)
            canvas.roundRect(
                pos.x - 3,
                pos.y - self.height - 3,
                self.width + 4,
                self.height + 4,
                self.border_radius,
                fill=1,
                stroke=0,
            )
        canvas.restoreState()
