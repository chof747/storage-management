from typing import Dict, List, Union
from .label_sheet import LabelSheet
from .print_strategy import PrintStrategyBase
from app.models.printable import Printable
from labels import Sheet
from io import BytesIO
from app.schemas.label_printing import LabelSheet as LabelSheetDefinition


class Printer:
    """The label printer class

    This class is using printing strategies to determine the specification of the labels
    and printing single labels for specific items

    It is receiving a set of items as dictionaries, a starring position and is then
    creating a pdf with the labels filled
    """

    @classmethod
    def create_printer(
        cls, strategy: str, sheet_definitions: List[LabelSheetDefinition]
    ):
        """Create a printer based on a specific printing strategy and
        starting positions for sheets
        """

        printing_strategy = PrintStrategyBase.create_printing_strategy(strategy)

        sheets: List[LabelSheet] = []
        n = 1
        for sheet_def in sheet_definitions:
            sheet = LabelSheet(n, printing_strategy.labelspecs)
            sheet.start_at(sheet_def.start_pos.row, sheet_def.start_pos.col)
            sheets.append(sheet)
            n = n + 1

        return Printer(printing_strategy, sheets)

    def __init__(self, strategy: PrintStrategyBase, sheets: List[LabelSheet] = []):
        self.__strategy = strategy
        self.__sheets = sheets
        self.__items: List[Printable] = []
        self.__maxlabels = sum(sheet.available_labels for sheet in sheets)

    def add(self, items: List[Printable]) -> int:
        """Adds items to the list of items to print

        Args:
            items (List[Printable]): the items to add - items must be instances of Printable
                                     and the queued_for_printing field must be True

        Returns:
            int: number of added items
        """
        to_be_added = [i for i in items if i.queued_for_printing]
        new_count = len(to_be_added)
        if new_count + len(self.__items) > self.__maxlabels:
            raise IndexError("Too many items for the specified sheets!")

        self.__items.extend(to_be_added)
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
            document.add_label(item.as_dict())
            left_labels_on_sheet = left_labels_on_sheet - 1
            if 0 == left_labels_on_sheet:
                sheet_num = sheet_num + 1
                left_labels_on_sheet = self.__new_sheet(document, sheet_num)

        result = BytesIO() if output is None else output
        document.save(result)

        self.__unset_all_from_printing_queue()

        return result if output is None else output

    def __new_sheet(self, document, sheet_num):
        document.partial_page(sheet_num + 1, self.__sheets[sheet_num].used_labels)
        return self.__sheets[sheet_num].available_labels

    def __unset_all_from_printing_queue(self):
        for item in self.__items:
            item.unset_for_printing()
