import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import polars as pl
from datasets import Dataset, load_dataset
from deltalake.writer import write_deltalake
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def prepare_individual_dataset(dataset: Dataset, category: str) -> pl.DataFrame:
    df = dataset.to_polars()
    df = df.with_columns(pl.lit(category).alias("category"))
    logger.info(f"Ingested {df.height} rows for category {category}")
    return df


def load_and_prepare(category: str, split: str) -> pl.DataFrame:
    from datasets import disable_progress_bars

    disable_progress_bars()
    dataset = load_dataset(
        os.getenv("DATASET_NAME"),
        category,
        trust_remote_code=True,
        split=split,
    )
    return prepare_individual_dataset(dataset, category)


def ingest_data() -> None:
    logger.info("Starting Ingestion")
    if not os.getenv("CATEGORIES"):
        raise ValueError(
            "Categories is not specified for dataset in the environment variable file"
        )
    if not os.getenv("DATASET_NAME"):
        raise ValueError("Dataset Name not specified in environment variables")
    if not os.getenv("BRONZE_PATH"):
        raise ValueError("Bronze dataset path not specified in environment variables")
    if os.getenv("BRONZE_ROW_LIMIT"):
        if os.getenv("BRONZE_ROW_LIMIT").isdigit():
            logger.warning("Row limit applied - running in dev mode")
            split = f"full[:{os.getenv('BRONZE_ROW_LIMIT')}]"
        else:
            raise ValueError("Bronze Row Limit is not a valid integer")
    else:
        split = "full"

    try:
        categories = os.getenv("CATEGORIES").split(",")
        load_and_prepare_with_split = partial(load_and_prepare, split=split)
        with ThreadPoolExecutor(max_workers=1) as executor:
            dfs = list(executor.map(load_and_prepare_with_split, categories))
        dataset_to_be_written = pl.concat(dfs)
        write_deltalake(
            os.getenv("BRONZE_PATH"), dataset_to_be_written.to_arrow(), mode="overwrite"
        )
        logger.info(
            f"Successfully ingested {dataset_to_be_written.height} rows to Bronze"
        )
    except Exception:
        logger.exception("Data Ingestion Failed")
        raise


if __name__ == "__main__":
    ingest_data()
