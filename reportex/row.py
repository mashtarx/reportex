from reportex.core import (
    MultiChildrenWidget,
    MainAxisAlignment,
    CrossAxisAlignment,
    Size,
    Position,
    BoxConstraints,
)
from reportex.exceptions import OverFlowError

from reportex.widgets import Expanded, Canvas


class Row(MultiChildrenWidget):
    def __init__(
        self,
        children,
        main_axis_alignment: MainAxisAlignment = MainAxisAlignment.CENTER,
        cross_axis_alignment: CrossAxisAlignment = CrossAxisAlignment.CENTER,
    ):
        super().__init__(children, None, None)
        self.main_axis_alignment = main_axis_alignment
        self.cross_axis_alignment = cross_axis_alignment

    @property
    def client_width(self):
        return self.width

    @property
    def client_height(self):
        return self.height

    @property
    def client_origin(self):
        return super().client_origin

    def _get_total_flex(self):
        flex = 0
        for child in self.children:
            if isinstance(child, Expanded):
                flex += child.flex
        return flex

    def layout(self, constraints: BoxConstraints) -> Size:
        size = Size(constraints.max_width, 0)
        if len(self.children) == 0:
            self.set_size(Size(0, 0))
            return size

        remwidth = constraints.max_width

        expanded: list[Expanded] = []
        flex_total = self._get_total_flex()

        for child in self.children:
            if isinstance(child, Expanded):
                expanded.append(child)
                continue
            child_size = child.layout(
                BoxConstraints(0, 0, remwidth, constraints.max_height)
            )
            if remwidth == 0 and (child.width > 0 or child.height > 0):
                breakpoint()
                raise OverFlowError(f"insufficient space for {child}")

            if child_size.height > size.height:
                size.height = child_size.height

            if (
                child_size.width > remwidth
                or child_size.height > constraints.max_height
            ):
                raise OverFlowError(f"insufficient space for {child}")

            remwidth -= child_size.width

        if len(expanded) > 0:
            width_frac = remwidth / flex_total
            for exp in expanded:
                wdth = width_frac * exp.flex
                exp_size = exp.layout(
                    BoxConstraints(0, 0, wdth, constraints.max_height)
                )
                if exp_size.height > size.height:
                    size.height = exp_size.height

                diff = remwidth - exp_size.width
                if abs(diff) < 1 / 1000:
                    exp.width = remwidth

                # if abs(diff) < 1/1000 or exp_size.height > constraints.max_height:
                #     breakpoint()
                #     raise OverFlowError()
                remwidth -= wdth

        match (self.main_axis_alignment):
            case MainAxisAlignment.START:
                self._set_offsets(0, size, constraints)
            case MainAxisAlignment.END:
                x = remwidth
                self._set_offsets(x, size, constraints)
            case MainAxisAlignment.CENTER:
                self._set_offsets(remwidth / 2, size, constraints)
            case MainAxisAlignment.SPACE_AROUND:
                around_space = remwidth / (len(self.children) + 1)
                self._set_space_around_offset(0, size, around_space, constraints)
            case MainAxisAlignment.SPACE_BETWEEN:
                if len(self.children) > 2:
                    between_space = remwidth / (len(self.children) - 1)
                else:
                    between_space = remwidth
                self._set_space_between_offset(0, size, between_space, constraints)

        self.set_size(size)
        return size

    def _set_offsets(self, x: float, size: Size, constraints: BoxConstraints):
        rwidth = constraints.max_width
        for child in self.children:
            y = 0
            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    y = (size.height - child.height) / 2
                case CrossAxisAlignment.END:
                    y = size.height - child.height
            child.offset = Position(x + (constraints.max_width - rwidth), y)
            rwidth -= child.width

    def _set_space_between_offset(
        self, x: float, size: Size, space: float, constraints: BoxConstraints
    ):
        rwidth = constraints.max_width

        for i, child in enumerate(self.children):
            y = 0

            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    y = (size.width - child.width) / 2
                case CrossAxisAlignment.END:
                    y = size.width - child.width

            if i == 0:
                child.offset = Position(x + (constraints.max_width - rwidth), y)
                rwidth -= child.width
            else:
                child.offset = Position(x + space + (constraints.max_width - rwidth), y)
                rwidth -= child.width + space

    def _set_space_around_offset(
        self, x: float, size: Size, space: float, constraints: BoxConstraints
    ):
        rwidth = constraints.max_width
        for child in self.children:
            y = 0
            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    y = (size.height - child.height) / 2
                case CrossAxisAlignment.END:
                    y = size.height - child.height
            child.offset = Position(x + space + (constraints.max_width - rwidth), y)
            rwidth -= child.width + space

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        for child in self.children:
            child.draw(canvas, pos)
