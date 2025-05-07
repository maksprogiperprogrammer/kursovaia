const profilePhoto = document.getElementById('photo-input');

profilePhoto.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const form = document.querySelector('.profile-person-img')
        const formData = new FormData(form);
        fetch('/set_photo', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при загрузке фотографии');
            }
            return response.json();
        })
        .then(data => {
            console.log('Фото успешно загружено:', data);
            const imagePreview = document.querySelector('.profile-person-img img');
            if (imagePreview) {
                imagePreview.src = URL.createObjectURL(file);
            }
        })
        .catch(error => {console.error('Ошибка:', error)});
    }
});