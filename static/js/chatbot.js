/**
 * College Darpan — AI Chatbot Controller (Darpan AI Assistant)
 * Works seamlessly with both the floating widget and the full-page chatbot interface.
 */

// Simple lightweight markdown parser for chat bubbles
function formatChatMessage(text) {
  if (!text) return '';
  
  let formatted = text
    // Escape HTML
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Markdown headers
    .replace(/^### (.*$)/gim, '<div style="font-weight: 800; font-size: 1.05rem; margin: 0.5rem 0 0.3rem; color: #111827;">$1</div>')
    .replace(/^## (.*$)/gim, '<div style="font-weight: 800; font-size: 1.15rem; margin: 0.6rem 0 0.4rem; color: #111827;">$1</div>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Code tags
    .replace(/`(.*?)`/g, '<code style="background: #F3F4F6; padding: 2px 6px; border-radius: 4px; font-size: 0.85em;">$1</code>')
    // Markdown alerts/callouts
    .replace(/&gt; \[!NOTE\]\s*(.*)/gim, '<div style="background: #E5F2FC; border-left: 3px solid #0284C7; padding: 6px 10px; border-radius: 4px; margin: 6px 0; font-size: 0.85rem; color: #0369A1;"><strong>ℹ Note:</strong> $1</div>')
    .replace(/&gt; \[!TIP\]\s*(.*)/gim, '<div style="background: #FFFBEB; border-left: 3px solid #F59E0B; padding: 6px 10px; border-radius: 4px; margin: 6px 0; font-size: 0.85rem; color: #92400E;"><strong>💡 Tip:</strong> $1</div>')
    .replace(/&gt; \[!IMPORTANT\]\s*(.*)/gim, '<div style="background: #FFF1F2; border-left: 3px solid #E11D48; padding: 6px 10px; border-radius: 4px; margin: 6px 0; font-size: 0.85rem; color: #9F1239;"><strong>⚠ Important:</strong> $1</div>')
    // Unordered list items
    .replace(/^\• (.*$)/gim, '<div style="margin-left: 14px; margin-bottom: 4px;">• $1</div>')
    .replace(/^- (.*$)/gim, '<div style="margin-left: 14px; margin-bottom: 4px;">• $1</div>')
    // Line breaks
    .replace(/\n\n/g, '<div style="height: 8px;"></div>')
    .replace(/\n/g, '<br/>');

  // Format simple markdown tables if present
  if (formatted.includes('|')) {
    formatted = formatSimpleTables(formatted);
  }

  return formatted;
}

function formatSimpleTables(html) {
  // Convert markdown pipes into clean responsive styled table
  const lines = html.split('<br/>');
  let inTable = false;
  let tableHtml = '<div style="overflow-x:auto; margin: 8px 0;"><table style="width:100%; border-collapse:collapse; font-size:0.85rem; border:1px solid #E5E7EB;">';
  let nonTableLines = [];

  for (let line of lines) {
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      inTable = true;
      if (line.includes('---')) continue; // Skip separator line
      const cells = line.split('|').map(c => c.trim()).filter((c, i, arr) => i > 0 && i < arr.length - 1);
      tableHtml += '<tr>';
      cells.forEach(cell => {
        tableHtml += `<td style="padding: 6px 10px; border: 1px solid #E5E7EB;">${cell}</td>`;
      });
      tableHtml += '</tr>';
    } else {
      if (inTable) {
        tableHtml += '</table></div>';
        nonTableLines.push(tableHtml);
        inTable = false;
        tableHtml = '<div style="overflow-x:auto; margin: 8px 0;"><table style="width:100%; border-collapse:collapse; font-size:0.85rem; border:1px solid #E5E7EB;">';
      }
      nonTableLines.push(line);
    }
  }
  if (inTable) {
    tableHtml += '</table></div>';
    nonTableLines.push(tableHtml);
  }
  return nonTableLines.join('<br/>');
}

// Chat Client Class
class DarpanChat {
  constructor(containerId, inputId, sendBtnId, isPopup = false) {
    this.container = document.getElementById(containerId);
    this.input = document.getElementById(inputId);
    this.sendBtn = document.getElementById(sendBtnId);
    this.isPopup = isPopup;
    this.init();
  }

  init() {
    if (!this.input || !this.sendBtn) return;

    this.sendBtn.addEventListener('click', () => this.sendMessage());
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.sendMessage();
      }
    });
  }

  appendMessage(text, sender = 'user', actions = [], colleges = [], source = null) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble chat-bubble-${sender}`;
    
    if (sender === 'assistant') {
      bubble.innerHTML = `<div>${formatChatMessage(text)}</div>`;

      // Render college cards if provided
      if (colleges && colleges.length > 0) {
        const cards = document.createElement('div');
        cards.style.cssText = 'margin-top:10px;display:flex;flex-direction:column;gap:6px;';
        colleges.forEach(col => {
          const card = document.createElement('div');
          card.style.cssText = 'background:#FDF4F7;border:1px solid #F6C9D5;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;';
          const details = document.createElement('div');
          const name = document.createElement('strong');
          name.style.cssText = 'color:#111827;font-size:0.88rem;';
          name.textContent = col.name || '';
          const metadata = document.createElement('div');
          metadata.style.cssText = 'font-size:0.775rem;color:#6B7280;';
          metadata.textContent = [col.district, col.institution_type].filter(Boolean).join(' • ');
          details.append(name, metadata);
          const link = document.createElement('a');
          link.href = `/colleges/${encodeURIComponent(col.id)}`;
          link.className = 'btn btn-sm btn-soft-pink';
          link.style.cssText = 'text-decoration:none;white-space:nowrap;';
          link.textContent = 'View Profile';
          card.append(details, link);
          cards.appendChild(card);
        });
        bubble.appendChild(cards);
      }

      // Render source indicator
      if (source) {
        const sourceNote = document.createElement('div');
        sourceNote.style.cssText = 'font-size:0.72rem;color:#9CA3AF;margin-top:8px;border-top:1px dashed #E5E7EB;padding-top:4px;';
        sourceNote.textContent = `🔍 ${source}`;
        bubble.appendChild(sourceNote);
      }

      // Render quick action pills
      if (actions && actions.length > 0) {
        const actionList = document.createElement('div');
        actionList.style.marginTop = '8px';
        actions.forEach(act => {
          const button = document.createElement('button');
          button.className = 'quick-action-pill';
          button.textContent = act;
          button.addEventListener('click', () => sendChatPrompt(act));
          actionList.appendChild(button);
        });
        bubble.appendChild(actionList);
      }
    } else {
      bubble.textContent = text;
    }

    this.container.appendChild(bubble);
    this.scrollToBottom();
  }

  showTypingIndicator() {
    const id = 'typingIndicator_' + Date.now();
    const ind = document.createElement('div');
    ind.id = id;
    ind.className = 'chat-bubble chat-bubble-assistant';
    ind.innerHTML = '<span style="color:#6B7280; font-size:0.85rem;">Darpan AI is searching verified records...</span>';
    this.container.appendChild(ind);
    this.scrollToBottom();
    return id;
  }

  removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  scrollToBottom() {
    this.container.scrollTop = this.container.scrollHeight;
  }

  async sendMessage(customText = null) {
    const text = (customText || this.input.value).trim();
    if (!text) return;

    if (!customText) this.input.value = '';
    this.appendMessage(text, 'user');

    const typingId = this.showTypingIndicator();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: 'user_session' })
      });
      const data = await response.json();
      this.removeTypingIndicator(typingId);

      if (data.success) {
        this.appendMessage(data.message, 'assistant', data.suggested_actions, data.matched_colleges, data.source);
      } else {
        this.appendMessage('Sorry, an error occurred while searching records. Please try again.', 'assistant');
      }
    } catch (err) {
      this.removeTypingIndicator(typingId);
      this.appendMessage('Connection error. Please verify the Flask server is running locally.', 'assistant');
    }
  }
}

// Global quick prompt dispatcher
let activeChatInstance = null;

function sendChatPrompt(promptText) {
  if (activeChatInstance) {
    activeChatInstance.sendMessage(promptText);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Check if on dedicated /chatbot page
  if (document.getElementById('fullChatMessages')) {
    activeChatInstance = new DarpanChat('fullChatMessages', 'fullChatInput', 'fullChatSendBtn', false);
  } 
  // Floating popup chat
  if (document.getElementById('floatingChatMessages')) {
    const popupChat = new DarpanChat('floatingChatMessages', 'floatingChatInput', 'floatingChatSendBtn', true);
    if (!activeChatInstance) activeChatInstance = popupChat;
  }
});
