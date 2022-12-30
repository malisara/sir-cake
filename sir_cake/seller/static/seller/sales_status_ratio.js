const getDataSalesStatus = async () => {
    const response = await fetch('/js-sales-status-ratio/');
    const json = await response.json();

    const data = {
        labels: json.status,
        datasets: [{
            label: 'Number of orders',
            backgroundColor: ['rgb(225, 157, 172)', 'rgb(235, 135, 159)'],
            data: json.quantity,
        }]
    };

    const config = {
        type: 'pie',
        data: data,
        options: {}
    };

    const myChart = new Chart(
        document.getElementById('ChartSalesRatio'),
        config
    );
}

getDataSalesStatus();