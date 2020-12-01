window.onload = startup
var intervalTime = 1000; //Ms 
var cpuElement, cpuTempElement,memoryElement, networkUploadElement, networkDownloadElement, batteryElement;
var chart1; 

function formToJson(form) { // Converting form data to json data.
    var json = "{"

    for (i = 0; i < form.length; i = i + 2) {   // Loops thrue every other element of the form
        key = form[i].id;                       // Adding the ID as key
        val = form[i].value;                    // Adding the value as value

        json += '"' + key + '":"' + val + '"';
        json += i != form.length - 2 ? "," : "}";

        if (form[i].nodeName == "SELECT")       // If the form type is SELECT then dont look for a input feald
            i++;
        else
            form[i + 1].value = form[i].value;  // If there is a input feald change the value of that to value
    }

    return JSON.stringify(JSON.parse(json));    // Return the json file
}

function jsonToForm(json, form) {   // Converting json to form data
    let obj = JSON.parse(JSON.stringify(json));
    
    console.log(obj);
    for (const [key, value] of Object.entries(obj)) { // For all elements of the json (key and value) set the correct element
        form.elements.namedItem(key).value = value;

        if (form.elements.namedItem(key).nodeName != "SELECT")      // If the element is not a SELECT then it has a input box
            form.elements.namedItem(key + "Typed").value = value;   // Set value of input box to value of element
    }
}

function updateSlider(formSlider) {         // Get data about the slider form the API
    receiveJSON("/api/config", data => {
        console.log(data)
        json = JSON.parse(data)
    })
}

function receiveJSON(url, onReceived) {     // Function to receive json data form the api
    var xhr = new XMLHttpRequest();
    var json = undefined;

    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");   // Sets the type of received data to json
    xhr.onreadystatechange = () -> {
        if (xhr.status == 200 && xhr.readyState == 4 && xhr.responseText != "") {
            json = JSON.parse(xhr.responseText);
            onReceived(json); // Using the provided function to handle the json filed received
        }
    }
    xhr.send(); // Sends the request
}

function sendJson(json, url) {      // Send json files to the server using the api
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json")    // Sets the correct header for the data beeing sendt
    xhr.send(json);
}

function startup() {    // Everything that is going to be done at startup
    console.log("Start up")
    cpuElement = document.getElementById("cpu"); 
    cpuTempElement = document.getElementById("cpuTemp");
    memoryElement = document.getElementById("mem");
    networkUploadElement = document.getElementById("networkUpload");
    networkDownloadElement = document.getElementById("networkDownload"); 
    batteryElement = document.getElementById("battery")

    chart1 = document.getElementById("chart1"); 

    form = document.getElementsByTagName("form")[0];

    // Update the sliders first
    receiveJSON("/api/config", data => {
        jsonToForm(data, form);
    });

    // Set the form to update the json on the server on every change
    form.onchange = function() {
        console.log("Form change");
        sendJson(formToJson(form), "/api/config");
    }

    // Functions for creating the nettwork and memmory graf
    Chart.defaults.global.defaultFontColor = 'white';
    var ctx = chart1.getContext('2d');
    var chart = new Chart(ctx, {
        type: 'line',
        responsive: false,
        width:500,
        height:300,
        scaleShowGridLines: false,
        showScale: false,
        maintainAspectRatio: this.maintainAspectRatio,
        barShowStroke: false,
        data: {
            labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
            datasets: [{
                label: 'CPU',
                borderColor: 'rgb(255, 99, 132)',
                data: []
            },
            {
                label: 'MEMORY',
                borderColor: 'rgb(99, 255, 132)',
                data: []
            }]
        },

        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }]
            },
            maintainAspectRatio: false,
            animation: {
                duration: 10,
            }
        }
    });

    // Updates values from the server (using the api) on a sett interval
    setInterval(function() {
        receiveJSON("/api/resources", function(data) {
            cpuElement.innerHTML = "CPU Usage: " + data.cpu + "%"; 
            cpuTempElement.innerHTML = "CPU Temp: " + data.temp + "C";
            memoryElement.innerHTML = "Memory Usage: " + data.ram + "%";
            networkUploadElement.innerHTML = "Network Upload: " + data.net.upload + "Mb/s";
            networkDownloadElement.innerHTML = "Network Download: " + data.net.download + "Mb/s";
            batteryElement.innerHTML = "Battery: " + data.battery + "%";

            if(chart.data.datasets[0].data.length < 10) {
                chart.data.datasets[0].data.push(parseInt(data.cpu))
                chart.data.datasets[1].data.push(parseInt(data.ram))

            } else {

                for(let i = 1; i < 10; i++) {
                    chart.data.datasets[0].data[i - 1] = chart.data.datasets[0].data[i];
                    chart.data.datasets[1].data[i - 1] = chart.data.datasets[1].data[i];

                }
                chart.data.datasets[0].data[9] = parseInt(data.cpu);
                chart.data.datasets[1].data[9] = parseInt(data.ram)
            }
            chart.update(); 

        });
    }, intervalTime);
}
