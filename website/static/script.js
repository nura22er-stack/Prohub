const API_BASE = 'http://localhost:5000/api';

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('app-count').textContent = stats.total_apps;
        document.getElementById('user-count').textContent = stats.total_users;
        document.getElementById('download-count').textContent = stats.total_downloads;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadTopApps() {
    try {
        const response = await fetch(`${API_BASE}/top-apps?limit=6`);
        const data = await response.json();
        
        const container = document.getElementById('top-apps');
        container.innerHTML = '';
        
        data.apps.forEach(app => {
            const card = document.createElement('div');
            card.className = 'app-card glass';
            card.innerHTML = `
                <div class="app-icon">📦</div>
                <div class="app-name">${app.name}</div>
                <div class="app-downloads">📥 ${app.downloads}</div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading apps:', error);
    }
}

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadTopApps();
    
    // Reload stats every 30 seconds
    setInterval(loadStats, 30000);
});

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
