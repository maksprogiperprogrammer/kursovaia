const postSection = document.getElementById('post-section');
const postCategory = document.getElementById('post-category')
const categories = document.querySelectorAll('.category');

postSection.addEventListener('change', function(){
    let choosenSection = postSection.value;
    let choosenCategory = postCategory.value;
    console.log(choosenSection);
    console.log(choosenCategory);
    postCategory.value = ""
    categories.forEach(category=>{
        let categorySectionId = category.getAttribute('data-section-id');
        if (categorySectionId===choosenSection){
            category.classList.remove('hidden');
        } else {
            category.classList.add('hidden');
        }
    })
})

const postForm = document.querySelector('.post-form') 
postForm.addEventListener('submit', function(event){
    event.preventDefault()
    const newData = new FormData(this)
    fetch('/create', {
        method: 'POST',
        body: newData
    })
    .then(response=>response.json())
    .then(data=>{
        if(data.answer){
            document.getElementById('create-message').textContent = data.message;
            postForm.reset()
        } else {
            document.getElementById('create-message').textContent = data.message;
        }
    })
})

const adminBtn = document.querySelector('.admin-button');
let isOpen = false;
adminBtn.addEventListener('click', function(){
    if (isOpen){
        isOpen=false;
        document.querySelector('.admin-div').style.maxHeight='0';
    } else {
        isOpen=true;
        document.querySelector('.admin-div').style.maxHeight='240px';
    }
})

const formCreateSection = document.getElementById('form-create-section');
const formCreateCategory = document.getElementById('form-create-category');

formCreateSection.addEventListener('submit', function(event){
    event.preventDefault()
    const newData = new FormData(this)
    fetch('/create-section', {
        method: 'POST',
        body: newData
    })
    .then(response=>response.json())
    .then(data=>{
        if(data.answer){
            document.querySelector('.admin-p').textContent = data.message;
            formCreateSection.reset()
        } else {
            document.querySelector('.admin-p').textContent = data.message;
        }
    })
})
formCreateCategory.addEventListener('submit', function(event){
    event.preventDefault()
    const newData = new FormData(this)
    fetch('/create-category', {
        method: 'POST',
        body: newData
    })
    .then(response=>response.json())
    .then(data=>{
        if(data.answer){
            document.querySelector('.admin-p').textContent = data.message;
            formCreateCategory.reset()
        } else {
            document.querySelector('.admin-p').textContent = data.message;
        }
    })
})