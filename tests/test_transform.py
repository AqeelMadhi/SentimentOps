import polars as pl
import pytest

from pipelines.transform import drop_nulls


@pytest.fixture
def create_fake_dataset_with_nulls() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "text": ["1", "2", None],
            "rating": ["a", "b", None],
        }
    )
    return df


@pytest.fixture
def create_fake_dataset_without_nulls() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "text": ["1", "2", "3"],
            "rating": ["a", "b", "c"],
        }
    )
    return df


def test_drop_nulls(create_fake_dataset_with_nulls):
    df = create_fake_dataset_with_nulls
    num_rows = df.height
    result = drop_nulls(df, ["text", "rating"]).height
    assert result == num_rows - 1


def test_drop_no_nulls(create_fake_dataset_without_nulls):
    df = create_fake_dataset_without_nulls
    num_rows = df.height
    result = drop_nulls(df, ["text", "rating"]).height
    assert result == num_rows
