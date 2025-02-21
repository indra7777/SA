document.getElementById('analyze-button').addEventListener('click', function() {
    const productUrl = document.getElementById('product-url').value;
    if (!productUrl) {
        alert('Please enter a product URL');
        return;
    }

    fetch(`/scrape?url=${encodeURIComponent(productUrl)}`)
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = `
                <h2>Sentiment Analysis Results</h2>
                <p>Positive: ${data.positive.toFixed(2)}%</p>
                <p>Neutral: ${data.neutral.toFixed(2)}%</p>
                <p>Negative: ${data.negative.toFixed(2)}%</p>
            `;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while analyzing the product.');
        });
});