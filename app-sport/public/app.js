"use strict";
// ---------- Données ----------
// MET = équivalent métabolique (Compendium of Physical Activities). kcal = MET × poids(kg) × heures.
const WEEK = [
  { d: "Lundi", name: "Haut du corps", met: 5.0, min: 40, bpm: 120, ex: ["Pompes 4×12", "Rowing haltères 4×10", "Développé épaules 3×12", "Dips chaise 3×10", "Gainage 3×45s"] },
  { d: "Mardi", name: "Cardio HIIT", met: 8.5, min: 25, bpm: 150, ex: ["Échauffement 5 min", "Burpees 40s / 20s ×8", "Mountain climbers 40s / 20s ×8", "Retour au calme 5 min"] },
  { d: "Mercredi", name: "Bas du corps", met: 5.5, min: 40, bpm: 125, ex: ["Squats 4×15", "Fentes 3×12/jambe", "Soulevé de terre roumain 4×10", "Pont fessier 3×15", "Mollets 3×20"] },
  { d: "Jeudi", name: "Repos actif", met: 3.0, min: 30, bpm: 100, ex: ["Marche 30 min", "Mobilité 10 min"] },
  { d: "Vendredi", name: "Full body", met: 6.0, min: 45, bpm: 130, ex: ["Thrusters 4×10", "Tractions/Rowing 4×8", "Pompes 3×15", "Fentes sautées 3×12", "Planche 3×1min"] },
  { d: "Samedi", name: "Cardio long", met: 7.0, min: 45, bpm: 140, ex: ["Course 40 min allure modérée", "Étirements 5 min"] },
  { d: "Dimanche", name: "Repos", met: 0, min: 0, bpm: 0, ex: ["Récupération complète"] },
];
const ACT = { sedentaire: 1.2, leger: 1.375, modere: 1.55, intense: 1.725 };
const GOAL = { perte: -400, maintien: 0, prise: 300 };

// ---------- Stockage ----------
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};
let profile = store.get("profile", { weight: 70, height: 175, age: 30, sex: "m", activity: "modere", goal: "maintien" });
let log = store.get("log", { sessions: [], meals: [] });
const save = () => { store.set("profile", profile); store.set("log", log); };

// ---------- Calculs ----------
const dayKey = (d = new Date()) => d.toISOString().slice(0, 10);
const todayIdx = () => (new Date().getDay() + 6) % 7; // lundi = 0
const bmr = (p) => Math.round(10 * p.weight + 6.25 * p.height - 5 * p.age + (p.sex === "m" ? 5 : -161)); // Mifflin-St Jeor
const target = (p) => Math.round(bmr(p) * ACT[p.activity] + GOAL[p.goal]);
const burn = (met, min, kg = profile.weight) => Math.round(met * kg * (min / 60));
const weekStart = () => { const d = new Date(); d.setDate(d.getDate() - todayIdx()); return dayKey(d); };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------- Musique ----------
const audio = new Audio();
let tracks = [], current = -1, ctx = null, beat = null;
fetch("music/playlist.json").then((r) => r.json()).then((t) => { tracks = t; }).catch(() => {});
const $ = (s) => document.querySelector(s);

function showPlayer(name, playing) { $("#player").hidden = false; $("#trackName").textContent = name; $("#play").textContent = playing ? "⏸" : "▶"; }
function playTrack(i) {
  stopBeat(); if (!tracks.length) return;
  current = (i + tracks.length) % tracks.length;
  audio.src = tracks[current].file; audio.play().catch(() => {});
  showPlayer(tracks[current].title, true);
}
audio.addEventListener("ended", () => playTrack(current + 1));
$("#next").onclick = () => playTrack(current + 1);
$("#prev").onclick = () => playTrack(current - 1);
$("#play").onclick = () => {
  if (beat) { stopBeat(); showPlayer("Beat arrêté", false); return; }
  if (audio.src && audio.paused) { audio.play(); showPlayer(tracks[current]?.title || "", true); }
  else { audio.pause(); showPlayer(tracks[current]?.title || "", false); }
};

// Générateur de rythme WebAudio : musique d'entraînement sans fichier, calée sur un BPM.
function startBeat(bpm) {
  stopBeat(); audio.pause();
  ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
  ctx.resume();
  let step = 0, next = ctx.currentTime + 0.05;
  const hit = (t, f, dur, vol, type = "sine") => {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t); if (type === "sine") o.frequency.exponentialRampToValueAtTime(40, t + dur);
    g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g).connect(ctx.destination); o.start(t); o.stop(t + dur);
  };
  const tick = () => {
    const spb = 60 / bpm / 2; // croche
    while (next < ctx.currentTime + 0.2) {
      if (step % 2 === 0) hit(next, 140, 0.18, 0.9);                    // kick sur les temps
      if (step % 4 === 2) hit(next, 220, 0.1, 0.25, "square");          // caisse claire
      if (step % 2 === 1) hit(next, 6000, 0.03, 0.08, "square");        // charleston
      next += spb; step++;
    }
  };
  beat = setInterval(tick, 50); tick();
  showPlayer(`Beat ${bpm} BPM`, true);
}
function stopBeat() { if (beat) { clearInterval(beat); beat = null; } }

// ---------- Séance (chrono + calories) ----------
let timer = null, elapsed = 0, active = null;
function startSession(i) {
  active = WEEK[i]; elapsed = 0; clearInterval(timer);
  timer = setInterval(() => { elapsed++; paintTimer(); }, 1000);
  if (active.bpm) startBeat(active.bpm);
  render("session");
}
function paintTimer() {
  const el = $("#clock"); if (!el) return;
  const m = Math.floor(elapsed / 60), s = elapsed % 60;
  el.textContent = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  $("#kcal").textContent = burn(active.met, elapsed / 60);
}
function finishSession() {
  clearInterval(timer); stopBeat(); audio.pause(); $("#player").hidden = true;
  const min = Math.max(1, Math.round(elapsed / 60));
  log.sessions.push({ date: dayKey(), name: active.name, min, kcal: burn(active.met, min) });
  save(); active = null; render("week");
}

// ---------- Vues ----------
const views = {
  week() {
    const ws = weekStart(), done = log.sessions.filter((s) => s.date >= ws);
    const total = done.reduce((t, s) => t + s.kcal, 0);
    return `<h1>Programme de la semaine</h1>
    <div class="card"><div class="mut">Cette semaine</div><b>${done.length} séance(s)</b> · <b>${total} kcal</b> brûlées</div>
    ${WEEK.map((w, i) => {
      const isDone = done.some((s) => s.name === w.name);
      return `<div class="card day ${i === todayIdx() ? "today" : ""} ${isDone ? "done" : ""}">
        <div class="grow"><h2>${w.d} — ${w.name}</h2><div class="mut">${w.ex.map(esc).join(" · ")}</div>
        ${w.min ? `<div class="mut">≈ ${burn(w.met, w.min)} kcal / ${w.min} min</div>` : ""}</div>
        ${w.min ? `<button class="pri" data-start="${i}">Go</button>` : ""}</div>`;
    }).join("")}`;
  },
  session() {
    return `<h1>${esc(active.name)}</h1>
    <div class="card" style="text-align:center"><div class="big" id="clock">00:00</div>
    <div><b id="kcal">0</b> kcal brûlées</div><div class="mut">MET ${active.met} × ${profile.weight} kg</div></div>
    <div class="card">${active.ex.map((e) => `<div>• ${esc(e)}</div>`).join("")}</div>
    <button class="pri" id="finish" style="width:100%">Terminer la séance</button>`;
  },
  meals() {
    const today = log.meals.filter((m) => m.date === dayKey());
    const eaten = today.reduce((t, m) => t + m.kcal, 0);
    const burned = log.sessions.filter((s) => s.date === dayKey()).reduce((t, s) => t + s.kcal, 0);
    const tgt = target(profile), pct = Math.min(100, (eaten / tgt) * 100);
    return `<h1>Repas & calories</h1>
    <div class="card"><div class="row"><b class="grow">${eaten} / ${tgt} kcal</b><span class="mut">séances : −${burned} kcal</span></div>
    <div class="bar"><i style="width:${pct}%"></i></div>
    <div class="mut">Objectif = métabolisme de base (${bmr(profile)}) × activité ${GOAL[profile.goal] ? (GOAL[profile.goal] > 0 ? "+" : "") + GOAL[profile.goal] : "±0"}. Estimation, pas une mesure.</div></div>
    <div class="card"><label>Décris ton repas (l'IA estime les calories)</label>
    <textarea id="mealText" rows="2" placeholder="2 œufs au plat, 2 tranches de pain complet, 1 banane"></textarea>
    <div class="row" style="margin-top:8px"><button class="pri grow" id="analyze">Analyser avec l'IA</button></div><div id="mealOut" class="mut"></div></div>
    ${today.map((m, i) => `<div class="card row"><div class="grow">${esc(m.text)}<div class="mut">P ${m.protein} · G ${m.carbs} · L ${m.fat}</div></div><b>${m.kcal}</b><button data-del="${i}">✕</button></div>`).join("")}`;
  },
  music() {
    return `<h1>Musique</h1>
    <div class="card"><h2>Beat intégré (sans fichier)</h2><div class="row">
      ${[100, 120, 140, 160].map((b) => `<button data-beat="${b}">${b} BPM</button>`).join("")}</div></div>
    <div class="card"><h2>Tes morceaux</h2><div class="mut">Dépose tes mp3 libres de droits dans <code>public/music/</code> puis liste-les dans <code>playlist.json</code>.</div>
      ${tracks.map((t, i) => `<div class="row" style="margin-top:6px"><button data-track="${i}">▶</button><span class="grow">${esc(t.title)}</span><span class="mut">${esc(t.playlist || "")}</span></div>`).join("")}</div>`;
  },
  coach() {
    return `<h1>Coach IA</h1><div id="chat">${chat.map((m) => `<div class="msg ${m.role}">${esc(m.content)}</div>`).join("") || '<div class="mut">Pose une question sur ton programme, un exercice, ta récupération.</div>'}</div>
    <div class="row" style="margin-top:8px"><input id="chatIn" class="grow" placeholder="Ton message"><button class="pri" id="send">Envoyer</button></div>`;
  },
  profile() {
    const f = (k, l, t = "number") => `<label>${l}</label><input data-p="${k}" type="${t}" value="${profile[k]}">`;
    const sel = (k, l, o) => `<label>${l}</label><select data-p="${k}">${Object.keys(o).map((x) => `<option ${profile[k] === x ? "selected" : ""}>${x}</option>`).join("")}</select>`;
    return `<h1>Profil</h1><div class="card">${f("weight", "Poids (kg)")}${f("height", "Taille (cm)")}${f("age", "Âge")}
    <label>Sexe</label><select data-p="sex"><option value="m" ${profile.sex === "m" ? "selected" : ""}>Homme</option><option value="f" ${profile.sex === "f" ? "selected" : ""}>Femme</option></select>
    ${sel("activity", "Activité quotidienne", ACT)}${sel("goal", "Objectif", GOAL)}</div>
    <div class="card">Métabolisme de base : <b>${bmr(profile)} kcal</b><br>Cible journalière : <b>${target(profile)} kcal</b></div>`;
  },
};

let tab = "week", chat = [];
function render(t = tab) {
  tab = t; $("#view").innerHTML = views[t]();
  document.querySelectorAll("nav button").forEach((b) => b.classList.toggle("on", b.dataset.tab === (t === "session" ? "week" : t)));
  if (t === "session") paintTimer();
}

// ---------- Événements ----------
async function api(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json(); if (!r.ok) throw new Error(j.error || "Erreur"); return j;
}
document.querySelector("nav").onclick = (e) => { const t = e.target.dataset.tab; if (t) render(t); };
document.addEventListener("click", async (e) => {
  const d = e.target.dataset;
  if (d.start != null) startSession(+d.start);
  else if (e.target.id === "finish") finishSession();
  else if (d.beat) startBeat(+d.beat);
  else if (d.track != null) playTrack(+d.track);
  else if (d.del != null) { const t = log.meals.filter((m) => m.date === dayKey()); log.meals.splice(log.meals.indexOf(t[+d.del]), 1); save(); render(); }
  else if (e.target.id === "analyze") {
    const text = $("#mealText").value.trim(); if (!text) return;
    e.target.disabled = true; $("#mealOut").textContent = "Analyse…";
    try {
      const r = await api("/api/meal", { text });
      log.meals.push({ date: dayKey(), text, ...r.total }); save(); render();
    } catch (err) { $("#mealOut").textContent = err.message; e.target.disabled = false; }
  } else if (e.target.id === "send") {
    const inp = $("#chatIn"), text = inp.value.trim(); if (!text) return;
    chat.push({ role: "user", content: text }); render();
    try {
      const ws = weekStart();
      const r = await api("/api/coach", { messages: chat, context: { profile, program: WEEK.map((w) => `${w.d}: ${w.name}`), seancesSemaine: log.sessions.filter((s) => s.date >= ws) } });
      chat.push({ role: "assistant", content: r.reply });
    } catch (err) { chat.push({ role: "assistant", content: "Erreur : " + err.message }); }
    render();
  }
});
document.addEventListener("change", (e) => {
  const k = e.target.dataset.p; if (!k) return;
  profile[k] = e.target.type === "number" ? Math.max(1, +e.target.value || 1) : e.target.value; save(); render();
});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
render("week");
