document.addEventListener('DOMContentLoaded', async function () {
    const plannerList = document.getElementById('date-planner');
    const bucketGrid = document.getElementById('bucket-grid');

    const statusClassMap = {
        'Planned': 'planned',
        'Completed': 'completed',
        'Want to Try': 'wish'
    };

    try {
        const data = await window.api.get('/api/dates');

        data.dateIdeas.forEach(idea => {
            const item = document.createElement('div');
            item.className = 'card';

            const title = document.createElement('h3');
            title.textContent = idea.title;

            const tag = document.createElement('span');
            tag.className = `tag ${statusClassMap[idea.status] || ''}`;
            tag.textContent = idea.status;

            item.append(title, tag);
            plannerList.appendChild(item);
        });

        bucketGrid.innerHTML = '';
        data.bucketItems.forEach(item => {
            const card = createBucketCard(item);
            bucketGrid.appendChild(card);
        });
    } catch (error) {
        console.error('Unable to load date planner data', error);
        plannerList.innerHTML = '<p style="color: var(--muted);">We could not load the planner right now.</p>';
        bucketGrid.innerHTML = '<p style="color: var(--muted);">Bucket list unavailable at the moment.</p>';
    }

    function createBucketCard(item) {
        const card = document.createElement('div');
        card.className = 'bucket-item';
        card.dataset.id = item.id;
        card.innerHTML = `<h4>${item.title}</h4><p>${item.completed ? 'Completed ✅' : 'Tap to mark complete'}</p>`;
        card.classList.toggle('completed', Boolean(item.completed));

        card.addEventListener('click', async function () {
            try {
                const updated = await window.api.post(`/api/bucket/${this.dataset.id}/toggle`);
                this.classList.toggle('completed', Boolean(updated.completed));
                this.querySelector('p').textContent = updated.completed ? 'Completed ✅' : 'Tap to mark complete';
            } catch (error) {
                console.error('Unable to update bucket item', error);
            }
        });

        return card;
    }
});
