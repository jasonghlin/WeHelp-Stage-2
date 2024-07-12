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
        "user": "admin",
        "password": mysql_password,
        "host": "taipei-day-trip-db.c90ws4we0uzp.us-west-2.rds.amazonaws.com",
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
            email VARCHAR(255) UNIQUE NOT NULL,
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


def update_user_name(new_name, user_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("UPDATE users SET name = %s WHERE id = %s")
        val = (new_name, user_id)
        db.execute(user_query, val)
        db_connection.commit()
        return True
    except Exception as e:
        logging.error("Error when update user name: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

def update_user_email(new_email, user_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("UPDATE users SET email = %s WHERE id = %s")
        val = (new_email, user_id)
        db.execute(user_query, val)
        db_connection.commit()
        return True
    except Exception as e:
        logging.error("Error when update user email: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

def update_user_password(new_password, user_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        user_query = ("UPDATE users SET password = %s WHERE id = %s")
        val = (new_password, user_id)
        db.execute(user_query, val)
        db_connection.commit()
        return True
    except Exception as e:
        logging.error("Error when update user password: %s", e, exc_info=True)
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
                booking_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
                number VARCHAR(255) UNIQUE,
                status INT,
                price INT,
                user_id INT,
                paid TINYINT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
            LEFT JOIN orders_bookings_relation ON bookings.id = orders_bookings_relation.booking_id
            WHERE bookings.user_id = %s AND bookings.attraction_id = %s AND orders_bookings_relation.order_id IS NULL
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
            LEFT JOIN orders_bookings_relation ON bookings.id = orders_bookings_relation.booking_id
            LEFT JOIN attractions ON bookings.attraction_id = attractions.id
            WHERE bookings.user_id = %s AND orders_bookings_relation.order_id IS NULL
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
        delete_query = "DELETE FROM bookings WHERE id IN (SELECT sub_query.id FROM (SELECT bookings.id FROM bookings LEFT JOIN orders_bookings_relation ON bookings.id = orders_bookings_relation.booking_id WHERE orders_bookings_relation.order_id IS NULL AND bookings.attraction_id = %s) AS sub_query)"
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

# create contact table
def create_contact_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS contact(
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT,
                name VARCHAR(50),
                email VARCHAR(255),
                phone VARCHAR(50),
                Foreign Key(order_id) References orders(id)
            )
"""
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating contact table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_contact_table()

def create_orders_bookings_relation_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS orders_bookings_relation(
                id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT,
                booking_id INT,
                Foreign Key(order_id) References orders(id),
                Foreign Key(booking_id) References bookings(id)
            )
"""
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating orders_bookings_relation table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_orders_bookings_relation_table()



# create new order
def create_db_order_contact(order_number, status, price, booking_id, user_id, paid, contact):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        order_query = ("INSERT INTO orders(number, status, price, user_id, paid) VALUES(%s, %s, %s, %s, %s)")
        val = (order_number, status, price, user_id, paid)
        db.execute(order_query, val)
        db_connection.commit()
        order_id = db.lastrowid
        # print(booking_id)
        for id in booking_id:
            # print(id)
            orders_bookings_relation_query = ("INSERT INTO orders_bookings_relation(order_id, booking_id) VALUES(%s, %s)")
            orders_bookings_relation_val = (order_id, id)
            db.execute(orders_bookings_relation_query, orders_bookings_relation_val)
            
        contact_query = ("INSERT INTO contact(order_id, name, email, phone) VALUES(%s, %s, %s, %s)")
        contact_val = (order_id, contact.name, contact.email, contact.phone)
        db.execute(contact_query, contact_val)
        
        db_connection.commit()
        return order_id
    except Exception as e:
        logging.error("Error when create order: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

# update order
def update_db_order_contact(order_id, order_number, status, paid):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        order_query = ("UPDATE orders SET number = %s, status = %s, paid = %s WHERE id = %s")
        val = (order_number, status, paid, order_id)
        db.execute(order_query, val)
        db_connection.commit()
        return True
    except Exception as e:
        logging.error("Error when create order: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()


def get_db_order_info(user_id, order_number):
    try: 
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        booking_query = ("""
            SELECT orders.user_id, orders.number, orders.price, orders.status, orders.paid, bookings.date, bookings.time, contact.name, contact.email, contact.phone, attractions.id AS attraction_id, attractions.name AS attraction_name, attractions.address, attractions.images
            FROM orders
            LEFT JOIN contact on orders.id = contact.order_id
            LEFT JOIN orders_bookings_relation ON orders.id = orders_bookings_relation.order_id
            LEFT JOIN bookings ON orders_bookings_relation.booking_id = bookings.id
            LEFT JOIN attractions ON bookings.attraction_id = attractions.id
            WHERE orders.user_id = %s AND orders.number = %s
""")
        # print(user.email)
        val = (user_id, order_number)
        db.execute(booking_query, val)
        result = db.fetchall()
        # print(result)
        if result:
            return result
        else:
            return {}
    except Exception as e:
        logging.error("Error when get user order: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

def get_db_user_order_info(user_id):
    try: 
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        order_query = ("""
            SELECT orders.user_id, orders.number, orders.price, orders.status, orders.paid, bookings.date, bookings.time, contact.name, contact.email, contact.phone, attractions.id AS attraction_id, attractions.name AS attraction_name, attractions.address, attractions.images
            FROM orders
            LEFT JOIN contact on orders.id = contact.order_id
            LEFT JOIN orders_bookings_relation ON orders.id = orders_bookings_relation.order_id
            LEFT JOIN bookings ON orders_bookings_relation.booking_id = bookings.id
            LEFT JOIN attractions ON bookings.attraction_id = attractions.id
            WHERE orders.user_id = %s
""")
        # print(user.email)
        val = (user_id, )
        db.execute(order_query, val)
        result = db.fetchall()
        # print(result)
        if result:
            return result
        else:
            return {}
    except Exception as e:
        logging.error("Error when get user order: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

def create_db_user_img_table():
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        db.execute("USE taipei_day_trip")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS user_img(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                url TEXT,
                Foreign Key(user_id) References users(id)
            )
"""
        db.execute(create_table_query)
    except Exception as e:
        logging.error("Error when creating contact table: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

create_db_user_img_table()

def check_img_exist(user_id):
    db_connection = get_db_connection()
    db = db_connection.cursor(dictionary = True)
    img_query = ("SELECT * FROM user_img where user_id = %s")
    val = (user_id, )
    db.execute(img_query, val)
    return db.fetchall()


def update_db_user_img(user_id, img_url):
    print("ok")
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        img_exist = check_img_exist(user_id)
        if img_exist:
            img_query = ("UPDATE user_img SET url = %s WHERE user_id = %s")
        else:
            img_query = ("INSERT INTO user_img(url, user_id) VALUES(%s, %s)")
        val = (img_url, user_id)
        db.execute(img_query, val)
        db_connection.commit()
    except Exception as e:
        logging.error("Error when create user img: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

def get_db_user_img(user_id):
    try:
        db_connection = get_db_connection()
        db = db_connection.cursor(dictionary = True)
        img_query = ("SELECT * FROM user_img WHERE user_id = %s")
        val = (user_id, )
        db.execute(img_query, val)
        return db.fetchone()
    except Exception as e:
        logging.error("Error when create user: %s", e, exc_info=True)
        return {}
    finally:
        db.close()
        db_connection.close()

