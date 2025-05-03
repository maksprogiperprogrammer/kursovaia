const postSection = document.getElementById('post-section');
const postCategory = document.getElementById('post-category')
const categories = document.querySelectorAll('.category');

postSection.addEventListener('change', function(){
    let choosenSection = postSection.value;
    console.log(choosenSection);
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