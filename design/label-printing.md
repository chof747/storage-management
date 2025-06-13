# Idea

Print labels for the storage bins for the hardware and consumable items

Use inkjet/laserjet labels

## Labels to use

- For small bins: [L4730REV-25
 from Avery][label_small]
- Bigger labels for bigger containers

## Features

- Define a *label printing strategy* which is attached to *storage bin classes*.
- Print the labels in batch (queing them)
- Prints can start at any position on a *label sheet*

[label_small]: https://www.avery-zweckform.com/produkt/universal-etiketten-l4730rev-25/retailers/de/de

## Solution

### Labelprinting

The [pylabels](https://pypi.org/project/pylabels/) library is perfectly suited for this:

- can specify label grids
- Allows sophisticated drawings
- can use partly used sheets

### Class Structure

- The way labels are printed will be defined by subclasses of `PrintStrategyBase`. They will determine
the specification of the label page and also contain the function to actually draw a label.
  - Data will be handed over as a standard python dictionary to keep it flexible for various types
  - Printing strategies will be registered and created by a factory method of the base class

- The labels will be printed by the `Printer` class which utilizes a specific subclass of
  `PrintStrategyBase` to get the specifics and printing method

- Label sheets will also be defined by the `LabelSheet` which contains the number of the sheet
  and a list of pairs of already used labels. The sheets will then be used according to their number
  to print all the selected objects.
  - Sheets also receives the specifications for the label

- The printable items will all be of `Base` class and the Mixin `Printable` this mixin will contain the queued_fo
  printing attribute and functions to mark and unmark it for queued for printing

### Sequence

1. The printer receives the strategies and initializes a list of useable sheets.
2. Sheets can then be added to the printer by the calling function and also labels
   can be marked as used.
3. When the label sheets are set the printer can print a series of labels by received as a list
   of printable items
4. The created sheets are presented as a pdf for the user to view and download
5. After the label is added to the sheet and the sheet is displayed the items printed are unmarked as queued
   for printing
