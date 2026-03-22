import os

import polars as pl
from datasets import load_dataset
from deltalake.writer import write_deltalake
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def prepare_individual_dataset(dataset, category):
    df = dataset.to_polars()
    df = df.with_columns(pl.lit(category).alias("category"))
    logger.info(f"Ingested {df.height} rows for category {category}")
    return df


def ingest_data():
    logger.info("Starting Ingestion")
    if not os.getenv("CATEGORIES"):
        raise ValueError(
            "Categories is not specified for dataset in the environment variable file"
        )
    if not os.getenv("DATASET_NAME"):
        raise ValueError("Dataset Name not specified in environment variables")
    if not os.getenv("BRONZE_PATH"):
        raise ValueError("Bronze dataset path not specified in environment variables")
    try:
        categories = os.getenv("CATEGORIES").split(",")
        dfs = []
        row_limit = os.getenv("BRONZE_ROW_LIMIT")
        if row_limit:
            logger.warning("Row limit applied - running in dev mode")
            split = f"full[:{row_limit}]"
        else:
            split = "full"
        for category in categories:
            dfs.append(
                prepare_individual_dataset(
                    dataset=load_dataset(
                        os.getenv("DATASET_NAME"),
                        category,
                        trust_remote_code=True,
                        split=split,
                    ),
                    category=category,
                )
            )
        dataset_to_be_written = pl.concat(dfs)
        write_deltalake(
            os.getenv("BRONZE_PATH"), dataset_to_be_written.to_arrow(), mode="overwrite"
        )
    except Exception:
        logger.exception("Data Ingestion Failed")


if __name__ == "__main__":
    ingest_data()
