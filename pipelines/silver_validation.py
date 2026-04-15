import pandera.polars as pa
import polars as pl


class SilverSchema(pa.DataFrameModel):
    rating: pl.Int8 = pa.Field(nullable=False, ge=1, le=5)
    verified_purchase: pl.Boolean = pa.Field(nullable=True)
    helpful_vote: pl.Int64 = pa.Field(nullable=True)
    title: pl.String = pa.Field(nullable=False)
    text: pl.String = pa.Field(nullable=False)
    timestamp: pl.Datetime("ms") = pa.Field(nullable=True)
    category: pl.String = pa.Field(nullable=True)
