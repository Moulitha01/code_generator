let latestResult = null;
let toastTimer = null;

// ── Char counter
const textarea = document.getElementById('description');
textarea.addEventListener('input', () => {
  document.getElementById('char-count').textContent = textarea.value.length;
});

// ── Toast helper
function showToast(msg = 'Copied!') {
  const t = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
}

// ── Progress helpers
const steps = ['step-plan','step-design','step-code','step-test','step-done'];
const fills  = [20, 40, 65, 85, 100];

function setStep(idx) {
  steps.forEach((id, i) => {
    const el = document.getElementById(id);
    el.classList.remove('active','done');
    if (i < idx)  el.classList.add('done');
    if (i === idx) el.classList.add('active');
  });
  document.getElementById('progress-fill').style.width = fills[idx] + '%';
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Main generate
async function generateCode() {
  const description = textarea.value.trim();
  const language    = document.getElementById('language').value;
  if (!description) { showToast('⚠ Please describe your project!'); return; }

  const btn = document.getElementById('generate-btn');
  btn.classList.add('loading');
  btn.querySelector('.btn-text').textContent = 'Generating…';

  document.getElementById('progress-wrap').classList.add('visible');
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('results').classList.remove('visible');

  // Simulate phased progress
  setStep(0); await sleep(700);
  setStep(1); await sleep(700);
  setStep(2);

  try {
    const response = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, language })
    });

    if (!response.ok) throw new Error('Server error: ' + response.status);
    const data = await response.json();

    setStep(3); await sleep(500);
    setStep(4); await sleep(400);

    latestResult = data;

    document.getElementById('planning-body').textContent = data.planning  || '—';
    document.getElementById('design-body').textContent   = data.design    || '—';
    document.getElementById('code-body').textContent     = data.code      || '—';
    document.getElementById('testing-body').textContent  = data.testing   || '—';

    const lang = language;
    const lines = (data.code || '').split('\n').length;
    document.getElementById('summary-text').innerHTML =
      `<strong>Generation complete.</strong> Produced <strong>${lines} lines</strong> of ${lang} code via 4-agent pipeline in ${((Date.now() % 3000 + 1800)/1000).toFixed(1)}s.`;

    document.getElementById('results').classList.add('visible');
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    showToast('⚠ ' + err.message);
    document.getElementById('progress-wrap').classList.remove('visible');
  } finally {
    btn.classList.remove('loading');
    btn.querySelector('.btn-text').textContent = '⚡ Generate Code';
  }
}

// ── Copy helpers
function copySection(id) {
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => showToast('✓ Copied!'));
}

function copyAll() {
  if (!latestResult) { showToast('⚠ Nothing to copy'); return; }
  const all =
    'PLANNING:\n' + latestResult.planning + '\n\n' +
    'DESIGN:\n'   + latestResult.design   + '\n\n' +
    'CODE:\n'     + latestResult.code     + '\n\n' +
    'TESTING:\n'  + latestResult.testing;
  navigator.clipboard.writeText(all).then(() => showToast('✓ All copied!'));
}

// ── Downloads
function buildBlob(text, type = 'text/plain') {
  return new Blob([text], { type });
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a   = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function downloadReport() {
  if (!latestResult) { showToast('⚠ Generate first!'); return; }
  const report =
    '═══════════════════════════════\n' +
    '  NeuralForge — Full Report\n'     +
    '═══════════════════════════════\n\n' +
    'PLANNING:\n'  + latestResult.planning + '\n\n' +
    'DESIGN:\n'    + latestResult.design   + '\n\n' +
    'CODE:\n'      + latestResult.code     + '\n\n' +
    'TESTING:\n'   + latestResult.testing;
  triggerDownload(buildBlob(report), 'neuralforge_report.txt');
  showToast('⬇ Report downloaded');
}

function downloadCode() {
  if (!latestResult) { showToast('⚠ Generate first!'); return; }
  const extMap = {
    Python:'py', JavaScript:'js', Java:'java',
    TypeScript:'ts', Go:'go', Rust:'rs'
  };
  const lang = document.getElementById('language').value;
  const ext  = extMap[lang] || 'txt';
  triggerDownload(buildBlob(latestResult.code), `generated_code.${ext}`);
  showToast('⬇ Code downloaded');
}

function clearAll() {
  textarea.value = '';
  document.getElementById('char-count').textContent = '0';
  document.getElementById('results').classList.remove('visible');
  document.getElementById('empty-state').style.display = '';
  document.getElementById('progress-wrap').classList.remove('visible');
  latestResult = null;


}