import dropbox
import config
import os

# ---------------------------------------------
# Define your local file path here
file_path = '<INSERT_YOUR_LOCAL_PATH_HERE>/'  # ← Example: 'C:/Users/YourName/Desktop/data/'

# Check if the path has been updated
if '<INSERT_YOUR_LOCAL_PATH_HERE>' in file_path:
    raise ValueError("Please update 'file_path' with the path to your local directory.")
# ---------------------------------------------

# Full path to the file that will be uploaded
file_from = file_path + 'weather.csv'

# Path in Dropbox where the file will be uploaded
file_to = '/weather_csv/weather.csv'

# Token generated in Dropbox to allow the app to access the Dropbox API
access_token = config.drop_key

# Create and initialize a Dropbox instance with the access token
dbx = dropbox.Dropbox(access_token)

# Open and read the local file
with open(file_from, 'rb') as f:
    # Upload weather.csv to Dropbox; if the file already exists, it will be overwritten
    dbx.files_upload(f.read(), file_to, mode=dropbox.files.WriteMode.overwrite)

print("Upload complete")
