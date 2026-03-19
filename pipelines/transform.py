from dotenv import load_dotenv
from loguru import logger
import polars as pl
import os
from deltalake.writer import write_deltalake
from deltalake import DeltaTable

load_dotenv()


def convert_data_types(df: pl.DataFrame) -> pl.DataFrame:
    try:
        return df.with_columns(
            pl.col("title", "text").cast(pl.Utf8),
            pl.col("rating").cast(pl.Int8),
            pl.from_epoch(pl.col("timestamp"), time_unit="ms"),
        )
    except Exception as e:
        logger.error(f"Something went wrong with conversion of data types: {e}")


def delete_unnecessary_columns(
    df: pl.DataFrame, list_of_columns_to_drop: list
) -> pl.DataFrame:
    try:
        return df.drop(list_of_columns_to_drop)
    except Exception as e:
        logger.error(
            f"Something went wrong - likely missing column(s). Exception is {e}"
        )


def drop_nulls(df: pl.DataFrame, critical_columns: list) -> pl.DataFrame:
    try:
        return df.drop_nulls(subset=critical_columns)
    except Exception as e:
        logger.error(f"Failed to drop nulls: {e}")


def remove_duplicates(df: pl.DataFrame, dedup_keys: list) -> pl.DataFrame:
    try:
        return df.unique(subset=dedup_keys)
    except Exception as e:
        logger.error(f"Failed to remove duplicates: {e}")


def basic_text_cleaning(df: pl.DataFrame) -> pl.DataFrame:
    try:
        return df.with_columns(
            pl.col("text").str.replace_all(r"<[^>]+>", "")
        .str.strip_chars())
    except Exception as e:
        logger.error(f"Failed to clean_text: {e}")


def transform():
    logger.info("Starting Silver Transformation")
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
        df.write_delta(os.getenv("SILVER_PATH"), mode="overwrite",delta_write_options = {"schema_mode":"overwrite"})
        logger.info(f"Successfully wrote {len(df)} rows to silver layer")
    except Exception as e:
        logger.error(f"Something went wrong during the transformation to silver: {e}")


if __name__ == "__main__":
    transform()
