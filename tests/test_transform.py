import polars as pl
import pytest

from pipelines.transform import drop_nulls
from pipelines.transform import remove_duplicates

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
def create_fake_dataset_with_one_null() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "text": ["1", "2", "3" , "4" , "5"],
            "rating": ["a", "b", "c", "d", None],
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

@pytest.fixture
def create_fake_dataset_with_duplicates() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "user_id": ["1", "2", "1"],
            "parent_asin": ["a", "b", "a"],
        }
    )
    return df

@pytest.fixture
def create_fake_dataset_with_one_duplicate() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "user_id": ["1", "2", " 3" , "4", "5" , "1"],
            "parent_asin": ["a", "b", "c", "d", "e", "a"],
        }
    )
    return df

@pytest.fixture
def create_fake_dataset_without_duplicates() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "user_id": ["1", "2", "3"],
            "parent_asin": ["a", "b", "c"],
        }
    )
    return df



def test_drop_nulls_when_nulls(create_fake_dataset_with_one_null):
    df = create_fake_dataset_with_one_null
    num_rows = df.height
    result = drop_nulls(df, ["text", "rating"]).height
    assert result == num_rows - 1


def test_drop_nulls_when_no_nulls(create_fake_dataset_without_nulls):
    df = create_fake_dataset_without_nulls
    num_rows = df.height
    result = drop_nulls(df, ["text", "rating"]).height
    assert result == num_rows

def test_drop_nulls_when_nulls_raises_runtime_error(create_fake_dataset_with_nulls):
    df=create_fake_dataset_with_nulls
    with pytest.raises(RuntimeError):
        drop_nulls(df, ["text","rating"])
    
def test_remove_duplicates_when_duplicates(create_fake_dataset_with_one_duplicate):
    df = create_fake_dataset_with_one_duplicate
    num_rows = df.height
    result = remove_duplicates(df, ["user_id", "parent_asin"]).height
    assert result == num_rows - 1
    
def test_remove_duplicates_without_duplicates(create_fake_dataset_without_duplicates):
    df = create_fake_dataset_without_duplicates
    num_rows = df.height
    result = remove_duplicates(df, ["user_id", "parent_asin"]).height
    assert result == num_rows

def test_remove_duplicates_when_duplicates_return_runtime_error(create_fake_dataset_with_duplicates):
    df = create_fake_dataset_with_duplicates
    with pytest.raises(RuntimeError):
        remove_duplicates(df, ["user_id", "parent_asin"])