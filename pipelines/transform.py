import os

import polars as pl
from dotenv import load_dotenv
from loguru import logger

from pipelines.constants import ACCEPTABLE_DATA_LOSS_THRESHOLD
from pipelines.silver_validation import SilverSchema
load_dotenv()


def convert_data_types(df: pl.DataFrame) -> pl.DataFrame:

    return df.with_columns(
        pl.col("title", "text").cast(pl.Utf8),
        pl.col("rating").cast(pl.Int8),
        pl.from_epoch(pl.col("timestamp"), time_unit="ms"),
    )


def delete_unnecessary_columns(
    df: pl.DataFrame, list_of_columns_to_drop: list
) -> pl.DataFrame:

    return df.drop(list_of_columns_to_drop)


def drop_nulls(df: pl.DataFrame, critical_columns: list) -> pl.DataFrame:
    num_rows = df.height
    df = df.drop_nulls(subset=critical_columns)
    num_rows_post_transformation = df.height
    if 1 - (num_rows_post_transformation / num_rows) > ACCEPTABLE_DATA_LOSS_THRESHOLD:
        raise RuntimeError(
            "Too many rows were removed as a result of the drop nulls step"
        )

    return df


def remove_duplicates(df: pl.DataFrame, dedup_keys: list) -> pl.DataFrame:
    num_rows = df.height
    df = df.unique(subset=dedup_keys)
    num_rows_post_transformation = df.height
    if 1 - (num_rows_post_transformation / num_rows) > ACCEPTABLE_DATA_LOSS_THRESHOLD:
        raise RuntimeError(
            "Too many rows were removed as a result of the remove duplicates step"
        )
    return df


def basic_text_cleaning(df: pl.DataFrame) -> pl.DataFrame:

    return df.with_columns(
        pl.col("text").str.replace_all(r"<[^>]+>", "").str.strip_chars()
    )


def transform() -> None:
    logger.info("Starting Silver Transformation")
    if not os.getenv("BRONZE_PATH"):
        raise ValueError("Bronze Path Environment Variable doesnt exist")
    if not os.getenv("SILVER_DEDUP_KEYS"):
        raise ValueError(
            "Silver De - Duplication Key Environment Variable doesnt exist"
        )
    if not os.getenv("SILVER_CRITICAL_COLUMNS"):
        raise ValueError("Silver Critical Columns Environment Variable doesnt exist")
    if not os.getenv("BRONZE_COLUMNS_TO_DROP"):
        raise ValueError("Bronze columns to drop Environment Variable doesnt exist")
    if not os.getenv("SILVER_PATH"):
        raise ValueError("Silver Path Environment Variable doesnt exist")
    try:
        df = pl.read_delta(os.getenv("BRONZE_PATH"))
        unnecessary_columns_to_drop = os.getenv("BRONZE_COLUMNS_TO_DROP").split(",")
        critical_columns = os.getenv("SILVER_CRITICAL_COLUMNS").split(",")
        dedup_keys = os.getenv("SILVER_DEDUP_KEYS").split(",")
        df = drop_nulls(df, critical_columns)
        df = remove_duplicates(df, dedup_keys)
        df = convert_data_types(df)
        df = basic_text_cleaning(df)
        df = delete_unnecessary_columns(df, unnecessary_columns_to_drop)
        SilverSchema.validate(df)
        logger.info(f"Successfully validated silver schema")
        df.write_delta(
            os.getenv("SILVER_PATH"),
            mode="overwrite",
            delta_write_options={"schema_mode": "overwrite"},
        )
        logger.info(f"Successfully wrote {df.height} rows to silver layer")
    except RuntimeError:
        logger.exception(
            "Too many records were removed during the silver transformation"
        )
        raise
    except Exception:
        logger.exception("Silver transformation pipeline failed")
        raise


if __name__ == "__main__":
    transform()
