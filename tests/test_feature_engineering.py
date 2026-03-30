import polars as pl
import pytest

from pipelines.feature_engineering import create_sentiment_label


@pytest.fixture
def create_test_dataset() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "rating": [1, 2, 3, 4, 5],
        }
    )
    return df


def test_create_sentiment_label(create_test_dataset):
    df = create_test_dataset
    df = create_sentiment_label(df)
    good_rows = df.filter(pl.col("sentiment_label") == "good").height
    average_rows = df.filter(pl.col("sentiment_label") == "average").height
    bad_rows = df.filter(pl.col("sentiment_label") == "bad").height
    assert good_rows == 2
    assert average_rows == 1
    assert bad_rows == 2
