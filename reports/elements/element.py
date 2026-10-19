"""
The smallest pieces of a report. Every element turns itself into LaTeX; sections are built from them.
"""


class Element:
    def to_tex(self) -> str:
        raise NotImplementedError


class Raw(Element):
    """LaTeX written by hand: prose, equations."""

    def __init__(self, tex: str):
        self.tex = tex

    def to_tex(self) -> str:
        return self.tex
