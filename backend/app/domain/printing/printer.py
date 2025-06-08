from typing import Dict, List, Union
from .label_sheet import LabelSheet
from .print_strategy import PrintStrategyBase
from labels import Sheet
from io import BytesIO


class Printer:
    """The label printer class

    This class is using printing strategies to determine the specification of the labels
    and printing single labels for specific items

    It is receiving a set of items as dictionaries, a starring position and is then
    creating a pdf with the labels filled
    """

    def __init__(self, strategy: PrintStrategyBase, sheets: List[LabelSheet] = []):
        self.__strategy = strategy
        self.__sheets = sheets
        self.__items: List[Dict[str, str]] = []
        self.__maxlabels = sum(sheet.available_labels for sheet in sheets)

    def add(self, items: List[Dict[str, str]]) -> int:
        """Adds items to the list of items to print

        Args:
            items (List[Dict[str, str]]): the items to add

        Returns:
            int: number of added items
        """
        new_count = len(items)
        if new_count + len(self.__items) > self.__maxlabels:
            raise IndexError("Too many items for the specified sheets!")

        self.__items.extend(items)
        return new_count

    def print(self, output: str | None = None) -> Union[BytesIO, None]:

        document = Sheet(
            self.__strategy.labelspecs,
            self.__strategy.draw_label,
            border=self.__strategy.draw_border,
        )

        sheet_num = 0
        left_labels_on_sheet = self.__new_sheet(document, sheet_num)

        for item in self.__items:
            # TODO: Add copies to printing strategy and use this in max_label count function
            document.add_label(item)
            left_labels_on_sheet = left_labels_on_sheet - 1
            if 0 == left_labels_on_sheet:
                sheet_num = sheet_num + 1
                left_labels_on_sheet = self.__new_sheet(document, sheet_num)

        result = BytesIO() if output is None else output
        document.save(result)

        return result if output is None else output

    def __new_sheet(self, document, sheet_num):
        document.partial_page(sheet_num + 1, self.__sheets[sheet_num].used_labels)
        return self.__sheets[sheet_num].available_labels
