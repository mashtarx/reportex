from reportlab.pdfgen.canvas import Canvas
from reportex.container import Container
from reportex.core import (
    BoxConstraints,
    Border,
    BorderSide,
    Position,
    Size,
    Widget,
    Color,
    Colors,
    INFINITY,
    MultiPageWidget,
    DocInfo,
)


from reportex.exceptions import OverFlowError


class Cell(Container):
    def __init__(
        self,
        *,
        child: Widget = None,
        border: Border = Border.zero(),
        border_radius=0,
        color: Color = None,
        shadow: bool = False,
        span=1,
        override_column_divider=False,
        override_row_divider=False,
    ):
        super().__init__(
            child=child,
            width=INFINITY,
            height=INFINITY,
            border=border,
            border_radius=border_radius,
            color=color,
            shadow=shadow,
        )

        self.span = span
        self.override_column_divider = override_column_divider
        self.override_row_divider = override_row_divider


class TableRow(Widget):
    parent: "Table"
    background: Color

    def __init__(
        self,
        *,
        cells: list[Cell],
        divider: BorderSide = BorderSide(),
        height=26,
        margin=0,
        background: Color = Colors.white,
    ):
        super().__init__(None, None)
        self._children = cells
        self.cells: list[Cell] = []
        self.divider = divider
        self.height = height
        self.margin = margin
        self.background = background

    @property
    def column_data(self):
        return self.parent.columns

    def init_cells(self):
        for ind, cell in enumerate(self._children):
            if not cell.color:
                cell.color = self.background
            coldata: "TableColumnData" = self.column_data[ind]
            cb = cell.border
            cell.border = Border.zero()
            box = Container(
                child=cell,
                width=coldata.width,
                height=self.height,
                border=Border(
                    right=cb.right if cell.override_column_divider else coldata.divider,
                    left=cb.left,
                    top=cb.top,
                    bottom=cb.bottom if cell.override_row_divider else self.divider,
                ),
                color=cell.color,
            )
            self.cells.append(box)
            box.parent = self

    def layout(self, constraints: BoxConstraints) -> Size:
        if constraints.max_height < self.height:
            raise OverFlowError(f"{self.height} is greater than available height")
        self.init_cells()
        size = Size(constraints.max_width, self.height)
        width = 0
        for ind, cell in enumerate(self.cells):
            coldata = self.column_data[ind]

            cell_size = cell.layout(BoxConstraints(0, 0, coldata.width, self.height))

            if cell_size.height > size.height:
                size.height = cell_size.height

            cell.offset = Position(width, 0)
            width += coldata.width + coldata.margin

        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        for cell in self.cells:
            cell.draw(canvas, pos)


class TableColumnData:
    def __init__(
        self,
        *,
        flex=1,
        margin=0,
        divider: BorderSide = BorderSide(),
    ):
        self.flex = flex
        self.margin = margin

        self.divider = divider

        self.width = None


class MultiPageTable(MultiPageWidget):
    columns: list[TableColumnData]
    rows: list[TableRow]
    border: Border

    def __init__(
        self,
        *,
        columns: list[TableColumnData],
        rows: list[TableRow],
        heading: TableRow = None,
        border: Border = Border.only(left=BorderSide(), top=BorderSide()),
    ):
        super().__init__(None, None)

        self.columns = columns
        self.rows = [] if rows is None else rows
        self.border = border
        if heading:
            rows.insert(0, heading)
        for row in rows:
            row.parent = self

    def layout(self, constraints: BoxConstraints) -> Size:
        self._set_column_widths(constraints.max_width)

        remheight = DocInfo.page.height - self.page_offset.y
        height = 0
        y = 0
        for row in self.rows:
            try:
                child_size = row.layout(
                    BoxConstraints(0, 0, constraints.max_width, remheight)
                )
            except OverFlowError:
                height += remheight
                remheight = DocInfo.page.height
                y = 0
                child_size = row.layout(
                    BoxConstraints(0, 0, constraints.max_width, remheight)
                )

            row.offset = Position(0, y)
            remheight -= child_size.height
            height += child_size.height
            y += child_size.height

        size = Size(constraints.max_width, height)
        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        remheight = DocInfo.page.height - self.page_offset.y
        for row in self.rows:
            if row.height > remheight:
                canvas.showPage()
                new_ppos = self.parent.page_broken()
                self.offset = Position(0, 0)
                pos = new_ppos.resolve(self.offset)
                remheight = DocInfo.page.height
            row.draw(canvas, pos)
            remheight -= row.height

    def _set_column_widths(self, width):
        for col in self.columns:
            width -= col.margin
        frac = width / self._flex

        for col in self.columns:
            colwidth = frac * col.flex
            col.width = colwidth

    @property
    def _flex(self):
        flex = 0
        for col in self.columns:
            flex += col.flex
        return flex


class Table(Widget):
    columns: list[TableColumnData]
    rows: list[TableRow]
    border: Border

    def __init__(
        self,
        *,
        columns: list[TableColumnData],
        rows: list[TableRow] = None,
        heading: TableRow = None,
        border: Border = Border.only(left=BorderSide(), top=BorderSide()),
    ):
        super().__init__(None, None)

        self.border = border
        self.columns = columns
        self.rows = [] if rows is None else rows
        self.allowed_rows: list[TableRow] = []
        if heading:
            rows.insert(0, heading)
        for row in rows:
            row.parent = self

    def layout(self, constraints: BoxConstraints) -> Size:
        size = Size(constraints.max_width, 0)
        self._set_column_widths(constraints.max_width)
        rem_height = constraints.max_height
        y = 0
        for row in self.rows:
            row_size = row.layout(
                BoxConstraints(0, 0, constraints.max_width, rem_height)
            )
            if rem_height < row_size.height:
                break

            self.allowed_rows.append(row)

            row.offset = Position(0, y)

            y += row_size.height + row.margin
            rem_height -= row_size.height

        size.height = y
        self.set_size(size)

        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        for row in self.allowed_rows:
            row.draw(canvas, pos)
        self._draw_self(canvas, pos)

    def _draw_self(self, canvas: Canvas, pos: Position):
        if self.border.top.width > 0:
            side = self.border.top
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            canvas.line(pos.x, pos.y, pos.x + self.width, pos.y)

        if self.border.right.width > 0:
            side = self.border.right
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            x = pos.x + self.width - side.width / 2
            canvas.line(x, pos.y, x, pos.y - self.height)

        if self.border.bottom.width > 0:
            side = self.border.bottom
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            y = pos.y - self.height + side.width / 2
            canvas.line(pos.x, y, pos.x + self.width, y)

        if self.border.left.width > 0:
            side = self.border.left
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            x = pos.x + side.width / 2
            canvas.line(x, pos.y, x, pos.y - self.height)

    def _set_column_widths(self, width):
        for col in self.columns:
            width -= col.margin
        frac = width / self._flex

        for col in self.columns:
            colwidth = frac * col.flex
            col.width = colwidth

    @property
    def _flex(self):
        flex = 0
        for col in self.columns:
            flex += col.flex
        return flex
