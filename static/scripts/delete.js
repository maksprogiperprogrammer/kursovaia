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