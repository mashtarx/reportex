from reportlab.pdfgen.canvas import Canvas
from reportex.core import (
    BoxConstraints,
    Position,
    MultiChildrenWidget,
    Size,
    Widget,
    MultiPageWidget,
    DocInfo,
)
from reportex.exceptions import OverFlowError


class PageBreak(Widget):
    def __init__(self):
        super().__init__(None, None)


class MultiPage(MultiChildrenWidget):
    def __init__(self, children: list[Widget], margin: int = 5):
        super().__init__(children, None, None)
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
        page_height = DocInfo.page.height

        height = 0
        remheight = page_height
        y = 0
        for child in self.children:
            if isinstance(child, MultiPageWidget):
                child.page_offset = Position(0, y)
                child_size = child.layout(constraints)
                child_span_pages = (child_size.height + y) // page_height

                child.offset = Position(0, y)
                if child_span_pages > 0:
                    y_ = (
                        child_size.height
                        - (page_height - y)
                        - (child_span_pages - 1) * page_height
                    )
                    remheight = page_height - y_
                else:
                    y_ = y + child_size.height
                    remheight -= y_

                height += child_size.height
                y = y_

            else:
                if remheight == 0:
                    raise OverFlowError("not sufficient space")
                child_size = child.layout(
                    BoxConstraints(0, 0, constraints.max_width, remheight)
                )

                child.offset = Position(0, y)
                y += child_size.height
                remheight += child_size.height
                height += child_size.height

        size = Size(constraints.max_width, height)
        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        for child in self.children:
            pos = parent_pos.resolve(self.offset)
            child.draw(canvas, pos)

    def page_broken(self):
        position = Position(0, DocInfo.page.height)
        self.offset = Position(self.margin, self.margin)
        return position.resolve(self.offset)
