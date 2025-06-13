from typing import List, Tuple
from pytest import raises
from app.domain.printing import LabelSheet, StorageBoxPrinter


def test_label_sheet_startat():
    expected: List[Tuple[int, int]] = [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
        (3, 1),
    ]

    sheet = LabelSheet(1, StorageBoxPrinter.labelspecs)
    sheet.start_at(3, 2)
    used_labels = sheet.used_labels
    assert len(used_labels) == 5
    for row, col in expected:
        assert any((row == r) & (col == c) for r, c in used_labels)

    assert 3 == sheet.available_labels


def test_label_sheet_markused():
    sheet = LabelSheet(1, StorageBoxPrinter.labelspecs)
    sheet.mark_as_used(3, 2)
    used_labels = sheet.used_labels
    assert len(used_labels) == 1
    assert all((3 == r) & (2 == c) for r, c in used_labels)
    assert 7 == sheet.available_labels


def test_label_sheet_row_validation():
    sheet = LabelSheet(1, StorageBoxPrinter.labelspecs)

    with raises(IndexError, match="Invalid starting row: 5"):
        sheet.mark_as_used(5, 1)
    with raises(IndexError, match="Invalid starting column: 3"):
        sheet.mark_as_used(1, 3)
    with raises(IndexError, match="Invalid starting row: 0"):
        sheet.mark_as_used(0, 3)
    with raises(IndexError, match="Invalid starting column: 0"):
        sheet.mark_as_used(1, 0)

    with raises(IndexError, match="Invalid starting row: 5"):
        sheet.start_at(5, 1)
    with raises(IndexError, match="Invalid starting column: 3"):
        sheet.start_at(1, 3)
