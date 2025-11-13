import pytest
import os

from app.domain.partsbox.partsbox_service import PartsboxService


@pytest.mark.requires_internet
def test_partsbox_service_online():
    parts = PartsboxService.fetch_parts(True)
    assert len(parts) > 0


@pytest.mark.requires_internet
def test_partsbox_service_update_label():
    PartsboxService._reset()
    parts = PartsboxService.fetch_parts(True)
    part = [p for p in parts if p.id == "19gcjr3fty4f6a8f5s1g68p0mf"][0]

    original_label = part.label
    assert original_label != "st_test"

    new_label = "st_test"
    PartsboxService.update_part_label(part.id, new_label)
    parts = PartsboxService.fetch_parts(True)
    updated_part = [p for p in parts if p.id == "19gcjr3fty4f6a8f5s1g68p0mf"][0]
    assert updated_part.label == new_label

    # Revert label change
    PartsboxService.update_part_label(part.id, original_label)
    parts = PartsboxService.fetch_parts(True)
    assert [p for p in parts if p.id == "19gcjr3fty4f6a8f5s1g68p0mf"][
        0
    ].label == original_label
