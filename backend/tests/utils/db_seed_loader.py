import csv
from typing import Type
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import Boolean, Float, Integer, String, inspect


def parse_value(value: str, column_type):
    """Parse values from csv to database"""

    if isinstance(column_type, Boolean):
        # Accept '1', '0', 'true', 'false' (case-insensitive)
        if value.lower() in ("1", "true"):
            return True
        elif value.lower() in ("0", "false"):
            return False
        else:
            raise ValueError(f"Cannot convert {value!r} to boolean")
    elif isinstance(column_type, Float):
        return float(value)
    elif isinstance(column_type, Integer):
        return int(value)
    elif isinstance(column_type, String) and "NULL" == value:
        return None
    return value  # default to string


def load_csv_to_model(session: Session, csv_path: Path, model: Type):
    """Load a CSV into a SQLAlchemy model using bulk insert."""

    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        records = []
        columns = {
            col.key: col.columns[0].type for col in inspect(model).mapper.column_attrs
        }
        for row in reader:
            filtered = {
                k: parse_value(v, columns[k]) for k, v in row.items() if k in columns
            }
            records.append(model(**filtered))
        session.bulk_save_objects(records)
    session.commit()


def load_seeds_from_dir(session: Session, seed_dir: Path, model_map: dict[str, Type]):
    """Load all CSVs from a directory, based on filename-to-model mapping."""

    for filename, model in model_map.items():
        csv_file = seed_dir / f"{filename}.csv"
        if csv_file.exists():
            print(f"Seeding {filename} from {csv_file}")
            load_csv_to_model(session, csv_file, model)
