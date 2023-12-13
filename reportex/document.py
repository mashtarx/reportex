from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportex.core import (
    BoxConstraints,
    Position,
    Size,
    Widget,
    SingleChildWidget,
)

from reportex.image import Image
from reportex.text import Text


class Page(SingleChildWidget):
    def __init__(
        self, *, child: Widget = None, margin=5, watermark: Image | Text = None
    ):
        super().__init__(child, None, None)
        self.watermark = watermark
        self.margin = margin

    @property
    def client_height(self):
        return self.height

    @property
    def client_width(self):
        return self.width

    @property
    def client_origin(self):
        return super().client_origin

    def layout(self, constraints: BoxConstraints) -> Size:
        size = Size(
            constraints.max_width - (2 * self.margin),
            constraints.max_height - (2 * self.margin),
        )

        self.child.layout(BoxConstraints(0, 0, size.width, size.height))
        self.child.offset = Position(self.margin, self.margin)
        self.set_size(Size(constraints.max_width, constraints.max_height))
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        self.child.draw(canvas, pos)

        if self.watermark:
            self._draw_watermark(canvas, pos)

    def _draw_watermark(self, canvas: Canvas, pos: Position):
        if isinstance(self.watermark, Image):
            ...
        elif isinstance(self.watermark, Text):
            ...


class Document(Widget):
    def __init__(self, *, doc_name, page_size=A4, pages: list[Page]):
        super().__init__(None, None)
        self.pages = pages
        self.page_size = page_size
        self.doc_name = doc_name
        self.offset = Position(0, 0)

    def create(self):
        print("page size: ", self.page_size)
        canvas = Canvas(self.doc_name, self.page_size)
        self.layout(BoxConstraints(0, 0, self.page_size[0], self.page_size[1]))
        self.draw(canvas, Position(0, self.page_size[1]))
        canvas.save()

    def layout(self, constraints: BoxConstraints) -> Size:
        size = Size(constraints.max_width, constraints.max_height)
        self.set_size(size)
        for page in self.pages:
            page.layout(
                BoxConstraints(
                    0,
                    0,
                    constraints.max_width,
                    constraints.max_height,
                )
            )
            page.offset = Position(0, 0)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        for page in self.pages:
            page.draw(canvas, parent_pos)
            canvas.showPage()
