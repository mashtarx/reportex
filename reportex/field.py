import enum

from reportex.container import Container
from reportex.text import Text, CtxFont
from reportex.core import (
    Border,
    Widget,
    INFINITY,
    MainAxisAlignment,
    CrossAxisAlignment,
    EdgeInset,
    Alignment,
    Color,
    Colors,
)
from reportex.widgets import Padding, SizedBox, Align
from reportex.row import Row
from reportex.column import Column


class LabeledFieldAlignment(enum.Enum):
    TOP_LEFT = enum.auto()
    TOP_CENTER = enum.auto()
    TOP_RIGHT = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    BOTTOM_LEFT = enum.auto()
    BOTTOM_CENTER = enum.auto()
    BOTTOM_RIGHT = enum.auto()


def LabledField(
    label: Widget,
    text: str = "",
    fill_color: Color = Colors.white,
    text_alignment: Alignment = Alignment.LEFT_MIDDLE,
    lable_side: LabeledFieldAlignment = LabeledFieldAlignment.LEFT,
    border: Border = Border.zero(),
    border_radius=True,
    space=5,
    content_padding=None,
) -> Widget:
    cpadding = (
        EdgeInset(top=2, bottom=1, left=2, right=1)
        if not content_padding
        else content_padding
    )
    ver_space = SizedBox(height=space)
    hor_space = SizedBox(width=space)
    widg = None
    field = Container(
        width=INFINITY,
        color=fill_color,
        border=border,
        border_radius=border_radius,
        child=Align(
            alignment=text_alignment,
            child=Padding(
                padding=cpadding,
                child=Text(text, font=CtxFont("Helvetica", 10)),
            ),
        ),
    )
    match (lable_side):
        case LabeledFieldAlignment.TOP_LEFT:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                cross_axis_alignment=CrossAxisAlignment.START,
                children=[label, ver_space, field],
            )
        case LabeledFieldAlignment.TOP_CENTER:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                cross_axis_alignment=CrossAxisAlignment.CENTER,
                children=[label, ver_space, field],
            )
        case LabeledFieldAlignment.TOP_RIGHT:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                cross_axis_alignment=CrossAxisAlignment.END,
                children=[label, ver_space, field],
            )
        case LabeledFieldAlignment.LEFT:
            widg = Row(
                main_axis_alignment=MainAxisAlignment.START,
                children=[label, hor_space, field],
            )
        case LabeledFieldAlignment.RIGHT:
            widg = Row(
                main_axis_alignment=MainAxisAlignment.START,
                children=[field, hor_space, label],
            )
        case LabeledFieldAlignment.BOTTOM_LEFT:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                cross_axis_alignment=CrossAxisAlignment.START,
                children=[field, ver_space, label],
            )
        case LabeledFieldAlignment.BOTTOM_CENTER:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                children=[field, ver_space, label],
            )
        case LabeledFieldAlignment.BOTTOM_RIGHT:
            widg = Column(
                main_axis_alignment=MainAxisAlignment.START,
                cross_axis_alignment=CrossAxisAlignment.END,
                children=[field, ver_space, label],
            )
    return widg
