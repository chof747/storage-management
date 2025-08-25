from dataclasses import dataclass

from app.models.printable import Printable


@dataclass
class PartsboxItem(Printable):
    """
    Represents a part from Partsbox.io with attributes for display and processing.
    This class is not tied to a database and is used as a plain Python object.
    """

    id: str
    name: str
    description: str
    total_stock: int
    storage_place: str
    material_part_number: str

    def to_dict(self):
        """
        Convert the PartsboxItem instance to a dictionary.

        :return: A dictionary representation of the instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "total_stock": self.total_stock,
            "storage_place": self.storage_place,
            "material_part_number": self.material_part_number,
        }
