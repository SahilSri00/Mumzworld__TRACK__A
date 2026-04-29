/**
 * Mumzworld Smart Shopping List — Frontend Logic
 * Handles: API calls, voice input (Web Speech API), result rendering, RTL switching
 */

const API_URL = '/api/parse';

// ── DOM Elements ──────────────────────────────────────────────
const messageInput = document.getElementById('messageInput');
const parseBtn = document.getElementById('parseBtn');
const btnLoader = document.getElementById('btnLoader');
const micBtn = document.getElementById('micBtn');
const charCount = document.getElementById('charCount');
const inputSection = document.getElementById('inputSection');
const resultsSection = document.getElementById('resultsSection');
const summaryText = document.getElementById('summaryText');
const overallConfidence = document.getElementById('overallConfidence');
const uncertaintyNotes = document.getElementById('uncertaintyNotes');
const outOfScopeBanner = document.getElementById('outOfScopeBanner');
const outOfScopeReason = document.getElementById('outOfScopeReason');
const shoppingItems = document.getElementById('shoppingItems');
const shoppingEmpty = document.getElementById('shoppingEmpty');
const calendarEvents = document.getElementById('calendarEvents');
const calendarEmpty = document.getElementById('calendarEmpty');
const itemCount = document.getElementById('itemCount');
const eventCount = document.getElementById('eventCount');
const jsonOutput = document.getElementById('jsonOutput');
const jsonToggle = document.getElementById('jsonToggle');
const newMessageBtn = document.getElementById('newMessageBtn');
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');
const langToggle = document.getElementById('langToggle');
const exampleChips = document.getElementById('exampleChips');

let isRecording = false;
let recognition = null;

// ── Initialize ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    setupEventListeners();
    setupSpeechRecognition();
});

function createParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 6; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 200 + 80;
        p.style.cssText = `
            width:${size}px;height:${size}px;
            left:${Math.random()*100}%;top:${Math.random()*100}%;
            animation-delay:${Math.random()*10}s;animation-duration:${15+Math.random()*15}s;
        `;
        container.appendChild(p);
    }
}

function setupEventListeners() {
    parseBtn.addEventListener('click', handleParse);
    messageInput.addEventListener('input', updateCharCount);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleParse();
    });
    micBtn.addEventListener('click', toggleRecording);
    newMessageBtn.addEventListener('click', resetToInput);
    jsonToggle.addEventListener('click', toggleJson);

    // Example chips
    exampleChips.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            messageInput.value = chip.dataset.message;
            updateCharCount();
            messageInput.focus();
        });
    });

    // Language toggle
    langToggle.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            langToggle.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const lang = btn.dataset.lang;
            document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
            document.documentElement.lang = lang;
            if (lang === 'ar') {
                messageInput.placeholder = 'مثال: محتاجة حفاضات لليلى مقاس ٣، عيد ميلادها الشهر الجاي محتاجة أغراض حفلة...';
            } else {
                messageInput.placeholder = "e.g., need diapers for Layla she's size 3, her birthday is next month need party stuff...";
            }
        });
    });
}

function updateCharCount() {
    charCount.textContent = `${messageInput.value.length} / 3000`;
}

// ── Speech Recognition ────────────────────────────────────────
function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.title = 'Voice input not supported in this browser';
        micBtn.style.opacity = '0.4';
        micBtn.style.cursor = 'default';
        return;
    }
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        messageInput.value = transcript;
        updateCharCount();
    };

    let networkRetries = 0;
    const MAX_RETRIES = 3;

    recognition.onerror = (event) => {
        console.warn('Speech error:', event.error);
        if (event.error === 'not-allowed') {
            stopRecording();
            showError('Microphone access denied. Please allow mic access in your browser settings.');
        } else if (event.error === 'network') {
            // Chrome's speech API often throws a network error on first try.
            // Silently retry a few times before giving up.
            networkRetries++;
            if (networkRetries >= MAX_RETRIES) {
                stopRecording();
                showError('Voice input unavailable. Make sure you are using http://localhost:8000 in Chrome.');
                networkRetries = 0;
            }
            // Otherwise let onend auto-restart
        }
        // For 'no-speech', 'aborted', etc. — let onend handle restart
    };

    recognition.onend = () => {
        // If we're still supposed to be recording, auto-restart
        if (isRecording) {
            setTimeout(() => {
                if (!isRecording) return; // User clicked stop during the delay
                try {
                    recognition.start();
                } catch (e) {
                    console.warn('Could not restart recognition:', e);
                    stopRecording();
                }
            }, 300); // Small delay prevents rapid-fire restarts
        }
    };
}

function toggleRecording() {
    if (!recognition) {
        showError('Voice input is not supported in this browser. Please use Chrome or Edge.');
        return;
    }
    if (isRecording) { stopRecording(); } else { startRecording(); }
}

function startRecording() {
    const activeLang = langToggle.querySelector('.lang-btn.active').dataset.lang;
    recognition.lang = activeLang === 'ar' ? 'ar-SA' : 'en-US';
    try {
        recognition.start();
    } catch (e) {
        // Already started — stop and restart
        recognition.stop();
        setTimeout(() => {
            try { recognition.start(); } catch (err) { console.warn(err); }
        }, 100);
    }
    isRecording = true;
    micBtn.classList.add('recording');
    messageInput.placeholder = activeLang === 'ar' ? 'جاري الاستماع... 🎤' : 'Listening... 🎤';
}

function stopRecording() {
    isRecording = false; // Set this FIRST so onend doesn't restart
    try { recognition.stop(); } catch (e) { /* already stopped */ }
    micBtn.classList.remove('recording');
    const activeLang = langToggle.querySelector('.lang-btn.active').dataset.lang;
    messageInput.placeholder = activeLang === 'ar'
        ? 'مثال: محتاجة حفاضات لليلى مقاس ٣...'
        : "e.g., need diapers for Layla she's size 3...";
}

// ── Parse Handler ─────────────────────────────────────────────
async function handleParse() {
    const message = messageInput.value.trim();
    if (!message) { showError('Please enter a message first.'); return; }

    parseBtn.disabled = true;
    parseBtn.classList.add('loading');

    try {
        const activeLang = langToggle.querySelector('.lang-btn.active').dataset.lang;
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, language_hint: activeLang }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error (${res.status})`);
        }

        const data = await res.json();
        renderResults(data);
    } catch (err) {
        showError(err.message || 'Something went wrong. Please try again.');
    } finally {
        parseBtn.disabled = false;
        parseBtn.classList.remove('loading');
    }
}

// ── Render Results ────────────────────────────────────────────
function renderResults(data) {
    // Switch to results view
    inputSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Set direction based on detected language
    if (data.detected_language === 'ar') {
        document.documentElement.dir = 'rtl';
        document.documentElement.lang = 'ar';
    }

    // Summary
    summaryText.textContent = data.summary;

    // Overall confidence
    const conf = Math.round(data.overall_confidence * 100);
    overallConfidence.textContent = `${conf}% confident`;
    overallConfidence.className = 'confidence-badge ' + (
        conf >= 80 ? 'confidence-high' : conf >= 60 ? 'confidence-medium' : 'confidence-low'
    );

    // Uncertainty notes
    uncertaintyNotes.innerHTML = '';
    if (data.uncertainty_notes && data.uncertainty_notes.length > 0) {
        data.uncertainty_notes.forEach(note => {
            const div = document.createElement('div');
            div.className = 'uncertainty-note';
            div.innerHTML = `<span>⚠️</span><span>${escapeHtml(note)}</span>`;
            uncertaintyNotes.appendChild(div);
        });
    }

    // Out of scope
    if (data.is_out_of_scope) {
        outOfScopeBanner.classList.remove('hidden');
        outOfScopeReason.textContent = data.out_of_scope_reason || 'This message is outside scope.';
    } else {
        outOfScopeBanner.classList.add('hidden');
    }

    // Shopping items
    shoppingItems.innerHTML = '';
    if (data.shopping_items && data.shopping_items.length > 0) {
        shoppingEmpty.classList.add('hidden');
        itemCount.textContent = `${data.shopping_items.length} item${data.shopping_items.length > 1 ? 's' : ''}`;
        data.shopping_items.forEach(item => {
            shoppingItems.appendChild(createShoppingItemCard(item));
        });
    } else {
        shoppingEmpty.classList.remove('hidden');
        itemCount.textContent = '0 items';
    }

    // Calendar events
    calendarEvents.innerHTML = '';
    if (data.calendar_events && data.calendar_events.length > 0) {
        calendarEmpty.classList.add('hidden');
        eventCount.textContent = `${data.calendar_events.length} event${data.calendar_events.length > 1 ? 's' : ''}`;
        data.calendar_events.forEach(event => {
            calendarEvents.appendChild(createCalendarEventCard(event));
        });
    } else {
        calendarEmpty.classList.remove('hidden');
        eventCount.textContent = '0 events';
    }

    // JSON
    jsonOutput.textContent = JSON.stringify(data, null, 2);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function createShoppingItemCard(item) {
    const div = document.createElement('div');
    const isUncertain = item.confidence < 0.6;
    div.className = `shopping-item priority-${item.priority}${isUncertain ? ' uncertain' : ''}`;

    const confPct = Math.round(item.confidence * 100);
    const confClass = confPct >= 80 ? 'confidence-high' : confPct >= 60 ? 'confidence-medium' : 'confidence-low';

    let detailsHtml = '';
    if (item.brand_preference) detailsHtml += `<span class="item-tag">🏷️ ${escapeHtml(item.brand_preference)}</span>`;
    if (item.size_or_age) detailsHtml += `<span class="item-tag">📏 ${escapeHtml(item.size_or_age)}</span>`;
    if (item.quantity) detailsHtml += `<span class="item-tag">📦 ×${item.quantity}</span>`;
    if (item.budget_max_aed) detailsHtml += `<span class="item-tag">💰 ≤ ${escapeHtml(String(item.budget_max_aed))}</span>`;
    if (item.priority === 'urgent' || item.priority === 'high') detailsHtml += `<span class="item-tag">🔥 ${item.priority}</span>`;

    div.innerHTML = `
        <div class="item-confidence ${confClass}">${confPct}%</div>
        <div class="item-top">
            <span class="item-name">${escapeHtml(item.item_name)}</span>
            <span class="item-category">${escapeHtml(item.category.replace('_', ' '))}</span>
        </div>
        ${detailsHtml ? `<div class="item-details">${detailsHtml}</div>` : ''}
        ${item.notes ? `<div style="font-size:0.83rem;color:var(--text-secondary);margin-bottom:6px">${escapeHtml(item.notes)}</div>` : ''}
        <div class="item-search">Search: <span>${escapeHtml(item.search_query)}</span></div>
        ${item.uncertainty_reason ? `<div class="item-uncertainty">⚠️ ${escapeHtml(item.uncertainty_reason)}</div>` : ''}
    `;
    return div;
}

function createCalendarEventCard(event) {
    const div = document.createElement('div');
    div.className = 'calendar-event';

    let dateDisplay = '?';
    let monthDisplay = '';
    if (event.estimated_date) {
        const d = new Date(event.estimated_date);
        dateDisplay = d.getDate();
        monthDisplay = d.toLocaleString('default', { month: 'short' });
    } else if (event.date_text) {
        dateDisplay = '📅';
        monthDisplay = '';
    }

    div.innerHTML = `
        <div class="event-date-badge">
            <span class="day">${dateDisplay}</span>
            <span>${monthDisplay}</span>
        </div>
        <div class="event-info">
            <div class="event-name">${escapeHtml(event.event_name)}</div>
            <div class="event-type">${escapeHtml(event.event_type.replace('_', ' '))}${event.date_text ? ' · ' + escapeHtml(event.date_text) : ''}</div>
            ${event.related_items && event.related_items.length > 0
                ? `<div class="event-related">🔗 ${event.related_items.map(i => escapeHtml(i)).join(', ')}</div>`
                : ''}
            ${event.uncertainty_reason ? `<div class="item-uncertainty" style="margin-top:8px">⚠️ ${escapeHtml(event.uncertainty_reason)}</div>` : ''}
        </div>
    `;
    return div;
}

// ── UI Helpers ─────────────────────────────────────────────────
function resetToInput() {
    resultsSection.classList.add('hidden');
    inputSection.classList.remove('hidden');
    messageInput.value = '';
    updateCharCount();
    document.documentElement.dir = 'ltr';
    document.documentElement.lang = 'en';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleJson() {
    jsonOutput.classList.toggle('hidden');
    jsonToggle.classList.toggle('open');
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorToast.classList.remove('hidden');
    setTimeout(() => errorToast.classList.add('hidden'), 5000);
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}
