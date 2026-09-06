(function () {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;

  // ---------- init ----------
  if (tg) {
    tg.ready();
    tg.expand();
    tg.setHeaderColor && tg.setHeaderColor('#1c1c1e');
    tg.setBackgroundColor && tg.setBackgroundColor('#1c1c1e');
  }

  const CASES = {
    common: { icon: '📦', min: 1, max: 1, label: 'Обычный' },
    rare:   { icon: '🔷', min: 1, max: 2, label: 'Редкий' },
    legend: { icon: '👑', min: 2, max: 3, label: 'Легендарный' },
  };

  const PRIZE_POOL = ['🎁', '🚀', '👾', '💎', '🔥', '🐉', '⚡', '⭐', '⭐', '⭐', '⭐', '⭐'];

  const state = {
    user: (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) || null,
    case: null,
    balance: Number(localStorage.getItem('gs_balance') || 0),
    opened: Number(localStorage.getItem('gs_opened') || 0),
  };

  // ---------- UI refs ----------
  const $ = (id) => document.getElementById(id);
  const balanceEl = $('balance');
  const openedEl = $('opened');
  const overlay = $('overlay');
  const caseClosed = $('caseClosed');
  const rollTrack = $('rollTrack');
  const revealBtn = $('revealBtn');
  const resultPanel = $('resultPanel');
  const resultStars = $('resultStars');
  const closeBtn = $('closeBtn');

  function save() {
    localStorage.setItem('gs_balance', String(state.balance));
    localStorage.setItem('gs_opened', String(state.opened));
  }

  function renderHeader() {
    balanceEl.textContent = `💎 ${state.balance} ⭐`;
    openedEl.textContent = `Открыто: ${state.opened}`;
  }

  // ---------- open flow ----------
  function startOpen(caseKey) {
    state.case = CASES[caseKey];
    caseClosed.textContent = state.case.icon;

    overlay.classList.remove('hidden');
    resultPanel.classList.add('hidden');
    revealBtn.classList.remove('hidden');
    caseClosed.classList.remove('hidden');
    rollTrack.classList.add('hidden');
    rollTrack.innerHTML = '';

    revealBtn.textContent = `Открыть ${state.case.label} кейс!`;
    revealBtn.onclick = () => animate();
  }

  function buildRollCells() {
    const cells = [];
    // один ряд: 5 ячеек с разной скоростью
    for (let i = 0; i < 5; i++) {
      const c = document.createElement('div');
      c.className = 'cell' + (i === 3 ? ' slow' : i === 4 ? ' slower' : '');
      c.textContent = PRIZE_POOL[Math.floor(Math.random() * PRIZE_POOL.length)];
      cells.push(c);
    }
    return cells;
  }

  function animate() {
    caseClosed.classList.add('hidden');
    revealBtn.classList.add('hidden');
    rollTrack.innerHTML = '';
    rollTrack.classList.remove('hidden');

    const cells = buildRollCells();
    cells.forEach((c) => rollTrack.appendChild(c));

    const dec = setInterval(() => {
      // периодически заменяем содержимое (эффект кручения)
      for (let i = 0; i < cells.length; i++) {
        if (Math.random() < 0.6) {
          cells[i].textContent = PRIZE_POOL[Math.floor(Math.random() * PRIZE_POOL.length)];
        }
      }
    }, 180);

    const stars = rand(state.case.min, state.case.max);
    setTimeout(() => {
      clearInterval(dec);
      rollTrack.classList.add('hidden');
      showResult(stars);
    }, 2400);
  }

  function showResult(stars) {
    state.balance += stars;
    state.opened += 1;
    resultStars.textContent = `+${stars}`;
    resultPanel.classList.remove('hidden');
    caseClosed.classList.add('hidden');
    renderHeader();
    save();
    // может не работать без бота, прикроем ошибки
    try {
      if (tg && typeof tg.sendData === 'function') {
        const data = JSON.stringify({
          action: 'spin',
          case: state.case && state.case.label,
          stars: stars,
          init: tg.initData || '',
        });
        tg.sendData(data);
        return; // не закрываем сразу - Telegram сам ответит
      }
    } catch (e) { /* ignore */ }
  }

  function rand(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  closeBtn.onclick = () => overlay.classList.add('hidden');

  // ---------- bind ----------
  document.querySelectorAll('.open-btn').forEach((btn) => {
    btn.onclick = () => startOpen(btn.dataset.case);
  });

  renderHeader();
})();