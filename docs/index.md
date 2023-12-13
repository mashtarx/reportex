# Introduction

![logo](assets/images/logo.jpg)

*Reportex* is a simple yet powerful framework for generating beautiful *PDFs* easily by composition.
*Reportex* is heavely inspired by ***flutter*** framework.
it is built on top of ***Reportlab***

## Installation

```
pip install reportex
```


## Basic Usage


create a python file main.py
```python title="main.py" linenums="1"
from reportex import Document, Page, Center, Text

def main():
    doc = Document(
        doc_name="doc.pdf",
        pages=[
            Page(
                child=Center(
                    child=Text("Hello World")
                )
            )
        ]
    )
    doc.create()

if __name__ == "__main__":
    main()
```

```cmd
python main.py
./doc.pdf
```

you get pdf like <a alt="" href="./assets/pdfs/hello_world.pdf" target="_blank">this </a>


Let's understand it line by line
```python title="main.py" linenums="1" hl_lines="1"
from reportex import Document, Page, Center, Text

def main():
    doc = Document(
        doc_name="doc.pdf",
        pages=[
            Page(
                child=Center(
                    child=Text("Hello World")
                )
            )
        ]
    )
    doc.create()

if __name__ == "__main__":
    main()
```
