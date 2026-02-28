from sqlalchemy import Table,Column,MetaData,String,Boolean,Date,Integer

metadata_obj =  MetaData()

nano_table = Table(
    "nano_banana_table",
    metadata_obj,
    Column("username",String,primary_key=True),
    Column("sub_premuim",Boolean),
    Column("sub_models",Boolean),
    Column("date",Date),
    Column("req",Integer)
)