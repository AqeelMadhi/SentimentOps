from dotenv import load_dotenv
from loguru import logger
import polars as pl
import os
from datasets import load_dataset
from deltalake.writer import write_deltalake

load_dotenv()


def prepare_individual_dataset(dataset, category, row_limit=None):
    df= dataset.to_polars()
    df=df.with_columns(pl.lit(category).alias("category"))
    logger.info(f"Ingested {len(df)} rows for category {category}")
    return df


def ingest_data():
    logger.info("Starting Ingestion")
    try:
        categories = os.getenv("CATEGORIES").split(",")
        dfs = []
        row_limit = os.getenv("BRONZE_ROW_LIMIT")
        if row_limit:
            logger.warning("Row limit applied - running in dev mode")
            split = f"full[:{row_limit}]"
        else:
            split = f"full"
        for category in categories:
            dfs.append(
                prepare_individual_dataset(
                    dataset=load_dataset(
                        os.getenv("DATASET_NAME"),
                        category,
                        trust_remote_code=True,
                        split=split
                    ),
                    category=category,
                    row_limit=row_limit
                )
            )
        dataset_to_be_written = pl.concat(dfs)
        write_deltalake(
            os.getenv("BRONZE_PATH"), dataset_to_be_written.to_arrow(), mode="overwrite")
    except Exception as e:
        logger.error(f"Ingestion Failed: {e}")


if __name__ == "__main__":
    ingest_data()
