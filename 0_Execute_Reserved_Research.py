from bs4 import BeautifulSoup
import requests
import pymssql
import json
import Product as pds
import NaverResearch as nvrsch

db_server = '127.0.0.1'
db_name = 'ecommerce'
user_id = 'ecomm'
user_pwd = 'Interstay$$2022'
port_number = 24700

conn = pymssql.connect(server=db_server, user=user_id, password=user_pwd, database=db_name, port=port_number)
cursor = conn.cursor()
cursor.execute('select top 1 research_id, research_type from Research where convert(varchar(10),reservedDate,120) = convert(varchar(10),getdate(),120) and startedDate is null and finishedDate is null')

research_id = 0
search_type = 'total'

for row in cursor:
    print(row[0], row[1])
    research_id = row[0]
    search_type = row[1]

conn.close()
if research_id > 0:
    nvrsch.perform_research(research_id, search_type, db_server, db_name,user_id, user_pwd, port_number)
