# storage/s3_handler.py

import s3fs
import json

def get_fs():
    """
    Returns an authenticated s3fs filesystem object.
    Requires AWS credentials to be set via environment variables,
    shared credentials file (~/.aws/credentials), or IAM role.
    """
    return s3fs.S3FileSystem(anon=False)

def upload_json_to_s3(path, data):
    """
    Uploads a JSON-serializable object to S3 at the specified path.
    
    Args:
        path (str): S3 path in the format 'bucket-name/prefix/file.json'
        data (dict): Python dictionary to upload as JSON
    """
    fs = get_fs()
    try:
        with fs.open(path, 'w') as f:
            json.dump(data, f)
        print(f"✅ Uploaded to S3: {path}")
    except Exception as e:
        print(f"❌ Failed to upload to S3: {e}")
        raise

def load_json(path):
    """
    Loads a JSON object from an S3 file.
    
    Args:
        path (str): Full S3 path to the JSON file.
    
    Returns:
        dict: Parsed JSON data
    """
    fs = get_fs()
    try:
        with fs.open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load from S3: {e}")
        raise

def list_data_files(prefix):
    """
    Lists all files under a given S3 prefix (folder path).
    
    Args:
        prefix (str): Prefix like 'bucket-name/bitcoin/'
    
    Returns:
        list[str]: File paths under that prefix
    """
    fs = get_fs()
    try:
        return fs.ls(prefix)
    except FileNotFoundError:
        print(f"⚠️ Prefix not found: {prefix}")
        return []
    except Exception as e:
        print(f"❌ Error listing S3 prefix '{prefix}': {e}")
        raise
