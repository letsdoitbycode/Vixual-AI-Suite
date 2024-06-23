const imageUpload = document.getElementById('image-upload');
const imagePreview = document.getElementById('image-preview'); // We will use this to display the image name
const descriptionBox = document.getElementById('description-box');
const generateBtn = document.getElementById('generate-btn');

imageUpload.addEventListener('change', () => {
    const file = imageUpload.files[0];
    if (file) {
        // Display the name of the uploaded file
        imagePreview.innerText = 'Selected file: ' + file.name;
    } else {
        imagePreview.innerText = '';
    }
});

generateBtn.addEventListener('click', generateDescription);

async function generateDescription() {
    const fileInput = document.getElementById('image-upload');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select an image file.');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
        descriptionBox.innerText = 'Generating description...'; // Display "Generating description..."
        const response = await fetch('/generate_description', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        descriptionBox.innerText = data.description; // Replace with actual description
    } catch (error) {
        console.error('Error generating description:', error);
    }
}
