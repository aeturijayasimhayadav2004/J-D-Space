document.addEventListener('DOMContentLoaded', function () {
    const lightbox = document.getElementById('lightbox');
    const lightboxContent = document.getElementById('lightbox-content');
    const closeBtn = document.getElementById('lightbox-close');

    document.querySelectorAll('[data-lightbox]').forEach(item => {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const type = this.dataset.type;
            const source = this.getAttribute('href');
            lightboxContent.innerHTML = '';

            if (type === 'video') {
                const video = document.createElement('video');
                video.controls = true;
                video.src = source;
                video.setAttribute('playsinline', '');
                lightboxContent.appendChild(video);
            } else {
                const img = document.createElement('img');
                img.src = source;
                img.alt = this.querySelector('img').alt;
                lightboxContent.appendChild(img);
            }

            lightbox.classList.add('active');
        });
    });

    closeBtn.addEventListener('click', () => {
        lightbox.classList.remove('active');
        lightboxContent.innerHTML = '';
    });

    lightbox.addEventListener('click', event => {
        if (event.target === lightbox) {
            lightbox.classList.remove('active');
            lightboxContent.innerHTML = '';
        }
    });
});
