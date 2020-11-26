window.onload = startup
var intervalTime = 1000; //Ms 
var cpuElement, cpuTempElement,memoryElement, networkUploadElement, networkDownloadElement; 
var chart1; 

function formToJson(form) {
    var json = "{"
    
    for (i = 0; i < form.length; i++) {
        key = form[i].attributes.name.nodeValue
        val = form[i].valueAsNumber
        
        json += '"'+key + '":"' + val + '"';
        json += i != form.length - 1 ? "," : "}"; 
    }

    return JSON.stringify(JSON.parse(json));
}

function jsonToForm(json, form) {
    let obj = JSON.parse(JSON.stringify(json));
    
    console.log(obj);
    for (const [key, value] of Object.entries(obj)) {
        form.elements.namedItem(key).value = value;
        form.elements.namedItem(key + "typed") = value;

        console.log("Change " + key + " to " + val);
    }
}

function updateSlider(formSlider) {
    receiveJSON("/api/config", data => {
        console.log(data)
        json = JSON.parse(data)
    })
}

function receiveJSON(url, onReceived) {
    var xhr = new XMLHttpRequest();
    var json = undefined;

    xhr.open("GET", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.status == 200 && xhr.readyState == 4 && xhr.responseText != "") {
            json = JSON.parse(xhr.responseText);
            onReceived(json);
        }
    }
    xhr.send();
}


function sendJson(json, url) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.send(json);
}

function startup() {
    console.log("Start up")
    cpuElement = document.getElementById("cpu"); 
    cpuTempElement = document.getElementById("cpuTemp");
    memoryElement = document.getElementById("mem");
    networkUploadElement = document.getElementById("networkUpload");
    networkDownloadElement = document.getElementById("networkDownload"); 
    chart1 = document.getElementById("chart1"); 

    form = document.getElementsByTagName("form")[0];

    receiveJSON("/api/config", data => {
        jsonToForm(data, form);
    });

    form.onchange = function() {
        console.log("Form change");
        sendJson(formToJson(form), "/api/config");
    }


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
    setInterval(function() {
        receiveJSON("/api/resources", function(data) {
            cpuElement.innerHTML = "CPU Usage: " + data.cpu + "%"; 
            cpuTempElement.innerHTML = "CPU Temp: " + data.temp + "C";
            memoryElement.innerHTML = "Memory Usage: " + data.ram + "%";
            networkUploadElement.innerHTML = "Network Upload: " + data.net.upload + "Mb/s";
            networkDownloadElement.innerHTML = "Network Download: " + data.net.download + "Mb/s";

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