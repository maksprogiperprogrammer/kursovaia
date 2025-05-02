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