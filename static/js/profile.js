const baseUrl = "http://localhost:8000/";

const followUser = () => {
    url = baseUrl + "follow/"

    $("#id_follow_form").on("submit", function(event) {
        event.preventDefault()
        $.ajax({
            type: "POST",
            url: url,
            data: $(this).serialize(),
            success: function(data) {
                userFollowers = data["userFollowers"]
                $("#id_follow_button").text(data["buttonText"])
                if (userFollowers == 0 || userFollowers == 1)
                    $("#id_user_follower_count").text(userFollowers + " follower")
                else
                    $("#id_user_follower_count").text(userFollowers + " followers")
            }
        })
    })
};

$(document).ready(function() {
    followUser()
})