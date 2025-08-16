# Binance EUR Bot (Spot, multi-crypto, paper/live)

## Lancer en dev
1) Copier `.env.example` en `.env` et ajuster si besoin.
2) `docker compose up --build`

- API FastAPI: http://localhost:8000/docs
- Frontend: http://localhost:5173/

## Passer en live
- Mettre `MODE=live` dans `.env`
- Renseigner `BINANCE_API_KEY` et `BINANCE_API_SECRET`
- Redémarrer: `docker compose up -d --build`

## Endpoints clés
- `GET /health`
- `GET /config` / `PATCH /config`
- `GET /symbols`
- `POST /paper/start` / `POST /paper/stop`
- `POST /live/start` / `POST /live/stop`
- `GET /positions`, `GET /orders`, `GET /signals`
- `POST /backtest` (params: pairs,timeframe,start,end, strategy params)
