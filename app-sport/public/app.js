"use strict";
// ---------- Données ----------
const DAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const MET = 5.0; // musculation intensité modérée (Compendium of Physical Activities) : kcal = MET × kg × heures
const ACT = { sedentaire: 1.2, leger: 1.375, modere: 1.55, intense: 1.725 };
const GOAL = { perte: -400, maintien: 0, prise: 300 };
const LEVEL = { debutant: 1, intermediaire: 1, avance: 1 };

// ---------- Stockage ----------
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { alert("Stockage plein ou bloqué : donnée non sauvegardée."); } },
  del(k) { try { localStorage.removeItem(k); } catch {} },
};
let profile = { weight: 70, height: 175, age: 30, sex: "m", activity: "modere", goal: "maintien", level: "debutant", equip: "salle complète", ...store.get("profile", {}) };
let plan = store.get("plan", Object.fromEntries(DAYS.map((d) => [d, []])));      // { Lundi: [{name,sets,reps,restSec,note}] }
let log = store.get("log", { sessions: [], meals: [] });
let advice = store.get("advice", {});                                           // { Lundi: {restDays, bodyNote} }
const save = () => { store.set("profile", profile); store.set("plan", plan); store.set("log", log); store.set("advice", advice); };

// ---------- Calculs ----------
const dayKey = (d = new Date()) => { const o = new Date(d - d.getTimezoneOffset() * 60000); return o.toISOString().slice(0, 10); };
const todayIdx = () => (new Date().getDay() + 6) % 7;
const bmr = (p) => Math.round(10 * p.weight + 6.25 * p.height - 5 * p.age + (p.sex === "m" ? 5 : -161)); // Mifflin-St Jeor
const target = (p) => Math.round(bmr(p) * ACT[p.activity] + GOAL[p.goal]);
const burn = (min) => Math.round(MET * profile.weight * (min / 60));
const weekStart = () => { const d = new Date(); d.setDate(d.getDate() - todayIdx()); return dayKey(d); };
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const $ = (s) => document.querySelector(s);

// ---------- Musique ----------
const audio = new Audio();
let tracks = [], current = -1, ctx = null, beat = null;
fetch("music/playlist.json").then((r) => r.json()).then((t) => { tracks = t; }).catch(() => {});
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
    const spb = 60 / bpm / 2;
    while (next < ctx.currentTime + 0.2) {
      if (step % 2 === 0) hit(next, 140, 0.18, 0.9);
      if (step % 4 === 2) hit(next, 220, 0.1, 0.25, "square");
      if (step % 2 === 1) hit(next, 6000, 0.03, 0.08, "square");
      next += spb; step++;
    }
  };
  beat = setInterval(tick, 50); tick();
  showPlayer(`Beat ${bpm} BPM`, true);
}
function stopBeat() { if (beat) { clearInterval(beat); beat = null; } }

// ---------- Photo (redimensionnée, gardée sur l'appareil) ----------
function loadPhoto(file) {
  return new Promise((ok, ko) => {
    const img = new Image(), url = URL.createObjectURL(file);
    img.onload = () => {
      const k = Math.min(1, 800 / Math.max(img.width, img.height)), c = document.createElement("canvas");
      c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url);
      ok(c.toDataURL("image/jpeg", 0.8));
    };
    img.onerror = () => ko(new Error("Image illisible")); img.src = url;
  });
}

// ---------- Séance ----------
let timer = null, elapsed = 0, active = null, restLeft = 0, restTimer = null;
function startSession(day) {
  const exos = plan[day]; if (!exos.length) return;
  active = { day, exos: exos.map((e) => ({ ...e, done: Array(e.sets).fill(false), reps: e.reps })) };
  elapsed = 0; clearInterval(timer);
  timer = setInterval(() => { elapsed++; paintTimer(); }, 1000);
  startBeat(120); render("session");
}
function paintTimer() {
  const el = $("#clock"); if (!el) return;
  el.textContent = `${String(Math.floor(elapsed / 60)).padStart(2, "0")}:${String(elapsed % 60).padStart(2, "0")}`;
  $("#kcal").textContent = burn(elapsed / 60);
}
function startRest(sec) {
  clearInterval(restTimer); restLeft = sec;
  const paint = () => { const el = $("#rest"); if (el) el.textContent = restLeft > 0 ? `Repos : ${restLeft} s` : "Repos terminé, c'est reparti"; };
  paint();
  restTimer = setInterval(() => {
    restLeft--; paint();
    if (restLeft <= 0) { clearInterval(restTimer); try { navigator.vibrate?.([200, 100, 200]); } catch {} }
  }, 1000);
}
function finishSession() {
  clearInterval(timer); clearInterval(restTimer); stopBeat(); audio.pause(); $("#player").hidden = true;
  const min = Math.max(1, Math.round(elapsed / 60));
  log.sessions.push({ date: dayKey(), day: active.day, min, kcal: burn(min),
    exos: active.exos.map((e) => ({ name: e.name, target: `${e.sets}×${e.reps}`, setsDone: e.done.filter(Boolean).length, reps: e.reps })) });
  save(); active = null; render("week");
}

// ---------- Vues ----------
let openDay = DAYS[todayIdx()], aiBusy = false, aiMsg = "", chat = [];
const views = {
  week() {
    const ws = weekStart(), done = log.sessions.filter((s) => s.date >= ws);
    return `<h1>Ma semaine</h1>
    <div class="card"><b>${done.length} séance(s)</b> · <b>${done.reduce((t, s) => t + s.kcal, 0)} kcal</b> brûlées cette semaine</div>
    ${DAYS.map((d, i) => {
      const n = plan[d].length, isDone = done.some((s) => s.day === d);
      return `<div class="card day ${i === todayIdx() ? "today" : ""} ${isDone ? "done" : ""}">
        <div class="grow"><h2>${d}</h2><div class="mut">${n ? plan[d].map((e) => esc(e.name)).join(" · ") : "Aucun exercice"}</div></div>
        <div class="row">${n ? `<button class="pri" data-start="${d}">Go</button>` : ""}<button data-day="${d}">Éditer</button></div></div>`;
    }).join("")}
    <h2>Historique</h2>
    ${log.sessions.slice(-8).reverse().map((s) => `<div class="card"><b>${esc(s.day)}</b> ${s.date} · ${s.min} min · ${s.kcal} kcal
      <div class="mut">${s.exos.map((e) => `${esc(e.name)} ${e.setsDone}/${e.target}`).join(" · ")}</div></div>`).join("") || '<div class="mut">Aucune séance enregistrée.</div>'}`;
  },
  day() {
    const exos = plan[openDay], adv = advice[openDay];
    return `<h1>${openDay}</h1><button data-back>← Semaine</button>
    <div class="card" style="margin-top:12px">
      ${exos.map((e, i) => `<div class="row" style="padding:6px 0"><div class="grow"><b>${esc(e.name)}</b>
        <div class="mut">${e.sets ? `${e.sets} × ${esc(e.reps)} · repos ${e.restSec} s` : "à calculer par l'IA"}${e.note ? " · " + esc(e.note) : ""}</div></div>
        <button data-delex="${i}">✕</button></div>`).join("") || '<div class="mut">Ajoute tes exercices du jour.</div>'}
      <div class="row" style="margin-top:8px"><input id="newEx" class="grow" placeholder="ex : Développé couché"><button class="pri" data-addex>Ajouter</button></div>
    </div>
    <div class="card"><h2>Calcul par l'IA</h2>
      <div class="mut">Séries, répétitions et repos selon ton poids (${profile.weight} kg), ton niveau (${profile.level}) et ton objectif (${profile.goal}).</div>
      ${store.get("photo", null) ? `<label class="row"><input type="checkbox" id="usePhoto" style="width:auto" checked> Inclure ma photo (envoyée à l'IA pour ce calcul, non conservée sur le serveur)</label>` : '<div class="mut">Ajoute une photo dans Profil pour affiner.</div>'}
      <button class="pri" data-ai style="width:100%;margin-top:8px" ${aiBusy || !exos.length ? "disabled" : ""}>${aiBusy ? "Calcul…" : "Calculer séries, reps et repos"}</button>
      <div class="mut">${esc(aiMsg)}</div>
      ${adv ? `<div style="margin-top:8px">${adv.bodyNote ? `<div class="mut">Photo : ${esc(adv.bodyNote)}</div>` : ""}<div class="mut">Récupération : ${esc(adv.restDays || "")}</div></div>` : ""}
    </div>`;
  },
  session() {
    return `<h1>${esc(active.day)}</h1>
    <div class="card" style="text-align:center"><div class="big" id="clock">00:00</div>
    <div><b id="kcal">0</b> kcal brûlées</div><div class="mut" id="rest">Coche une série pour lancer le repos</div></div>
    ${active.exos.map((e, i) => `<div class="card"><h2>${esc(e.name)}</h2>
      <div class="mut">Objectif : ${e.sets} × ${esc(e.reps)} · repos ${e.restSec} s${e.note ? " · " + esc(e.note) : ""}</div>
      <div class="row" style="margin-top:6px">${e.done.map((d, j) => `<button class="${d ? "pri" : ""}" data-set="${i}:${j}">${j + 1}${d ? " ✓" : ""}</button>`).join("")}</div>
      <label>Reps réalisées</label><input data-reps="${i}" value="${esc(e.reps)}"></div>`).join("")}
    <button class="pri" id="finish" style="width:100%">Terminer et enregistrer</button>`;
  },
  meals() {
    const today = log.meals.filter((m) => m.date === dayKey());
    const eaten = today.reduce((t, m) => t + m.kcal, 0);
    const burned = log.sessions.filter((s) => s.date === dayKey()).reduce((t, s) => t + s.kcal, 0);
    const tgt = target(profile), pct = Math.min(100, (eaten / tgt) * 100);
    return `<h1>Repas & calories</h1>
    <div class="card"><div class="row"><b class="grow">${eaten} / ${tgt} kcal</b><span class="mut">séances : ${burned} kcal</span></div>
    <div class="bar"><i style="width:${pct}%"></i></div>
    <div class="mut">Cible = métabolisme de base (${bmr(profile)}) × activité ${GOAL[profile.goal] ? (GOAL[profile.goal] > 0 ? "+" : "") + GOAL[profile.goal] : "±0"}. Estimation, pas une mesure.</div></div>
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
    return `<h1>Coach IA</h1><div id="chat">${chat.map((m) => `<div class="msg ${m.role}">${esc(m.content)}</div>`).join("") || '<div class="mut">Pose une question sur tes exercices, ta récupération, ta progression.</div>'}</div>
    <div class="row" style="margin-top:8px"><input id="chatIn" class="grow" placeholder="Ton message"><button class="pri" id="send">Envoyer</button></div>`;
  },
  profile() {
    const f = (k, l, t = "number") => `<label>${l}</label><input data-p="${k}" type="${t}" value="${esc(profile[k])}">`;
    const sel = (k, l, o) => `<label>${l}</label><select data-p="${k}">${Object.keys(o).map((x) => `<option ${profile[k] === x ? "selected" : ""}>${x}</option>`).join("")}</select>`;
    const photo = store.get("photo", null);
    return `<h1>Profil</h1><div class="card">${f("weight", "Poids (kg)")}${f("height", "Taille (cm)")}${f("age", "Âge")}
    <label>Sexe</label><select data-p="sex"><option value="m" ${profile.sex === "m" ? "selected" : ""}>Homme</option><option value="f" ${profile.sex === "f" ? "selected" : ""}>Femme</option></select>
    ${sel("level", "Niveau", LEVEL)}${sel("activity", "Activité quotidienne", ACT)}${sel("goal", "Objectif", GOAL)}${f("equip", "Matériel", "text")}</div>
    <div class="card"><h2>Photo de mon corps</h2>
      ${photo ? `<img src="${photo}" style="max-width:100%;border-radius:10px">` : '<div class="mut">Aucune photo.</div>'}
      <div class="row" style="margin-top:8px"><input type="file" id="photoIn" accept="image/*" class="grow">${photo ? '<button data-photo-del>Supprimer</button>' : ""}</div>
      <div class="mut">Gardée uniquement sur cet appareil. Envoyée à l'IA (Anthropic) seulement quand tu coches « Inclure ma photo ».</div></div>
    <div class="card">Métabolisme de base : <b>${bmr(profile)} kcal</b><br>Cible journalière : <b>${target(profile)} kcal</b></div>`;
  },
};

let tab = "week";
function render(t = tab) {
  tab = t; $("#view").innerHTML = views[t]();
  document.querySelectorAll("nav button").forEach((b) => b.classList.toggle("on", b.dataset.tab === (t === "session" || t === "day" ? "week" : t)));
  if (t === "session") paintTimer();
}

// ---------- Événements ----------
async function api(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.error || "Erreur " + r.status); return j;
}
document.querySelector("nav").onclick = (e) => { const t = e.target.dataset.tab; if (t) render(t); };
document.addEventListener("click", async (e) => {
  const d = e.target.dataset;
  if (d.start) startSession(d.start);
  else if (d.day) { openDay = d.day; aiMsg = ""; render("day"); }
  else if (d.back != null) render("week");
  else if (d.addex != null) {
    const v = $("#newEx").value.trim(); if (!v) return;
    plan[openDay].push({ name: v.slice(0, 80), sets: 0, reps: "", restSec: 90, note: "" }); save(); render();
  } else if (d.delex != null) { plan[openDay].splice(+d.delex, 1); save(); render(); }
  else if (d.ai != null) {
    aiBusy = true; aiMsg = ""; const usePhoto = $("#usePhoto")?.checked; render();
    try {
      const r = await api("/api/plan", { day: openDay, exercises: plan[openDay].map((x) => x.name),
        profile: { poids: profile.weight, taille: profile.height, age: profile.age, sexe: profile.sex, niveau: profile.level, objectif: profile.goal, materiel: profile.equip },
        photo: usePhoto ? store.get("photo", null) : null });
      plan[openDay] = r.exercises; advice[openDay] = { restDays: r.restDays, bodyNote: r.bodyNote }; save();
      aiMsg = "Confiance de l'estimation : " + (r.confidence || "?");
    } catch (err) { aiMsg = err.message; }
    aiBusy = false; render();
  } else if (d.set) {
    const [i, j] = d.set.split(":").map(Number), ex = active.exos[i];
    ex.done[j] = !ex.done[j]; const rs = ex.restSec; render();
    if (ex.done[j]) startRest(rs);
  } else if (e.target.id === "finish") finishSession();
  else if (d.beat) startBeat(+d.beat);
  else if (d.track != null) playTrack(+d.track);
  else if (d.photoDel != null) { store.del("photo"); render(); }
  else if (d.del != null) { const t = log.meals.filter((m) => m.date === dayKey()); log.meals.splice(log.meals.indexOf(t[+d.del]), 1); save(); render(); }
  else if (e.target.id === "analyze") {
    const text = $("#mealText").value.trim(); if (!text) return;
    e.target.disabled = true; $("#mealOut").textContent = "Analyse…";
    try { const r = await api("/api/meal", { text }); log.meals.push({ date: dayKey(), text, ...r.total }); save(); render(); }
    catch (err) { $("#mealOut").textContent = err.message; e.target.disabled = false; }
  } else if (e.target.id === "send") {
    const inp = $("#chatIn"), text = inp.value.trim(); if (!text) return;
    chat.push({ role: "user", content: text }); render();
    try {
      const ws = weekStart();
      const r = await api("/api/coach", { messages: chat, context: { profile, plan, seancesSemaine: log.sessions.filter((s) => s.date >= ws) } });
      chat.push({ role: "assistant", content: r.reply });
    } catch (err) { chat.push({ role: "assistant", content: "Erreur : " + err.message }); }
    render();
  }
});
document.addEventListener("change", async (e) => {
  const t = e.target;
  if (t.dataset.reps != null) { active.exos[+t.dataset.reps].reps = t.value; return; }
  if (t.id === "photoIn" && t.files[0]) {
    try { store.set("photo", await loadPhoto(t.files[0])); render(); } catch (err) { alert(err.message); }
    return;
  }
  const k = t.dataset.p; if (!k) return;
  profile[k] = t.type === "number" ? Math.max(1, +t.value || 1) : t.value; save(); render();
});
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
render("week");
