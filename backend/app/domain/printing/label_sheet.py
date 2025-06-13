from typing import Iterable, List, Set, Tuple
from labels import Specification


class LabelSheet:
    """Class containing the required information for label sheets

    Order of the sheet (for usage)
    List of used labels
    Offering two ways to define used labels:
      - Start column, start row
      - Single pairs
    """

    def __init__(self, sheet_number: int, specs: Specification):
        self.__sheet_number = sheet_number
        self.__used_labels: Set[Tuple[int, int]] = set()
        self.__max_row = specs.rows
        self.__max_col = specs.columns

    def start_at(self, start_row: int, start_col: int):
        """Sets up the sheet so that it starts with a label in the start_row and start_column provided.

        Rows are printed first

        Args:
          start_row (int): Row of the first available label
          start_col (int): Column of the first available label
        """
        self.__validate_position(start_row, start_col)

        self.__used_labels.clear()

        # mark all fully used columns
        for r in range(1, start_row):
            for c in range(1, self.__max_col + 1):
                self.__used_labels.add((r, c))

        # mark the rows before the start row in start column
        for c in range(1, start_col):
            self.__used_labels.add((start_row, c))

    def __validate_position(self, start_row, start_col):
        if start_row < 1 or start_row > self.__max_row:
            raise IndexError(f"Invalid starting row: {start_row}")
        if start_col < 1 or start_col > self.__max_col:
            raise IndexError(f"Invalid starting column: {start_col}")

    def mark_as_used(self, row: int, col: int):
        """Mark one label position as used

        Args:
            row (int): row index of the label that has been used
            col (int): column index of the label that has been used
        """
        self.__validate_position(row, col)
        self.__used_labels.add((row, col))

    @property
    def used_labels(self) -> Iterable[Tuple[int, int]]:
        """list of used labels
        Returns:
            Iterable[Tuple[int, int]]: used labels
        """
        return self.__used_labels

    @property
    def available_labels(self) -> int:
        return (self.__max_col * self.__max_row) - len(self.__used_labels)
