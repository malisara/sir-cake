const getSalescategory = async () => {
    const response = await fetch('/js-sold-per-category/');
    const json = await response.json();

    const data = {
        labels: json.category,
        datasets: [{
            label: 'Revenues (€)',
            backgroundColor: ['rgb(197, 87, 112)', 'rgb(235, 135, 159)', 'rgb(225, 157, 172)'],
            data: json.total_sales,
        }]
    };

    const config = {
        type: 'bar',
        data: data,
        options: {
            plugins: {
                legend: {
                    display: false,

                }
            }

        }
    };

    const myChart = new Chart(
        document.getElementById('ChartSoldCategory'),
        config
    );
}

getSalescategory();