// Taken from: https://www.w3schools.com/howto/howto_js_countdown.asp

var expire_date = new Date(expire_date).getTime()
// Update the count down every 1 second
var x = setInterval(function () {
    var now = new Date().getTime();
    var time_left = expire_date - now;

    var minutes = Math.floor((time_left % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((time_left % (1000 * 60)) / 1000);

    document.getElementById("countdown").innerHTML = minutes + "m " + seconds + "s ";

    // Count down is over 
    if (time_left < 0) {
        clearInterval(x);
        document.getElementById("countdown").innerHTML = "EXPIRED";
    }
}, 1000);

