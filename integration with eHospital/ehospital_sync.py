# %%
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# %%
# MySQL connection parameters from environment variables
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT', '3306')
DATABASE = os.getenv('DB_NAME')
USERNAME = os.getenv('DB_USERNAME')
PASSWORD = os.getenv('DB_PASSWORD')

# Validate that all required environment variables are set
required_vars = ['DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# %%
# Create MySQL connection using mysql-connector-python
try:
    connection = mysql.connector.connect(
        host=HOST,
        port=int(PORT),
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD
    )
    
    if connection.is_connected():
        print(f"Successfully connected to MySQL database: {DATABASE}")
        print(f"MySQL Server version: {connection.get_server_info()}")
        
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")
    connection = None


# %%
# Alternative: Create SQLAlchemy engine for pandas integration
engine = create_engine(f'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
print("SQLAlchemy engine created successfully")


# %%
# Load the doctor_registration table
try:
    # Method 1: Using pandas with SQLAlchemy engine
    query = """ SELECT  EmailId email , password plaintext_password, concat_ws(" ",Fname,Lname) as name FROM PRD01.doctors_registration; """
    doctor_registration_df = pd.read_sql(query, engine)
    
    print(f"Successfully loaded doctor_registration table")
    print(f"Shape: {doctor_registration_df.shape}")
    print(f"Columns: {list(doctor_registration_df.columns)}")
    
except Exception as e:
    print(f"Error loading table: {e}")
    doctor_registration_df = None


# %%
doctor_registration_df

# %%
# Clean up connections
if connection and connection.is_connected():
    connection.close()
    print("MySQL connection closed")

if engine:
    engine.dispose()
    print("SQLAlchemy engine disposed")


# %%
from passlib.hash import bcrypt
doctor_registration_df['password'] = doctor_registration_df['plaintext_password'].apply(
    lambda pwd: bcrypt.using(rounds=10).hash(pwd)
)


# %%
import uuid
doctor_registration_df['id'] = [str(uuid.uuid4()) for _ in range(len(doctor_registration_df))]
import time
doctor_registration_df.drop(columns=['plaintext_password'], inplace=True)
doctor_registration_df['role'] = 'user'
doctor_registration_df['profile_image_url'] = '/user.png'
doctor_registration_df['api_key'] = None
doctor_registration_df['settings'] = """{"ui": {"models": ["dti6302_chatbot"]}}"""
doctor_registration_df['info'] = 'null'
doctor_registration_df['oauth_sub'] = None
doctor_registration_df['created_at'] = int(time.time())
doctor_registration_df['updated_at'] = int(time.time())
doctor_registration_df['last_active_at'] = int(time.time())
doctor_registration_df['active'] = 1


# %%
user_df = doctor_registration_df.drop(columns=['active'], inplace=False)
auth_df = doctor_registration_df[['id', 'email', 'password','active']]

# %%
import sqlite3
# Connect to SQLite database for insert/update operations
conn = sqlite3.connect('webui.db')
cursor = conn.cursor()

# Loop through auth_df and sync with SQLite
insert_count = 0
update_count = 0

ids_list = []

for index, row in auth_df.iterrows():
    email = row['email']
    user_id = row['id']
    password = row['password']
    #print(email)
    
    # Check if email exists in SQLite auth table
    cursor.execute(""" SELECT id FROM auth WHERE email = ? """, (email,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Email exists, update only the password
        cursor.execute("""
            UPDATE auth 
            SET password = ?
            WHERE email = ?
        """, (password, email))
        update_count += 1
        print(f"Updated password for email: {email}")
        
    else:
        # Email doesn't exist, insert the whole record
        cursor.execute("""
            INSERT INTO auth (id, email, password, active)
            VALUES (?, ?, ?, ?)
        """, (user_id, email, password, 1))  # assuming active = 1 for new records
        insert_count += 1
        
        ids_list.append(user_id)
        print(f"Inserted new record for email: {email}")
        

import ast
cursor.execute(""" SELECT user_ids FROM "group" WHERE name = 'DTI6302' """ )
# Fetch all results
user_ids = cursor.fetchall()
current_list = ast.literal_eval(user_ids[0][0])

new_list = list(set(current_list + ids_list))
print(new_list)
cursor.execute("""
            UPDATE "group"
            SET user_ids = ?
            WHERE name = ?
        """, (str(new_list), "DTI6302"))


# Commit the changes
conn.commit()

print(f"\nSummary:")
print(f"Records inserted: {insert_count}")
print(f"Records updated: {update_count}")
print(f"Total processed: {len(auth_df)}")



# Loop through user_df and sync with SQLite user table
user_insert_count = 0
user_update_count = 0

for index, row in user_df.iterrows():
    email = row['email']
    user_id = row['id']
    name = row['name']
    role = row['role']
    profile_image_url = row['profile_image_url']
    api_key = row['api_key']
    created_at = row['created_at']
    updated_at = row['updated_at']
    last_active_at = row['last_active_at']
    settings = row['settings']
    info = row['info']
    oauth_sub = row['oauth_sub']
    
    # Check if email exists in SQLite user table
    cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Email exists, update the record (all fields except id and email)
        cursor.execute("""
            UPDATE user 
            SET name = ?, role = ?, profile_image_url = ?, api_key = ?, 
                updated_at = ?, last_active_at = ?, settings = ?, info = ?, oauth_sub = ?
            WHERE email = ?
        """, (name, role, profile_image_url, api_key, updated_at, last_active_at, 
              settings, info, oauth_sub, email))
        user_update_count += 1
        print(f"Updated user record for email: {email}")
        
    else:
        # Email doesn't exist, insert the whole record
        cursor.execute("""
            INSERT INTO user (id, name, email, role, profile_image_url, api_key, 
                            created_at, updated_at, last_active_at, settings, info, oauth_sub)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, email, role, profile_image_url, api_key, 
              created_at, updated_at, last_active_at, settings, info, oauth_sub))
        user_insert_count += 1
        print(f"Inserted new user record for email: {email}")

# Commit the changes
conn.commit()

print(f"\nUser Table Sync Summary:")
print(f"Records inserted: {user_insert_count}")
print(f"Records updated: {user_update_count}")
print(f"Total processed: {len(user_df)}")


# Close the connection
conn.close()



