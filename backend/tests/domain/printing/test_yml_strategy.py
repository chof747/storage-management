from pydantic import ValidationError
from app.schemas.printing_strategy import PrintingStrategyDefinition
from pathlib import Path
from yaml import safe_load
from pytest import raises

RESOURCE_PATH = Path(__file__).parent.parent.parent / "resources"


def test_printingstrategy_yml_pydantic_validation():
    with open(str(RESOURCE_PATH / "print-strategy-test.yml"), "r") as f:
        data = safe_load(f)

    strategy = PrintingStrategyDefinition(**data)
    assert "Gridfinity" == strategy.name


def test_printingstrategy_yml_wrong_validation():
    with open(str(RESOURCE_PATH / "print-strategy-test-wrong.yml"), "r") as f:
        data = safe_load(f)

    with raises(ValidationError) as valerror:
        strategy = PrintingStrategyDefinition(**data)
    print(valerror)
    assert "label_specification.columns" in str(valerror.value)
    assert "Input should be a valid integer" in str(valerror.value)
