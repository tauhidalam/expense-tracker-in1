document.addEventListener('DOMContentLoaded', function() {
    // Code to handle chart rendering
    // For example, you can use Chart.js for rendering charts

    var ctxExpense = document.getElementById('expenseChart').getContext('2d');
    var expenseChart = new Chart(ctxExpense, {
        type: 'bar',
        data: {
            labels: ['Rent', 'Utilities', 'Food', 'Entertainment'],
            datasets: [{
                label: 'Expenses',
                data: [1200, 300, 450, 200], // Sample data
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    var ctxFund = document.getElementById('fundChart').getContext('2d');
    var fundChart = new Chart(ctxFund, {
        type: 'pie',
        data: {
            labels: ['Savings', 'Emergency Fund', 'Repair Fund'],
            datasets: [{
                label: 'Funds',
                data: [5000, 1500, 800], // Sample data
                backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'],
                borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'],
                borderWidth: 1
            }]
        }
    });
});
