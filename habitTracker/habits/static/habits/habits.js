document.addEventListener("DOMContentLoaded", function(){
    var addViewerBtn = document.querySelector('#add-viewer-btn');

    if(addViewerBtn !== null ) {
        addViewerBtn.addEventListener('click', addViewer, false);
    }

});

function addViewer() {
    var habitId = this.dataset.habit;
    var usernameInput = document.querySelector('#username-in');
    var messageDiv = document.querySelector('#message')

    fetch('/sendRequest', {
        method: "POST",
        body: JSON.stringify({
            to: usernameInput.value,
            habit: habitId
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if(result.success === false) {
            messageDiv.classList = "alert alert-danger";
        } else {
            messageDiv.classList = "alert alert-success";
        }

        messageDiv.innerText = result.message;
    });
}