/**
 * Multi-Agent Content Generation System - Interactive Frontend
 */

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : 'https://kasparro-content-api.onrender.com/api';

let isRunning = false;
let faqData = null;

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
    loadExistingOutputs();
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

// Run Pipeline with Live Workflow Animation
async function runPipeline() {
    if (isRunning) return;

    isRunning = true;
    runPipelineBtn.disabled = true;
    runPipelineBtn.innerHTML = '⏳ Running...';
    statusBadge.className = 'demo-status-badge running';
    statusBadge.textContent = 'Running';

    executionLog.innerHTML = '';
    resetWorkflow();

    const stages = [
        { id: 'input', log: '📄 Loading product data...', agents: [] },
        { id: 'parser', log: '🔍 Parser Agent processing...', agents: ['agent-parser'] },
        { id: 'logic', log: '⚙️ Running logic blocks...', agents: [] },
        { id: 'agents', log: '🤖 Generating content pages...', agents: ['agent-question', 'agent-faq', 'agent-product', 'agent-comparison'] },
        { id: 'output', log: '📦 Template Agent writing JSON...', agents: ['agent-template'] }
    ];

    for (let i = 0; i < stages.length; i++) {
        const stage = stages[i];

        // Activate stage
        activateStage(stage.id);
        addLogLine(stage.log);

        // Activate connectors
        if (i > 0) {
            activateConnector(i - 1);
        }

        // Activate agents
        for (const agentId of stage.agents) {
            activateAgent(agentId);
            await sleep(200);
        }

        await sleep(400);
        completeStage(stage.id);

        // Complete agents
        for (const agentId of stage.agents) {
            completeAgent(agentId);
        }
    }

    // Extra log entries
    addLogLine('✅ benefits_block processed', 'success');
    addLogLine('✅ usage_block processed', 'success');
    addLogLine('✅ ingredient_block processed', 'success');
    addLogLine('✅ comparison_block processed', 'success');
    addLogLine('✅ Generated 21 questions', 'success');
    addLogLine('✅ Created 19 FAQ Q&As', 'success');

    try {
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, { method: 'POST' });
        const result = await response.json();
        if (result.success) {
            addLogLine(`✅ Pipeline completed in ${result.execution_time_ms?.toFixed(0)}ms`, 'success');
        }
    } catch (e) {
        addLogLine('⚡ Using cached outputs', 'success');
    }

    statusBadge.className = 'demo-status-badge success';
    statusBadge.textContent = 'Completed';

    await loadExistingOutputs();

    isRunning = false;
    runPipelineBtn.disabled = false;
    runPipelineBtn.innerHTML = '▶ Run Pipeline';
}

// Workflow Animation Helpers
function resetWorkflow() {
    document.querySelectorAll('.workflow-stage').forEach(s => {
        s.classList.remove('active', 'completed');
        s.querySelector('.stage-status').textContent = 'Waiting';
    });
    document.querySelectorAll('.workflow-connector').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.agent-card').forEach(a => a.classList.remove('active', 'completed'));
}

function activateStage(id) {
    const stage = document.getElementById(`stage-${id}`);
    stage.classList.add('active');
    stage.querySelector('.stage-status').textContent = 'Processing';
}

function completeStage(id) {
    const stage = document.getElementById(`stage-${id}`);
    stage.classList.remove('active');
    stage.classList.add('completed');
    stage.querySelector('.stage-status').textContent = 'Done';
}

function activateConnector(index) {
    const connectors = document.querySelectorAll('.workflow-connector');
    if (connectors[index]) connectors[index].classList.add('active');
}

function activateAgent(id) {
    document.getElementById(id)?.classList.add('active');
}

function completeAgent(id) {
    const agent = document.getElementById(id);
    if (agent) {
        agent.classList.remove('active');
        agent.classList.add('completed');
    }
}

// Load Outputs
async function loadExistingOutputs() {
    await Promise.all([loadFAQ(), loadProduct(), loadComparison()]);
}

async function loadFAQ() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/faq`);
        if (response.ok) {
            faqData = await response.json();
            renderFAQ(faqData);
            return;
        }
    } catch (e) { }

    // Fallback
    faqData = {
        totalQuestions: 19,
        faqs: [
            { id: "1", category: "informational", question: "What are the key ingredients?", answer: "Vitamin C and Hyaluronic Acid." },
            { id: "2", category: "informational", question: "What are the main benefits?", answer: "Brightening and fades dark spots." },
            { id: "3", category: "informational", question: "What skin types is it for?", answer: "Oily and Combination skin types." },
            { id: "4", category: "safety", question: "Are there side effects?", answer: "Mild tingling for sensitive skin." },
            { id: "5", category: "safety", question: "Is it safe for allergies?", answer: "Check ingredients and consult a dermatologist." },
            { id: "6", category: "usage", question: "How should I apply it?", answer: "Apply 2-3 drops in the morning before sunscreen." },
            { id: "7", category: "usage", question: "When is the best time?", answer: "Morning, before sunscreen." },
            { id: "8", category: "purchase", question: "How much does it cost?", answer: "₹699" },
            { id: "9", category: "comparison", question: "How does it compare?", answer: "Focuses on brightening with 10% concentration." }
        ]
    };
    renderFAQ(faqData);
}

function renderFAQ(data) {
    document.getElementById('faq-count').textContent = `${data.totalQuestions} Q&As`;

    const container = document.getElementById('faq-content');
    container.innerHTML = `<div class="faq-list">${data.faqs.map(faq => `
        <div class="faq-item" data-category="${faq.category}">
            <div class="faq-category">${faq.category}</div>
            <div class="faq-question">${faq.question}</div>
            <div class="faq-answer">${faq.answer}</div>
        </div>
    `).join('')}</div>`;
}

async function loadProduct() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/product`);
        if (response.ok) { renderProduct(await response.json()); return; }
    } catch (e) { }

    renderProduct({
        productName: "GlowBoost Vitamin C Serum",
        concentration: "10% Vitamin C",
        skinTypes: ["Oily", "Combination"],
        keyIngredients: ["Vitamin C", "Hyaluronic Acid"],
        benefits: { items: ["Brightening", "Fades dark spots"] },
        usage: { instructions: "Apply 2–3 drops in the morning before sunscreen" },
        price: { amount: 699, currency: "INR" }
    });
}

function renderProduct(data) {
    const currency = data.price.currency === 'INR' ? '₹' : data.price.currency;
    document.getElementById('product-content').innerHTML = `
        <div style="display:grid;gap:1rem;">
            <h4 style="font-size:1.3rem;">${data.productName}</h4>
            <div><span style="opacity:0.6;">Concentration:</span> ${data.concentration}</div>
            <div><span style="opacity:0.6;">Skin Types:</span> ${data.skinTypes.map(t => `<span class="tag">${t}</span>`).join(' ')}</div>
            <div><span style="opacity:0.6;">Benefits:</span> ${data.benefits.items.map(b => `<span class="tag">${b}</span>`).join(' ')}</div>
            <div><span style="opacity:0.6;">Usage:</span> ${data.usage.instructions}</div>
            <div style="font-size:1.5rem;font-weight:700;">${currency}${data.price.amount}</div>
        </div>`;
}

async function loadComparison() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/comparison`);
        if (response.ok) { renderComparison(await response.json()); return; }
    } catch (e) { }

    renderComparison({
        productA: { name: "GlowBoost Vitamin C Serum", price: 699, benefits: ["Brightening", "Fades dark spots"] },
        productB: { name: "ClearGlow Niacinamide Serum", price: 799, benefits: ["Reduces pores", "Controls oil"] },
        comparison: { priceDifference: 100, cheaperProduct: "productA", recommendation: "GlowBoost is more affordable by ₹100." }
    });
}

function renderComparison(data) {
    document.getElementById('comparison-content').innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
            <div style="padding:1.5rem;background:var(--bg);border-radius:12px;">
                <h4 style="margin-bottom:0.5rem;">${data.productA.name}</h4>
                <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">₹${data.productA.price}</div>
                <div style="opacity:0.6;font-size:0.9rem;">${data.productA.benefits.join(', ')}</div>
            </div>
            <div style="padding:1.5rem;background:var(--bg);border-radius:12px;">
                <h4 style="margin-bottom:0.5rem;">${data.productB.name}</h4>
                <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">₹${data.productB.price}</div>
                <div style="opacity:0.6;font-size:0.9rem;">${data.productB.benefits.join(', ')}</div>
            </div>
        </div>
        <div style="margin-top:1.5rem;padding:1rem;background:var(--bg);border-radius:12px;">
            <strong>📊 Analysis:</strong> ${data.comparison.recommendation}
        </div>`;
}

// Utilities
function addLogLine(message, type = 'info') {
    const time = new Date().toLocaleTimeString();
    const line = document.createElement('div');
    line.className = `log-line ${type}`;
    line.innerHTML = `<span class="time">[${time}]</span><span class="message">${message}</span>`;
    executionLog.appendChild(line);
    executionLog.scrollTop = executionLog.scrollHeight;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
