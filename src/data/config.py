from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()

        self.alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.fred_key = os.getenv("FRED_API_KEY")
        self.news_key = os.getenv("NEWS_API_KEY")

        self.db_path = os.getenv("DB_PATH")

        self.mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
        self.mlflow_exp = os.getenv("MLFLOW_EXPERIMENT_NAME")

        self.model = os.getenv("DEFAULT_MODEL")
        self.horizon = int(os.getenv("PREDICTION_HORIZON", 5))


if __name__ == "__main__":
    config = Config()
    print("DB:", config.db_path)
    print("Model:", config.model)