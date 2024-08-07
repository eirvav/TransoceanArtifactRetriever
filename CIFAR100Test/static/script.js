let selectedImages = new Set();

function search() {
    const query = document.getElementById('search-input').value;
    const statusDiv = document.getElementById('status');
    const resultsContainer = document.getElementById('results');
    const downloadBtn = document.getElementById('download-btn');

    statusDiv.innerHTML = 'Searching...';
    resultsContainer.innerHTML = '';
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
        checkStatus(data.task_id);
    })
    .catch(error => {
        console.error('Error:', error);
        statusDiv.innerHTML = 'An error occurred while searching.';
    });
}

function checkStatus(taskId) {
    const statusDiv = document.getElementById('status');
    const resultsContainer = document.getElementById('results');

    fetch(`/status/${taskId}`)
    .then(response => response.json())
    .then(data => {
        if (data.state === 'PENDING') {
            statusDiv.innerHTML = 'Processing...';
            setTimeout(() => checkStatus(taskId), 1000);
        } else if (data.state === 'SUCCESS') {
            statusDiv.innerHTML = '';
            displayResults(data.result);
        } else {
            statusDiv.innerHTML = `Error: ${data.status}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        statusDiv.innerHTML = 'An error occurred while checking status.';
    });
}

function displayResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';
    results.forEach(item => {
        const imgContainer = document.createElement('div');
        imgContainer.className = 'img-container';
        
        const imgElement = document.createElement('img');
        imgElement.src = `/image/${item.path}`;
        imgElement.alt = `Similarity: ${item.score.toFixed(2)}`;
        imgElement.title = `Similarity: ${item.score.toFixed(2)}`;
        imgElement.addEventListener('click', () => toggleImageSelection(item.path, imgContainer));
        
        imgContainer.appendChild(imgElement);
        resultsContainer.appendChild(imgContainer);
    });
    document.getElementById('download-btn').classList.remove('hidden');
}

function toggleImageSelection(imagePath, imgContainer) {
    if (selectedImages.has(imagePath)) {
        selectedImages.delete(imagePath);
        imgContainer.classList.remove('selected');
    } else {
        selectedImages.add(imagePath);
        imgContainer.classList.add('selected');
    }
}

function downloadSelected() {
    if (selectedImages.size > 0) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/download';
        
        selectedImages.forEach(imagePath => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'images[]';
            input.value = imagePath;
            form.appendChild(input);
        });
        
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