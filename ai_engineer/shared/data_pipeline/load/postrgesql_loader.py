"""
    Receive data and load to postgresql database using polars
"""
import uuid

import polars as pl

from ai_engineer.shared.data_pipeline.load.base import BaseLoader


class PostgreDBLoaderWithPolars(BaseLoader):
    """
        Load polars DataFrame to postgresql database
        Use polars write_database with adbc engine

        Input:
            polars.DataFrame
        Output:
            None
    """
    def __init__(self,
            destination_table_name: str,
            uri: str,
            load_mode: str = "append", # "append" | "replace" | "fail"
            delete_filter_column: str | None = None,
            delete_filter_type: str | None = None, # SQL type to cast delete filter value, e.g. "date"
            **kwargs
        ) -> None:
        self.destination_table_name = destination_table_name
        self.uri = uri
        self.load_mode = load_mode
        self.delete_filter_column = delete_filter_column
        self.delete_filter_type = delete_filter_type
        self.kwargs = kwargs

    def delete_before_load(self, filter_value: str | None = None) -> None:
        """
            Delete all rows in destination table that delete_filter_column equals filter_value
        """
        if self.delete_filter_column is None:
            return

        import adbc_driver_postgresql.dbapi as pg_dbapi

        placeholder = "$1" if self.delete_filter_type is None else f"$1::{self.delete_filter_type}"
        query = (
            f"DELETE FROM {self.destination_table_name} "
            f"WHERE {self.delete_filter_column} = {placeholder}"
        )
        with pg_dbapi.connect(self.uri) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (filter_value,))
            connection.commit()

    def _get_destination_column_types(self) -> dict[str, str]:
        """
            Map column name -> postgres data_type of the destination table.
        """
        import adbc_driver_postgresql.dbapi as pg_dbapi

        schema, _, table = self.destination_table_name.rpartition(".")
        schema = schema or "public"
        with pg_dbapi.connect(self.uri) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT column_name, data_type FROM information_schema.columns "
                    "WHERE table_schema = $1 AND table_name = $2",
                    (schema, table),
                )
                return {row[0]: row[1] for row in cursor.fetchall()}

    def _normalize_for_adbc(self, records: pl.DataFrame) -> pl.DataFrame:
        """
            ADBC/Postgres cannot map some Arrow types, so coerce them to match
            the destination postgres column types:
            - Null dtype (cot toan null)   -> Utf8
            - List dtype                   -> Utf8 (noi cac phan tu bang ", ")
            - cot dich la uuid             -> Binary (16 bytes)
            - cot dich la date             -> Date
            - cot dich la timestamp        -> Datetime
        """
        destination_types = self._get_destination_column_types()

        null_columns = [
            column for column, dtype in zip(records.columns, records.dtypes)
            if dtype == pl.Null
        ]
        if null_columns:
            records = records.with_columns(
                [pl.col(column).cast(pl.Utf8) for column in null_columns]
            )

        list_columns = [
            column for column, dtype in zip(records.columns, records.dtypes)
            if isinstance(dtype, pl.List)
        ]
        if list_columns:
            records = records.with_columns(
                [
                    pl.col(column).cast(pl.List(pl.Utf8)).list.join(", ").alias(column)
                    for column in list_columns
                ]
            )

        uuid_columns = [
            column for column in records.columns
            if destination_types.get(column) == "uuid"
        ]
        if uuid_columns:
            records = records.with_columns(
                [
                    pl.col(column)
                    .map_elements(
                        lambda value: uuid.UUID(value).bytes if isinstance(value, str)
                        else value.bytes,
                        return_dtype=pl.Binary,
                    )
                    .alias(column)
                    for column in uuid_columns
                ]
            )

        date_columns = [
            column for column in records.columns
            if destination_types.get(column) == "date"
        ]
        if date_columns:
            records = records.with_columns(
                [pl.col(column).cast(pl.Date) for column in date_columns]
            )

        timestamp_columns = [
            column for column in records.columns
            if destination_types.get(column, "").startswith("timestamp")
        ]
        if timestamp_columns:
            records = records.with_columns(
                [pl.col(column).cast(pl.Datetime) for column in timestamp_columns]
            )

        return records

    def load(self, records: pl.DataFrame):
        """
            Load polars DataFrame to postgresql database
        """
        if records.height == 0:
            return

        print("NUMBER of rows to write to postgresql:")
        print(len(records))

        records = self._normalize_for_adbc(records)

        records.write_database(
            table_name=self.destination_table_name,
            connection=self.uri,
            if_table_exists=self.load_mode,
            engine="adbc",
            engine_options=self.kwargs or None,
        )
