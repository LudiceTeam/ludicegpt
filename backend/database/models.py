from sqlalchemy import Table,Column,Integer,String,MetaData,ARRAY,Boolean
from sqlalchemy.dialects.postgresql import JSONB


metadata_obj = MetaData()

table = Table("ai_girl_data",
              metadata_obj,
              Column("username",String,primary_key=True),
              Column("balance",Integer),
              Column("zap",Integer),
              Column("sub",Boolean),
              Column("date",String),
              Column("basic_sub",Boolean),
              Column("last_ref",String) # дата когда обновили запросы
)