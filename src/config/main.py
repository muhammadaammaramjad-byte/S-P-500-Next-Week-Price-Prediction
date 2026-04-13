from config import Config

def main():
    config = Config()

    print("🚀 Starting SP500 Pipeline...")
    print(f"📁 Database: {config.db_path}")
    print(f"🤖 Model: {config.model}")
    print(f"📊 Horizon: {config.horizon} days")

    # Example: check API keys
    if not config.alpha_key:
        raise ValueError("Missing ALPHA_VANTAGE_API_KEY")

    if not config.fred_key:
        raise ValueError("Missing FRED_API_KEY")

    print("✅ Config loaded successfully!")

if __name__ == "__main__":
    main()