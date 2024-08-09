let selectedImages = new Set();
let currentEnlargedImage = '';

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
            
            const enlargeIcon = document.createElement('i');
            enlargeIcon.className = 'fas fa-search-plus enlarge-icon';
            enlargeIcon.addEventListener('click', (e) => {
                e.stopPropagation();
                enlargeImage(item.path);
            });
            
            imgContainer.appendChild(imgElement);
            imgContainer.appendChild(enlargeIcon);
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

function enlargeImage(imagePath) {
    const modal = document.getElementById('imageModal');
    const enlargedImg = document.getElementById('enlargedImage');
    enlargedImg.src = `/static/images/${imagePath}`;
    currentEnlargedImage = imagePath;
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
}

function downloadEnlarged() {
    if (currentEnlargedImage) {
        const link = document.createElement('a');
        link.href = `/static/images/${currentEnlargedImage}`;
        link.download = currentEnlargedImage;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            search();
        }
    });

    // Close modal when clicking outside the image
    window.onclick = function(event) {
        const modal = document.getElementById('imageModal');
        if (event.target == modal) {
            closeModal();
        }
    }
});

function lazyLoadImages() {
    const images = document.querySelectorAll('.img-container img');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => {
        img.dataset.src = img.src;
        img.src = '';  // Clear the src to prevent immediate loading
        observer.observe(img);
    });
}

// Call this function after populating your results
lazyLoadImages();