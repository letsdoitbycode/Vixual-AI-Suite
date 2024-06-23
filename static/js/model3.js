const imageUpload = document.getElementById('image-upload');
const imagePreview = document.getElementById('image-preview');
const generateBtn = document.getElementById('generate-btn');
const answerResult = document.getElementById('answerResult');
const answerDiv = document.getElementById('answer');
const imageName = document.getElementById('image-name');

function displayImagePreview(file) {
    imagePreview.textContent = `Image: ${file.name}`;
    imagePreview.style.display = 'block';
}

imageUpload.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        displayImagePreview(file);
    } else {
        imagePreview.textContent = '';
    }
});

generateBtn.addEventListener('click', () => {
    const formData = new FormData();
    const file = imageUpload.files[0];
    const question = document.getElementById('question').value;

    if (!file || !question) {
        alert('Please upload an image and type a question.');
        return;
    }

    formData.append('image', file);
    formData.append('question', question);

    fetch('/generate_and_answer', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        answerDiv.textContent = data.answer;
        answerResult.style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
});
