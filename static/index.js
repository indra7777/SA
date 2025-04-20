// Sentiment Flow UI/UX - index.js
const form = document.getElementById('analyze-form');
const productUrlInput = document.getElementById('product-url');
const platformSelect = document.getElementById('platform-select');
const loadingSection = document.getElementById('loading-section');
const resultSection = document.getElementById('result-section');
const productImage = document.getElementById('product-image');
const productTitle = document.getElementById('product-title');
const productDesc = document.getElementById('product-desc');
const positivePct = document.getElementById('positive-pct');
const neutralPct = document.getElementById('neutral-pct');
const negativePct = document.getElementById('negative-pct');
const sentimentChartCanvas = document.getElementById('sentiment-chart');
const analyzeAnotherBtn = document.getElementById('analyze-another');

let selectedPlatform = 'flipkart';

function detectPlatform(url) {
    if (url.includes('flipkart.com')) return 'flipkart';
    if (url.includes('dell.com')) return 'dell';
    if (url.includes('nykaa.com')) return 'nykaa';
    if (url.includes('nike.com')) return 'nike';
    if (url.includes('myntra.com')) return 'myntra';
    return 'flipkart';
}

platformSelect.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        selectedPlatform = e.target.dataset.platform;
        Array.from(platformSelect.children).forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
    }
});

productUrlInput.addEventListener('input', (e) => {
    const url = e.target.value;
    const platform = detectPlatform(url);
    selectedPlatform = platform;
    Array.from(platformSelect.children).forEach(btn => {
        btn.classList.toggle('active', btn.dataset.platform === platform);
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = productUrlInput.value.trim();
    if (!url) {
        productUrlInput.classList.add('input-error');
        productUrlInput.placeholder = 'Please enter a product URL!';
        return;
    }
    productUrlInput.classList.remove('input-error');
    form.style.display = 'none';
    loadingSection.style.display = 'flex';
    resultSection.style.display = 'none';

    let apiUrl;
    switch (selectedPlatform) {
        case 'flipkart':
            apiUrl = `/scrape?url=${encodeURIComponent(url)}`;
            break;
        case 'dell':
            apiUrl = `/scrape/dell?url=${encodeURIComponent(url)}`;
            break;
        case 'nykaa':
            apiUrl = `/scrape/nykaa?url=${encodeURIComponent(url)}`;
            break;
        case 'nike':
            apiUrl = `/scrape/nike?url=${encodeURIComponent(url)}`;
            break;
        case 'myntra':
            apiUrl = `/scrape/myntra?url=${encodeURIComponent(url)}`;
            break;
        default:
            apiUrl = `/scrape?url=${encodeURIComponent(url)}`;
    }

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        loadingSection.style.display = 'none';
        if (data.error) throw new Error(data.error);
        // Show product info if available
        if (data.product_title) {
            productTitle.textContent = data.product_title;
            productTitle.style.display = 'block';
        } else {
            productTitle.textContent = '';
            productTitle.style.display = 'none';
        }
        if (data.description) {
            productDesc.textContent = data.description;
            productDesc.style.display = 'block';
        } else if (data.product_details) {
            productDesc.textContent = data.product_details;
            productDesc.style.display = 'block';
        } else {
            productDesc.textContent = '';
            productDesc.style.display = 'none';
        }
        if (data.image_url) {
            productImage.src = data.image_url;
            productImage.style.display = 'block';
        } else if (data.image_urls) {
            productImage.src = data.image_urls.split(',')[0];
            productImage.style.display = 'block';
        } else {
            productImage.style.display = 'none';
        }
        // Sentiment stats
        let sentiment;
        if (data.sentiment_analysis) {
            sentiment = data.sentiment_analysis;
        } else {
            sentiment = data;
        }
        const total = (sentiment.positive || 0) + (sentiment.neutral || 0) + (sentiment.negative || 0);
        const posPct = total ? (sentiment.positive / total * 100) : 0;
        const neuPct = total ? (sentiment.neutral / total * 100) : 0;
        const negPct = total ? (sentiment.negative / total * 100) : 0;
        positivePct.textContent = `${posPct.toFixed(1)}%`;
        neutralPct.textContent = `${neuPct.toFixed(1)}%`;
        negativePct.textContent = `${negPct.toFixed(1)}%`;
        // Chart
        if (window.sentimentChart) window.sentimentChart.destroy();
        window.sentimentChart = new Chart(sentimentChartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [sentiment.positive, sentiment.neutral, sentiment.negative],
                    backgroundColor: [
                        'rgba(0, 200, 117, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                cutout: '70%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: { font: { size: 16 } }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value}`;
                            }
                        }
                    }
                }
            }
        });
        resultSection.style.display = 'flex';
    } catch (err) {
        loadingSection.style.display = 'none';
        form.style.display = 'block';
        alert('Error: ' + err.message);
    }
});

analyzeAnotherBtn.addEventListener('click', () => {
    resultSection.style.display = 'none';
    form.style.display = 'block';
    productUrlInput.value = '';
    productUrlInput.focus();
});