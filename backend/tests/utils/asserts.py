from typing import List, Union
from deepdiff import DeepDiff


def assert_dict_contains(
    test_reason: str,
    expected: dict,
    actual: dict,
    exclude_paths: Union[str, List, None] = None,
):

    diff = DeepDiff(expected, actual, ignore_order=True, exclude_paths=exclude_paths)
    assert diff == {}, f"{test_reason} shows unexpected difference: \n{diff}"
