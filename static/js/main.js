/**
 * College Darpan — Main Frontend Logic
 * Handles navigation, shortlisting, comparisons state, and UI helpers.
 */

// Toast notification helper
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast-container');
  if (existing) existing.remove();

  const container = document.createElement('div');
  container.className = 'toast-container';
  container.style.cssText = `
    position: fixed;
    top: 85px;
    right: 20px;
    z-index: 9999;
    background: #FFFFFF;
    border-left: 4px solid ${type === 'success' ? '#10B981' : type === 'warning' ? '#F59E0B' : '#3B82F6'};
    border-radius: 8px;
    padding: 12px 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    font-size: 0.9rem;
    font-weight: 600;
    color: #1F2937;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
  `;
  container.innerHTML = `<span>${type === 'success' ? '✓' : 'ℹ'}</span> ${message}`;
  document.body.appendChild(container);

  setTimeout(() => {
    container.style.opacity = '0';
    container.style.transform = 'translateY(-10px)';
    setTimeout(() => container.remove(), 300);
  }, 3200);
}

// Comparison selection is stored in the signed Flask session. localStorage is
// read only once to migrate selections created by the older client version.
const CompareManager = {
  async request(action, payload = {}) {
    const response = await fetch('/api/compare', {
      method: action ? 'POST' : 'GET',
      headers: action ? { 'Content-Type': 'application/json' } : {},
      credentials: 'same-origin',
      body: action ? JSON.stringify({ action, ...payload }) : undefined
    });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || 'Unable to update comparison.');
    this.updateBadge(data.count);
    return data;
  },
  async initialize() {
    try {
      let data = await this.request();
      let legacyIds = [];
      try {
        legacyIds = JSON.parse(localStorage.getItem('darpan_compare_ids') || '[]');
      } catch { /* Ignore malformed legacy browser state. */ }

      if (data.count === 0 && Array.isArray(legacyIds) && legacyIds.length) {
        try {
          data = await this.request('set', { ids: legacyIds.slice(0, 4) });
        } catch (error) {
          console.warn('Discarding an invalid legacy comparison selection:', error);
        }
      }
      localStorage.removeItem('darpan_compare_ids');
      this.updateBadge(data.count);
    } catch (error) {
      // Keep the server-rendered badge visible if the API is temporarily unavailable.
      console.error('Could not load comparison selection:', error);
    }
  },
  async add(collegeId, collegeName) {
    try {
      const data = await this.request('add', { id: collegeId });
      if (data.already_selected) {
        showToast(`${collegeName || 'College'} is already selected for comparison.`, 'warning');
      } else {
        showToast(`Added ${collegeName || 'College'} to comparison. (${data.count}/4)`, 'success');
      }
      return true;
    } catch (error) {
      showToast(error.message, 'warning');
      return false;
    }
  },
  async remove(collegeId) {
    try {
      await this.request('remove', { id: collegeId });
      return true;
    } catch (error) {
      showToast(error.message, 'warning');
      return false;
    }
  },
  async clear() {
    try {
      await this.request('clear');
      return true;
    } catch (error) {
      showToast(error.message, 'warning');
      return false;
    }
  },
  updateBadge(count) {
    const serverCount = Number.isInteger(count) ? count : null;
    const badges = document.querySelectorAll('.compare-count-badge');
    badges.forEach(badge => {
      const shownCount = serverCount === null ? Number(badge.textContent) || 0 : serverCount;
      badge.textContent = shownCount;
      badge.classList.toggle('is-visible', shownCount > 0);
    });
  },
  async openComparison() {
    try {
      const data = await this.request();
      if (data.count < 2) {
        showToast('Add at least 2 colleges to compare them.', 'warning');
        return;
      }
      window.location.href = '/compare';
    } catch (error) {
      showToast(error.message, 'warning');
    }
  }
};

// Shortlist in localStorage
const ShortlistManager = {
  getStored() {
    try {
      return JSON.parse(localStorage.getItem('darpan_shortlist') || '[]');
    } catch {
      return [];
    }
  },
  toggle(collegeId, collegeName) {
    let list = this.getStored();
    const index = list.indexOf(collegeId);
    if (index > -1) {
      list.splice(index, 1);
      showToast(`Removed from your shortlisted colleges.`, 'info');
    } else {
      list.push(collegeId);
      showToast(`Saved ${collegeName || 'College'} to your shortlist!`, 'success');
    }
    localStorage.setItem('darpan_shortlist', JSON.stringify(list));
    this.updateButtons();
  },
  updateButtons() {
    const list = this.getStored();
    document.querySelectorAll('.btn-shortlist').forEach(btn => {
      const cid = parseInt(btn.dataset.collegeId);
      if (list.includes(cid)) {
        btn.innerHTML = '★ Saved';
        btn.classList.add('saved');
      } else {
        btn.innerHTML = '☆ Shortlist';
        btn.classList.remove('saved');
      }
    });
  }
};

// Toggle Floating Chatbot Popup
function toggleFloatingChat() {
  const popup = document.getElementById('floatingChatPopup');
  if (!popup) return;
  const isShown = popup.style.display === 'flex';
  popup.style.display = isShown ? 'none' : 'flex';
  if (!isShown) {
    const input = document.getElementById('floatingChatInput');
    if (input) input.focus();
  }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  CompareManager.updateBadge();
  CompareManager.initialize();
  ShortlistManager.updateButtons();

  // Mobile menu toggle
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');
  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
      navLinks.style.flexDirection = 'column';
      navLinks.style.position = 'absolute';
      navLinks.style.top = '72px';
      navLinks.style.left = '0';
      navLinks.style.width = '100%';
      navLinks.style.background = '#FFFFFF';
      navLinks.style.padding = '1.5rem';
      navLinks.style.boxShadow = 'var(--shadow-md)';
    });
  }
});
