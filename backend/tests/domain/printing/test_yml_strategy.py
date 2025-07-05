from pydantic import ValidationError
from app.schemas.printing_strategy import PrintingStrategyDefinition
from app.domain.printing import PrintStrategyBase
from app.domain.printing.spec_print_strategy import (
    SpecPrintStrategy,
    read_spec_from_yml,
    register_yml_strategy,
)
from pathlib import Path
from yaml import safe_load
from pytest import raises
from app.domain.printing.print_strategy import get_all_printing_strategies

RESOURCE_PATH = Path(__file__).parent.parent.parent / "resources"


def test_printingstrategy_yml_pydantic_validation():
    with open(str(RESOURCE_PATH / "print-strategy-test.yml"), "r") as f:
        data = safe_load(f)

    strategy = PrintingStrategyDefinition(**data)
    assert "GridfinityYml" == strategy.name

    assert (
        "{% if item.length %}{{item.length|default('') }}{% endif %}"
        in strategy.label_content.template
    )


def test_printingstrategy_yml_wrong_validation():
    with open(str(RESOURCE_PATH / "print-strategy-test-wrong.yml"), "r") as f:
        data = safe_load(f)

    with raises(ValidationError) as valerror:
        strategy = PrintingStrategyDefinition(**data)
    print(valerror)
    assert "label_specification.columns" in str(valerror.value)
    assert "Input should be a valid integer" in str(valerror.value)


def test_spec_conversion():
    from labels import Specification

    with open(str(RESOURCE_PATH / "print-strategy-test.yml"), "r") as f:
        strategy = SpecPrintStrategy(read_spec_from_yml(f))

    ymlspec = strategy.specification

    for attr in ymlspec.label_specification.__dict__.keys():
        assert getattr(ymlspec.label_specification, attr) == getattr(
            strategy.labelspecs, attr
        )


def test_registration(clear_registries):
    assert "GridfinityYml" not in get_all_printing_strategies()

    register_yml_strategy(str(RESOURCE_PATH / "print-strategy-test.yml"))
    strategy = PrintStrategyBase.create_printing_strategy("GridfinityYml")
    assert strategy.draw_border == False
    assert strategy.labelspecs.columns == 10
    assert strategy.copies == 2

    assert "GridfinityYml" in get_all_printing_strategies()
