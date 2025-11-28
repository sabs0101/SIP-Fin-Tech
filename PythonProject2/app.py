from flask import Flask, jsonify, request, render_template
import requests
import pandas as pd
import numpy as np
import re
import random
from datetime import datetime
from math import pow

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here'

# =========================================================================
# 🔑 API KEY CONFIGURATION (Replace placeholder key here)
# =========================================================================
ALPHA_VANTAGE_KEY = "XMSCKLZPWA5AQFYH"  # <--- PASTE YOUR REAL KEY HERE
# =========================================================================


# --- GLOBAL DATA / CONFIG ---
# Inside app.py

# --- FD and PPF Data (10 Unique Fixed Income Assets for local calculation) ---
FIXED_ASSET_RATES = {
    # FD Rates (8 unique FD rates + 2 PPF rates = 10 fixed assets)
    "FD: Unity SFB": 0.0810,
    "FD: Suryoday SFB": 0.0805,
    "FD: Ujjivan SFB": 0.0795,
    "FD: RBL Bank": 0.0775,
    "FD: Bandhan Bank": 0.0750,
    "FD: IndusInd Bank": 0.0725,
    "FD: Axis Bank": 0.0710,
    "FD: HDFC Bank": 0.0695,
    "PPF: Account 1": 0.0710,  # PPF is used as a separate, fixed-rate category
    "PPF: Account 2": 0.0710
}

# --- THE MASTER ASSET LIST (30 Total Options) ---
TOP_ASSET_IDS = [
    # ------------------------------------
    # 10 STOCK Options (Real Tickers - BSE/NSE)
    # ------------------------------------
    "STOCK: RELIANCE INDS (RELIANCE.BSE)",
    "STOCK: INFOSYS LTD (INFY.BSE)",
    "STOCK: HDFC BANK (HDFCBANK.BSE)",
    "STOCK: TCS (TCS.BSE)",
    "STOCK: ICICI BANK (ICICIBANK.BSE)",
    "STOCK: HIND UNILEVER (HINDUNILVR.BSE)",
    "STOCK: KOTAK BANK (KOTAKBANK.BSE)",
    "STOCK: L&T (LT.BSE)",
    "STOCK: SBIN (SBIN.BSE)",
    "STOCK: ASIAN PAINTS (ASIANPAINT.BSE)",

    # ------------------------------------
    # 10 MUTUAL FUND Options (MFAPI Codes)
    # ------------------------------------
    "MF: Parag Parikh Flexi Cap Fund | 128628",
    "MF: Quant Small Cap Fund | 120828",
    "MF: Axis Bluechip Fund | 119551",
    "MF: Mirae Asset Large Cap | 118837",
    "MF: Canara Robeco Equity Tax | 100030",
    "MF: SBI Small Cap Fund | 119069",
    "MF: Nippon India Large Cap | 120536",
    "MF: HDFC Mid-Cap Opportunities | 101880",
    "MF: ICICI Pru Technology Fund | 119553",
    "MF: Kotak Emerging Equity | 119555",

    # ------------------------------------
    # 10 FIXED INCOME Options (Matching the Rates Map)
    # ------------------------------------
    "FD: Unity SFB",
    "FD: Suryoday SFB",
    "FD: Ujjivan SFB",
    "FD: RBL Bank",
    "FD: Bandhan Bank",
    "FD: IndusInd Bank",
    "FD: Axis Bank",
    "FD: HDFC Bank",
    "PPF: Account 1",
    "PPF: Account 2"
]

# ----------------------------------------------------
# --- SECTION 1: HELPER AND SIMULATION FUNCTIONS (MUST BE DEFINED FIRST) ---
# ----------------------------------------------------

def generate_sample_data(months, base_nav, trend, volatility):
    history = []
    current_nav = base_nav
    start_date = datetime.now() - pd.DateOffset(months=months - 1)

    for i in range(months):
        date = start_date + pd.DateOffset(months=i)
        fluctuation = random.uniform(-volatility / 2, volatility / 2)
        monthly_change = trend + fluctuation
        current_nav += monthly_change

        history.append({"date": date.strftime('%Y-%m-%d'), "value": round(current_nav, 4)})
    return history


def get_stock_fallback_simulation(asset_id, months):
    base_nav = 150.00
    trend = 0.3
    volatility = 5.0
    return generate_sample_data(months, base_nav, trend, volatility)


def get_mf_fallback_simulation(asset_id, months):
    base_nav = 35.00
    trend = 0.4
    volatility = 3.0
    return generate_sample_data(months, base_nav, trend, volatility)


def get_fixed_asset_hybrid_simulation(asset_name, duration_months, annual_rate, monthly_investment_amount):
    # Generates unique, smooth growth for FDs/PPFs (Visual Fix)
    monthly_rate = annual_rate / 12.0
    seed = abs(hash(asset_name))

    current_value = 0.0
    growth_history = []

    start_date = datetime.now() - pd.DateOffset(months=duration_months)

    for month in range(1, duration_months + 1):
        current_value += monthly_investment_amount
        interest = current_value * monthly_rate
        current_value += interest

        unique_random = random.Random(seed + month)
        micro_vol = (unique_random.random() * 0.00005)
        current_value *= (1 + micro_vol)

        date = start_date + pd.DateOffset(months=month - 1)

        growth_history.append({"date": date.strftime('%Y-%m-%d'), "value": round(current_value, 2)})
    return growth_history


def get_asset_code(asset_name, asset_type):
    # Extracts the Ticker, Scheme Code, or FD Ref
    if asset_type == 'STOCK':
        match = re.search(r'\((.*?)\)', asset_name)
        if match:
            full_ticker = match.group(1)
            if '.NS' in full_ticker:
                return f"NSE:{full_ticker.replace('.NS', '')}"
            if '.BSE' in full_ticker:
                return f"BSE:{full_ticker.replace('.BSE', '')}"
            return f"EXCH:{full_ticker}"
        return "EXCH:TICKER"

    if asset_type == 'MF':
        parts = asset_name.split('|')
        if len(parts) > 1:
            return f"SCHEME:{parts[1].strip()}"
        return "ISIN:MFREF"

    if asset_type == 'FD':
        return f"FD-REF-{random.randint(100000000, 999999999)}"

    if asset_type == 'PPF':
        return "PPF-GOV-IND"

    return "N/A"


def get_error_object(asset_id, asset_type):
    return {
        "assetName": asset_id, "assetType": asset_type, "totalInvested": 0,
        "currentValue": 0, "absoluteReturn": 0, "cagrReturnPercent": "ERROR: Data API Failed",
        "navHistory": [], "assetCode": get_asset_code(asset_id, asset_type)
    }


# --- Fixed Deposit Calculation (Guaranteed Return) ---
# NOTE: This must be defined before get_recommendations
def calculate_fixed_return(asset_name, asset_type, monthly_investment, duration_months, annual_rate):
    monthly_rate = annual_rate / 12.0

    future_value = monthly_investment * ((pow(1 + monthly_rate, duration_months) - 1) / monthly_rate) * (
                1 + monthly_rate)

    total_invested = monthly_investment * duration_months
    absolute_return = future_value - total_invested
    cagr = annual_rate * 100.0

    growth_history = get_fixed_asset_hybrid_simulation(asset_name, duration_months, annual_rate, monthly_investment)

    return {
        "assetName": asset_name, "assetType": asset_type, "totalInvested": round(total_invested, 2),
        "currentValue": round(future_value, 2), "absoluteReturn": round(absolute_return, 2),
        "cagrReturnPercent": f"{cagr:.2f}%", "navHistory": growth_history,
        "assetCode": get_asset_code(asset_name, asset_type)
    }


# ----------------------------------------------------
# --- SECTION 2: DATA FETCHING FUNCTIONS (API Calls) ---
# ----------------------------------------------------

def fetch_stock_data(asset_name, symbol, months):
    # This must be defined before the route that calls it
    try:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&"
            f"symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
        )

        if ALPHA_VANTAGE_KEY == "YOUR_API_KEY_HERE":
            raise Exception("API Key missing. Forcing simulation.")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data or "Note" in data:
            raise ValueError(f"API Error or Limit Hit: {data.get('Note', 'Generic Error')}")

        time_series = data.get("Monthly Adjusted Time Series")
        if not time_series:
            raise ValueError("Time series data not found in API response.")

        history = []
        sorted_dates = sorted(time_series.keys())
        history_to_process = sorted_dates[-months:]

        for date_str in history_to_process:
            price = time_series[date_str]['5. adjusted close']
            history.append({"date": date_str, "value": round(float(price), 4)})

        print(f"✅ STOCK API SUCCESS: Fetched real data for {symbol}")
        return history

    except Exception as e:
        print(f"❌ STOCK API FAILURE for {asset_name}: {e}. Using simulation.")
        return get_stock_fallback_simulation(symbol, months)


def fetch_mf_data(scheme_code, months):
    # This must be defined before the route that calls it
    try:
        url = f'https://api.mfapi.in/mf/{scheme_code}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if 'data' not in data or not data['data']:
            raise ValueError("MFAPI returned empty history.")

        history = []
        for entry in reversed(data['data']):
            day, month, year = entry['date'].split('-')
            iso_date = f"{year}-{month}-{day}"
            history.append({"date": iso_date, "value": round(float(entry['nav']), 4)})

        history = history[-months:]

        print(f"✅ MF API SUCCESS: Fetched real data for Scheme {scheme_code}")
        return history
    except Exception as e:
        print(f"❌ MF API FAILURE for Scheme {scheme_code}: {e}. Using simulation.")
        return get_mf_fallback_simulation(scheme_code, months)


# ----------------------------------------------------
# --- SECTION 3: FLASK ROUTES (REST API) ---
# ----------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/planner/recommendations', methods=['GET'])
def get_recommendations():
    try:
        monthly_investment = float(request.args.get('monthlyInvestment', 5000))
        duration_months = int(request.args.get('durationMonths', 36))
        asset_filter = request.args.get('assetFilter', 'ALL').upper()
    except ValueError:
        return jsonify({"error": "Invalid input parameters. Monthly investment and duration must be numbers."}), 400

    # 1. APPLY FILTER LOGIC
    if asset_filter == 'ALL':
        filtered_asset_ids = TOP_ASSET_IDS
    else:
        filtered_asset_ids = [
            asset_id for asset_id in TOP_ASSET_IDS
            if asset_id.split(':')[0].strip() == asset_filter
        ]

    results = []
    for asset_id in filtered_asset_ids:
        asset_type = asset_id.split(':')[0].strip()

        # --- Dispatch to Calculation ---
        if asset_type == 'FD' or asset_type == 'PPF':
            annual_rate = FIXED_ASSET_RATES.get(asset_id, 0.07)
            # Calls the correctly defined function
            result = calculate_fixed_return(asset_id, asset_type, monthly_investment, duration_months, annual_rate)
        else:
            # Market-linked assets need API data first

            if asset_type == 'STOCK':
                match = re.search(r'\((.*?)\)', asset_id)
                symbol = match.group(1) if match else "RELIANCE.NS"
                history = fetch_stock_data(asset_id, symbol, duration_months)

            elif asset_type == 'MF':
                scheme_code = asset_id.split('|')[1].strip()
                history = fetch_mf_data(scheme_code, duration_months)
            else:
                history = []

                # --- Calculation for Market-Linked Assets ---
            if len(history) < duration_months or not history:
                results.append(get_error_object(asset_id, asset_type));
                continue

            # Re-calculate CAGR and value based on retrieved history
            total_invested = monthly_investment * duration_months
            total_units = sum(monthly_investment / item['value'] for item in history)
            final_value = total_units * history[-1]['value']
            absolute_return = final_value - total_invested

            years = duration_months / 12
            cagr = (pow(final_value / total_invested, 1 / years) - 1) * 100 if total_invested else 0

            result = {
                "assetName": asset_id, "assetType": asset_type, "totalInvested": round(total_invested, 2),
                "currentValue": round(final_value, 2), "absoluteReturn": round(absolute_return, 2),
                "cagrReturnPercent": f"{cagr:.2f}%", "navHistory": history,
                "assetCode": get_asset_code(asset_id, asset_type)
            }

        results.append(result)

    # Note: Sorting is done here for the Top 10 display
    results.sort(key=lambda x: float(x['cagrReturnPercent'].replace('%', '')), reverse=True)

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, port=8080)