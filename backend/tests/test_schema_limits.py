import pytest
from pydantic import ValidationError

from app.schemas import MarketingEventCreate, ProgramWrite, TrainerWrite


@pytest.mark.parametrize(
    ("schema", "field", "limit"),
    [
        (ProgramWrite, "image_url", 500),
        (TrainerWrite, "designation", 120),
        (TrainerWrite, "profile_image", 500),
    ],
)
def test_admin_write_fields_enforce_storage_lengths(schema, field, limit):
    with pytest.raises(ValidationError):
        schema(**{field: "x" * (limit + 1)})


def test_admin_write_field_empty_string_defaults_are_preserved():
    assert ProgramWrite(name="Program", slug="program", category="Category").image_url == ""
    trainer = TrainerWrite(full_name="Trainer", slug="trainer")
    assert trainer.designation == ""
    assert trainer.profile_image == ""


def test_marketing_metadata_is_limited_to_8_kib():
    with pytest.raises(ValidationError, match="8 KiB"):
        MarketingEventCreate(event_type="PAGE_VIEW", metadata={"value": "x" * 8192})


def test_marketing_metadata_within_limit_is_accepted():
    event = MarketingEventCreate(event_type="PAGE_VIEW", metadata={"page": "/home"})
    assert event.metadata == {"page": "/home"}
