const postsEditButtons = document.querySelectorAll('.edit-post');

postsEditButtons.forEach(button => {
    button.addEventListener('click', function() {
        const postId = button.getAttribute('data-post-id');
        const postElement = document.getElementById(`post-${postId}`);

        if (postElement) {
            const theme = postElement.querySelector('.post-theme');
            const text = postElement.querySelector('.post-text');
            const date = postElement.querySelector('.post-created');
            date.classList.add('hidden');
            
            const originalTheme = theme.textContent;
            const originalText = text.dataset.text;
            
            const themeInput = document.createElement('input');
            themeInput.type = 'text';
            themeInput.value = originalTheme;
            themeInput.classList.add('edit-theme-input'); 
            const textTextarea = document.createElement('textarea');
            textTextarea.value = originalText;
            textTextarea.rows = 5;
            textTextarea.classList.add('edit-text-textarea'); 
            
            theme.replaceWith(themeInput);
            text.replaceWith(textTextarea);
            
            const saveButton = document.createElement('button');
            saveButton.textContent = 'Сохранить';
            saveButton.classList.add('save-button');
            const cancelButton = document.createElement('button');
            cancelButton.textContent = 'Отмена';
            cancelButton.classList.add('cancel-button'); 
            postElement.appendChild(saveButton);
            postElement.appendChild(cancelButton);
            
            saveButton.addEventListener('click', function() {
                const newTheme = themeInput.value;
                const newText = textTextarea.value;
                fetch(`/edit_post/${postId}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ theme: newTheme, text: newText })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.answer) {
                        date.classList.remove('hidden');
                        theme.textContent = newTheme;
                        text.textContent = newText;
                        theme.textContent = newTheme;
                        text.dataset.text = newText;

                        themeInput.replaceWith(theme);
                        textTextarea.replaceWith(text);
                        saveButton.remove();
                        cancelButton.remove();
                    } else {
                        alert(data.message);
                    }
                })
            });
            
            cancelButton.addEventListener('click', function() {
                date.classList.remove('hidden');
                theme.textContent = originalTheme;
                text.textContent = originalText;
                themeInput.replaceWith(theme);
                textTextarea.replaceWith(text);
                saveButton.remove();
                cancelButton.remove();
            });
        }
    });
});