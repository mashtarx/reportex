class ReportexError(Exception):
    def __init__(self, msg="", *args: object) -> None:
        super().__init__(*args)

        self.msg = msg


class OverFlowError(ReportexError):
    ...


class FontError(ReportexError):
    ...
