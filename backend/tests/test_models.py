from sqlalchemy import MetaData,Table,Column,String

metadata_obj = MetaData()

test_table = Table(
    "test_table",
    metadata_obj,
    Column("test",String,primary_key=True)
)