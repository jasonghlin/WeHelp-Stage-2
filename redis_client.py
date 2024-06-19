# redis_client.py
import redis
import logging

logging.basicConfig(level=logging.INFO)

try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    logging.info("Connected to Redis successfully.")
except redis.ConnectionError as e:
    logging.error(f"Failed to connect to Redis: {e}")
