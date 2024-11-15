const { load } = require("mime");

function addToLocalStorage(key,data){
    localStorage.setItem(key) = data;
}

function retrieveFromLocalStorage(key){
    return localStorage.getItem(key)
}

function logout(){
    $.ajax({
        type: "POST",
        url: "/logout",
        success: function(data) {
            console.log(data)
            window.location.href = "login";
        }
    });
}

function history(e){
    const form = new FormData(e.target);
    date = form.get("date")
    console.log(date)
    $.ajax({
        type: "POST",
        url: "/ajaxhistory",
        data:{
            "date":date
        },
        success: function(response){
            console.log(response)
            resdata = JSON.parse(response)
            
            $("#date_legend").empty().append("Date: ")
            $("#date").empty().append(resdata.date)

            $("#calories_legend").empty().append("Calories: ")
            $("#calories").empty().append(resdata.calories)

            $("#burnout_legend").empty().append("Burnout: ")
            $("#burnout").empty().append(resdata.burnout)

            $("#history-data").empty().append(JSON.stringify(response));
        }
    })
}


function sendRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxsendrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function cancelRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxcancelrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function approveRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxapproverequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function dashboard(e, email){
    $.ajax({
        type: "POST",
        url: "/ajaxdashboard",
        data:{
            "email":email
        },
        success: function(response){
            console.log(response)
            resdata = JSON.parse(response)
            
            $("#enroll_legend").empty().append("ENrolled: ")
            $("#enroll").empty().append(resdata.enroll)
        }
    })
}

function removeFromFavorites(exerciseId) {
    // Get the CSRF token if applicable
    const csrfToken = document.querySelector('input[name="csrf_token"]')?.value;

    $.ajax({
        type: "POST",
        url: "/remove_favorite",
        contentType: "application/json", // Specify JSON content type
        data: JSON.stringify({ 
            "exercise_id": exerciseId,
            "csrf_token": csrfToken // Include if CSRF token is needed
        }),
        success: function(response) {
            if (response.status === 'success') { // Check for success in the response
                console.log("Favorite removed successfully");
                // Remove the card from the page
                const card = document.querySelector(`[data-exercise-id='${exerciseId}']`);
                if (card) {
                    card.remove(); // Remove the specific exercise card from the DOM
                }
            } else {
                alert("Failed to remove the favorite.");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error:", error);
            console.error("Status:", status);
            console.error("XHR:", xhr);
            alert("An error occurred while trying to remove the favorite.");
        }
    });
}
