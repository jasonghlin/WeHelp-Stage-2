from dotenv import load_dotenv
import os
import mysql.connector
import logging

load_dotenv(dotenv_path='./.env')
mysql_password = os.environ.get("MYSQL")

def get_db_connection():
    try:
       dbconfig = {
        "user": "root",
        "password": mysql_password,
        "host": "localhost",
        "database": "taipei_day_trip"
    }
       cnxpool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool", 
        pool_size=5,         
        **dbconfig
    )
       cnx = cnxpool.get_connection()
       print("---Database connection successful---")
    except mysql.connector.Error as err:
        print(f'Database connection error: {err}')
        raise
    return cnx

def get_db_attractions(page, keyword=None):
    db_connection = get_db_connection()
    try:
        db = db_connection.cursor(dictionary = True)
        attraction_query = (
            # """
            #    SELECT attractions.id, name, CAT AS category, description, address, direction AS transport, MRT AS mrt, latitude AS lat, longitude AS lng, images
            #    FROM attractions INNER JOIN attraction_images ON attractions.id = attraction_images.attraction_id
            #    WHERE name like %s OR mrt like %s
            # """
            """
               SELECT attractions.id, name, CAT AS category, description, address, direction AS transport, MRT AS mrt, latitude AS lat, longitude AS lng, images
               FROM attractions               
            """
            )
        if keyword:
            attraction_query += "WHERE name like %s OR mrt like %s"
        offset = page * 12
        attraction_query += "LIMIT 12 OFFSET %s"
        if keyword:
            val = (f"%{keyword}%", f"%{keyword}%", offset)
        else:
            val = (offset, )
        print(attraction_query, offset)
        db.execute(attraction_query, val)
        return db.fetchall()
    except Exception as e:
        logging.error("Error when fetching user info: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()





# SELECT attractions.id, name, CAT AS category, description, address, direction AS transport, MRT AS mrt, latitude AS lat, longitude AS lng, image_url AS images FROM attractions INNER JOIN attraction_images ON attractions.id = attraction_images.attraction_id WHERE name like "%北%" OR mrt like "%北%";