from sqlalchemy import Table,Column,String,MetaData


metadata_obj = MetaData()

ai_table = Table(
    "ai_choose_table",
    metadata_obj,
    Column("username",String,primary_key = True),
    Column("ai_name",String)
)