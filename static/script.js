let selectedImages = new Set();

function search() {
    const query = document.getElementById('search-input').value;
    const resultsContainer = document.getElementById('results');
    const loader = document.getElementById('loader');
    const downloadBtn = document.getElementById('download-btn');

    resultsContainer.innerHTML = '';
    loader.classList.remove('hidden');
    downloadBtn.classList.add('hidden');
    selectedImages.clear();

    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${encodeURIComponent(query)}`
    })
    .then(response => response.json())
    .then(data => {
        loader.classList.add('hidden');
        resultsContainer.innerHTML = '';
        data.forEach(item => {
            const imgContainer = document.createElement('div');
            imgContainer.className = 'img-container';
            
            const imgElement = document.createElement('img');
            imgElement.src = `/static/images/${item.path}`;
            imgElement.alt = `Similarity: ${item.score.toFixed(2)}`;
            imgElement.title = `Similarity: ${item.score.toFixed(2)}`;
            imgElement.addEventListener('click', () => toggleImageSelection(item.path, imgContainer));
            
            imgContainer.appendChild(imgElement);
            resultsContainer.appendChild(imgContainer);
        });
        updateDownloadButton();
    })
    .catch(error => {
        console.error('Error:', error);
        loader.classList.add('hidden');
        resultsContainer.innerHTML = 'An error occurred while searching.';
    });
}

function toggleImageSelection(imagePath, imgContainer) {
    if (selectedImages.has(imagePath)) {
        selectedImages.delete(imagePath);
        imgContainer.classList.remove('selected');
    } else {
        selectedImages.add(imagePath);
        imgContainer.classList.add('selected');
    }
    updateDownloadButton();
}

function updateDownloadButton() {
    const downloadBtn = document.getElementById('download-btn');
    if (selectedImages.size > 0) {
        downloadBtn.classList.remove('hidden');
    } else {
        downloadBtn.classList.add('hidden');
    }
}

function downloadSelected() {
    if (selectedImages.size > 0) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/download';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'images';
        input.value = JSON.stringify(Array.from(selectedImages));
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            search();
        }
    });
});