const deleteComment = document.querySelectorAll('.delete-comment');

deleteComment.forEach(del => {
    del.addEventListener('click', function(){
        commentToDelete = del.getAttribute('data-comment-id');
        fetch(`delete_comment/${commentToDelete}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                document.getElementById(`comment-${commentToDelete}`).remove(); 
            } else {
                alert('Ошибка');
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }) 
});

const deletePost = document.querySelectorAll('.delete-post');

deletePost.forEach(del => {
    del.addEventListener('click', function(){
        postToDelete = del.getAttribute('data-post-id');
        fetch(`delete_post/${postToDelete}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                document.getElementById(`post-${postToDelete}`).remove(); 
            } else {
                alert('Ошибка');
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }) 
});