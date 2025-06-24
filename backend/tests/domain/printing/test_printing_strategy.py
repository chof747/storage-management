from pytest import fixture

from app.domain.printing import get_all_printing_strategies, PrintStrategyBase
from reportlab.pdfbase.pdfmetrics import stringWidth
from tests.utils.helpers import generate_random_text


@fixture
def newprintingtrategy() -> PrintStrategyBase:
    from .new_printing_strategy import TestPrintingStrategy

    return PrintStrategyBase.create_printing_strategy("Test Strategy")


def test_get_default_printing_strategies():
    strategies = get_all_printing_strategies()

    assert "Gridfinity" in strategies
    assert "Storage Box" in strategies


def test_get_new_printing_strategy(newprintingtrategy):

    ts = newprintingtrategy.__class__

    strategies = get_all_printing_strategies()
    assert ts.name in strategies


def test_default_border(newprintingtrategy):
    strategy = PrintStrategyBase.create_printing_strategy("Gridfinity")
    assert False == strategy.draw_border

    assert newprintingtrategy.draw_border


def test_shrinking_text(newprintingtrategy):

    fs = 12
    min_fs = 9
    fn = "Helvetica"
    max_tw = newprintingtrategy.labelspecs.label_width

    def generate_text_that_is_too_long() -> str:
        n = 3
        text = generate_random_text(n)

        while True:
            tw = stringWidth(text, fn, fs)
            if tw > max_tw:
                break
            else:
                n = n + 3
                text = generate_random_text(n)

        return text

    line = generate_text_that_is_too_long()
    print(line)
    font_size = newprintingtrategy.shrink_font_if_needed(
        line, fs, min_fs, newprintingtrategy.labelspecs.label_width, fn
    )
    assert font_size < fs

    line = "A"
    font_size = newprintingtrategy.shrink_font_if_needed(
        line, fs, min_fs, newprintingtrategy.labelspecs.label_width, fn
    )
    assert font_size == fs

    line = generate_random_text(1000)
    font_size = newprintingtrategy.shrink_font_if_needed(
        line, fs, min_fs, newprintingtrategy.labelspecs.label_width, fn
    )
    assert font_size == min_fs
