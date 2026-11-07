/**
 * College Darpan — Recommendation Wizard Interactivity
 * Multi-Category Dynamic Options & Priority Slider Controls
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Category-Aware Exam and Branch Options ---
  const categorySelect = document.getElementById('categorySelectStream');
  const examSelect = document.getElementById('examSelect');
  const branchSelect = document.getElementById('branchSelect');
  const budgetSelect = document.getElementById('budgetInput');

  const categoryConfigs = {
    polytechnic: {
      exams: [
        { value: 'TS POLYCET', text: 'TS POLYCET (10th Class SSC Entrance)' }
      ],
      branches: [
        { value: 'CME', text: 'Computer Engineering (CME)' },
        { value: 'ECE', text: 'Electronics & Communication (ECE)' },
        { value: 'EEE', text: 'Electrical & Electronics (EEE)' },
        { value: 'MECH', text: 'Mechanical Engineering (MECH)' },
        { value: 'CIVIL', text: 'Civil Engineering (CIVIL)' },
        { value: 'AUTO', text: 'Automobile Engineering (AUTO)' },
        { value: 'PKG', text: 'Packaging Technology (PKG)' },
        { value: 'Any', text: 'Any Diploma Branch' }
      ],
      budgets: [
        { value: '', text: 'No Strict Fee Limit' },
        { value: '5000', text: 'Under ₹5,000 (Govt Polytechnic Rate ₹3,800)' },
        { value: '20000', text: 'Under ₹20,000 (Private Subsidized Rate)' }
      ]
    },
    engineering: {
      exams: [
        { value: 'TS EAPCET', text: 'TS EAPCET (Intermediate 1st Year Entry)' },
        { value: 'TS ECET', text: 'TS ECET (Diploma Lateral Entry to 2nd Year)' }
      ],
      branches: [
        { value: 'AIML', text: 'Artificial Intelligence & Machine Learning (AIML)' },
        { value: 'CSE', text: 'Computer Science and Engineering (CSE)' },
        { value: 'CSD', text: 'Data Science (CSD / AIDS)' },
        { value: 'INF', text: 'Information Technology (IT)' },
        { value: 'ECE', text: 'Electronics & Communication (ECE)' },
        { value: 'EEE', text: 'Electrical & Electronics (EEE)' },
        { value: 'MECH', text: 'Mechanical Engineering (MECH)' },
        { value: 'CIVIL', text: 'Civil Engineering (CIVIL)' },
        { value: 'Any', text: 'Any Allied Engineering Branch' }
      ],
      budgets: [
        { value: '', text: 'No Strict Budget Limit' },
        { value: '40000', text: 'Under ₹40,000 (Govt Subsidized Rate)' },
        { value: '100000', text: 'Under ₹1,00,000 / year' },
        { value: '125000', text: 'Under ₹1,25,000 / year' },
        { value: '150000', text: 'Under ₹1,50,000 / year' }
      ]
    },
    pharmacy: {
      exams: [
        { value: 'TS EAPCET', text: 'TS EAPCET (BiPC & MPC Streams)' },
        { value: 'TS POLYCET', text: 'TS POLYCET / Merit (D.Pharm Diploma)' }
      ],
      branches: [
        { value: 'BPH', text: 'Bachelor of Pharmacy (B.Pharm — 4 Years)' },
        { value: 'PHD', text: 'Doctor of Pharmacy (Pharm.D — 6 Years with Hospital Residency)' },
        { value: 'DPH', text: 'Diploma in Pharmacy (D.Pharm — 2 Years)' },
        { value: 'Any', text: 'Any Pharmacy Program' }
      ],
      budgets: [
        { value: '', text: 'No Strict Fee Limit' },
        { value: '50000', text: 'Under ₹50,000 (University Rate)' },
        { value: '90000', text: 'Under ₹90,000 / year' },
        { value: '120000', text: 'Under ₹1,20,000 / year' }
      ]
    }
  };

  function updateCategoryOptions(cat, preserveValues = false) {
    const config = categoryConfigs[cat] || categoryConfigs.engineering;
    
    if (examSelect) {
      const curExam = examSelect.value;
      examSelect.innerHTML = '';
      config.exams.forEach(e => {
        const opt = document.createElement('option');
        opt.value = e.value;
        opt.textContent = e.text;
        if (preserveValues && opt.value === curExam) opt.selected = true;
        examSelect.appendChild(opt);
      });
    }

    if (branchSelect) {
      const curBranch = branchSelect.value;
      branchSelect.innerHTML = '';
      config.branches.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.value;
        opt.textContent = b.text;
        if (preserveValues && opt.value === curBranch) opt.selected = true;
        branchSelect.appendChild(opt);
      });
    }

    if (budgetSelect) {
      const curBudget = budgetSelect.value;
      budgetSelect.innerHTML = '';
      config.budgets.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.value;
        opt.textContent = b.text;
        if (preserveValues && opt.value === curBudget) opt.selected = true;
        budgetSelect.appendChild(opt);
      });
    }
  }

  if (categorySelect) {
    categorySelect.addEventListener('change', (e) => {
      updateCategoryOptions(e.target.value.toLowerCase(), false);
    });

    // Initial run if category is preselected
    const initialCategory = categorySelect.value.toLowerCase() || 'engineering';
    updateCategoryOptions(initialCategory, true);
  }

  // --- Priority Sliders Handling ---
  const sliders = [
    { id: 'w_branch', valId: 'val_branch' },
    { id: 'w_fee', valId: 'val_fee' },
    { id: 'w_placements', valId: 'val_placements' },
    { id: 'w_location', valId: 'val_location' },
    { id: 'w_infra', valId: 'val_infra' }
  ];

  function updateSliderValues() {
    sliders.forEach(s => {
      const input = document.getElementById(s.id);
      const display = document.getElementById(s.valId);
      if (input && display) {
        display.textContent = input.value;
      }
    });
  }

  sliders.forEach(s => {
    const input = document.getElementById(s.id);
    if (input) {
      input.addEventListener('input', updateSliderValues);
    }
  });

  updateSliderValues();

  // Preset Buttons
  const presetButtons = document.querySelectorAll('.priority-preset-btn');
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const preset = btn.dataset.preset;
      if (preset === 'placements') {
        setSliders(3, 2, 5, 2, 3);
      } else if (preset === 'affordability') {
        setSliders(3, 5, 2, 2, 2);
      } else if (preset === 'balanced') {
        setSliders(3, 3, 3, 2, 2.5);
      } else if (preset === 'location') {
        setSliders(3, 2.5, 3, 5, 2);
      }
      updateSliderValues();
    });
  });

  function setSliders(b, fee, p, loc, inf) {
    const elB = document.getElementById('w_branch');
    const elF = document.getElementById('w_fee');
    const elP = document.getElementById('w_placements');
    const elL = document.getElementById('w_location');
    const elI = document.getElementById('w_infra');
    if (elB) elB.value = b;
    if (elF) elF.value = fee;
    if (elP) elP.value = p;
    if (elL) elL.value = loc;
    if (elI) elI.value = inf;
  }
});
