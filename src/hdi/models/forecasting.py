"""Time series forecasting: ARIMA, Prophet, LSTM."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from hdi.config import FORECAST_HORIZON, SEED

logger = logging.getLogger(__name__)


@dataclass
class ForecastResult:
    """Container for forecast outputs."""
    method: str
    country: str
    indicator: str
    historical: pd.DataFrame  # year, value
    forecast: pd.DataFrame    # year, predicted, ci_lower, ci_upper
    metrics: dict             # MAE, RMSE, MAPE on validation set


def arima_forecast(
    series: pd.Series,
    country: str,
    indicator: str,
    horizon: int = 7,
    order: tuple[int, int, int] = (1, 1, 1),
) -> ForecastResult:
    """ARIMA forecast for a single country-indicator time series.

    Parameters
    ----------
    series : time-indexed series (year as index)
    horizon : number of years to forecast
    order : (p, d, q) ARIMA order
    """
    from statsmodels.tsa.arima.model import ARIMA

    series = series.dropna().sort_index()
    if len(series) < 10:
        raise ValueError(f"Not enough data points for ARIMA: {len(series)}")

    # Train-test split (last 3 years for validation)
    train = series.iloc[:-3]
    test = series.iloc[-3:]

    model = ARIMA(train, order=order)
    fitted = model.fit()

    # Validation
    val_pred = fitted.forecast(steps=len(test))
    mae = np.mean(np.abs(test.values - val_pred.values))
    rmse = np.sqrt(np.mean((test.values - val_pred.values) ** 2))
    mape = np.mean(np.abs((test.values - val_pred.values) / test.values)) * 100

    # Full model forecast
    full_model = ARIMA(series, order=order).fit()
    forecast = full_model.get_forecast(steps=horizon)
    pred = forecast.predicted_mean
    ci = forecast.conf_int(alpha=0.05)

    last_year = series.index[-1]
    forecast_years = range(last_year + 1, last_year + 1 + horizon)

    return ForecastResult(
        method="ARIMA",
        country=country,
        indicator=indicator,
        historical=pd.DataFrame({"year": series.index, "value": series.values}),
        forecast=pd.DataFrame({
            "year": forecast_years,
            "predicted": pred.values,
            "ci_lower": ci.iloc[:, 0].values,
            "ci_upper": ci.iloc[:, 1].values,
        }),
        metrics={"MAE": mae, "RMSE": rmse, "MAPE": mape},
    )


def prophet_forecast(
    series: pd.Series,
    country: str,
    indicator: str,
    horizon: int = 7,
) -> ForecastResult:
    """Prophet forecast for a single country-indicator time series."""
    from prophet import Prophet

    series = series.dropna().sort_index()
    df = pd.DataFrame({
        "ds": pd.to_datetime(series.index.astype(str) + "-01-01"),
        "y": series.values,
    })

    # Train-test split
    train = df.iloc[:-3]
    test = df.iloc[-3:]

    model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    model.fit(train)

    # Validation
    val_future = model.make_future_dataframe(periods=3, freq="YS")
    val_pred = model.predict(val_future)
    val_pred = val_pred.iloc[-3:]
    mae = np.mean(np.abs(test["y"].values - val_pred["yhat"].values))
    rmse = np.sqrt(np.mean((test["y"].values - val_pred["yhat"].values) ** 2))
    mape = np.mean(np.abs((test["y"].values - val_pred["yhat"].values) / test["y"].values)) * 100

    # Full forecast
    full_model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    full_model.fit(df)
    future = full_model.make_future_dataframe(periods=horizon, freq="YS")
    pred = full_model.predict(future)
    pred = pred.iloc[-horizon:]

    last_year = series.index[-1]
    forecast_years = range(last_year + 1, last_year + 1 + horizon)

    return ForecastResult(
        method="Prophet",
        country=country,
        indicator=indicator,
        historical=pd.DataFrame({"year": series.index, "value": series.values}),
        forecast=pd.DataFrame({
            "year": forecast_years,
            "predicted": pred["yhat"].values,
            "ci_lower": pred["yhat_lower"].values,
            "ci_upper": pred["yhat_upper"].values,
        }),
        metrics={"MAE": mae, "RMSE": rmse, "MAPE": mape},
    )


def lstm_forecast(
    df: pd.DataFrame,
    country: str,
    target_col: str,
    feature_cols: list[str] | None = None,
    horizon: int = 7,
    lookback: int = 5,
    hidden_size: int = 64,
    epochs: int = 100,
    seed: int = SEED,
) -> ForecastResult:
    """LSTM sequence model for country-level forecasting.

    Parameters
    ----------
    df : panel DataFrame filtered to a single country
    target_col : column to forecast
    feature_cols : additional feature columns (multivariate)
    horizon : forecast years
    lookback : number of historical years per input sequence
    """
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)

    cols = [target_col] + (feature_cols or [])
    data = df[cols].dropna().values.astype(np.float32)

    if len(data) < lookback + 3:
        raise ValueError(f"Not enough data for LSTM: {len(data)} rows, need {lookback + 3}")

    # Normalize
    mean = data.mean(axis=0)
    std = data.std(axis=0) + 1e-8
    data_norm = (data - mean) / std

    # Create sequences
    X, y = [], []
    for i in range(len(data_norm) - lookback):
        X.append(data_norm[i:i + lookback])
        y.append(data_norm[i + lookback, 0])  # target is first column
    X = np.array(X)
    y = np.array(y)

    # Train-test split
    split = len(X) - 3
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.FloatTensor(y_train)
    X_test_t = torch.FloatTensor(X_test)

    # Model
    input_size = X.shape[2]

    class LSTMModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :]).squeeze(-1)

    model = LSTMModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        pred = model(X_train_t)
        loss = criterion(pred, y_train_t)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Validation
    model.eval()
    with torch.no_grad():
        val_pred = model(X_test_t).numpy()
    val_pred_orig = val_pred * std[0] + mean[0]
    y_test_orig = y_test * std[0] + mean[0]

    mae = np.mean(np.abs(y_test_orig - val_pred_orig))
    rmse = np.sqrt(np.mean((y_test_orig - val_pred_orig) ** 2))
    mape = np.mean(np.abs((y_test_orig - val_pred_orig) / y_test_orig)) * 100

    # Multi-step forecast
    last_seq = torch.FloatTensor(data_norm[-lookback:]).unsqueeze(0)
    forecasts = []
    with torch.no_grad():
        for _ in range(horizon):
            pred = model(last_seq)
            forecasts.append(pred.item())
            new_row = np.zeros((1, 1, input_size), dtype=np.float32)
            new_row[0, 0, 0] = pred.item()
            last_seq = torch.cat([last_seq[:, 1:, :], torch.FloatTensor(new_row)], dim=1)

    forecasts_orig = np.array(forecasts) * std[0] + mean[0]

    years = df["year"].values if "year" in df.columns else np.arange(len(data))
    last_year = int(years[-1])
    forecast_years = range(last_year + 1, last_year + 1 + horizon)

    # Simple CI estimate (±2 * validation RMSE)
    ci_width = 2 * rmse

    return ForecastResult(
        method="LSTM",
        country=country,
        indicator=target_col,
        historical=pd.DataFrame({
            "year": years[-len(data):],
            "value": data[:, 0],
        }),
        forecast=pd.DataFrame({
            "year": list(forecast_years),
            "predicted": forecasts_orig,
            "ci_lower": forecasts_orig - ci_width,
            "ci_upper": forecasts_orig + ci_width,
        }),
        metrics={"MAE": mae, "RMSE": rmse, "MAPE": mape},
    )


def batch_forecast(
    panel: pd.DataFrame,
    countries: list[str],
    indicator: str,
    methods: list[str] | None = None,
    horizon: int = 7,
) -> dict[str, list[ForecastResult]]:
    """Run forecasts for multiple countries and methods.

    Returns dict: method_name -> list of ForecastResult.
    """
    if methods is None:
        methods = ["arima", "prophet"]

    results = {m: [] for m in methods}

    for iso3 in countries:
        country_data = panel[panel["iso3"] == iso3].sort_values("year")
        if indicator not in country_data.columns:
            continue
        series = country_data.set_index("year")[indicator].dropna()
        if len(series) < 10:
            continue

        for method in methods:
            try:
                if method == "arima":
                    r = arima_forecast(series, iso3, indicator, horizon)
                elif method == "prophet":
                    r = prophet_forecast(series, iso3, indicator, horizon)
                elif method == "lstm":
                    r = lstm_forecast(country_data, iso3, indicator, horizon=horizon)
                else:
                    continue
                results[method].append(r)
            except Exception as e:
                logger.warning("Forecast failed: %s/%s/%s: %s", method, iso3, indicator, e)

    return results
