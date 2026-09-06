(function () {
  'use strict';

  const tg = window.Telegram && window.Telegram.WebApp;

  if (tg) {
    tg.ready();
    tg.expand();
    if (tg.setHeaderColor) tg.setHeaderColor('#07070c');
    if (tg.setBackgroundColor) tg.setBackgroundColor('#07070c');
  }

  const CASES = {
    common: { icon: '📦', min: 1, max: 1, name: 'Классик' },
    rare:   { icon: '🔷', min: 1, max: 2, name: 'Мистика' },
    legend: { icon: '👑', min: 2, max: 3, name: 'Легенда' },
  };

  const ITEMS = ['🎁', '🚀', '👾', '💎', '🔥', '🐉', '⚡', '🪙', '🕯️', '🗝️'];
  const state = {
    user: (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) || null,
    balance: Number(localStorage.getItem('gs_balance') || 0),
    opened: Number(localStorage.getItem('gs_opened') || 0),
  };

  const $ = (id) => document.getElementById(id);
  const balanceEl = $('balance');
  const pillOpened = $('pillOpened');
  const footStats = $('footStats');
  const scene = $('scene');
  const phaseBox = $('phaseBox');
  const phaseRoll = $('phaseRoll');
  const phaseWin = $('phaseWin');
  const case3d = $('case3d');
  const track = $('track');
  const winNum = $('winNum');
  const orbit = $('orbit');

  const haptic = (type) => { try { tg && tg.HapticFeedback && tg.HapticFeedback[type](); } catch (e) {} };

  function save() {
    localStorage.setItem('gs_balance', String(state.balance));
    localStorage.setItem('gs_opened', String(state.opened));
  }

  function render() {
    balanceEl.textContent = String(state.balance);
    pillOpened.textContent = state.opened;
    footStats.textContent = state.opened ? `Открытых кейсов: ${state.opened}` : 'Выполни задание в боте, чтобы открыть кейс';
  }

  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

  // ---------- open sequence ----------
  function startOpen(key) {
    const c = CASES[key];
    if (!c) return;

    haptic('impactOccurred', 'light');
    scene.classList.remove('hidden');
    phaseBox.classList.remove('hidden');
    phaseRoll.classList.add('hidden');
    phaseWin.classList.add('hidden');
    const stopCase = (el) => (el.style.animation = 'none');
    case3d.textContent = c.icon;
    case3d.style.animation = '';

    $('pulseLabel').textContent = 'Открываем...';

    setTimeout(() => { case3d.classList.add('burst'); }, 640);
    setTimeout(() => { phaseBox.classList.add('hidden'); roll(c); }, 900);
  }

  function roll(c) {
    haptic('notificationOccurred', 'success');
    phaseRoll.classList.remove('hidden');
    track.innerHTML = '';
    const cells = [];
    for (let i = 0; i < 5; i++) {
      const el = document.createElement('div');
      el.className = 'cell' + (i === 3 ? ' slow' : i === 4 ? ' slower ' : '');
      el.textContent = randomItem();
      track.appendChild(el);
      cells.push(el);
    }
    const tick = setInterval(() => {
      cells.forEach((el) => { if (Math.random() < 0.65) el.textContent = randomItem(); });
    }, 170);

    setTimeout(() => {
      clearInterval(tick);
      phaseRoll.classList.add('hidden');
      win(rand(c.min, c.max));
    }, 2000);
  }

  function win(stars) {
    haptic('notificationOccurred', 'success');
    phaseWin.classList.remove('hidden');
    orbit.style.animation = '';

    const target = stars;
    let v = 0;
    const step = () => {
      v += Math.max(1, Math.ceil((target - v) / 4));
      if (v > target) v = target;
      winNum.textContent = String(v);
      if (v < target) { requestAnimationFrame(step); }
      else {
        state.balance += target;
        state.opened += 1;
        save();
        render();
        sendSpin(c, target);
      }
    };
    requestAnimationFrame(step);
  }

  function randomItem() { return ITEMS[Math.floor(Math.random() * ITEMS.length)]; }

  function sendSpin(c, stars) {
    try {
      if (tg && typeof tg.sendData === 'function') {
        tg.sendData(JSON.stringify({ action: 'spin', case: c.name, stars, init: tg.initData || '' }));
      }
    } catch (e) {}
  }

  $('winClose').onclick = () => { haptic('impactOccurred', 'light'); scene.classList.add('hidden'); };

  document.querySelectorAll('.case').forEach((card) => {
    card.querySelector('.open-btn').onclick = (e) => {
      e.stopPropagation();
      startOpen(card.dataset.case);
    };
  });

  render();
})();