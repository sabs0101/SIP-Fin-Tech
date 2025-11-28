# 📈 Smart Financial Dashboard

A Flask-based web application and SIP (Systematic Investment Plan) investment tracker. This project provides a user-friendly dashboard for personalized investment planning. Users can enter a monthly investment amount, select a duration, and filter by asset class to get top recommended assets. It fetches real financial data (using the Alpha Vantage API for stocks and the MFAPI for mutual funds) and computes projected returns for different asset types (stocks, mutual funds, fixed deposits, PPF). The dashboard displays total invested amount, projected final value, absolute gain, and annualized return (CAGR), along with an interactive NAV history chart for each recommendation. It also features a welcoming splash screen and intuitive UI to help users make informed decisions.  
**(Note: You must provide your own Alpha Vantage API key in the code for live stock data.)**

---

## ✅ Features

- **Personalized Recommendations:** Calculates top 10 investment options based on user-input monthly investment, time horizon, and asset class (All, Stocks, Mutual Funds, Fixed Deposits (FD), PPF).
- **Multiple Asset Support:** Includes Indian-market assets such as BSE/NSE stocks, mutual fund schemes (via MFAPI), Fixed Deposits, and Public Provident Fund.
- **Real Data Integration:** Fetches historical price/NAV data using Alpha Vantage API (stocks) and MFAPI (mutual funds). If live API calls fail or no key is provided, the app simulates data for demonstration.
- **SIP Calculator:** Uses the standard SIP formula and compounding to project future value for FDs and PPF based on a fixed annual interest rate.
- **Interactive Dashboard:** Beautiful web UI with a splash screen. Displays recommended assets as clickable cards; clicking a card shows detailed metrics (Total Invested, Final Value, Absolute Gain, CAGR) and a Chart.js line graph of NAV history.
- **Responsive Design:** Modern HTML/CSS/JavaScript front-end for an engaging user experience. The Chart.js graphs allow zoom and pan for closer inspection of investment growth.
- **Filter & Sorting:** Users can filter by asset class (e.g. Stocks only, Mutual Funds only), and the results are automatically sorted by highest projected CAGR.

---

## 🧰 Technologies Used

- **Backend:** Python 3.x with Flask web framework.
- **Data Processing:** Pandas and NumPy for calculations and data manipulation.
- **APIs & Libraries:** Requests for HTTP calls; external APIs Alpha Vantage (for stock prices) and MFAPI (for mutual fund NAVs).
- **Frontend:** HTML, CSS, and JavaScript with Chart.js (via CDN) for interactive charts.
- **Environment:** Project includes a Python virtual environment setup (shown by `.venv` folder) with dependencies.

---

## 💾 Installation

### Clone the repository:
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/PythonProject2
```

### Set up Python environment:
Ensure you have Python 3 installed. It’s recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### Install dependencies:
```bash
pip install flask pandas numpy requests
```
*(If a `requirements.txt` file is added, you can run `pip install -r requirements.txt`.)*

### Configure API Key:
- Open `app.py` in the project root.
- Replace the placeholder:
```python
ALPHA_VANTAGE_KEY = "XMSCKLZPWA5AQFYH"
```
with your own Alpha Vantage API key (free signup at [Alpha Vantage](https://www.alphavantage.co/)).

*(No API key is required for MFAPI.)*

### Run the application:
```bash
python app.py
```

### View in browser:
Navigate to:  
[http://localhost:8080](http://localhost:8080)

---

## 📌 Usage

### Launch the App:
Open the web browser and go to `http://localhost:8080`. You will see a splash screen titled **"Welcome to My SIP Investment Tracker 💰"**. Click the **“Click to Continue 🚀”** button to enter the dashboard.

### Input Parameters:
- **Monthly Investment (₹):** Enter the amount you plan to invest every month (default is ₹5000).
- **Duration (Months):** Enter the number of months for your investment plan (default is 36).
- **Asset Class Filter:** Choose an asset class from the dropdown: *All Assets*, *Stocks Only*, *Mutual Funds Only*, *Fixed Deposits Only*, or *PPF Only*.

### Get Recommendations:
Click the **“Get Top Recommendations 🚀”** button. A loading spinner will appear while fetching data and calculating results.

### View Results:
- The dashboard will display the **Top 10 Investment Options** in a grid of cards. Each card shows: a shortened asset name, asset type, and projected **CAGR**. The cards are sorted by highest CAGR.

### Detailed View:
Click on any investment card to open the detailed view. This view shows:
- **Total Invested**
- **Final Value**
- **Absolute Gain**
- **Annualized (CAGR)**
- **NAV History Chart:** An interactive line chart (Chart.js) of the asset’s NAV history or projected values over time. You can zoom/pan for detail.

### Filter & Re-run:
You can change the input parameters or asset filter and click the button again to see updated recommendations.

### API Endpoint:
For developers, the app also provides a JSON API at:
```
/api/planner/recommendations?monthlyInvestment=5000&durationMonths=36&assetFilter=ALL
```

The endpoint returns a JSON array of recommendation objects with:
```json
{
  "assetName": "...",
  "assetType": "...",
  "totalInvested": ...,
  "currentValue": ...,
  "absoluteReturn": ...,
  "cagrReturnPercent": ...,
  "navHistory": [...],
  "assetCode": "..."
}
```

---

## 🤝 Contributing

Contributions are welcome! Here are some guidelines for contributing:

- **Bug Reports & Feature Requests:** Please open an issue to discuss any bugs or feature ideas. Provide as much detail as possible (error messages, steps to reproduce, etc.).
- **Development:** Fork the repository and create a feature branch for your contribution (e.g. `feature/new-widget`). Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- **Pull Requests:** After making changes, submit a pull request. Clearly describe your changes and link any related issues.
- **Testing:** Currently, no automated tests are provided; manually verify your changes.
- **Documentation:** If you add new features or change behavior, please update this README or add documentation as needed.

We appreciate all contributions and strive to keep the project open and collaborative.

---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute the code. See the [LICENSE](LICENSE) file for details (or add a LICENSE file to the repository).  
If you use this project, consider giving attribution and enjoy building with it!

