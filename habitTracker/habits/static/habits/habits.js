document.addEventListener("DOMContentLoaded", function(){
    var addViewerBtn = document.querySelector('#add-viewer-btn');
    if(addViewerBtn !== null ) {
        addViewerBtn.addEventListener('click', addViewer, false);
    }

    var requestIcon = document.querySelector('#request-icon');
    if(requestIcon !== null) {
        requestIcon.addEventListener('click', function() {
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
        }, false);
    }


    fetch('/getRequestsCount', {
        method: "GET"
    })
    .then(response => response.json())
    .then(result => {
        var requestIconBadge = document.querySelector('#requests-count');
        console.log(result.count)
        updateBadgeCount(result.count);
    });
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
    console.log(count)
    requestIconBadge.dataset.count = count;
    if(count === 0) {
        console.log(count)
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
    console.log("finished")
}

function loaderDropDown() {
    console.log("loader")
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