/* ═══════════════════════════════════════
   FORGE — CODE GENERATOR
   script.js
   ═══════════════════════════════════════ */

let latestResult = null;
let currentPage  = 0;
let toastTimer   = null;

const TOTAL_PAGES = 5;

// ── DOM shortcuts
const $ = id => document.getElementById(id);

// ── Char counter
$('description').addEventListener('input', () => {
  $('char-count').textContent = $('description').value.length;
});

// ─────────────────────────────────────────
// PAGE NAVIGATION
// ─────────────────────────────────────────

function goTo(index) {
  const pages   = document.querySelectorAll('.page');
  const navBtns = document.querySelectorAll('.topbar-step');

  // Exit current
  pages[currentPage].classList.remove('active');
  pages[currentPage].classList.add('exit');

  // Clean exit class after anim
  setTimeout(() => pages[currentPage].classList.remove('exit'), 450);

  // Enter new
  currentPage = index;
  pages[currentPage].classList.add('active');

  // Update topbar steps
  navBtns.forEach((btn, i) => {
    btn.classList.remove('active', 'done');
    if (i < currentPage)  btn.classList.add('done');
    if (i === currentPage) btn.classList.add('active');
  });

  // Update counter
  $('step-counter').textContent =
    String(currentPage + 1).padStart(2, '0') + ' / ' +
    String(TOTAL_PAGES).padStart(2, '0');

  // Scroll result content to top
  const resultText = pages[currentPage].querySelector('.result-text');
  if (resultText) resultText.scrollTop = 0;
}

// ─────────────────────────────────────────
// GENERATION PIPELINE
// ─────────────────────────────────────────

async function startGeneration() {
  const description = $('description').value.trim();
  const langInput   = document.querySelector('input[name="lang"]:checked');
  const language    = langInput ? langInput.value : 'Python';

  if (!description) {
    showToast('⚠ DESCRIBE YOUR PROJECT FIRST');
    return;
  }

  // Reset states
  resetResultPages();
  latestResult = null;

  // Move to planning page first
  goTo(1);

  try {
    const response = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, language })
    });

    if (!response.ok) throw new Error('SERVER ERROR ' + response.status);

    const data = await response.json();
    latestResult = data;

    // Populate all sections
    populatePage('planning', data.planning);
    populatePage('design',   data.design);
    populatePage('code',     data.code);
    populatePage('testing',  data.testing);

    // Set language badge
    $('code-lang-badge').textContent = language.toUpperCase();

    // Set complete stats
    const lines = (data.code || '').split('\n').length;
    $('complete-stats').innerHTML =
      `<strong>${lines} LINES</strong> OF ${language.toUpperCase()} — 4-AGENT PIPELINE`;

    // Show complete block on testing page
    $('complete-block').classList.remove('hidden');

  } catch (err) {
    showToast('⚠ ' + err.message.toUpperCase());
    goTo(0);
  }
}

// Reveal a page section (hide skeleton, show content, show next btn)
function populatePage(name, content) {
  $(`${name}-loading`).classList.add('hidden');
  $(`${name}-content`).classList.remove('hidden');
  $(`${name}-body`).textContent = content || '— No content returned —';

  // Show next button if it exists
  const nextBtn = $(`${name === 'planning' ? 'plan' : name}-next`);
  if (nextBtn) nextBtn.classList.remove('hidden');
}

// Reset all result pages for fresh generation
function resetResultPages() {
  ['planning', 'design', 'code', 'testing'].forEach(name => {
    const loading = $(`${name}-loading`);
    const content = $(`${name}-content`);
    if (loading) {
      loading.classList.remove('hidden');
      loading.style.display = '';
    }
    if (content) content.classList.add('hidden');

    const body = $(`${name}-body`);
    if (body) body.textContent = '';
  });

  // Hide next buttons
  ['plan-next', 'design-next', 'code-next'].forEach(id => {
    const el = $(id);
    if (el) el.classList.add('hidden');
  });

  // Hide complete block
  const cb = $('complete-block');
  if (cb) cb.classList.add('hidden');
}

// ─────────────────────────────────────────
// COPY / DOWNLOAD
// ─────────────────────────────────────────

function copySection(id) {
  const text = $(id)?.textContent;
  if (!text) return showToast('NOTHING TO COPY');
  navigator.clipboard.writeText(text).then(() => showToast('✓ COPIED'));
}

function copyAll() {
  if (!latestResult) return showToast('⚠ GENERATE FIRST');
  const all =
    'PLANNING:\n'      + latestResult.planning + '\n\n' +
    'ARCHITECTURE:\n'  + latestResult.design   + '\n\n' +
    'CODE:\n'          + latestResult.code     + '\n\n' +
    'TESTING:\n'       + latestResult.testing;
  navigator.clipboard.writeText(all).then(() => showToast('✓ ALL COPIED'));
}

function downloadCode() {
  if (!latestResult) return showToast('⚠ GENERATE FIRST');
  const langInput = document.querySelector('input[name="lang"]:checked');
  const lang      = langInput ? langInput.value : 'Python';
  const extMap    = { Python:'py', JavaScript:'js', TypeScript:'ts', Go:'go', Rust:'rs', Java:'java' };
  const ext       = extMap[lang] || 'txt';
  triggerDownload(new Blob([latestResult.code], { type: 'text/plain' }), `generated.${ext}`);
  showToast('↓ CODE DOWNLOADED');
}

function downloadReport() {
  if (!latestResult) return showToast('⚠ GENERATE FIRST');
  const report =
    '════════════════════════════\n' +
    '  FORGE — GENERATION REPORT\n' +
    '════════════════════════════\n\n' +
    'PLANNING:\n'      + latestResult.planning + '\n\n' +
    'ARCHITECTURE:\n'  + latestResult.design   + '\n\n' +
    'CODE:\n'          + latestResult.code     + '\n\n' +
    'TESTING:\n'       + latestResult.testing;
  triggerDownload(new Blob([report], { type: 'text/plain' }), 'forge_report.txt');
  showToast('↓ REPORT DOWNLOADED');
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a   = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function startOver() {
  goTo(0);
  $('description').value = '';
  $('char-count').textContent = '0';
  latestResult = null;
}

// ─────────────────────────────────────────
// TOAST
// ─────────────────────────────────────────

function showToast(msg) {
  const toast = $('toast');
  $('toast-msg').textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2400);
}

// ─────────────────────────────────────────
// KEYBOARD
// ─────────────────────────────────────────

document.addEventListener('keydown', e => {
  // Ctrl+Enter to generate from input page
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && currentPage === 0) {
    startGeneration();
  }
  // Escape to go back
  if (e.key === 'Escape' && currentPage > 0) {
    goTo(currentPage - 1);
  }
});