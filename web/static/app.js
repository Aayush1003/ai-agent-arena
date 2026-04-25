/**
 * Agent Arena — Dashboard Controller
 * Handles SSE streaming, UI updates, and animations.
 */

let eventSource = null;
let eventCount = 0;
let memoryCount = 0;
let isRunning = false;

const AGENT_COLORS = {
    planner: '#a78bfa',
    researcher: '#60a5fa',
    coder: '#34d399',
    critic: '#f472b6',
};

const BADGE_ICONS = {
    planner: 'P',
    researcher: 'R',
    coder: 'C',
    critic: 'CR',
    turn: 'T',
    system: 'SYS',
    memory: 'DB',
    done: '✓',
};

// ===== GAME CONTROL =====

function startGame() {
    if (isRunning) return;
    isRunning = true;

    const mission = document.getElementById('missionInput').value.trim();
    if (!mission) return;

    // Reset UI
    resetUI();
    document.getElementById('startBtn').disabled = true;
    updateStat('statStatus', 'Running');

    // Start game on server
    fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mission }),
    })
    .then(res => res.json())
    .then(() => {
        // Connect to SSE stream
        connectSSE();
    })
    .catch(err => {
        console.error('Failed to start game:', err);
        isRunning = false;
        document.getElementById('startBtn').disabled = false;
    });
}

function connectSSE() {
    if (eventSource) eventSource.close();

    eventSource = new EventSource('/stream');
    eventSource.onmessage = (e) => {
        try {
            const event = JSON.parse(e.data);
            handleEvent(event);
        } catch (err) {
            console.error('SSE parse error:', err);
        }
    };
    eventSource.onerror = () => {
        eventSource.close();
        isRunning = false;
        document.getElementById('startBtn').disabled = false;
    };
}

// ===== EVENT HANDLER =====

function handleEvent(event) {
    const { type, data } = event;
    if (type === 'heartbeat') return;

    switch (type) {
        case 'game_start':
            addFeedItem('system', 'Mission Launched', `"${data.mission}"`, 'system');
            break;

        case 'turn_start':
            addFeedItem('turn', `Turn ${data.turn} / ${data.max_turns}`, 'Starting new agent cycle...', 'turn');
            updateStat('statTurn', `${data.turn} / ${data.max_turns}`);
            // Reset pipeline highlights
            resetPipeline();
            break;

        case 'agent_start':
            activatePipelineAgent(data.agent, data.color);
            activateAgentCard(data.agent);
            addFeedItem(data.agent, data.name, 'Initializing...', data.agent, true);
            break;

        case 'agent_action':
            updateAgentCard(data.agent, data.action, data.step, data.total_steps);
            addFeedItem(data.agent, `Step ${data.step}/${data.total_steps}`, data.action, data.agent);
            break;

        case 'agent_complete':
            completeAgentCard(data.agent, data.result);
            completePipelineAgent(data.agent);
            addFeedItem(data.agent, `${data.name} — Done`, data.result, data.agent, true);
            if (data.decision === 'mission_accomplished') {
                updateStat('statStatus', 'Complete');
            }
            break;

        case 'memory_store':
            memoryCount += data.entries.length;
            updateStat('statMemory', memoryCount);
            data.entries.forEach(entry => {
                addFeedItem('memory', 'Memory Stored', entry, 'memory');
            });
            break;

        case 'turn_end':
            if (data.status === 'continue') {
                addFeedItem('system', 'Cycle Complete', `Turn ${data.turn} finished. Looping back to Planner...`, 'system');
            }
            break;

        case 'game_end':
            addFeedItem('done', 'Mission Complete', `Finished in ${data.total_turns} turns.`, 'done', true);
            updateStat('statStatus', 'Done');
            showOverlay(data);
            isRunning = false;
            document.getElementById('startBtn').disabled = false;
            if (eventSource) eventSource.close();
            break;
    }
}

// ===== UI HELPERS =====

function resetUI() {
    const feed = document.getElementById('feedScroll');
    feed.innerHTML = '';
    eventCount = 0;
    memoryCount = 0;
    document.getElementById('eventCount').textContent = '0 events';
    updateStat('statTurn', '—');
    updateStat('statStatus', 'Idle');
    updateStat('statMemory', '0');
    resetPipeline();
    resetAllAgentCards();
    dismissOverlay();
}

function updateStat(id, value) {
    const el = document.getElementById(id);
    if (el) el.querySelector('.stat-value').textContent = value;
}

function getTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

// ===== FEED =====

function addFeedItem(badgeType, label, text, badgeClass, highlight = false) {
    const feed = document.getElementById('feedScroll');
    const empty = document.getElementById('feedEmpty');
    if (empty) empty.remove();

    eventCount++;
    document.getElementById('eventCount').textContent = `${eventCount} events`;

    const item = document.createElement('div');
    item.className = `feed-item${highlight ? ' highlight' : ''}`;
    if (highlight) item.style.setProperty('--accent-color', AGENT_COLORS[badgeClass] || '');

    item.innerHTML = `
        <div class="feed-badge ${badgeClass}">${BADGE_ICONS[badgeType] || '•'}</div>
        <div class="feed-content">
            <div class="feed-label">${label}</div>
            <div class="feed-text">${text}</div>
        </div>
        <div class="feed-time">${getTimestamp()}</div>
    `;

    feed.appendChild(item);
    feed.scrollTop = feed.scrollHeight;
}

// ===== PIPELINE =====

function resetPipeline() {
    document.querySelectorAll('.pipeline-agent').forEach(el => {
        el.classList.remove('active', 'done');
        el.style.removeProperty('--accent-color');
    });
}

function activatePipelineAgent(agent, color) {
    // Mark previous as done
    const order = ['planner', 'researcher', 'coder', 'critic'];
    const idx = order.indexOf(agent);
    order.forEach((a, i) => {
        const el = document.getElementById(`pipe-${a}`);
        if (i < idx) {
            el.classList.remove('active');
            el.classList.add('done');
        } else if (i === idx) {
            el.classList.remove('done');
            el.classList.add('active');
            el.style.setProperty('--accent-color', color);
        }
    });
}

function completePipelineAgent(agent) {
    const el = document.getElementById(`pipe-${agent}`);
    el.classList.remove('active');
    el.classList.add('done');
}

// ===== AGENT CARDS =====

function resetAllAgentCards() {
    ['planner', 'researcher', 'coder', 'critic'].forEach(agent => {
        const card = document.getElementById(`card-${agent}`);
        card.classList.remove('active', 'done');
        const status = document.getElementById(`status-${agent}`);
        status.className = 'card-status idle';
        status.textContent = 'IDLE';
        document.getElementById(`action-${agent}`).textContent = 'Waiting for mission...';
        document.querySelector(`#progress-${agent} .progress-bar`).style.width = '0%';
    });
}

function activateAgentCard(agent) {
    // Deactivate others
    ['planner', 'researcher', 'coder', 'critic'].forEach(a => {
        if (a !== agent) {
            const card = document.getElementById(`card-${a}`);
            if (card.classList.contains('active')) {
                card.classList.remove('active');
                card.classList.add('done');
            }
        }
    });

    const card = document.getElementById(`card-${agent}`);
    card.classList.remove('done');
    card.classList.add('active');
    card.style.setProperty('--accent', AGENT_COLORS[agent]);

    const status = document.getElementById(`status-${agent}`);
    status.className = 'card-status active';
    status.textContent = 'WORKING';

    document.getElementById(`action-${agent}`).textContent = 'Initializing...';
    document.querySelector(`#progress-${agent} .progress-bar`).style.width = '5%';
    document.querySelector(`#progress-${agent} .progress-bar`).style.background =
        `linear-gradient(90deg, ${AGENT_COLORS[agent]}, ${AGENT_COLORS[agent]}88)`;
}

function updateAgentCard(agent, action, step, totalSteps) {
    document.getElementById(`action-${agent}`).textContent = action;
    const pct = Math.round((step / totalSteps) * 100);
    document.querySelector(`#progress-${agent} .progress-bar`).style.width = `${pct}%`;
}

function completeAgentCard(agent, result) {
    const card = document.getElementById(`card-${agent}`);
    card.classList.remove('active');
    card.classList.add('done');

    const status = document.getElementById(`status-${agent}`);
    status.className = 'card-status done';
    status.textContent = 'DONE';

    document.getElementById(`action-${agent}`).textContent = result;
    document.querySelector(`#progress-${agent} .progress-bar`).style.width = '100%';
    document.querySelector(`#progress-${agent} .progress-bar`).style.background =
        `linear-gradient(90deg, ${AGENT_COLORS[agent]}, var(--green))`;
}

// ===== OVERLAY =====

function showOverlay(data) {
    document.getElementById('overlaySummary').textContent =
        `Mission "${data.mission}" completed in ${data.total_turns} turns with all objectives met.`;
    document.getElementById('overlay').classList.add('visible');
}

function dismissOverlay() {
    document.getElementById('overlay').classList.remove('visible');
}

// ===== KEYBOARD SHORTCUT =====
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !isRunning && document.activeElement.id === 'missionInput') {
        startGame();
    }
    if (e.key === 'Escape') {
        dismissOverlay();
    }
});
