const sections = document.querySelectorAll('.section');
const categories = document.querySelectorAll('.category');

const firsSection = document.querySelector('.section');
firsSection.classList.add('active');

const posts = document.querySelectorAll('.post');
let selectedCategory = 'all';
let sectionId = 'all'

sections.forEach(section => {
    section.addEventListener('click', function(){
        
        selectedCategory = 'all';

        sections.forEach(sect => {
            sect.classList.remove('active');
        });
        categories.forEach(cat=> {
            cat.classList.remove('active');
        })
        section.classList.add('active')
        sectionId = section.getAttribute('data-section-id'); 
        categories.forEach(category => {  
            const categorySectionId = category.getAttribute('data-section-id'); 
            if (categorySectionId === sectionId) {
                category.classList.remove('hidden');
            } else if (sectionId==='all'){
                category.classList.remove('hidden');
            }
            else {
                category.classList.add('hidden');
            }
        });
        filterPosts()
    })
});

categories.forEach(category=> {
    category.addEventListener('click', function(){
        categories.forEach(cat=> {
            cat.classList.remove('active');
        })
        this.classList.add('active');
        selectedCategory = category.getAttribute('data-category-id');
        filterPosts()
    })
})

function filterPosts(){
    posts.forEach(post=>{
        const postSectionId = post.getAttribute('data-section-id');
        const postCategoryId = post.getAttribute('data-category-id');
        if((postSectionId===sectionId||sectionId === 'all')&&(selectedCategory==='all'||postCategoryId===selectedCategory)){
            post.classList.remove('hidden');
        } 
        else {
            post.classList.add('hidden');
        }
    })
}

