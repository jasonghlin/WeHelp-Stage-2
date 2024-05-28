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
    try:
        db_connection = get_db_connection()
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
        db.execute(attraction_query, val)
        return db.fetchall()
    except Exception as e:
        logging.error("Error when fetching attractions info: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def get_db_attraction_by_id(attraction_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        attraction_query = (
            """
                SELECT attractions.id, name, CAT AS category, description, address, direction AS transport, MRT AS mrt, latitude AS lat, longitude AS lng, images
                FROM attractions
                WHERE attractions.id = %s
            """
        )
        val = (attraction_id, )
        db.execute(attraction_query, val)
        return db.fetchone()
    except Exception as e:
        logging.error("Error when fetching attractions info: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def get_db_mrts():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        mrts_query = ("SELECT MRT as mrt, COUNT(*) FROM attractions GROUP BY mrt ORDER BY COUNT(*) DESC")
        db.execute(mrts_query)
        return db.fetchall()
    except Exception as e:
        logging.error("Error when fetching attractions info: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()