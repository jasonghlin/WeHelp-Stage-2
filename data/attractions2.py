from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Float, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')
mysql_password = os.environ.get("MYSQL")

# --- database.py ---
# MYSQL Series
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://root:{mysql_password}@127.0.0.1:3306/taipei_day_trip"

# MYSQL Series
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)

Base = declarative_base()

# --- models.py ---
class Attractions(Base):
    __tablename__ = 'attractions'

    id = Column(Integer, primary_key=True, index=True)
    SERIAL_NO = Column(String(50), unique=True)
    name = Column(String(255), unique=True)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String(255))
    CAT = Column(String(50))
    description = Column(Text)
    direction = Column(Text)
    MRT = Column(String(50))
    MEMO_TIME = Column(Text)
    rate = Column(Integer)
    date = Column(DateTime)
    avBegin = Column(DateTime)
    avEnd = Column(DateTime)
    langinfo = Column(Integer)
    REF_WP = Column(Integer)
    POI = Column(String(1))
    idpt = Column(String(50))

class AttractionImages(Base):
    __tablename__ = 'attraction_images'

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(Text)
    attraction_id = Column(Integer, ForeignKey("attractions.id"))

# Base.metadata.create_all(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    with engine.connect() as conn:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=conn)
        db = SessionLocal()

        with open("taipei-attractions.json", 'r') as file:
            raw_data = json.load(file)
            data = raw_data["result"]["results"]

        for attraction in data:
            serial_no = attraction["SERIAL_NO"]
            existing_attraction = db.query(Attractions).filter_by(SERIAL_NO=serial_no).first()

            if existing_attraction:
                print(f"Attraction with SERIAL_NO {serial_no} already exists. Skipping.")
                continue

            new_attraction_model = Attractions(
                SERIAL_NO=attraction["SERIAL_NO"],
                name=attraction["name"],
                latitude=attraction["latitude"],
                longitude=attraction["longitude"],
                address=attraction["address"],
                CAT=attraction["CAT"],
                description=attraction["description"],
                direction=attraction["direction"],
                MRT=attraction["MRT"],
                MEMO_TIME=attraction["MEMO_TIME"],
                rate=attraction["rate"],
                date=attraction["date"],
                avBegin=attraction["avBegin"],
                avEnd=attraction["avEnd"],
                langinfo=attraction["langinfo"],
                REF_WP=attraction["REF_WP"],
                POI=attraction["POI"],
                idpt=attraction["idpt"]
            )

            db.add(new_attraction_model)
            db.flush()
            last_row_id = new_attraction_model.id

            img_urls = attraction["file"].split("https://")
            jpg_png_urls = [url for url in img_urls if url.endswith(".jpg") or url.endswith(".JPG") or url.endswith(".png") or url.endswith(".PNG")]
            for url in jpg_png_urls:
                new_attraction_image_model = AttractionImages(
                    image_url=url,
                    attraction_id=last_row_id
                )
                db.add(new_attraction_image_model)

            db.commit()

        db.close()
