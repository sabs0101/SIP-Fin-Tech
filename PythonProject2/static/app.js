let navChartInstance = null;
let allRecommendations = [];

// --- SPLASH SCREEN HANDLER ---
(function() {
    // This code must run immediately to bind the splash button.
    const startButton = document.getElementById('start-button');
    if (startButton) {
        startButton.addEventListener('click', function() {
            document.getElementById('splash-screen').classList.add('hidden');
            // Show the main containers
            const mainDashboard = document.getElementById('main-dashboard');
            const mainHeader = document.getElementById('main-header');
            if (mainDashboard) mainDashboard.classList.remove('hidden');
            if (mainHeader) mainHeader.classList.remove('hidden');
        });
    }
})();


// --- Wait for the entire HTML structure to be ready for the main app logic ---
document.addEventListener('DOMContentLoaded', function() {
    "use strict";

    // --- CORE EVENT LISTENER: MAIN DASHBOARD BUTTON ---
    document.getElementById('recommendation-button').addEventListener('click', async function(e) {
        e.preventDefault();

        // 1. Get Data and Prepare UI
        const form = document.getElementById('recommendation-form');
        const formData = new FormData(form);

        const monthlyInvestment = formData.get('monthlyInvestment');
        const durationMonths = formData.get('durationMonths');
        const assetFilter = document.getElementById('asset-filter').value;

        const params = new URLSearchParams({
            monthlyInvestment: monthlyInvestment,
            durationMonths: durationMonths,
            assetFilter: assetFilter
        }).toString();

        const endpoint = `/api/planner/recommendations?${params}`;

        const loadingDiv = document.getElementById('loading');
        const recContainer = document.getElementById('recommendations-container');
        const resultsDiv = document.getElementById('results');
        const advisoryDiv = document.getElementById('advisory-message');

        resultsDiv.classList.add('hidden');
        recContainer.classList.add('hidden');
        advisoryDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');

        try {
            // 2. Attempt the Network Call
            const response = await fetch(endpoint);

            if (!response.ok) {
                console.error(`NETWORK FAILURE! Status: ${response.status}. URL: ${endpoint}`);
                const errorText = await response.text();
                console.error('Python Server Error Trace:', errorText);
                alert(`API Request Failed. HTTP Status ${response.status}. Check Python console.`);
                return;
            }

            // 3. Process the successful JSON response
            allRecommendations = await response.json();

            if (allRecommendations.length > 0 && allRecommendations[0].cagrReturnPercent.startsWith("ERROR")) {
                alert(`Backend Calculation Error: ${allRecommendations[0].cagrReturnPercent}`);
                return;
            }

            // 4. Success Path
            renderRecommendationCards(allRecommendations);
            renderAdvisoryMessage(allRecommendations, assetFilter);
            recContainer.classList.remove('hidden');

            if (allRecommendations.length > 0) {
                displayDetailedResult(allRecommendations[0]);
                resultsDiv.classList.remove('hidden');
            }

        } catch (error) {
            console.error('CRITICAL UNCAUGHT JS/NETWORK ERROR:', error);
            alert(`An unhandled error occurred (JS or Network). Please see the browser console (F12) for details.`);
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });


    // --- HELPER FUNCTION TO GET ASSET CODE (omitted for space) ---
    function getAssetCodeForCard(assetName) {
        const match = assetName.match(/\((.*?)\)/);
        if (match) {
            return match[1].trim();
        }
        const parts = assetName.split('|');
        if (parts.length > 1) {
            return parts[1].trim();
        }
        return assetName.split(':')[1] ? assetName.split(':')[1].trim() : 'N/A';
    }

    // --- NEW: ADVISORY MESSAGE LOGIC (omitted for space) ---
    function renderAdvisoryMessage(recommendations, assetFilter) {
        const advisoryDiv = document.getElementById('advisory-message');
        if (recommendations.length === 0) {
            advisoryDiv.classList.add('hidden');
            return;
        }

        const bestOption = recommendations[0];
        const bestType = bestOption.assetType;
        const bestName = bestOption.assetName.split(':')[1] ? bestOption.assetName.split(':')[1].trim() : bestOption.assetName;
        const bestRate = bestOption.cagrReturnPercent;

        let message = `<p><strong>Advisory:</strong> Based on historical returns and your duration, the top-performing asset is **${bestName}** with an Annualized Return (CAGR) of **${bestRate}**.</p>`;

        if (bestType === 'STOCK' || bestType === 'MF') {
            message += `<p>💡 **Strategy Note:** Mutual Funds and Stocks are best suited for **longer-term (7+ years)** goals to maximize compounding and mitigate short-term volatility.</p>`;
        } else if (bestType === 'FD' || bestType === 'PPF') {
            message += `<p>💡 **Strategy Note:** Fixed Deposits and PPF are ideal for **shorter-to-medium term goals (1-5 years)** and for guaranteed **capital preservation.**</p>`;
        }

        advisoryDiv.innerHTML = message;
        advisoryDiv.classList.remove('hidden');
    }


    // --- CORE RENDERING FUNCTIONS (omitted for space) ---

    function renderRecommendationCards(recommendations) {
        const container = document.getElementById('card-grid');
        container.innerHTML = '';

        if (recommendations.length === 0) {
            container.innerHTML = '<p style="grid-column: span 4; text-align: center;">No recommendations found based on your criteria.</p>';
            return;
        }

        const topCagr = recommendations[0].cagrReturnPercent;

        recommendations.forEach((data, index) => {
            const card = document.createElement('div');

            const isBest = data.cagrReturnPercent === topCagr && data.assetType !== 'FD' && data.assetType !== 'PPF';

            card.className = 'recommendation-card' + (isBest ? ' best-option' : '');
            card.dataset.index = index;

            let displayAssetName = data.assetName.split(':')[1] ? data.assetName.split(':')[1].trim() : data.assetName;

            card.innerHTML = `
                <h3>${displayAssetName.substring(0, 18).trim()}...</h3>
                <p>Type: <strong>${data.assetType}</strong></p>
                <p>CAGR: <span class="card-cagr">${data.cagrReturnPercent}</span></p>
            `;

            card.addEventListener('click', () => displayDetailedResult(data));

            container.appendChild(card);
        });
    }


    function displayDetailedResult(data) {

        const formatCurrency = (value) => {
            const number = parseFloat(value);
            if (isNaN(number)) return '₹0.00';
            return `₹${number.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        };

        const investmentDuration = document.getElementById('duration').value;
        const finalValue = formatCurrency(data.currentValue);

        document.getElementById('result-asset-name').textContent = `${data.assetName} [Code: ${data.assetCode}]`;

        document.getElementById('total-invested').textContent = formatCurrency(data.totalInvested);
        document.getElementById('current-value').textContent = formatCurrency(data.currentValue);

        const absReturnEl = document.getElementById('absolute-return');
        const absoluteReturnValue = parseFloat(data.absoluteReturn);

        absReturnEl.textContent = formatCurrency(data.absoluteReturn);
        absReturnEl.classList.remove('highlight-gain', 'highlight-loss');

        if (absoluteReturnValue >= 0) {
            absReturnEl.classList.add('highlight-gain');
        } else {
            absReturnEl.classList.add('highlight-loss');
        }

        document.getElementById('cagr-return').textContent = data.cagrReturnPercent;

        const chartContainer = document.querySelector('.chart-container');
        if (data.navHistory && data.navHistory.length > 0) {
            renderChart(data.navHistory, data.assetType, investmentDuration, finalValue);
            chartContainer.style.display = 'block';
        } else {
            if(navChartInstance) navChartInstance.destroy();
            chartContainer.style.display = 'none';
        }

        document.getElementById('results').classList.remove('hidden');
    }


    // --- FUNCTION TO RENDER CHART (THE FINAL FIX IS HERE) ---
    function renderChart(history, assetType, investmentDuration, finalValue) {
        const ctx = document.getElementById('navChart').getContext('2d');

        const dates = history.map(item => item.date);
        const values = history.map(item => item.value);

        if (navChartInstance) {
            navChartInstance.destroy();
        }

        let graphLabel;
        let lineTension;
        const durationInYears = (investmentDuration / 12).toFixed(1);
        var axisConfig;

        if (assetType === 'STOCK' || assetType === 'MF') {
            // 1. Find Min/Max Values for Dynamic Zoom
            const floatValues = values.map(v => parseFloat(v));
            const minVal = Math.min(...floatValues);
            const maxVal = Math.max(...floatValues);

            // Add a 5% buffer padding
            const buffer = (maxVal - minVal) * 0.05;

            // Use low tension for realistic market volatility (jagged line)
            graphLabel = assetType === 'STOCK' ? `Past ${durationInYears} Years History (API Data)` : `Past ${durationInYears} Years History (API Data)`;
            lineTension = 0.15;

            // Define axis configuration for zoom
            axisConfig = {
                min: Math.floor(minVal - buffer), // Zoom in aggressively
                max: Math.ceil(maxVal + buffer),  // Zoom in aggressively
                display: true,
                title: { display: true, text: 'Value (₹)' },
                beginAtZero: false // Crucial: Tell Chart.js NOT to start at zero
            };

        } else {
            // Fixed income (FD/PPF): High tension for a smooth compounding curve
            graphLabel = `Projected Final Value: ${finalValue} (over ${durationInYears} Years)`;
            lineTension = 0.9;
            // For compounding, we start near zero or at zero
            axisConfig = {
                min: 0, // Ensure the compounding curve starts near the bottom
                display: true,
                title: { display: true, text: 'Value (₹)' },
                beginAtZero: true // Crucial: Start at zero for compounding curves
            };
        }


        navChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: graphLabel,
                    data: values,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: lineTension
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: true, title: { display: true, text: 'Date' } },
                    y: axisConfig // Apply the dynamically generated axis configuration
                },
                plugins: {
                    legend: { display: true }
                }
            }
        });
    }

}); // Closes the DOMContentLoaded listener