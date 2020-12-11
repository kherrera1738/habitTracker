var app = {};

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
            radios[i].addEventListener('click', setupRadio, false);
        }
    }

    var rangeType = document.querySelector('#rangeType');
    if(rangeType !== null) {
        rangeType.addEventListener('click', setupTypeBox, false);
    }

    var queryButton = document.getElementById('query-btn');
    if(queryButton !== null) {
        queryButton.addEventListener('click', query, false);
    }

    var chart = document.getElementById('myChart');
    app.config = {
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
    };

    getWeekData(chart, app.config);
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
            maxPerDayData(result.data, config.data.datasets[0].data);
            console.log(config);

            var ctx = chart.getContext('2d');
            chart.style.display = "block";
            app.chartObj = new Chart(ctx, config);
        });
    }
}

function setupRadio() {
    var dateSel = this.value,
    monthForm = document.querySelector('#monthYearEntries'),
    dateForm = document.querySelector('#dayEntries'),
    rangeBox = document.querySelector('#rangeBox');

    monthForm.style.display = dateSel === "year" || dateSel === "month" ? 'block' : 'none';
    dateForm.style.display = dateSel === "day" ?  'block' : 'none';
    rangeBox.style.display = monthForm.style.display === 'block' || dateForm.style.display === 'block' ? 'inline' : 'none';
}

function setupTypeBox() {
    var ends = document.getElementsByClassName('end'),
    displayType = this.value === "single" ? 'none' : 'inline'; 
    for(var i = 0; i < ends.length; i++){
        ends[i].style.display = displayType;
    }
}

function maxPerDayData(inputArray, outputArray) {
    var length = inputArray.length;

    if(length > 0) {
        outputArray.push({
            t: moment(inputArray[length-1].date),
            y: parseFloat(inputArray[length-1].content)
        });
        for(var i = length - 2, j = 0; i >= 0; i--) {
            var curr_entry = inputArray[i],
            date = moment(curr_entry.date);
            if(outputArray[j].t.day() !== date.day()) {
                outputArray.push({
                    t: date,
                    y: parseFloat(curr_entry.content)
                });
                j += 1;
            } else {
                var content = parseFloat(curr_entry.content); 
                outputArray[j].y = content > outputArray[j].y ? content : outputArray[j].y;
            }
        }
    }
}

function query() {
    var queryMessage = document.querySelector('#queryMessage'),
    body = { 
        id: habitId
    };
    queryMessage.style.display = 'none';

    if(makeQueryBody(body)) {
        makeQuery(body);
    } else {
        queryMessage.style.display = 'inline';
        queryMessage.innerText = 'Something went wrong. Make sure end is not before start and dates are filled';
    }
}

function makeQueryBody(body) {
    var valid = true;
    body.getBy = getRadioBtnValue();

    if(body.getBy !== 'thisWeek') {
        valid = addInput(body);
        fixMonthYearDay(body);
    }

    return valid;
}

function getRadioBtnValue() {
    var radioBtns = document.getElementsByName('dataQuery');
    for(var i = 0; i < radioBtns.length; i++) {
        if(radioBtns[i].checked) {
            return radioBtns[i].value;
        }
    }
}

function fixMonthYearDay(body) {
    if(body.getBy === 'month' || body.getBy === 'year') {
        body.start = body.start + '-01';
        if(body.hasOwnProperty('end')) {
            body.end = body.end + '-01';
        }
    }
}

function addEndInput(body, formGroup) {
    formInputs = formGroup.querySelector('.end'),
    endInput = formInputs.querySelector('input');

    if(endInput.value === '') {
        return false;
    } else {
        body.end = endInput.value;
    }

    if(body.end < body.start) {
        return false;
    }
    return true;
}

function addInput(body) {
    var group = body.getBy === 'day' ? 'dayEntries' : 'monthYearEntries',
    rangeBox = document.getElementById('rangeType'),
    formGroup = document.getElementById(group),
    formInputs = formGroup.querySelector('.start'),
    startInput = formInputs.querySelector('input');
    if(startInput.value === '') {
        return false;
    } else {
        body.range = rangeBox.value;
        body.start = startInput.value;

        if(body.range === 'range') {
            return addEndInput(body, formGroup);
        }
    }
    return true;
}

function makeQuery(body) {
    fetch('/getHabitData', {
        method: "POST",
        body: JSON.stringify(body)
    })
    .then(response => response.json())
    .then(result => {
        app.config.data.datasets[0].data = [];

        maxPerDayData(result.data, app.config.data.datasets[0].data);

        app.chartObj.update();
    });
}