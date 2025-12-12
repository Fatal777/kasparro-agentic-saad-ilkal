/**
 * Multi-Agent Content Generation System - Interactive Frontend
 * 
 * NO HARDCODED FALLBACKS - All content is dynamically loaded from the LangGraph API
 */

const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : 'https://kasparro-content-api.onrender.com/api';

let isRunning = false;

// DOM Elements
const header = document.getElementById('header');
const themeToggle = document.getElementById('themeToggle');
const runPipelineBtn = document.getElementById('runPipelineBtn');
const statusBadge = document.getElementById('pipelineStatus');
const executionLog = document.getElementById('executionLog');
const tabs = document.querySelectorAll('.tab');
const tabPanels = document.querySelectorAll('.tab-panel');
const filterBtns = document.querySelectorAll('.filter-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initHeader();
    initTabs();
    initCategoryFilter();
    initPipelineButton();
    // Load outputs from API
    setTimeout(() => {
        loadAllOutputs();
    }, 100);
});

// Theme Toggle
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });
}

// Floating Header
function initHeader() {
    window.addEventListener('scroll', () => {
        header.classList.toggle('scrolled', window.scrollY > 50);
    });
}

// Tabs
function initTabs() {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
        });
    });
}

// Category Filter
function initCategoryFilter() {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterFAQs(btn.dataset.category);
        });
    });
}

function filterFAQs(category) {
    const items = document.querySelectorAll('.faq-item');
    items.forEach(item => {
        if (category === 'all' || item.dataset.category === category) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

// Pipeline Button
function initPipelineButton() {
    runPipelineBtn.addEventListener('click', runPipeline);
}

// Run Pipeline with Auto-Scroll and Animations
async function runPipeline() {
    if (isRunning) return;

    isRunning = true;
    runPipelineBtn.disabled = true;
    runPipelineBtn.innerHTML = '⏳ Running...';
    statusBadge.className = 'console-badge running';
    statusBadge.textContent = 'Running';
    executionLog.innerHTML = '';

    try {
        addLogEntry('🚀', 'Starting LangGraph pipeline...', 'info');

        const stages = [
            { id: 'parser', name: 'Parse Products', icon: '📦', delay: 800 },
            { id: 'logic', name: 'Run Logic Blocks', icon: '🔧', delay: 800 },
            { id: 'question', name: 'Generate Questions (LLM)', icon: '❓', delay: 3000 },
            { id: 'faq', name: 'Generate FAQ (LLM)', icon: '📝', delay: 3000 },
            { id: 'product', name: 'Generate Product Page (LLM)', icon: '🛍️', delay: 2000 },
            { id: 'comparison', name: 'Generate Comparison (LLM)', icon: '⚖️', delay: 2000 },
            { id: 'template', name: 'Write Outputs', icon: '✨', delay: 500 }
        ];

        // Animate stages (visual feedback only)
        for (let i = 0; i < stages.length; i++) {
            const stage = stages[i];
            activateNode(stage.id);
            addLogEntry(stage.icon, `${stage.name}...`, 'info');
            await sleep(stage.delay * 0.5); // Faster animation since real work is async
            completeNode(stage.id);
            if (i < stages.length - 1) activateArrow(`arrow-${i + 1}`);
        }

        // Call actual API
        addLogEntry('📡', 'Starting async job...', 'info');
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, { method: 'POST' });
        const result = await response.json();

        if (response.ok && result.job_id) {
            addLogEntry('⏳', `Job ID: ${result.job_id}`, 'info');

            // Poll for status
            let status = 'processing';
            let formattedId = result.job_id.substring(0, 8);
            let pollCount = 0;

            while (status === 'pending' || status === 'processing') {
                await sleep(2000);
                pollCount++;

                const jobRes = await fetch(`${API_BASE_URL}/jobs/${result.job_id}`);
                if (!jobRes.ok) throw new Error('Failed to poll job status');

                const job = await jobRes.json();
                status = job.status;

                if (pollCount % 5 === 0) {
                    addLogEntry('🔄', `Job ${formattedId}... still processing`, 'info');
                }

                if (status === 'completed') {
                    // Show success
                    addLogEntry('✅', `Success! Job completed.`, 'success');
                    statusBadge.className = 'console-badge idle';
                    statusBadge.textContent = 'Complete';

                    // Render outputs directly from job result (Stateless)
                    await loadAllOutputs(job.result);

                    // Scroll to outputs
                    await sleep(800);
                    const outputSection = document.getElementById('output-section');
                    if (outputSection) {
                        outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                    return; // Done
                } else if (status === 'failed') {
                    throw new Error(job.error || 'Job failed mysteriously');
                }
            }
        } else {
            throw new Error(result.detail || result.message || 'Pipeline failed to start');
        }

    } catch (e) {
        addLogEntry('❌', `Error: ${e.message}`, 'error');
        statusBadge.className = 'console-badge error';
        statusBadge.textContent = 'Error';
    } finally {
        isRunning = false;
        runPipelineBtn.disabled = false;
        runPipelineBtn.innerHTML = '▶ Run Pipeline';
    }
}

function activateNode(id) {
    const node = document.querySelector(`[data-node="${id}"]`);
    if (node) node.classList.add('active');
}

function completeNode(id) {
    const node = document.querySelector(`[data-node="${id}"]`);
    if (node) {
        node.classList.remove('active');
        node.classList.add('completed');
    }
}

function activateArrow(id) {
    const arrow = document.getElementById(id);
    if (arrow) {
        arrow.classList.add('active');
        setTimeout(() => arrow.classList.add('completed'), 500);
    }
}

function addLogEntry(icon, message, type = 'info') {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `<span class="log-time">${time}</span><span class="log-icon">${icon}</span><span class="log-msg">${message}</span>`;
    executionLog.appendChild(entry);
    executionLog.scrollTop = executionLog.scrollHeight;
}

// Load All Outputs - Renders data directly from Job Result
async function loadAllOutputs(jobResult = null) {
    if (!jobResult) {
        showPlaceholder(document.getElementById('faq-content'), 'Run pipeline to generate content');
        showPlaceholder(document.getElementById('product-content'), 'Run pipeline to generate content');
        showPlaceholder(document.getElementById('comparison-content'), 'Run pipeline to generate content');
        return;
    }

    console.log('Rendering outputs from job result...');

    // Extract data from job result
    const faqData = jobResult.faq_output;
    const productData = jobResult.product_output;
    const comparisonData = jobResult.comparison_output;

    renderFAQ(faqData);
    renderProduct(productData);
    renderComparison(comparisonData);
}

// Show placeholder
function showPlaceholder(element, message) {
    if (element) {
        element.innerHTML = `
            <div style="padding: 2rem; text-align: center; opacity: 0.6;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
                <div>${message}</div>
                <div style="margin-top: 1rem; font-size: 0.85rem;">
                    Click <strong>Run Pipeline</strong> to generate content with LLM
                </div>
            </div>
        `;
    }
}

function renderFAQ(data) {
    const faqCountEl = document.getElementById('faq-count');
    const faqContentEl = document.getElementById('faq-content');

    if (!data) {
        if (faqCountEl) faqCountEl.textContent = '0 Q&As';
        showPlaceholder(faqContentEl, 'FAQ generation failed');
        return;
    }

    if (faqCountEl) {
        faqCountEl.textContent = `${data.totalQuestions || data.faqs?.length || 0} Q&As`;
    }

    if (faqContentEl && data.faqs) {
        faqContentEl.innerHTML = `<div class="faq-list">${data.faqs.map(faq => `
            <div class="faq-item" data-category="${faq.category}">
                <div class="faq-category">${faq.category}</div>
                <div class="faq-question">${faq.question}</div>
                <div class="faq-answer">${faq.answer}</div>
            </div>
        `).join('')}</div>`;
    }
}

function renderProduct(data) {
    const productContentEl = document.getElementById('product-content');

    if (!data) {
        showPlaceholder(productContentEl, 'Product generation failed');
        return;
    }

    if (productContentEl) {
        const currency = data.price?.currency === 'INR' ? '₹' : (data.price?.currency || '₹');
        productContentEl.innerHTML = `
            <div style="display:grid;gap:1.25rem;">
                <div style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;">${data.productName}</div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;">
                    <div><span style="opacity:0.6;font-size:0.85rem;">Concentration</span><div style="font-weight:600;">${data.concentration || 'N/A'}</div></div>
                    <div><span style="opacity:0.6;font-size:0.85rem;">Price</span><div style="font-weight:700;font-size:1.5rem;">${currency}${data.price?.amount || 0}</div></div>
                </div>
                <div><span style="opacity:0.6;font-size:0.85rem;">Skin Types</span><div style="margin-top:0.5rem;">${(data.skinTypes || []).map(t => `<span class="tag">${t}</span>`).join(' ')}</div></div>
                <div><span style="opacity:0.6;font-size:0.85rem;">Key Ingredients</span><div style="margin-top:0.5rem;">${(data.keyIngredients || []).map(i => `<span class="tag">${i}</span>`).join(' ')}</div></div>
                <div><span style="opacity:0.6;font-size:0.85rem;">Benefits</span><div style="margin-top:0.5rem;">${(data.benefits?.items || []).map(b => `<span class="tag">${b}</span>`).join(' ')}</div></div>
                <div><span style="opacity:0.6;font-size:0.85rem;">How to Use</span><div style="margin-top:0.5rem;">${data.usage?.instructions || data.usage || ''}</div></div>
            </div>`;
    }
}

function renderComparison(data) {
    const comparisonContentEl = document.getElementById('comparison-content');

    if (!data) {
        showPlaceholder(comparisonContentEl, 'Comparison generation failed');
        return;
    }

    if (comparisonContentEl) {
        comparisonContentEl.innerHTML = `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem;">
                <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
                    <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.5rem;">Product A</div>
                    <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">${data.productA?.name || 'Product A'}</div>
                    <div style="font-size:1.75rem;font-weight:700;margin-bottom:1rem;">₹${data.productA?.price || 0}</div>
                    <div style="font-size:0.85rem;opacity:0.7;">${(data.productA?.benefits || []).join(' • ')}</div>
                </div>
                <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
                    <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.5rem;">Product B</div>
                    <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">${data.productB?.name || 'Product B'}</div>
                    <div style="font-size:1.75rem;font-weight:700;margin-bottom:1rem;">₹${data.productB?.price || 0}</div>
                    <div style="font-size:0.85rem;opacity:0.7;">${(data.productB?.benefits || []).join(' • ')}</div>
                </div>
            </div>
            <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
                <div style="font-weight:600;margin-bottom:1rem;">📊 Analysis</div>
                <div style="display:grid;gap:0.75rem;font-size:0.9rem;">
                    <div><span style="opacity:0.6;">Price Difference:</span> <strong>₹${Math.abs(data.comparison?.priceDifference || 0)}</strong></div>
                    <div><span style="opacity:0.6;">More Affordable:</span> <strong>${data.comparison?.cheaperProduct === 'productA' ? data.productA?.name : data.productB?.name}</strong></div>
                    <div style="padding-top:0.75rem;border-top:1px solid var(--border);"><span style="opacity:0.6;">Recommendation:</span> ${data.comparison?.recommendation || ''}</div>
                </div>
            </div>`;
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
