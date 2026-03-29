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
    document.getElementById('editor').value = code;
    document.getElementById('stdin-input').value = inputs;
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
