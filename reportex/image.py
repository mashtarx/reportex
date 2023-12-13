import io
import json
import uuid
import requests
from PIL import Image as imagemod
from PIL.Image import Image as PilImage
from reportlab.pdfgen.canvas import Canvas

from reportex.core import Widget, Size, Position, BoxConstraints, Border, BASE_DIR


class Image(Widget):
    image: PilImage

    def __init__(
        self, *, image: PilImage, width=None, height=None, border: Border = None
    ):
        super().__init__(width, height)
        self.image: PilImage = image
        self.border = border
        self._opened_img = None

    @classmethod
    def from_file(
        cls,
        *,
        filename: str,
        width: float = None,
        height: float = None,
        border: Border = None
    ) -> "Image":
        img = imagemod.open(filename)
        return cls(image=img, width=width, height=height, border=border)

    @classmethod
    def from_network(
        cls,
        *,
        url: str,
        width: float = None,
        height: float = None,
        border: Border = None
    ) -> "Image":
        img = None
        with open(BASE_DIR / "reportex" / "cache" / "network_images.json") as f:
            cache = json.load(f)

        if cache.get(url):
            img = imagemod.open(BASE_DIR / "reportex" / "cache" / cache[url])

        else:
            resp = requests.get(url)
            if resp.status_code == 200:
                content = io.BytesIO(resp.content)
                img = imagemod.open(content)
                name = uuid.uuid4().hex + "." + img.format
                img.save(BASE_DIR / "reportex" / "cache" / name)
                with open(
                    BASE_DIR / "reportex" / "cache" / "network_images.json", "w"
                ) as f:
                    cache[url] = name
                    json.dump(cache, f)
            else:
                print("failed to get image from ", url)
            img = imagemod.open(BASE_DIR / "reportex" / "cache" / cache[url])

        return cls(image=img, width=width, height=height)

    @classmethod
    def from_memory(
        cls,
        *,
        buffer: bytes,
        width: float = None,
        height: float = None,
        border: Border = None
    ) -> "Image":
        ...

    def get_borders_size(self):
        w = h = 0
        if not self.border:
            return w, h
        if self.border.left:
            w += self.border.left.width
        if self.border.right:
            w += self.border.right.width

        if self.border.top:
            h += self.border.top.width
        if self.border.bottom:
            h += self.border.bottom.width

        return w, h

    def _client_size(self) -> Size:
        bw, bh = self.get_borders_size()
        if not self.width or not self.height:
            return Size(0, 0)
        return Size(self.width - bw, self.height - bh)

    def layout(self, constraints: BoxConstraints) -> Size:
        bw, bh = self.get_borders_size()
        size = Size(0, 0)
        if self.width and self.width <= (constraints.max_width - bw):
            size.width = self.width
        else:
            size.width = constraints.max_width - bw
        if self.height and self.height <= (constraints.max_height - bh):
            size.height = self.height
        else:
            size.height = constraints.max_height - bw

        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)

        if self.border:
            self._draw_borders(canvas, pos)
        bw, bh = self.get_borders_size()
        size = self._client_size()
        canvas.drawImage(
            self.image.filename,
            pos.x + bw / 2,
            pos.y - (bh / 2) - size.height,
            size.width,
            size.height,
        )

    def _draw_borders(self, canvas: Canvas, pos: Position):
        canvas.saveState()
        if self.border.is_all_sided():
            self._draw_all_sided_borders(canvas, pos)
        else:
            self._draw_sided_borders(canvas, pos)
        canvas.restoreState()

    def _draw_sided_borders(self, canvas: Canvas, pos: Position):
        if self.border.left:
            side = self.border.left
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            canvas.line(pos.x + 0.5, pos.y, pos.x + 0.5, pos.y - self.height)
        if self.border.top:
            side = self.border.top
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            canvas.line(pos.x, pos.y - 0.5, pos.x + self.width, pos.y - 0.5)
        if self.border.right:
            side = self.border.right
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            canvas.line(
                pos.x + self.width - 0.5,
                pos.y,
                pos.x + self.width - 0.5,
                pos.y - self.height,
            )
        if self.border.bottom:
            side = self.border.bottom
            canvas.setLineWidth(side.width)
            color = side.color.normalize()
            canvas.setStrokeColorRGB(color.r, color.g, color.b, color.a)
            canvas.line(
                pos.x,
                pos.y - self.height + 0.5,
                pos.x + self.width,
                pos.y - self.height + 0.5,
            )

    def _draw_all_sided_borders(self, canvas: Canvas, pos: Position):
        canvas.rect(
            pos.x + 0.5,
            pos.y - self.height + 0.5,
            self.width - 1,
            self.height - 1,
        )
