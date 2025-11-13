# API Documentation

## Overview

The Crypto Trading Platform provides a RESTful API built with FastAPI for running backtests, fetching market data, and managing trading strategies.

Base URL: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication in development mode. For production, implement API key authentication by setting the `X-API-Key` header.

## Endpoints

### Health Check

Check API health status.

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### List Strategies

Get all available trading strategies.

**GET** `/strategies`

**Response:**
```json
{
  "strategies": [
    {
      "name": "ma_crossover",
      "description": "Moving Average Crossover Strategy",
      "params": {
        "short_period": 10,
        "long_period": 30,
        "ma_type": "sma"
      }
    },
    ...
  ]
}
```

### Run Backtest

Execute a backtest with specified parameters.

**POST** `/backtest`

**Request Body:**
```json
{
  "strategy": "ma_crossover",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000.0,
  "commission": 0.001,
  "slippage": 0.0005,
  "strategy_params": {
    "short_period": 10,
    "long_period": 30
  },
  "position_sizing": "fixed"
}
```

**Response:**
```json
{
  "strategy": "MA_Crossover",
  "symbol": "BTC/USDT",
  "initial_capital": 10000.0,
  "final_equity": 12500.0,
  "total_return": 25.0,
  "metrics": {
    "total_return": 25.0,
    "annualized_return": 28.5,
    "sharpe_ratio": 1.85,
    "sortino_ratio": 2.15,
    "max_drawdown": 8.5,
    "calmar_ratio": 3.35,
    "win_rate": 62.5,
    "total_trades": 48,
    "winning_trades": 30,
    "losing_trades": 18
  },
  "config": {
    "commission": 0.001,
    "slippage": 0.0005,
    "initial_capital": 10000.0,
    "position_sizing": "fixed"
  },
  "total_trades": 48
}
```

### Fetch Market Data

Fetch OHLCV data for a symbol.

**POST** `/data/fetch`

**Request Body:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "start_date": "2023-01-01",
  "end_date": "2023-01-31",
  "limit": 1000
}
```

**Response:**
```json
{
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "rows": 744,
  "data": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "open": 16500.0,
      "high": 16550.0,
      "low": 16480.0,
      "close": 16520.0,
      "volume": 1234.56
    },
    ...
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

- 60 requests per minute per IP
- 1000 requests per hour per IP

## Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Examples

### Python Example

```python
import requests

# Run a backtest
response = requests.post(
    "http://localhost:8000/backtest",
    json={
        "strategy": "rsi",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_capital": 10000,
        "strategy_params": {
            "period": 14,
            "overbought": 70,
            "oversold": 30
        }
    }
)

results = response.json()
print(f"Total Return: {results['total_return']:.2f}%")
```

### cURL Example

```bash
curl -X POST http://localhost:8000/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "macd",
    "symbol": "ETH/USDT",
    "timeframe": "4h",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 10000
  }'
```
