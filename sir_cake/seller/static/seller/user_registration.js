const getDataUserRegistration = async () => {
    const response = await fetch('/js-user-registration-statistic/');
    const json = await response.json();

    const data = {
        labels: json.date,
        datasets: [{
            label: 'Users registered',
            backgroundColor: ['rgb(225, 157, 172)'],
            data: json.number_users,
        }]
    };

    const config = {
        type: 'bar',
        data: data,
        options: {}
    };

    const myChart = new Chart(
        document.getElementById('ChartUseRegistration'),
        config
    );
}

getDataUserRegistration();