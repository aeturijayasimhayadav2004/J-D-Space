document.addEventListener('DOMContentLoaded', async function () {
    const blogContainer = document.getElementById('blog-container');
    blogContainer.innerHTML = '';

    try {
        const data = await window.api.get('/api/blog');
        if (!data.posts.length) {
            const empty = document.createElement('p');
            empty.textContent = 'No love letters posted yet — maybe tonight?';
            empty.style.color = 'var(--muted)';
            blogContainer.appendChild(empty);
            return;
        }

        data.posts.forEach(post => {
            const card = document.createElement('article');
            card.className = 'blog-card';

            const title = document.createElement('h3');
            title.textContent = post.title;

            const body = document.createElement('p');
            body.textContent = post.body;

            const meta = document.createElement('div');
            meta.className = 'meta';
            meta.textContent = `${post.date} • Written by ${post.author}`;

            card.append(title, body, meta);
            blogContainer.appendChild(card);
        });
    } catch (error) {
        console.error('Unable to load blog posts', error);
        const failure = document.createElement('p');
        failure.textContent = 'We could not fetch the blog posts right now.';
        failure.style.color = 'var(--muted)';
        blogContainer.appendChild(failure);
    }
});
