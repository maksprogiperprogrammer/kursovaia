const regBtn = document.getElementById('reg-btn')
const logBtn = document.getElementById('log-btn')
const regForm = document.getElementById('reg-form')
const logForm = document.getElementById('log-form')

regBtn.addEventListener('click', function(){
    regBtn.classList.add('hidden')
    logBtn.classList.remove('hidden')
    logForm.classList.add('hidden')
    regForm.classList.remove('hidden')
})

logBtn.addEventListener('click', function(){
    regBtn.classList.remove('hidden')
    logBtn.classList.add('hidden')
    logForm.classList.remove('hidden')
    regForm.classList.add('hidden')
})

regForm.addEventListener('submit', function(event){
    event.preventDefault();
    const newData = new FormData(this);

    fetch('/reg', {
        method: 'POST',
        body: newData
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            document.getElementById('reg-message').textContent = data.message;
            setTimeout(function() {
                window.location.href = 'profile'; 
            }, 500); 
        } else {
            document.getElementById('reg-message').textContent = data.message;
        }
    })
    .catch(error => console.error('Ошибка:',error));
})

logForm.addEventListener('submit', function(event){
    event.preventDefault();
    const newData = new FormData(this);

    fetch('/log', {
        method: 'POST',
        body: newData
    })
    .then(response => response.json())
    .then(data => {
        if (data.answer) {
            document.getElementById('log-message').textContent = data.message;
            setTimeout(function() {
                window.location.href = 'profile'; 
            }, 500); 
        } else {
            document.getElementById('log-message').textContent = data.message;
        }
    })
    .catch(error => console.error('Ошибка:',error));
})