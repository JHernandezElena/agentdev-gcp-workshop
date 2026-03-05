from agent import SimpleLangGraphApp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
PROJECT_ID=os.getenv("PROJECT_ID")
LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")


if __name__ == "__main__":
    app = SimpleLangGraphApp(PROJECT_ID, LOCATION)
    app.set_up()
    print(app.query("What are the details of a smartphone?"))
    print(app.query("What are the details of a coffee?"))
    print(app.query("What are the details of a shoe?"))
    print(app.query("What are the details of a headphone?"))
    print(app.query("What are the details of a speaker?"))