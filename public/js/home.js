document.addEventListener('DOMContentLoaded', async function () {
    const dayCounter = document.getElementById('days-count');
    const timelineList = document.getElementById('upcoming-timeline');

    try {
        const data = await window.api.get('/api/home');
        const startDate = data.startDate ? new Date(data.startDate) : new Date();
        const today = new Date();
        const diff = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
        dayCounter.textContent = diff.toLocaleString();

        timelineList.innerHTML = '';
        data.upcomingEvents.forEach(event => {
            const item = document.createElement('div');
            item.className = 'timeline-item';

            const title = document.createElement('h4');
            const eventDate = new Date(event.date + 'T00:00:00');
            title.textContent = eventDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });

            const description = document.createElement('p');
            description.textContent = event.label;

            item.append(title, description);
            timelineList.appendChild(item);
        });
    } catch (error) {
        console.error('Unable to load home data', error);
        dayCounter.textContent = '—';
        const fallback = document.createElement('p');
        fallback.textContent = 'We could not load the upcoming events right now.';
        fallback.style.color = 'var(--muted)';
        timelineList.appendChild(fallback);
    }
});
