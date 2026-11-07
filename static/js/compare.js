/**
 * College Darpan — Comparison Page Controller
 */

async function removeComparedCollege(collegeId) {
  if (await CompareManager.remove(Number(collegeId))) {
    window.location.href = '/compare';
  }
}

async function addCollegeToCompareFromSelect() {
  const select = document.getElementById('addCollegeSelect');
  if (!select || !select.value) return;

  const option = select.options[select.selectedIndex];
  if (await CompareManager.add(Number(select.value), option.text)) {
    window.location.href = '/compare';
  }
}

async function clearAllComparedColleges() {
  if (await CompareManager.clear()) {
    window.location.href = '/compare';
  }
}

async function askChatbotToExplainComparison(collegeNames) {
  const modal = document.getElementById('aiComparisonModal');
  const content = document.getElementById('aiComparisonSummaryContent');
  if (!modal || !content) return;

  modal.style.display = 'flex';
  content.innerHTML = '<div style="padding: 20px; text-align: center; color: #6B7280;">Darpan AI is analyzing academic, financial, and placement trade-offs...</div>';

  const query = `Compare ${collegeNames.join(' and ')}`;
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query })
    });
    const data = await res.json();
    if (data.success) {
      content.innerHTML = formatChatMessage(data.message);
    } else {
      content.innerHTML = '<p>Unable to generate comparison summary at this time.</p>';
    }
  } catch (err) {
    content.innerHTML = '<p>Connection error. Please try again.</p>';
  }
}

function closeAiComparisonModal() {
  const modal = document.getElementById('aiComparisonModal');
  if (modal) modal.style.display = 'none';
}
