import json
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv(dotenv_path='../.env')
mysql_password = os.environ.get("MYSQL")

with open("taipei-attractions.json", 'r') as file:
    raw_data = json.load(file)
    data = raw_data["result"]["results"]



dbconfig = {
    "user": "newuser",
    "password": mysql_password,
    "host": "localhost"
}

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool", 
        pool_size=5,         
        **dbconfig
    )
cnx = cnxpool.get_connection()
db = cnx.cursor(dictionary = True)

try: 
    # create table schema 
    db.execute("CREATE DATABASE IF NOT EXISTS taipei_day_trip")
    db.execute("USE taipei_day_trip")
    create_table_query = """
        CREATE TABLE IF NOT EXISTS attractions(
            id INT PRIMARY KEY AUTO_INCREMENT,
            SERIAL_NO VARCHAR(50),
            name VARCHAR(255),
            latitude FLOAT,
            longitude FLOAT,
            address VARCHAR(255),
            CAT VARCHAR(50),
            description TEXT,
            direction TEXT,
            MRT VARCHAR(50),
            MEMO_TIME TEXT,
            rate INT,
            date DATE,
            avBegin DATE,
            avEnd DATE,
            langinfo INT,
            REF_WP INT,
            POI CHAR(1),
            idpt VARCHAR(50),
            images TEXT
        )
    """
    db.execute(create_table_query)

    # create_image_table_query = """
    #     CREATE TABLE IF NOT EXISTS attraction_images(
    #         id INT PRIMARY KEY AUTO_INCREMENT,
    #         image_url TEXT,
    #         attraction_id INT,
    #         Foreign Key(attraction_id) References attractions(id)
    #     )
    # """
    # db.execute(create_image_table_query)
    
    # insert data
    for attraction in data:
        img_urls = attraction["file"].split("https://")
        jpg_png_urls = [url for url in img_urls if url.endswith(".jpg") or url.endswith(".JPG") or url.endswith(".png")or url.endswith(".PNG")]
        jpg_png_urls_json = json.dumps(jpg_png_urls)
        print(jpg_png_urls)
        insert_query = """
        INSERT INTO attractions(
            SERIAL_NO,
            name,
            latitude,
            longitude,
            address,
            CAT,
            description,
            direction,
            MRT,
            MEMO_TIME,
            rate,
            date,
            avBegin,
            avEnd,
            langinfo,
            REF_WP,
            POI,
            idpt,
            images
        ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
        insert_values = (
            attraction["SERIAL_NO"],
            attraction["name"],
            float(attraction["latitude"]),
            float(attraction["longitude"]),
            attraction["address"],
            attraction["CAT"],
            attraction["description"],
            attraction["direction"],
            attraction["MRT"],
            attraction["MEMO_TIME"],
            int(attraction["rate"]),
            attraction["date"],
            attraction["avBegin"],
            attraction["avEnd"],
            attraction["langinfo"],
            attraction["REF_WP"],
            attraction["POI"],
            attraction["idpt"],
            jpg_png_urls_json
        )
        db.execute(insert_query, insert_values)
        last_row_id = db.lastrowid

        
        cnx.commit()
        
except Exception as e:
    print("Error", e)
finally:
    print('success')
    db.close()
    cnx.close()
    