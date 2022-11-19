const baseUrl = "http://localhost:8000/";

const likePost = (likeButton) => {
    postId = likeButton.data("post-id");
    url = baseUrl + "like-post/?post_id=" + postId;

    $.ajax({
        type: "GET",
        url: url,
        data: {post_id: postId},
        success: function(data) {
            if(data == 0) $("#id_like_" + postId).text("No likes")
            else if(data == 1) $("#id_like_" + postId).text("Liked by " + data + " person")
            else $("#id_like_" + postId).text("Liked by " + data + " people")
        }
    })
};

$(document).ready(function() {
    $(".like_unlike_posts").on("click", function(event) {
        event.preventDefault()
        likePost($(this))
    })
})