import os

import polars as pl
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def create_sentiment_label(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col("rating") <= 2)
        .then(pl.lit("bad"))
        .when(pl.col("rating") == 3)
        .then(pl.lit("average"))
        .otherwise(pl.lit("good"))
        .alias("sentiment_label")
    )


def create_text_length(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    return df.with_columns(
        pl.col(column_name).str.len_chars().alias(f"{column_name}_text_length")
    )


def create_word_count(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    return df.with_columns(
        pl.col(column_name).str.split(" ").list.len().alias(f"{column_name}_word_count")
    )


def engineer() -> None:
    logger.info("Gold transformation started")
    if not os.getenv("GOLD_PATH"):
        raise ValueError("Gold path doesnt exist")
    if not os.getenv("SILVER_PATH"):
        raise ValueError("Silver Path doesnt exist")
    try:
        df = pl.read_delta(os.getenv("SILVER_PATH"))
        df = create_sentiment_label(df)
        df = create_text_length(df, "title")
        df = create_text_length(df, "text")
        df = create_word_count(df, "title")
        df = create_word_count(df, "text")
        df.write_delta(
            os.getenv("GOLD_PATH"),
            mode="overwrite",
            delta_write_options={"schema_mode": "overwrite"},
        )
        logger.info(f"Successfully wrote {df.height} rows to gold layer")
    except Exception:
        logger.exception("Gold transformation failed")
        raise


if __name__ == "__main__":
    engineer()
