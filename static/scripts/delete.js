const deleteComment = document.querySelectorAll('.delete-comment');

deleteComment.forEach(del => {
    del.addEventListener('click', function(){
        commentToDelete = del.getAttribute('data-comment-id');
        fetch(`/delete_comment/${commentToDelete}`, {
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
        fetch(`/delete_post/${postToDelete}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                document.getElementById(`post-${postToDelete}`).remove(); 
            } else {
                alert(data.answer);
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }) 
});

const banUser = document.querySelectorAll('.ban-button');

banUser.forEach(ban => {
    ban.addEventListener('click', function(){
        userToBan = ban.value;
        who = ban.getAttribute('data-user');
        let result = confirm(`Вы уверены что хотите удалить ${who}?`)
        if (result){
            fetch(`/ban_user/${userToBan}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (response.ok) {
                    user = document.querySelectorAll(`.user-${userToBan}`);
                    user.forEach(u=>{
                        u.textContent = 'забанен'
                    })
                } else {
                    alert('ошибка');
                }
            })
            .catch(error => console.error('Ошибка:', error));
        }
    }) 

});