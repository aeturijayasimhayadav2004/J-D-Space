document.addEventListener('DOMContentLoaded', async function () {
    try {
        const data = await window.api.get('/api/fun');
        setupWheel(data.wheelIdeas || []);
        setupQuiz(data.quizQuestions || []);
        setupPoll(data.pollOptions || []);
    } catch (error) {
        console.error('Unable to load fun zone data', error);
    }
});

function setupWheel(ideas) {
    const wheel = document.getElementById('date-wheel');
    const spinBtn = document.getElementById('spin-btn');
    const result = document.getElementById('wheel-result');

    if (!wheel || !spinBtn) {
        return;
    }

    spinBtn.addEventListener('click', function () {
        if (!ideas.length) {
            result.textContent = 'No ideas right now. Add some in the database!';
            return;
        }

        const idea = ideas[Math.floor(Math.random() * ideas.length)];
        const rotation = 720 + Math.floor(Math.random() * 360);
        wheel.style.transform = `rotate(${rotation}deg)`;
        setTimeout(() => {
            result.textContent = idea.idea || idea;
        }, 1200);
    });
}

function setupQuiz(questions) {
    const quizContainer = document.getElementById('quiz-container');
    if (!quizContainer) {
        return;
    }

    quizContainer.innerHTML = '';
    const form = document.createElement('form');
    form.id = 'quiz-form';

    questions.forEach((item, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'quiz-question card';

        const question = document.createElement('h4');
        question.textContent = `${index + 1}. ${item.question}`;

        const options = document.createElement('div');
        options.className = 'quiz-options';

        item.options.forEach(option => {
            const label = document.createElement('label');
            const input = document.createElement('input');
            input.type = 'radio';
            input.name = `question-${item.id}`;
            input.value = option.id;
            label.appendChild(input);
            label.append(` ${option.label}`);
            options.appendChild(label);
        });

        wrapper.append(question, options);
        form.appendChild(wrapper);
    });

    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'btn';
    submitBtn.textContent = 'Check our answers';
    form.appendChild(submitBtn);

    const feedback = document.createElement('p');
    feedback.id = 'quiz-feedback';
    feedback.style.marginTop = '1rem';
    form.appendChild(feedback);

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        let score = 0;
        questions.forEach(item => {
            const answer = form.querySelector(`input[name="question-${item.id}"]:checked`);
            if (answer && parseInt(answer.value, 10) === item.answerId) {
                score += 1;
            }
        });

        feedback.textContent = `We got ${score} / ${questions.length} correct!`;
    });

    quizContainer.appendChild(form);
}

function setupPoll(initialOptions) {
    const pollContainer = document.getElementById('poll-container');
    if (!pollContainer) {
        return;
    }

    let options = initialOptions;

    function renderPoll() {
        pollContainer.innerHTML = '';
        const totalVotes = options.reduce((sum, option) => sum + option.votes, 0) || 1;

        options.forEach(option => {
            const optionEl = document.createElement('div');
            optionEl.className = 'poll-option';
            optionEl.dataset.id = option.id;

            const label = document.createElement('span');
            label.textContent = option.label;

            const bar = document.createElement('div');
            bar.className = 'poll-bar';

            const fill = document.createElement('div');
            fill.className = 'poll-bar-fill';
            fill.style.width = `${Math.round((option.votes / totalVotes) * 100)}%`;
            bar.appendChild(fill);

            const count = document.createElement('span');
            count.className = 'poll-count';
            count.textContent = `${option.votes} votes`;

            optionEl.append(label, bar, count);
            pollContainer.appendChild(optionEl);
        });
    }

    pollContainer.addEventListener('click', async function (event) {
        const optionEl = event.target.closest('.poll-option');
        if (!optionEl) return;

        try {
            const result = await window.api.post('/api/poll/vote', { optionId: parseInt(optionEl.dataset.id, 10) });
            options = result.options;
            renderPoll();
        } catch (error) {
            console.error('Unable to record vote', error);
        }
    });

    renderPoll();
}
