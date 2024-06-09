from dotenv import load_dotenv
import os
import mysql.connector
import logging
from fastapi import Depends

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

# attractions

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
            # print(row_count)
        else:
            db.execute(attraction_query)
            db.fetchall()
            row_count = db.rowcount
            # print(row_count)
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
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("INSERT INTO users(name, email, password) VALUES(%s, %s, %s)")
        val = (user_hash.name, user_hash.email, user_hash.hashed_password)
        db.execute(user_query, val)
        db_connection.commit()
    except Exception as e:
        logging.error("Error when create user: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def get_user_dependencies():
    from routers.user import UserLoginRequest
    return UserLoginRequest

def get_user(user = Depends(get_user_dependencies)):
    try: 
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("SELECT * FROM users WHERE email = %s")
        # print(user.email)
        val = (user.email, )
        db.execute(user_query, val)
        result = db.fetchone()
        # print(result)
        if result:
            return result
        else:
            return {}
    except Exception as e:
        logging.error("Error when get user: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def create_bookings_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS bookings(
                id INT PRIMARY KEY AUTO_INCREMENT,
                attraction_id INT,
                user_id INT,
                date DATE,
                time CHAR(10),
                price INT,
                Foreign Key(attraction_id) References attractions(id),
                Foreign Key(user_id) References users(id)
            )
"""
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating user table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_bookings_table()


def create_orders_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS orders(
                id INT PRIMARY KEY AUTO_INCREMENT,
                prime INT,
                booking_id INT,
                user_id INT,
                Foreign Key(booking_id) References bookings(id),
                Foreign Key(user_id) References users(id)
            )
"""
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating user table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_orders_table()

# booking
def get_user_dependencies():
    from routers.booking_attraction import AttractionBookingInfo
    return AttractionBookingInfo

def create_db_booking(user_id, booking_info = Depends(get_user_dependencies)):
    try: 
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        existing_booking_query = """
            SELECT bookings.id, bookings.attraction_id, bookings.user_id, bookings.date, bookings.time, bookings.price FROM bookings
            LEFT JOIN orders ON bookings.id = orders.booking_id
            WHERE bookings.user_id = %s AND bookings.attraction_id = %s AND orders.id IS NULL
""" 
        existing_booking_val = (user_id, booking_info.attractionId)
        db.execute(existing_booking_query, existing_booking_val)
        existing_booking = db.fetchone()
        if existing_booking:
            booking_query = ("""
            UPDATE bookings SET attraction_id = %s, date = %s, time = %s, price = %s
            WHERE id = %s
""")
            val = (booking_info.attractionId, booking_info.date, booking_info.time, booking_info.price, existing_booking['id'])
        else:
            booking_query = ("""
                INSERT INTO bookings(attraction_id, user_id, date, time, price)
                VALUES(%s, %s, %s, %s, %s)
    """)
            # print(user.email)
            val = (booking_info.attractionId, user_id, booking_info.date, booking_info.time, booking_info.price)
        db.execute(booking_query, val)
        db_connection.commit()
        return True
        # print(result)
    except Exception as e:
        logging.error("Error when create booking: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def fetch_db_user_booking(user_id):
    try: 
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        booking_query = ("""
            SELECT bookings.id, bookings.attraction_id, bookings.user_id, bookings.date, bookings.time, bookings.price, attractions.images, attractions.name, attractions.address FROM bookings
            LEFT JOIN orders ON bookings.id = orders.booking_id
            LEFT JOIN attractions ON bookings.attraction_id = attractions.id
            WHERE bookings.user_id = %s AND orders.id IS NULL
""")
        # print(user.email)
        val = (user_id, )
        db.execute(booking_query, val)
        result = db.fetchall()
        # print(result)
        if result:
            return result
        else:
            return {}
    except Exception as e:
        logging.error("Error when get user booking: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def delete_db_booking(attraction_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        delete_query = "DELETE FROM bookings WHERE attraction_id = %s"
        delete_val = (attraction_id, )
        db.execute(delete_query, delete_val)
        db_connection.commit()
        return True
    except Exception as e:
        logging.error("Error when delete booking: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()