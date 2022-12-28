const getDataSales = async () => {
    const response = await fetch('/js-sales-graph/');
    const json = await response.json();

    const data = {
        labels: json.date,
        datasets: [{
            label: 'Revenue',
            backgroundColor: ['rgb(254, 200, 216)'],
            data: json.sales,
        }]
    };

    const config = {
        type: 'line',
        data: data,
        options: {}
    };

    const myChart = new Chart(
        document.getElementById('chartSales'),
        config
    );
}

getDataSales();