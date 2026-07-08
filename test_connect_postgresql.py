from sqlalchemy import create_engine, text

# 1. Define your connection parameters
USERNAME = 'postgres'
PASSWORD = 'postgres'
HOST = 'localhost'
PORT = '5433'  # Default PostgreSQL port
DATABASE = 'chatbot_db'

# 2. Create the connection URL
# Format: postgresql+psycopg://user:password@host:port/database
DATABASE_URL = f"postgresql+psycopg://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# 3. Create the engine
engine = create_engine(DATABASE_URL)

# 4. Test the connection
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("Connection successful!")
        print("PostgreSQL Version:", result.fetchone()[0])
except Exception as e:
    print("An error occurred:")
    print(e)
