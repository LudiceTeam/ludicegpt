from sqlalchemy import MetaData,Table,Column,String,Boolean

metadata_obj = MetaData()

sale_table = Table(
    "sale_table",
    metadata_obj,
    Column("username",String,primary_key= True),
    Column("sale",Boolean)
)