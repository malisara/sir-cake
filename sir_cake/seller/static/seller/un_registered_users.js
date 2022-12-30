const getDataRegisterUser = async () => {
    const response = await fetch('/js-un-registered-users/');
    const json = await response.json();

    const data = {
        labels: json.user_status,
        datasets: [{
            label: 'Number of users',
            backgroundColor: ['rgb(197, 87, 112)', 'rgb(235, 135, 159)'],
            data: json.number_users,
        }]
    };

    const config = {
        type: 'pie',
        data: data,
        options: {}
    };

    const myChart = new Chart(
        document.getElementById('ChartUnregisteredUsers'),
        config
    );
}

getDataRegisterUser();