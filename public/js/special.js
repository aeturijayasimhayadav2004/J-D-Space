function updateCountdown(card, targetDate) {
    const now = new Date();
    const distance = targetDate - now;

    if (distance <= 0) {
        card.querySelector('span').textContent = 'Today!';
        return;
    }

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((distance / (1000 * 60)) % 60);
    const seconds = Math.floor((distance / 1000) % 60);
    card.querySelector('span').textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

document.addEventListener('DOMContentLoaded', async function () {
    const timeline = document.getElementById('special-timeline');
    const countdownGrid = document.getElementById('countdown-grid');

    try {
        const data = await window.api.get('/api/special');

        timeline.innerHTML = '';
        data.milestones.forEach(item => {
            const element = document.createElement('div');
            element.className = 'timeline-item';

            const title = document.createElement('h4');
            title.textContent = `${item.date} — ${item.title}`;

            const description = document.createElement('p');
            description.textContent = item.description;

            element.append(title, description);
            timeline.appendChild(element);
        });

        countdownGrid.innerHTML = '';
        data.countdowns.forEach(entry => {
            const card = document.createElement('div');
            card.className = 'countdown-card';
            card.id = entry.id;

            const heading = document.createElement('h3');
            heading.textContent = entry.title;

            const time = document.createElement('span');
            time.textContent = 'Calculating…';

            card.append(heading, time);
            countdownGrid.appendChild(card);

            const targetDate = new Date(entry.date);
            updateCountdown(card, targetDate);
            setInterval(() => updateCountdown(card, targetDate), 1000);
        });
    } catch (error) {
        console.error('Unable to load special days', error);
        timeline.innerHTML = '<p style="color: var(--muted);">Our memories are taking a nap right now.</p>';
        countdownGrid.innerHTML = '<p style="color: var(--muted);">Countdowns are snoozing too.</p>';
    }
});
