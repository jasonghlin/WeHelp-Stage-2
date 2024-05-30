from dotenv import load_dotenv
import os
import mysql.connector
import logging

load_dotenv(dotenv_path='./.env')
mysql_password = os.environ.get("MYSQL")

def get_db_connection():
    try:
       dbconfig = {
        "user": "newuser",
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
            val_1 = (f"%{keyword}%", f"%{keyword}%")
            db.execute(attraction_query, val_1)
            db.fetchall()
            row_count = db.rowcount
            print(row_count)
        else:
            db.execute(attraction_query)
            db.fetchall()
            row_count = db.rowcount
            print(row_count)
        offset = page * 12
        attraction_query += "LIMIT 12 OFFSET %s"
        if keyword:
            val = (f"%{keyword}%", f"%{keyword}%", offset)
        else:
            val = (offset, )
        db.execute(attraction_query, val)
        if (page + 1) * 12 >= row_count:
            return {"data": db.fetchall(), "lastPage": True}
        else:
            return {"data": db.fetchall(), "lastPage": False}
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

# create user table if not exist
def create_users_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users(
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating user table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_users_table()

def check_db_user(user):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("SELECT * FROM users WHERE email = %s")
        val = (user.email, )
        db.execute(user_query, val)
        return db.fetchone()
    except Exception as e:
        logging.error("Error when fetching user info: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def create_db_user(user_hash):
    db_connection = get_db_connection()
    db = db_connection.cursor(dictionary = True)
    user_query = ("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)")
    val = (user_hash.name, user_hash.email, user_hash.password)
    db.execute(user_query, val)
    db_connection.commit()