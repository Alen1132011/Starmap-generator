(() => {
  const canvas = document.getElementById('sky');
  const ctx = canvas.getContext('2d');
  const scoreEl = document.getElementById('score');
  const timeEl = document.getElementById('time');
  const bestEl = document.getElementById('best');
  const missionEl = document.getElementById('mission');
  const previewEl = document.getElementById('signal-preview');
  const overlay = document.getElementById('sky-message');
  const feedback = document.getElementById('feedback');
  const startButton = document.getElementById('start-button');
  const soundButton = document.getElementById('sound-toggle');

  const signals = [
    {name:'AMBER FOUR-POINT', color:'#f2a65a', shape:'cross', glyph:'✦'},
    {name:'ICE BLUE DIAMOND', color:'#8fd8ed', shape:'diamond', glyph:'◆'},
    {name:'MINT TRIANGLE', color:'#83d6c1', shape:'triangle', glyph:'▲'},
    {name:'VIOLET SIX-POINT', color:'#c2a0f5', shape:'six', glyph:'✶'}
  ];

  let stars = [];
  let score = 0;
  let timeLeft = 45;
  let running = false;
  let timerId = null;
  let soundOn = false;
  let audioContext = null;
  let activeSignal = signals[0];
  let width = 0;
  let height = 0;
  let dpr = 1;
  let lastFrame = 0;

  let best = 0;
  try { best = Number(localStorage.getItem('starHuntBest')) || 0; } catch (_) {}
  bestEl.textContent = String(best).padStart(2, '0');

  function resize() {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = rect.width;
    height = rect.height;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
  }

  function random(min, max) { return Math.random() * (max - min) + min; }
  function choose(list) { return list[Math.floor(Math.random() * list.length)]; }

  function makeStar(signal, x, y) {
    return {
      x, y, radius: random(5, 8), phase: random(0, Math.PI * 2),
      pulse: random(0.7, 1.5), signal,
      isTarget: false
    };
  }

  function newRound() {
    activeSignal = choose(signals);
    const count = Math.min(22 + score, 38);
    stars = [];
    for (let i = 0; i < count; i++) {
      const other = choose(signals.filter(item => item !== activeSignal));
      stars.push(makeStar(other, random(22, width - 22), random(22, height - 22)));
    }
    const target = makeStar(activeSignal, random(30, width - 30), random(30, height - 30));
    target.isTarget = true;
    stars.push(target);
    missionEl.textContent = 'Find the ' + activeSignal.name + ' signal.';
    previewEl.textContent = activeSignal.glyph;
    previewEl.style.color = activeSignal.color;
    draw();
  }

  function drawShape(star, now) {
    const pulse = 0.82 + Math.sin(now / 420 * star.pulse + star.phase) * 0.18;
    const r = star.radius * pulse;
    ctx.save();
    ctx.translate(star.x, star.y);
    ctx.fillStyle = star.signal.color;
    ctx.globalAlpha = 0.72 + pulse * 0.2;
    ctx.shadowColor = star.signal.color;
    ctx.shadowBlur = star.isTarget ? 14 : 7;
    ctx.beginPath();
    if (star.signal.shape === 'diamond') {
      ctx.moveTo(0, -r); ctx.lineTo(r * .78, 0); ctx.lineTo(0, r); ctx.lineTo(-r * .78, 0);
    } else if (star.signal.shape === 'triangle') {
      ctx.moveTo(0, -r); ctx.lineTo(r, r * .8); ctx.lineTo(-r, r * .8);
    } else {
      const points = star.signal.shape === 'six' ? 12 : 8;
      for (let i = 0; i < points; i++) {
        const angle = -Math.PI / 2 + i * Math.PI * 2 / points;
        const radius = i % 2 === 0 ? r : r * .32;
        if (i === 0) ctx.moveTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
        else ctx.lineTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
      }
    }
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  function draw(now = performance.now()) {
    if (!width || !height) return;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#071525';
    ctx.fillRect(0, 0, width, height);

    for (let i = 0; i < 70; i++) {
      const x = (i * 97.3) % width;
      const y = (i * 53.7) % height;
      ctx.fillStyle = `rgba(190,220,240,${0.12 + (i % 4) * 0.08})`;
      ctx.fillRect(x, y, i % 9 === 0 ? 2 : 1, i % 9 === 0 ? 2 : 1);
    }
    stars.forEach(star => drawShape(star, now));
  }

  function animate(now) {
    if (!running) return;
    draw(now);
    requestAnimationFrame(animate);
  }

  function playTone(frequency, duration = 0.09) {
    if (!soundOn) return;
    try {
      audioContext = audioContext || new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      oscillator.frequency.value = frequency;
      oscillator.type = 'sine';
      gain.gain.setValueAtTime(0.055, audioContext.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
      oscillator.connect(gain);
      gain.connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + duration);
    } catch (_) {}
  }

  function startGame() {
    clearInterval(timerId);
    score = 0;
    timeLeft = 45;
    running = true;
    scoreEl.textContent = '00';
    timeEl.textContent = '45';
    overlay.classList.add('hidden');
    feedback.textContent = 'SCAN ACTIVE · FIND THE SIGNAL';
    newRound();
    requestAnimationFrame(animate);
    timerId = setInterval(() => {
      timeLeft -= 1;
      timeEl.textContent = String(timeLeft).padStart(2, '0');
      if (timeLeft <= 0) endGame();
    }, 1000);
  }

  function endGame() {
    running = false;
    clearInterval(timerId);
    const isNewBest = score > best;
    if (isNewBest) {
      best = score;
      bestEl.textContent = String(best).padStart(2, '0');
      try { localStorage.setItem('starHuntBest', String(best)); } catch (_) {}
    }
    overlay.innerHTML = `<div class="message-mark">✳</div><h2>SCAN COMPLETE</h2><p>You caught <strong>${score}</strong> signal${score === 1 ? '' : 's'}. ${isNewBest ? 'New personal best.' : 'Every scan gets easier with practice.'}</p><button id="start-button" class="start-button" type="button">SCAN AGAIN</button>`;
    overlay.classList.remove('hidden');
    document.getElementById('start-button').addEventListener('click', startGame);
    feedback.textContent = 'SESSION ENDED · BEST ' + String(best).padStart(2, '0');
    missionEl.textContent = 'Scan finished. Ready for another round?';
    previewEl.textContent = '✦';
    draw();
  }

  canvas.addEventListener('click', event => {
    if (!running) return;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const hit = [...stars].reverse().find(star => Math.hypot(star.x - x, star.y - y) < 22);
    if (!hit) return;
    if (hit.isTarget) {
      score += 1;
      scoreEl.textContent = String(score).padStart(2, '0');
      feedback.textContent = 'SIGNAL LOCKED · +1 POINT';
      playTone(660, 0.12);
      newRound();
    } else {
      timeLeft = Math.max(0, timeLeft - 2);
      timeEl.textContent = String(timeLeft).padStart(2, '0');
      feedback.textContent = 'FALSE SIGNAL · -2 SECONDS';
      playTone(180, 0.16);
      if (timeLeft <= 0) endGame();
    }
  });

  soundButton.addEventListener('click', () => {
    soundOn = !soundOn;
    soundButton.textContent = 'SOUND: ' + (soundOn ? 'ON' : 'OFF');
    soundButton.setAttribute('aria-pressed', String(soundOn));
    if (soundOn) playTone(520, 0.08);
  });

  startButton.addEventListener('click', startGame);
  window.addEventListener('resize', resize);
  resize();
})();
