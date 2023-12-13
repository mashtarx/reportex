import shutil
import json
import pathlib
import abc
import enum
from dataclasses import dataclass
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportex.exceptions import FontError


INFINITY = 10000
DISC = 1 / 5000


@dataclass
class BoxConstraints:
    min_width: float
    min_height: float
    max_width: float
    max_height: float


class EdgeInset:
    top: float
    bottom: float
    left: float
    right: float

    def __init__(
        self, *, left: float = 0, right: float = 0, top: float = 0, bottom: float = 0
    ):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    @classmethod
    def symmetric(cls, *, horizontal: float = 0, vertical: float = 0) -> "EdgeInset":
        return cls(left=horizontal, right=horizontal, top=vertical, bottom=vertical)

    @classmethod
    def all(cls, value: float = 4) -> "EdgeInset":
        return cls(left=value, right=value, top=value, bottom=value)

    def __repr__(self):
        return (
            f"EdgeInset(left={self.left}, top={self.top}, right={self.right},"
            f"bottom={self.bottom})"
        )


@dataclass
class Size:
    width: float
    height: float


@dataclass
class Position:
    x: float
    y: float

    def resolve(self, pos: "Position") -> "Position":
        return Position(x=self.x + pos.x, y=self.y - pos.y)

    def resolvex(self, x) -> float:
        return self.x + x

    def resolvey(self, y) -> float:
        return self.y - y


class DocInfo:
    page: Size = Size(A4[0], A4[1])


def Rect(canvas: Canvas, x, y, width, height):
    canvas.rect(x, y - height, width, height)


class Axis(enum.Enum):
    HORIZONTAL = enum.auto()
    VERTICAL = enum.auto()


class Alignment(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP_CENTER = enum.auto()
    LEFT_MIDDLE = enum.auto()
    RIGHT_MIDDLE = enum.auto()
    BOTTOM_CENTER = enum.auto()
    CENTER = enum.auto()


class CrossAxisAlignment(enum.Enum):
    START = enum.auto()
    END = enum.auto()
    CENTER = enum.auto()


class MainAxisAlignment(enum.Enum):
    START = enum.auto()
    END = enum.auto()
    CENTER = enum.auto()
    SPACE_AROUND = enum.auto()
    SPACE_BETWEEN = enum.auto()


class Widget(abc.ABC):
    width: float | None
    height: float | None
    offset: float | None
    canvas: Canvas

    parent: "Widget"

    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height
        self.offset = None
        self.parent = None

    def layout(self, constraints: BoxConstraints) -> Size:
        ...

    def draw(self, canvas: Canvas, parent_pos: Position):
        ...

    def set_size(self, size: Size):
        self.width = size.width
        self.height = size.height

    def set_position(self, pos: Position):
        self.position = pos


class SingleChildWidget(Widget):
    child: Widget | None
    client_origin: Position

    def __init__(self, child: Widget, width, height):
        super().__init__(width, height)
        self.child = child
        if child:
            child.parent = self

    @abc.abstractproperty
    def client_width(self):
        ...

    @abc.abstractproperty
    def client_height(self):
        ...

    @abc.abstractproperty
    def client_origin(self):
        return Position(0, 0)


class MultiPageWidget(Widget):
    page_offset: Position

    def __init__(self, width=None, height=None):
        super().__init__(width, height)
        self.page_offset = Position(0, 0)


class MultiPageSingleWidget(MultiPageWidget):
    ...


class MultiPageMultiChildrenWidget(MultiPageWidget):
    ...


class MultiChildrenWidget(Widget):
    children: list[Widget]
    client_origin: Position

    def __init__(self, children: list[Widget], width=None, height=None):
        super().__init__(width, height)
        self.children = children
        for child in children:
            child.parent = self

    @abc.abstractproperty
    def client_width(self):
        ...

    @abc.abstractproperty
    def client_height(self):
        ...

    @abc.abstractproperty
    def client_origin(self):
        return Position(0, 0)


class Color:
    def __init__(self, r, g, b, a=255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def normalize(self) -> "Color":
        return Color(self.r / 255, self.g / 255, self.b / 255, self.a / 255)


class Colors:
    red = Color(255, 0, 0, 255)
    green = Color(0, 255, 0, 255)
    blue = Color(0, 0, 255, 255)
    white = Color(255, 255, 255, 255)
    black = Color(0, 0, 0, 255)
    grey = Color(128, 128, 128, 255)
    metalgrey = Color(128, 133, 137, 255)
    silver = Color(192, 192, 192, 255)
    orange = Color(255, 87, 51, 255)
    brown = Color(165, 42, 42, 255)
    yellow = Color(255, 255, 0, 255)
    cyan = Color(0, 255, 255, 255)
    amber = Color(255, 191, 0, 255)
    crimson = Color(220, 20, 60, 255)
    darkred = Color(139, 0, 0, 255)
    khaki = Color(240, 230, 140, 255)
    violet = Color(238, 130, 238, 255)
    magenta = Color(255, 0, 255, 255)
    purple = Color(128, 0, 128, 255)
    indigo = Color(75, 0, 130, 255)
    olive = Color(128, 128, 0, 255)
    cadetblue = Color(95, 158, 160, 255)
    steelblue = Color(70, 130, 180, 255)
    skyblue = Color(135, 206, 235, 255)
    maroon = Color(128, 0, 0, 255)
    wheet = Color(245, 222, 179, 255)


class BorderSide:
    def __init__(self, *, width=1, color: Color = Colors.black):
        self.width = width
        self.color = color

    @classmethod
    def zero(cls):
        return cls(width=0, color=Colors.white)


class Border:
    def __init__(
        self,
        *,
        left: BorderSide | None = None,
        top: BorderSide | None = None,
        right: BorderSide | None = None,
        bottom: BorderSide | None = None,
    ):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @classmethod
    def zero(cls):
        return cls(
            left=BorderSide.zero(),
            top=BorderSide.zero(),
            right=BorderSide.zero(),
            bottom=BorderSide.zero(),
        )

    @classmethod
    def only(
        cls,
        left: BorderSide = BorderSide.zero(),
        top: BorderSide = BorderSide.zero(),
        right: BorderSide = BorderSide.zero(),
        bottom: BorderSide = BorderSide.zero(),
    ):
        return cls(left=left, top=top, right=right, bottom=bottom)

    @classmethod
    def all(cls, side: BorderSide = BorderSide()):
        return cls(left=side, top=side, right=side, bottom=side)

    def is_all_sided(self) -> bool:
        # breakpoint()
        sd = BorderSide()
        for side in [self.left, self.top, self.right, self.bottom]:
            if not side:
                return False
            elif side.color != sd.color or side.width != sd.width:
                return False

        return True

    @property
    def sides(self) -> list[BorderSide]:
        return [self.left, self.top, self.right, self.bottom]


class Side(enum.Enum):
    LEFT = enum.auto()
    TOP = enum.auto()
    RIGHT = enum.auto()
    BOTTOM = enum.auto()


def available_fonts() -> list[str]:
    ...


BASE_DIR = pathlib.Path(__file__).parent.parent


class FontsManager:
    __fonts = []
    canvas: Canvas = None
    font_dir = BASE_DIR / "reportex" / "fonts"

    @classmethod
    def init(cls):
        ttfs = cls._load_ttf_fonts()
        for fnt in ttfs:
            cls._register_font(fnt["name"], pathlib.Path(cls.font_dir / fnt["fname"]))
            cls.__fonts.append(fnt["name"])

    @staticmethod
    def _load_ttf_fonts() -> list[dict]:
        path = BASE_DIR / "reportex" / "fonts" / "conf.json"
        with open(path) as f:
            conf = json.load(f)
        return conf["registered"]

    @classmethod
    def _register_font(self, name, path):
        pdfmetrics.registerFont(TTFont(name, path))

    @classmethod
    def register_ttf(cls, name, path: pathlib.Path):
        if not (
            path.exists
            and path.is_file
            and path.suffix != ""
            and path.suffix[1:] == "ttf"
        ):
            raise FontError("invalid tff file path")
        fl = pathlib.Path(shutil.copy(path, cls.font_dir))
        conf = cls.font_dir / "conf.json"
        with open(conf) as f:
            cont = json.load(f)

        obj = {"name": name, "fname": fl.name}
        cont["registered"].append(obj)

        with open(conf, "w") as f:
            json.dump(cont, f)

    @classmethod
    @property
    def registered_fonts(cls):
        conf = cls.font_dir / "conf.json"
        with open(conf) as f:
            cont = json.load(f)
        return cont["registered"]

    @classmethod
    @property
    def all_fonts(cls):
        canv = Canvas("")
        bltin = canv.getAvailableFonts()
        rg = cls.registered_fonts
        for fnt in rg:
            bltin.append(fnt["name"])
        return bltin


FontsManager.init()
