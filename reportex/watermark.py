from reportlab.pdfgen.canvas import Canvas
from reportex.core import BoxConstraints, Position, SingleChildWidget, Size
from reportex.image import Image
from reportex.text import Text


class WaterMark(SingleChildWidget):
    def __init__(self, child: Image | Text, width, height):
        super().__init__(child, width, height)

    def layout(self, constraints: BoxConstraints) -> Size:
        return super().layout(constraints)

    def draw(self, canvas: Canvas, parent_pos: Position):
        return super().draw(canvas, parent_pos)
