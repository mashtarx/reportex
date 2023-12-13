import reportlab.pdfbase.pdfmetrics as metrics


from reportex.core import Widget, Canvas, Position, BoxConstraints, Size


class CtxFont:
    def __init__(self, name, size):
        self.name = name
        self.size = size


class Text(Widget):
    font: CtxFont = CtxFont("Helvetica", 10)

    def __init__(self, text: str, font=None, word_space=1):
        super().__init__(None, None)
        self.text: str = text

        self._line_width = 0
        self.calc_lines = 1
        self._lines = []
        self._rem_space = []
        self.word_count = []
        self._top_offset = 3

        if font:
            self.font = font
        self.leading = self.line_height
        self.word_space = word_space

    @property
    def line_height(self):
        asc, dsc = self.get_ascent_decent()
        return asc + dsc

    def word_width(self, string):
        return metrics.stringWidth(string, self.font.name, self.font.size)

    def get_ascent_decent(self):
        ascent = metrics.getAscent(self.font.name, self.font.size)
        descent = metrics.getDescent(self.font.name, self.font.size)
        return ascent, -descent

    @property
    def space_width(self):
        return metrics.stringWidth(" ", self.font.name, self.font.size)

    def _wrap_word(self, word) -> list[str]:
        # breakpoint()
        width = self._line_width
        words = []
        nword = ""
        for c in word:
            new = nword + c
            if self.word_width(new) > width:
                words.append(nword)
                nword = c
            else:
                nword = new
        if nword:
            words.append(nword)
        return words

    def _wrap(self, width) -> list[str]:
        # breakpoint()
        lines = []
        words = []
        for w in self.text.split():
            if self.word_width(w) <= self._line_width:
                words.append(w)
            else:
                words.extend(self._wrap_word(w))

        space_left = width
        line = []
        wcount = 1
        for ind, word in enumerate(words):
            wwidth = self.word_width(word) + self.space_width

            if wwidth <= space_left:
                line.append(word + " ")
                space_left -= self.word_width(word) + self.space_width

            elif self.word_width(word) <= space_left:
                line.append(word)
                space_left -= self.word_width(word)

            else:
                lines.append("".join(line))
                self._rem_space.append(space_left)
                self.word_count.append(wcount)
                wcount = 1
                line = []
                line.append(word + " ")
                space_left = width
                space_left -= self.word_width(word) + self.space_width
            wcount += 1

        if line:
            lines.append("".join(line))
            self._rem_space.append(space_left)
        if wcount > 1:
            self.word_count.append(wcount)

        self._lines = lines

    def _get_clipped(self, height) -> list[str]:
        asc, dsc = self.get_ascent_decent()
        line_height = asc + dsc
        result = []
        for line in self._lines:
            if height >= line_height:
                result.append(line)
            height -= line_height
        return result

    @property
    def wrapped(self):
        return "\n".join(self._lines)

    @property
    def no_lines(self):
        return len(self._lines)

    def layout(self, constraints: BoxConstraints):
        w = constraints.max_width
        self._line_width = w
        self._wrap(self._line_width)
        if self.word_width(self.text) < w:
            w = self.word_width(self.text)

        height = (
            self.line_height if self.no_lines == 1 else self.no_lines * self.line_height
        )

        h = height if height <= constraints.max_height else constraints.max_height

        size = Size(w, h)
        self.set_size(size)
        return size

    def draw(self, canvas: Canvas, parent_pos: Position):
        pos = parent_pos.resolve(self.offset)
        asc, _ = self.get_ascent_decent()
        obj = canvas.beginText(pos.x, pos.y - asc)

        last_ind = len(self._lines) - 1
        obj.setFont(self.font.name, self.font.size, leading=self.leading)
        for ind, line in enumerate(self._get_clipped(self.height)):
            wspace = self.word_space
            line = line.rstrip()

            """distribute the remaining space of each line"""

            if ind != last_ind:
                wc = self.word_count[ind]
                if wc > 2:
                    wc -= 2
                rem = self._rem_space[ind]
                frac = rem / wc
                wspace = frac
                obj.setWordSpace(wspace)

            obj.textLine(line)
            obj.setWordSpace(0)
        canvas.drawText(obj)


if __name__ == "__main__":
    font = CtxFont("Helvetica", 1)
    Text("hello world")
