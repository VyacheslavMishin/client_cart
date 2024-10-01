import os
from dotenv import load_dotenv

load_dotenv()


get_env_var = lambda var_name: os.environ.get(var_name, None)

SQLALCHEMY_DATABASE_URL = get_env_var('database-url')

