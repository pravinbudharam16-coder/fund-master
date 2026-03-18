function getPrediction() {
    fetch("/api/prediction")
        .then(res => res.json())
        .then(data => {
            document.getElementById("income").innerText = data.predicted_income;
            document.getElementById("expense").innerText = data.predicted_expense;
            document.getElementById("savings").innerText = data.predicted_savings;
        })
        .catch(() => alert("Prediction API error"));
}