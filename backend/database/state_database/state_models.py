from sqlalchemy import Table,Column,String,Boolean,MetaData

metadata_obj = MetaData()

state_table = Table(
    "state_table",
    metadata_obj,
    Column("username",String,primary_key=True),
    Column("chat",Boolean)
    )
