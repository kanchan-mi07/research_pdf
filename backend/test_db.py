from sqlalchemy import create_engine

DATABASE_URL = "postgresql://askgalore_owner:npg_z5x9UBmVvAfP@ep-cold-silence-aok2c585.c-2.ap-southeast-1.aws.neon.tech/askgalore?sslmode=require"

engine = create_engine(DATABASE_URL)
try:
  with engine.connect() as connection:
    print("Database connection successful!")
except Exception as e:
  print(f"Database connection failed:\n{e}")