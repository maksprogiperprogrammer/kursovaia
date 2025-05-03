const commentForm = document.getElementById('comment-form');

commentForm.addEventListener('submit', function(event){
    event.preventDefault()

    const newData = new FormData(this);
    fetch('/comment', {
        method: 'POST',
        body: newData
    })
    .then(response=>response.json())
    .then(data=>{
        if (data.answer){
            document.getElementById('comment-message').textContent = data.message;
            commentForm.reset();
        } else{
            document.getElementById('comment-message').textContent = data.message;
        }
        
    })
    .catch(error=>console.error('Ошибка:',error))
})