from sqlalchemy import Table,MetaData,String,Column


metadata_obj = MetaData()

refresh_table = Table(
    "refresh_table",
    metadata_obj,
    Column("username",String,primary_key=True),
    Column("token",String)
)