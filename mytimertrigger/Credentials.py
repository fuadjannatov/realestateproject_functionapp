import os
import dotenv
dotenv.load_dotenv()

login = os.environ.get("login")
password = os.environ.get("password")
server = os.environ.get("server")
database = os.environ.get("database")