# Partsbox integration

## Idea

Integrate [partsbox.io](https://partsbox.com/) into the storage manager to:

- List all parts in the partboxio in the storage manager
- Integrate the Storage places of partsbox io with the ones in storage manager (via names)
- Allow printing of labels
- Use as parts in the future projects and BOM feature

## Solution

[partsbox.io](https://partsbox.com/) can be integrated via an [API](https://partsbox.com/api.html).

The integration will implement the following operations:

### 1. List all parts

Similar to the `Hardware` page of the solution a new `Electronic Parts` page will be created which displays and filters all the items from partsbox io in a read-only manner with the actions:

- Goto respective page on partsbox
- Mark for label printing
- (future) Add to project

The parts will be displayed with the following attributes:

- Part Name
- Description (abbreviated)
- Total Stock (as the some of all stock entries)
- Storage Place (the name of the storage that contains the most stock)
