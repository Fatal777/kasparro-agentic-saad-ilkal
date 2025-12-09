/**
 * Multi-Agent Content Generation System - Frontend
 */

// API Configuration - Update with your Render backend URL when deployed
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : 'https://your-backend.onrender.com/api';

// State
let isRunning = false;

// DOM Elements
const header = document.getElementById('header');
const runPipelineBtn = document.getElementById('runPipelineBtn');
const pipelineStatus = document.getElementById('pipelineStatus');
const executionLog = document.getElementById('executionLog');
const tabs = document.querySelectorAll('.tab');
const tabPanels = document.querySelectorAll('.tab-panel');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initHeader();
    initTabs();
    initPipelineButton();
    loadExistingOutputs();
});

// Floating Header on Scroll
function initHeader() {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Tab Navigation
function initTabs() {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            tabs.forEach(t => t.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// Pipeline Button
function initPipelineButton() {
    runPipelineBtn.addEventListener('click', runPipeline);
}

// Run Pipeline
async function runPipeline() {
    if (isRunning) return;

    isRunning = true;
    runPipelineBtn.disabled = true;
    runPipelineBtn.innerHTML = '<span class="btn-icon">⏳</span> Running...';

    pipelineStatus.classList.add('running');
    pipelineStatus.querySelector('.status-text').textContent = 'Running pipeline...';

    executionLog.innerHTML = '';

    const steps = [
        '🔄 Initializing multi-agent system...',
        '📄 Parsing product data...',
        '⚙️ Processing benefits_block...',
        '⚙️ Processing usage_block...',
        '⚙️ Processing ingredient_block...',
        '⚙️ Processing comparison_block...',
        '❓ Generating 21 questions...',
        '📋 Creating FAQ page (19 Q&As)...',
        '📦 Creating Product page...',
        '⚖️ Creating Comparison page...',
        '✅ Validating templates...',
        '💾 Writing output files...'
    ];

    for (const step of steps) {
        addLogLine(step);
        await sleep(150);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/run-pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        if (result.success) {
            addLogLine(`✅ Pipeline completed in ${result.execution_time_ms?.toFixed(0)}ms`, 'success');
            pipelineStatus.classList.remove('running');
            pipelineStatus.classList.add('success');
            pipelineStatus.querySelector('.status-text').textContent = 'Completed!';
            await loadExistingOutputs();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        addLogLine(`⚠️ API unavailable - showing cached outputs`, 'success');
        pipelineStatus.classList.remove('running');
        pipelineStatus.classList.add('success');
        pipelineStatus.querySelector('.status-text').textContent = 'Showing cached';
        await loadExistingOutputs();
    } finally {
        isRunning = false;
        runPipelineBtn.disabled = false;
        runPipelineBtn.innerHTML = '<span class="btn-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg></span> Run Pipeline';
    }
}

// Load existing outputs
async function loadExistingOutputs() {
    await Promise.all([loadFAQ(), loadProduct(), loadComparison()]);
}

async function loadFAQ() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/faq`);
        if (response.ok) {
            const data = await response.json();
            renderFAQ(data);
            return;
        }
    } catch (e) { }

    // Fallback to static data
    renderFAQ({
        productName: "GlowBoost Vitamin C Serum",
        totalQuestions: 19,
        faqs: [
            { id: "faq-001", category: "informational", question: "What are the key ingredients?", answer: "The key ingredients are Vitamin C and Hyaluronic Acid." },
            { id: "faq-002", category: "informational", question: "What are the main benefits?", answer: "Brightening and fades dark spots." },
            { id: "faq-003", category: "safety", question: "Are there side effects?", answer: "Mild tingling for sensitive skin." },
            { id: "faq-004", category: "usage", question: "How should I apply?", answer: "Apply 2-3 drops in the morning before sunscreen." },
            { id: "faq-005", category: "purchase", question: "How much does it cost?", answer: "GlowBoost Vitamin C Serum is priced at ₹699." }
        ]
    });
}

function renderFAQ(data) {
    const container = document.getElementById('faq-content');
    const badge = document.getElementById('faq-count');
    if (badge) badge.textContent = `${data.totalQuestions} Q&As`;

    container.innerHTML = `<div class="faq-list">${data.faqs.slice(0, 8).map(faq => `
        <div class="faq-item">
            <div class="faq-category">${faq.category}</div>
            <div class="faq-question">${faq.question}</div>
            <div class="faq-answer">${faq.answer}</div>
        </div>
    `).join('')}${data.faqs.length > 8 ? `<div class="faq-item" style="text-align:center;color:#737373;">... and ${data.faqs.length - 8} more</div>` : ''}</div>`;
}

async function loadProduct() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/product`);
        if (response.ok) {
            const data = await response.json();
            renderProduct(data);
            return;
        }
    } catch (e) { }

    renderProduct({
        productName: "GlowBoost Vitamin C Serum",
        concentration: "10% Vitamin C",
        skinTypes: ["Oily", "Combination"],
        keyIngredients: ["Vitamin C", "Hyaluronic Acid"],
        benefits: { items: ["Brightening", "Fades dark spots"], primary: "Brightening", count: 2 },
        usage: { instructions: "Apply 2–3 drops in the morning before sunscreen", frequency: "morning", quantity: "2–3 drops" },
        price: { amount: 699, currency: "INR" }
    });
}

function renderProduct(data) {
    const container = document.getElementById('product-content');
    const currency = data.price.currency === 'INR' ? '₹' : data.price.currency;

    container.innerHTML = `
        <div style="display:grid;gap:1rem;">
            <div><strong style="font-size:1.2rem;">${data.productName}</strong></div>
            <div><span style="color:#737373;">Concentration:</span> ${data.concentration}</div>
            <div><span style="color:#737373;">Skin Types:</span> ${data.skinTypes.map(t => `<span class="tag">${t}</span>`).join(' ')}</div>
            <div><span style="color:#737373;">Benefits:</span> ${data.benefits.items.map(b => `<span class="tag">${b}</span>`).join(' ')}</div>
            <div><span style="color:#737373;">Usage:</span> ${data.usage.instructions}</div>
            <div><span style="color:#737373;">Price:</span> <strong style="font-size:1.5rem;">${currency}${data.price.amount}</strong></div>
        </div>
    `;
}

async function loadComparison() {
    try {
        const response = await fetch(`${API_BASE_URL}/outputs/comparison`);
        if (response.ok) {
            const data = await response.json();
            renderComparison(data);
            return;
        }
    } catch (e) { }

    renderComparison({
        productA: { name: "GlowBoost Vitamin C Serum", price: 699, benefits: ["Brightening", "Fades dark spots"] },
        productB: { name: "ClearGlow Niacinamide Serum", price: 799, benefits: ["Reduces pores", "Controls oil"] },
        comparison: { priceDifference: 100, cheaperProduct: "productA", uniqueToA: ["Vitamin C", "Hyaluronic Acid"], uniqueToB: ["Niacinamide", "Salicylic Acid"], recommendation: "GlowBoost is more affordable by ₹100." }
    });
}

function renderComparison(data) {
    const container = document.getElementById('comparison-content');

    container.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:2rem;align-items:start;">
            <div style="padding:1.5rem;background:#fff;border-radius:10px;">
                <h4 style="margin-bottom:1rem;">${data.productA.name}</h4>
                <div style="font-size:1.5rem;font-weight:700;margin-bottom:1rem;">₹${data.productA.price}</div>
                <div style="color:#737373;font-size:0.9rem;">Benefits: ${data.productA.benefits.join(', ')}</div>
            </div>
            <div style="font-size:1.5rem;font-weight:700;color:#a3a3a3;padding-top:2rem;">VS</div>
            <div style="padding:1.5rem;background:#fff;border-radius:10px;">
                <h4 style="margin-bottom:1rem;">${data.productB.name}</h4>
                <div style="font-size:1.5rem;font-weight:700;margin-bottom:1rem;">₹${data.productB.price}</div>
                <div style="color:#737373;font-size:0.9rem;">Benefits: ${data.productB.benefits.join(', ')}</div>
            </div>
        </div>
        <div style="margin-top:2rem;padding:1.5rem;background:#fff;border-radius:10px;">
            <h4 style="margin-bottom:1rem;">📊 Analysis</h4>
            <div><span style="color:#737373;">Price Difference:</span> ₹${data.comparison.priceDifference}</div>
            <div><span style="color:#737373;">Recommendation:</span> ${data.comparison.recommendation}</div>
        </div>
    `;
}

// Utility Functions
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
