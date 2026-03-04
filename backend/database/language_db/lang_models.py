from sqlalchemy import MetaData,Column,Table,String

metadata_obj = MetaData()

language_table = Table(
    "language_table",
    metadata_obj,
    Column("username",String,primary_key=True),
    Column("lang",String)
)