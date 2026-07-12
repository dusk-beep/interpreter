// Start the system from Splash screen
function startSystem() {
    document.getElementById('splash').style.display = 'none';
    document.getElementById('main-ui').style.display = 'block';
}

// Tab Switching Logic
function showTab(tabId) {
    // Hide all contents
    const contents = document.getElementsByClassName('tab-content');
    for (let s of contents) s.classList.remove('active');

    // Deactivate all buttons
    const buttons = document.getElementsByClassName('nav-item');
    for (let b of buttons) b.classList.remove('active');

    // Show selected
    document.getElementById(tabId).classList.add('active');
    document.getElementById('btn-' + tabId).classList.add('active');
}

function getExampleCode(button) {
    const card = button.closest('.feature-card');
    return card ? card.querySelector('.code-box code').textContent : '';
}

async function copyExample(button) {
    const code = getExampleCode(button);
    if (!code) return;

    await navigator.clipboard.writeText(code);
    const oldText = button.innerText;
    button.innerText = 'Copied';
    setTimeout(() => {
        button.innerText = oldText;
    }, 1200);
}

function useExample(button, inputs = '') {
    const code = getExampleCode(button);
    const editor = document.getElementById('editor');
    
    editor.value = code;
    document.getElementById('stdin-input').value = inputs;
    
    // NEW: Manually trigger the highlight and scroll reset
    updateHighlight(); 
    editor.scrollTop = 0;
    syncScroll();

    showTab('playground');
}

// Execute Code
async function runManglish() {
    const code = document.getElementById('editor').value;
    const stdinInput = document.getElementById('stdin-input').value;
    const outputDiv = document.getElementById('terminal-output');

    // Switch to output tab automatically
    showTab('output');
    outputDiv.innerText = ">> ACCESSING KERNEL...\n>> RUNNING MONE_INTERPRETER...\n\n";

    try {
        const response = await fetch('http://127.0.0.1:5000/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code, inputs: stdinInput })
        });
        const data = await response.json();
        outputDiv.innerText += data.output;
    } catch (err) {
        outputDiv.innerHTML += `<span style="color:red">>> CRITICAL_ERROR: CONNECTION_REFUSED</span>`;
    }
}

// Optimized Highlight with "Line-End" Fix
function updateHighlight() {
    const editor = document.getElementById('editor');
    const highlightLayer = document.getElementById('highlight-layer');
    let code = editor.value;

    // Escape HTML
    code = code.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

    // Keywords, Strings, Comments, Numbers
    const bigRegex = /(".*?"|'.*?')|(#.*)|(\b(?:namaskaram|nanni|parayu|eduku|anengil|enkil|allengil|pravarthanam|thirike|kodku|ghatana|avarthikuka)\b)|(\b\d+(\.\d+)?\b)/g;

    const highlightedCode = code.replace(bigRegex, (match, string, comment, keyword, number) => {
        if (string) return `<span class="token-string">${match}</span>`;
        if (comment) return `<span class="token-comment">${match}</span>`;
        if (keyword) return `<span class="token-keyword">${match}</span>`;
        if (number) return `<span class="token-number">${match}</span>`;
        return match;
    });

    // The Fix: Always add a trailing space/newline so the heights match perfectly
    highlightLayer.innerHTML = highlightedCode + (code.endsWith('\n') ? ' <br>' : ' ');
    
    syncScroll();
}

// Robust Tab Handling (Supports Block Indent)
editor.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = this.selectionStart;
        const end = this.selectionEnd;

        // If user has selected multiple lines
        if (start !== end) {
            const lines = this.value.substring(start, end).split('\n');
            const indentedLines = lines.map(line => "    " + line).join('\n');
            this.value = this.value.substring(0, start) + indentedLines + this.value.substring(end);
            this.selectionStart = start;
            this.selectionEnd = start + indentedLines.length;
        } else {
            // Single cursor indent
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
        updateHighlight();
    }
});

// Auto-Sync on Scroll (Visual Insurance)
editor.addEventListener('scroll', syncScroll);

function syncScroll() {
    const editor = document.getElementById('editor');
    const highlightLayer = document.getElementById('highlight-layer');
    
    // Sync both vertical and horizontal scroll
    highlightLayer.scrollTop = editor.scrollTop;
    highlightLayer.scrollLeft = editor.scrollLeft;
}

// Add this inside your window.onload or at the end of startSystem()
document.addEventListener('DOMContentLoaded', () => {
    updateHighlight();
});

// Update useExample to refresh highlights
function useExample(button, inputs = '') {
    const code = getExampleCode(button);
    const editor = document.getElementById('editor');
    
    editor.value = code;
    document.getElementById('stdin-input').value = inputs;
    
    // Force a highlight refresh
    updateHighlight();
    showTab('playground');
    
    // Reset scroll to top
    editor.scrollTop = 0;
    syncScroll();
}
