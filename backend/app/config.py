from pydantic import BaseModel
import os

class Settings(BaseModel):
    mode: str = os.getenv("MODE", "paper")
    quote_asset: str = os.getenv("QUOTE_ASSET", "EUR")
    timeframe: str = os.getenv("TIMEFRAME", "1h")
    pairs: list[str] = os.getenv("PAIRS","BTC,ETH,BNB,SOL").split(",")
    budget_eur: float = float(os.getenv("BUDGET_EUR", "140"))
    alloc_per_trade_eur: float = float(os.getenv("ALLOC_PER_TRADE_EUR","25"))
    max_concurrent_pos: int = int(os.getenv("MAX_CONCURRENT_POS","4"))

    sma_fast: int = int(os.getenv("SMA_FAST","20"))
    sma_slow: int = int(os.getenv("SMA_SLOW","50"))
    rsi_len: int = int(os.getenv("RSI_LEN","14"))
    rsi_buy: float = float(os.getenv("RSI_BUY","50"))
    rsi_sell: float = float(os.getenv("RSI_SELL","45"))
    atr_len: int = int(os.getenv("ATR_LEN","14"))
    atr_mult_stop: float = float(os.getenv("ATR_MULT_STOP","2.0"))

    binance_key: str = os.getenv("BINANCE_API_KEY","")
    binance_secret: str = os.getenv("BINANCE_API_SECRET","")

    db_user: str = os.getenv("POSTGRES_USER","bot")
    db_pwd: str = os.getenv("POSTGRES_PASSWORD","botpass")
    db_name: str = os.getenv("POSTGRES_DB","botdb")
    db_host: str = os.getenv("DB_HOST","db")
    db_port: str = os.getenv("DB_PORT","5432")

    secret_key: str = os.getenv("SECRET_KEY","change-me")

    @property
    def dsn(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()
