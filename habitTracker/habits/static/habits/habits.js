document.addEventListener("DOMContentLoaded", function(){
    var addViewerBtn = document.querySelector('#add-viewer-btn');
    if(addViewerBtn !== null ) {
        addViewerBtn.addEventListener('click', addViewer, false);
    }

    var requestIcon = document.querySelector('#request-icon');
    if(requestIcon !== null) {
        requestIcon.addEventListener('click', setUpRequestIcon, false);
    }

    var radios = document.getElementsByName('dataQuery');
    if(radios !== null) { 
        for(var i = 0; i < radios.length; i++) {
            radios[i].addEventListener('click', function() {
                var dateSel = this.value,
                monthForm = document.querySelector('#monthYearEntries'),
                dateForm = document.querySelector('#dayEntries'),
                rangeBox = document.querySelector('#rangeBox');

                if(dateSel === "year" || dateSel === "month") {
                    monthForm.style.display = 'block';
                    dateForm.style.display = 'none';
                    rangeBox.style.display = 'inline';
                } else if (dateSel === "day") {
                    dateForm.style.display = 'block';
                    monthForm.style.display = 'none';
                    rangeBox.style.display = 'inline';
                } else {
                    dateForm.style.display = 'none';
                    monthForm.style.display = 'none';
                    rangeBox.style.display = 'none';
                }
            });
        }
    }

    var rangeType = document.querySelector('#rangeType');
    if(rangeType !== null) {
        rangeType.addEventListener('click', function() {
            var ends = document.getElementsByClassName('end');
            if(this.value === "single") {
                console.log(this.value);
                for(var i = 0; i < ends.length; i++){
                    ends[i].style.display = 'none';
                }
            } else {
                console.log(this.value);
                for(var i = 0; i < ends.length; i++){
                    ends[i].style.display = 'inline';
                }
            }
        });
    }

    var chart = document.getElementById('myChart'),
    config = {
        type: 'line',
        data: {
            datasets:   [
                {
                    label: "Value", 
                    data: [],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 0.2)'
                    ],
                    borderWidth: 1
                }
            ]
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    }

    getWeekData(chart, config);
    loadRequestCount();
});

// helper functions

function addViewer() {
    var habitId = this.dataset.habit;
    var usernameInput = document.querySelector('#username-in');
    var messageDiv = document.querySelector('#message');

    fetch('/sendRequest', {
        method: "POST",
        body: JSON.stringify({
            to: usernameInput.value,
            habit: habitId
        })
    })
    .then(response => response.json())
    .then(result => {
        if(result.success === false) {
            messageDiv.classList = "alert alert-danger";
        } else {
            messageDiv.classList = "alert alert-success";
        }

        messageDiv.innerText = result.message;
    });
}

function updateBadgeCount(count) {
    var requestIconBadge = document.querySelector('#requests-count');
    count = count > 0 ? count : 0;
    requestIconBadge.dataset.count = count;
    if(count === 0) {
        setRequestIconEmpty()
    } else {
        requestIconBadge.innerText = count;   
    }
}

function setRequestIconEmpty() {
    var requestDropDown = document.querySelector('#request-dropdown'),
    a = document.createElement('a'),
    requestIconBadge = document.querySelector('#requests-count');
    
    requestDropDown.innerHTML = "";

    a.classList = "dropdown-item";
    a.href = "#";
    a.innerText = "No Requests";

    requestDropDown.append(a);
    requestIconBadge.innerText = ""; 
}

function loaderDropDown() {
    var requestDropDown = document.querySelector('#request-dropdown'),
    loaderDiv = document.createElement('div');
    container = document.createElement('div');

    loaderDiv.classList = "loader dropdown-item";
    container.classList = "container";

    container.append(loaderDiv);
    requestDropDown.innerHTML = "";
    requestDropDown.append(container);
}

function getViewRequests(requestDropDown) {
    fetch('/getViewRequests', {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        if(result.length > 0) {
            requestDropDown.innerHTML = "";
            for (let index = 0; index < result.length; index++) {
                const viewRequest = result[index],
                div = document.createElement('div'),
                sentence =  document.createElement('p'),
                acceptBtn = document.createElement('button'),
                rejectBtn = document.createElement('button');
    
                acceptBtn.classList = "btn btn-login btn-sm mr-1";
                rejectBtn.classList = "btn btn-secondary btn-sm";
                acceptBtn.innerText = "Accept";
                rejectBtn.innerText = "Reject";
                acceptBtn.dataset.id = viewRequest.id;
                rejectBtn.dataset.id = viewRequest.id;
    
                acceptBtn.addEventListener('click', sendRequestReply, false);
                rejectBtn.addEventListener('click', sendRequestReply, false);
    
                div.classList = "dropdown-item hidable";
                sentence.innerText = `${viewRequest.sender} wants you to view their ${viewRequest.habit} habit`;
    
                div.append(sentence);
                div.append(acceptBtn);
                div.append(rejectBtn);
                requestDropDown.append(div);    
            }
        } else {
            setRequestIconEmpty();
        }
    });
}

function sendRequestReply() {
    var messageDiv = document.querySelector('#message');
    fetch('/replyRequest', {
        method: "POST",
        body: JSON.stringify({
            requestId: this.dataset.id,
            reply: this.innerText
        })
    })
    .then(response => response.json())
    .then(result => {
        if(result.success === false) {
            messageDiv.classList = "alert alert-danger";
        } else {
            messageDiv.classList = "alert alert-success";
        }

        messageDiv.innerText = result.message;
    })

    this.parentNode.style.animationPlayState = 'running';
    var requestIconBadge = document.querySelector('#requests-count');
    updateBadgeCount(requestIconBadge.dataset.count - 1);
}

function setUpRequestIcon() {
    var requestDropDown = document.querySelector('#request-dropdown');
    if(this.dataset.closed === "true") {
        requestDropDown.classList.add('show');
        
        loaderDropDown();

        getViewRequests(requestDropDown);

        this.dataset.closed = "false"
    } else {
        requestDropDown.classList.remove('show');
        this.dataset.closed = "true"
    }
}

function loadRequestCount() {
    fetch('/getRequestsCount', {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        var requestIconBadge = document.querySelector('#requests-count');
        updateBadgeCount(result.count);
    });
}

function getWeekData(chart, config) {
    if(chart !== null) {
        habitId = chart.dataset.id

        fetch('/getHabitData', {
            method: "POST",
            body: JSON.stringify({
                id: habitId, 
                getBy: "thisWeek"
            })
        })
        .then(response => response.json())
        .then(result => {
            var data = config.data.datasets[0].data,
            length = result.data.length;

            if(length > 0) {
                data.push({
                    t: moment(result.data[length-1].date),
                    y: parseFloat(result.data[length-1].content)
                });
                for(var i = length - 2, j = 0; i >= 0; i--) {
                    var date = moment(result.data[i].date);
                    if(data[j].t.day() !== date.day()) {
                        data.push({
                            t: date,
                            y: parseFloat(result.data[i].content)
                        });
                        j += 1;
                    } else {
                        var content = parseFloat(result.data[i].content); 
                        data[j].y = content > data[j].y ? content : data[j].y;
                    }
                }
            }

            // console.log(data.length);
            console.log(config);

            var ctx = chart.getContext('2d');
            chart.style.display = "block";
            var myChart = new Chart(ctx, config);
        });
    }
}