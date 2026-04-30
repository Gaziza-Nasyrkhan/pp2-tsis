import psycopg2
import csv
import json

# PostgreSQL configuration (directly in code)
config = {
    'dbname': 'snake',
    'user': 'postgres',
    'password': 'pp2psql',
    'host': '127.0.0.1',
    'port': '5432'
}

# Connect to database
try:
    conn = psycopg2.connect(**config)
    print("✅ Connected to database successfully!")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit()

cur = conn.cursor()

# Rest of your code continues here...