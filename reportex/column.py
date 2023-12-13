from reportex.core import (
    MultiChildrenWidget,
    MainAxisAlignment,
    CrossAxisAlignment,
    BoxConstraints,
    Size,
    Position,
)

from reportex.widgets import Expanded, Canvas

from reportex.exceptions import OverFlowError


class Column(MultiChildrenWidget):
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
        size = Size(0, constraints.max_height)
        if len(self.children) == 0:
            self.set_size(Size(0, 0))
            return size

        remheight = constraints.max_height

        expanded: list[Expanded] = []
        total_flex = self._get_total_flex()
        for child in self.children:
            if isinstance(child, Expanded):
                expanded.append(child)
                continue

            child_size = child.layout(
                BoxConstraints(0, 0, constraints.max_width, remheight)
            )
            if remheight == 0 and (child.width > 0 or child.height > 0):
                raise OverFlowError(f"insufficient space for {child}")
            if child_size.width > size.width:
                size.width = child_size.width

            if (
                child_size.height > remheight
                or child_size.width > constraints.max_width
            ):
                raise OverFlowError(f"insufficient space for {child}")

            remheight -= child_size.height

        if len(expanded) > 0:
            height_frac = remheight / total_flex
            for exp in expanded:
                ht = height_frac * exp.flex
                exp_size = exp.layout(BoxConstraints(0, 0, constraints.max_width, ht))
                if exp_size.width > size.width:
                    size.width = exp_size.width
                if (
                    exp_size.height > remheight
                    or exp_size.width > constraints.max_width
                ):
                    raise OverFlowError()
                remheight -= ht

        match (self.main_axis_alignment):
            case MainAxisAlignment.START:
                self._set_offsets(size, 0, constraints)
            case MainAxisAlignment.END:
                y = remheight
                self._set_offsets(size, y, constraints)
            case MainAxisAlignment.CENTER:
                self._set_offsets(size, remheight / 2, constraints)
            case MainAxisAlignment.SPACE_AROUND:
                around_space = remheight / (len(self.children) + 1)
                self._set_space_around_offset(size, 0, around_space, constraints)
            case MainAxisAlignment.SPACE_BETWEEN:
                if len(self.children) > 2:
                    between_space = remheight / (len(self.children) - 1)
                else:
                    between_space = remheight
                self._set_space_between_offset(size, 0, between_space, constraints)

        self.set_size(size)
        return size

    def _set_offsets(self, size: Size, y, constraints: BoxConstraints):
        rheight = constraints.max_height
        for child in self.children:
            x = 0
            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    x = (size.width - child.width) / 2
                case CrossAxisAlignment.END:
                    x = size.width - child.width
            child.offset = Position(x, y + (constraints.max_height - rheight))
            rheight -= child.height

    def _set_space_between_offset(
        self, size: Size, y: float, space: float, constraints: BoxConstraints
    ):
        rheight = constraints.max_height

        for i, child in enumerate(self.children):
            x = 0

            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    x = (size.width - child.width) / 2
                case CrossAxisAlignment.END:
                    x = size.width - child.width

            if i == 0:
                child.offset = Position(x, y + (constraints.max_height - rheight))
                rheight -= child.height
            else:
                child.offset = Position(
                    x, y + space + (constraints.max_height - rheight)
                )
                rheight -= child.height + space

    def _set_space_around_offset(
        self, size: Size, y: float, space: float, constraints: BoxConstraints
    ):
        rheight = constraints.max_height
        for child in self.children:
            x = 0
            match (self.cross_axis_alignment):
                case CrossAxisAlignment.CENTER:
                    x = (size.width - child.width) / 2
                case CrossAxisAlignment.END:
                    x = size.width - child.width
            child.offset = Position(x, y + space + (constraints.max_height - rheight))
            rheight -= child.height + space

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        for child in self.children:
            child.draw(canvas, pos)
