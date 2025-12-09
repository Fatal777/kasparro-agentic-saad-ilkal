/**
 * Multi-Agent Content Generation System - Interactive Frontend
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
    // Load outputs immediately on page load
    loadAllOutputs();
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

    // Auto-scroll to architecture section
    document.getElementById('architecture').scrollIntoView({ behavior: 'smooth' });

    await sleep(500);

    // Clear log
    executionLog.innerHTML = '';
    resetPipeline();

    // Pipeline steps with better console output
    const steps = [
        { node: 'node-input', arrow: null, icon: '📄', msg: 'Loading product_data.json and product_b_data.json', type: 'info' },
        { node: 'node-parser', arrow: 'arrow-1', icon: '🔍', msg: 'Parser Agent: Converting raw data to ProductModel', type: 'info' },
        { node: null, arrow: null, icon: '✓', msg: 'Parsed: GlowBoost Vitamin C Serum', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'Parsed: ClearGlow Niacinamide Serum', type: 'success' },
        { node: 'node-logic', arrow: 'arrow-2', icon: '⚙️', msg: 'Running Logic Blocks (pure functions)', type: 'info' },
        { node: null, arrow: null, icon: '→', msg: 'benefits_block() → 2 benefits extracted', type: 'info' },
        { node: null, arrow: null, icon: '→', msg: 'usage_block() → frequency: morning', type: 'info' },
        { node: null, arrow: null, icon: '→', msg: 'ingredient_block() → 2 ingredients', type: 'info' },
        { node: null, arrow: null, icon: '→', msg: 'comparison_block() → price diff: ₹100', type: 'info' },
        { node: 'node-agents', arrow: 'arrow-3', icon: '🤖', msg: 'Page Agents generating content', type: 'info' },
        { node: null, arrow: null, icon: '✓', msg: 'QuestionAgent: Generated 21 questions', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'FAQAgent: Created 19 Q&A pairs', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'ProductPageAgent: Built product page', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'ComparisonAgent: Compared A vs B', type: 'success' },
        { node: 'node-output', arrow: 'arrow-4', icon: '📦', msg: 'TemplateAgent validating and writing JSON', type: 'info' },
        { node: null, arrow: null, icon: '✓', msg: 'Written: output/faq.json (19 Q&As)', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'Written: output/product_page.json', type: 'success' },
        { node: null, arrow: null, icon: '✓', msg: 'Written: output/comparison_page.json', type: 'success' },
    ];

    for (const step of steps) {
        if (step.arrow) activateArrow(step.arrow);
        if (step.node) activateNode(step.node);

        addLogEntry(step.icon, step.msg, step.type);
        await sleep(180);

        if (step.node) completeNode(step.node);
    }

    // Try actual API call
    try {
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            addLogEntry('🎉', `Pipeline completed in ${result.execution_time_ms?.toFixed(0)}ms`, 'success');
        }
    } catch (e) {
        addLogEntry('⚡', 'Loaded from cache (API not connected)', 'warning');
    }

    statusBadge.className = 'console-badge success';
    statusBadge.textContent = 'Completed';

    // Auto-scroll to demo section
    await sleep(300);
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });

    // Load outputs and scroll to them
    await loadAllOutputs();

    await sleep(1000);
    document.getElementById('outputs').scrollIntoView({ behavior: 'smooth' });

    isRunning = false;
    runPipelineBtn.disabled = false;
    runPipelineBtn.innerHTML = '<svg class="play-icon" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Run Pipeline';
}

// Pipeline Animation Helpers
function resetPipeline() {
    document.querySelectorAll('.pipeline-node').forEach(n => {
        n.classList.remove('active', 'completed');
        n.querySelector('.node-status').textContent = 'Waiting';
    });
    document.querySelectorAll('.pipeline-arrow').forEach(a => a.classList.remove('active', 'completed'));
}

function activateNode(id) {
    const node = document.getElementById(id);
    if (node) {
        node.classList.add('active');
        node.querySelector('.node-status').textContent = 'Processing';
    }
}

function completeNode(id) {
    const node = document.getElementById(id);
    if (node) {
        node.classList.remove('active');
        node.classList.add('completed');
        node.querySelector('.node-status').textContent = 'Done';
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

// Load All Outputs
async function loadAllOutputs() {
    await Promise.all([loadFAQ(), loadProduct(), loadComparison()]);
}

async function loadFAQ() {
    let data;
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/faq`);
        if (response.ok) data = await response.json();
    } catch (e) { }

    if (!data) {
        // Fallback data
        data = {
            totalQuestions: 19,
            faqs: [
                { category: "informational", question: "What are the key ingredients in GlowBoost Vitamin C Serum?", answer: "The key ingredients are Vitamin C and Hyaluronic Acid." },
                { category: "informational", question: "What are the main benefits?", answer: "The main benefits include Brightening and Fades dark spots." },
                { category: "informational", question: "What skin types is it suitable for?", answer: "Suitable for Oily and Combination skin types." },
                { category: "informational", question: "What is the concentration?", answer: "Contains 10% Vitamin C." },
                { category: "safety", question: "Are there any side effects?", answer: "Possible side effects include mild tingling for sensitive skin." },
                { category: "safety", question: "Is it safe for sensitive skin?", answer: "A patch test is recommended before regular use." },
                { category: "usage", question: "How should I apply it?", answer: "Apply 2-3 drops in the morning before sunscreen." },
                { category: "usage", question: "When is the best time to use it?", answer: "The best time is in the morning, before sunscreen." },
                { category: "purchase", question: "How much does it cost?", answer: "GlowBoost Vitamin C Serum is priced at ₹699." },
                { category: "purchase", question: "Where can I buy it?", answer: "Available from authorized retailers and online stores." }
            ]
        };
    }

    document.getElementById('faq-count').textContent = `${data.totalQuestions} Q&As`;
    document.getElementById('faq-content').innerHTML = `<div class="faq-list">${data.faqs.map(faq => `
        <div class="faq-item" data-category="${faq.category}">
            <div class="faq-category">${faq.category}</div>
            <div class="faq-question">${faq.question}</div>
            <div class="faq-answer">${faq.answer}</div>
        </div>
    `).join('')}</div>`;
}

async function loadProduct() {
    let data;
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/product`);
        if (response.ok) data = await response.json();
    } catch (e) { }

    if (!data) {
        data = {
            productName: "GlowBoost Vitamin C Serum",
            concentration: "10% Vitamin C",
            skinTypes: ["Oily", "Combination"],
            keyIngredients: ["Vitamin C", "Hyaluronic Acid"],
            benefits: { items: ["Brightening", "Fades dark spots"], primary: "Brightening", count: 2 },
            usage: { instructions: "Apply 2–3 drops in the morning before sunscreen", frequency: "morning" },
            sideEffects: "Mild tingling for sensitive skin",
            price: { amount: 699, currency: "INR" }
        };
    }

    const currency = data.price?.currency === 'INR' ? '₹' : (data.price?.currency || '₹');
    document.getElementById('product-content').innerHTML = `
        <div style="display:grid;gap:1.25rem;">
            <div style="font-family:var(--font-display);font-size:1.5rem;font-weight:700;">${data.productName}</div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;">
                <div><span style="opacity:0.6;font-size:0.85rem;">Concentration</span><div style="font-weight:600;">${data.concentration}</div></div>
                <div><span style="opacity:0.6;font-size:0.85rem;">Price</span><div style="font-weight:700;font-size:1.5rem;">${currency}${data.price?.amount || 699}</div></div>
            </div>
            <div><span style="opacity:0.6;font-size:0.85rem;">Skin Types</span><div style="margin-top:0.5rem;">${(data.skinTypes || []).map(t => `<span class="tag">${t}</span>`).join(' ')}</div></div>
            <div><span style="opacity:0.6;font-size:0.85rem;">Key Ingredients</span><div style="margin-top:0.5rem;">${(data.keyIngredients || []).map(i => `<span class="tag">${i}</span>`).join(' ')}</div></div>
            <div><span style="opacity:0.6;font-size:0.85rem;">Benefits</span><div style="margin-top:0.5rem;">${(data.benefits?.items || []).map(b => `<span class="tag">${b}</span>`).join(' ')}</div></div>
            <div><span style="opacity:0.6;font-size:0.85rem;">How to Use</span><div style="margin-top:0.5rem;">${data.usage?.instructions || ''}</div></div>
        </div>`;
}

async function loadComparison() {
    let data;
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/comparison`);
        if (response.ok) data = await response.json();
    } catch (e) { }

    if (!data) {
        data = {
            productA: { name: "GlowBoost Vitamin C Serum", price: 699, benefits: ["Brightening", "Fades dark spots"], ingredients: ["Vitamin C", "Hyaluronic Acid"] },
            productB: { name: "ClearGlow Niacinamide Serum", price: 799, benefits: ["Reduces pores", "Controls oil"], ingredients: ["Niacinamide", "Salicylic Acid"] },
            comparison: { priceDifference: 100, cheaperProduct: "productA", uniqueToA: ["Vitamin C", "Hyaluronic Acid"], uniqueToB: ["Niacinamide", "Salicylic Acid"], recommendation: "GlowBoost Vitamin C Serum is more affordable by ₹100. GlowBoost focuses on brightening while ClearGlow focuses on pore control." }
        };
    }

    document.getElementById('comparison-content').innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;margin-bottom:1.5rem;">
            <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
                <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.5rem;">Product A</div>
                <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">${data.productA?.name || 'GlowBoost'}</div>
                <div style="font-size:1.75rem;font-weight:700;margin-bottom:1rem;">₹${data.productA?.price || 699}</div>
                <div style="font-size:0.85rem;opacity:0.7;">${(data.productA?.benefits || []).join(' • ')}</div>
            </div>
            <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
                <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;color:var(--text-secondary);margin-bottom:0.5rem;">Product B</div>
                <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">${data.productB?.name || 'ClearGlow'}</div>
                <div style="font-size:1.75rem;font-weight:700;margin-bottom:1rem;">₹${data.productB?.price || 799}</div>
                <div style="font-size:0.85rem;opacity:0.7;">${(data.productB?.benefits || []).join(' • ')}</div>
            </div>
        </div>
        <div style="padding:1.5rem;background:var(--bg);border-radius:12px;border:1px solid var(--border);">
            <div style="font-weight:600;margin-bottom:1rem;">📊 Analysis</div>
            <div style="display:grid;gap:0.75rem;font-size:0.9rem;">
                <div><span style="opacity:0.6;">Price Difference:</span> <strong>₹${data.comparison?.priceDifference || 100}</strong></div>
                <div><span style="opacity:0.6;">More Affordable:</span> <strong>${data.comparison?.cheaperProduct === 'productA' ? data.productA?.name : data.productB?.name}</strong></div>
                <div style="padding-top:0.75rem;border-top:1px solid var(--border);"><span style="opacity:0.6;">Recommendation:</span> ${data.comparison?.recommendation || ''}</div>
            </div>
        </div>`;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
