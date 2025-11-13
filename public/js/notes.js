function renderNotes(board, notes) {
    board.innerHTML = '';

    if (!notes.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No notes yet. Leave some love!';
        empty.style.color = 'var(--muted)';
        board.appendChild(empty);
        return;
    }

    notes.forEach(note => {
        const card = document.createElement('div');
        card.className = 'note-card';
        card.innerHTML = `<p>${note.message}</p><small>— ${note.author} • ${note.date}</small>`;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-secondary';
        deleteBtn.textContent = 'Delete';
        deleteBtn.style.marginTop = '1rem';
        deleteBtn.style.padding = '0.4rem 0.85rem';
        deleteBtn.addEventListener('click', async function () {
            try {
                await window.api.del(`/api/notes/${note.id}`);
                loadNotes(board);
            } catch (error) {
                console.error('Unable to delete note', error);
            }
        });

        card.appendChild(deleteBtn);
        board.appendChild(card);
    });
}

async function loadNotes(board) {
    try {
        const data = await window.api.get('/api/notes');
        renderNotes(board, data.notes);
    } catch (error) {
        console.error('Unable to load notes', error);
        board.innerHTML = '<p style="color: var(--muted);">We could not load notes right now.</p>';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('note-form');
    const board = document.getElementById('notes-board');

    loadNotes(board);

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const message = form.message.value.trim();
        const author = form.author.value.trim() || 'Someone in love';

        if (!message) {
            return;
        }

        try {
            await window.api.post('/api/notes', { message, author });
            form.reset();
            loadNotes(board);
        } catch (error) {
            console.error('Unable to save note', error);
        }
    });
});
