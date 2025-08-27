from app.models.partsbox_item import PartsboxItem  # Adjust the import path as needed


def test_printable_feature_partsbox_item():
    item = PartsboxItem(
        id="123",
        name="Test Part",
        description="A test part",
        total_stock=10,
        storage_place="Test Storage",
        material_part_number="TP-001",
    )

    # Test initial state
    assert not item.queued

    # Test setting for printing
    item.set_for_printing()
    assert item.queued

    # Test unsetting for printing
    item.unset_for_printing()
    assert not item.queued
