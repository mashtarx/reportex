from reportlab.pdfgen.canvas import Canvas


from reportex.core import (
    Size,
    BoxConstraints,
    Position,
    Widget,
    SingleChildWidget,
    Alignment,
    EdgeInset,
    Axis,
    Color,
    Colors,
    INFINITY,
)

from reportex.container import Container


class Align(SingleChildWidget):
    def __init__(self, *, child: Widget, alignment: Alignment):
        super().__init__(child=child, width=None, height=None)
        self.alignment = alignment

    @property
    def client_width(self):
        return self.width

    @property
    def client_height(self):
        return self.height

    @property
    def client_origin(self):
        return super().client_origin

    def layout(self, constraints: BoxConstraints):
        child_size = self.child.layout(constraints)
        size = child_size

        self.child.offset = Position(0, 0)
        self.set_size(size)
        return size

    def _set_offset(self):
        psize = Size(self.parent.client_width, self.parent.client_height)
        size = Size(self.width, self.height)
        origin = self.parent.client_origin
        match (self.alignment):
            case Alignment.LEFT:
                self.offset = Position(origin.x, origin.y)
            case Alignment.TOP_CENTER:
                self.offset = Position(
                    (psize.width - size.width) / 2 + origin.x, origin.y
                )
            case Alignment.RIGHT:
                self.offset = Position(origin.x + psize.width - size.width, origin.y)
            case Alignment.LEFT_MIDDLE:
                self.offset = Position(
                    origin.x, origin.y + (psize.height - size.height) / 2
                )
            case Alignment.RIGHT_MIDDLE:
                self.offset = Position(
                    psize.width - size.width + origin.x,
                    (psize.height - size.height) / 2 + origin.y,
                )
            case Alignment.BOTTOM_CENTER:
                self.offset = Position(
                    (psize.width - size.width) / 2 + origin.x,
                    (psize.height - size.height) + origin.y,
                )
            case Alignment.CENTER:
                self.offset = Position(
                    x=(psize.width - size.width) / 2 + origin.x,
                    y=(psize.height - size.height) / 2 + origin.y,
                )

    def draw(self, canvas: Canvas, parent_pos: Position):
        self._set_offset()

        pos = parent_pos.resolve(self.offset)
        if self.child is not None:
            self.child.draw(canvas, pos)


class Padding(SingleChildWidget):
    def __init__(self, *, child: Widget, padding: EdgeInset):
        super().__init__(child, None, None)
        self.padding = padding

    @property
    def client_height(self):
        return self.height - self.padding.top - self.padding.bottom

    @property
    def client_width(self):
        return self.width - self.padding.left - self.padding.right

    @property
    def client_origin(self):
        return Position(self.padding.left, self.padding.right)

    def layout(self, constraints: BoxConstraints) -> Size:
        child_max_width = constraints.max_width - (
            self.padding.left + self.padding.right
        )
        child_max_height = constraints.max_height - (
            self.padding.top + self.padding.bottom
        )
        child_size = self.child.layout(
            constraints=BoxConstraints(
                min_width=0,
                min_height=0,
                max_width=child_max_width,
                max_height=child_max_height,
            )
        )

        size = Size(constraints.max_width, constraints.max_height)

        if child_size.width < child_max_width:
            size.width = child_size.width + self.padding.left + self.padding.right
        if child_size.height < child_max_height:
            size.height = child_size.height + self.padding.top + self.padding.bottom

        self.set_size(size)
        self.child.offset = Position(x=self.padding.left, y=self.padding.top)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        self.child.draw(canvas, pos)


class Expanded(SingleChildWidget):
    def __init__(self, *, child: Widget, flex: int = 1):
        super().__init__(child, None, None)
        self.flex = flex

    @property
    def client_width(self):
        return self.width

    @property
    def client_height(self):
        return self.height

    @property
    def client_origin(self):
        return super().client_origin

    def layout(self, constraints: BoxConstraints) -> Size:
        w = constraints.max_width
        h = constraints.max_height
        child_size = self.child.layout(constraints)
        if self.parent.__class__.__name__ == "Column":
            w = child_size.width
        else:
            h = child_size.height
        self.child.offset = Position(0, 0)
        size = Size(w, h)
        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        self.child.draw(canvas, pos)


class Center(SingleChildWidget):
    def __init__(self, child: Widget):
        super().__init__(child, None, None)

    @property
    def client_width(self):
        return self.width

    @property
    def client_height(self):
        return self.height

    @property
    def client_origin(self):
        return super().client_origin

    def layout(self, constraints: BoxConstraints) -> Size:
        child_size = self.child.layout(constraints)
        x = (constraints.max_width - child_size.width) / 2
        y = (constraints.max_height - child_size.height) / 2
        self.child.offset = Position(x, y)
        self.set_size(child_size)
        return child_size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        self.child.draw(canvas, pos)


class Divider(Widget):
    def __init__(
        self,
        *,
        axis: Axis = Axis.HORIZONTAL,
        width: float = 2,
        color: Color = Colors.grey,
    ):
        super().__init__(None, None)
        self.axis = axis
        self.linewidth = width
        self.color = color

    def layout(self, constraints: BoxConstraints) -> Size:
        size = Size(0, 0)
        if self.axis == Axis.HORIZONTAL:
            size.height = self.linewidth
        else:
            size.width = self.linewidth

        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        canvas.saveState()
        c = self.color.normalize()
        canvas.setStrokeColorRGB(c.r, c.g, c.b, c.a)
        canvas.setLineWidth(self.linewidth)

        if self.axis == Axis.HORIZONTAL:
            self._draw_horizontal(canvas, parent_pos)
        else:
            self._draw_vertical(canvas, parent_pos)

        canvas.restoreState()

    def _draw_horizontal(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        if self.parent.width > 0:
            canvas.line(
                parent_pos.x, pos.y - 0.5, parent_pos.x + self.parent.width, pos.y - 0.5
            )

    def _draw_vertical(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        if self.parent.height > 0:
            canvas.line(
                pos.x + 0.5,
                parent_pos.y,
                pos.x + 0.5,
                parent_pos.y - self.parent.height,
            )


def SizedBox(*, width=None, height=None, child: Widget = None) -> Widget:
    return Container(width=width, height=height, child=child)
