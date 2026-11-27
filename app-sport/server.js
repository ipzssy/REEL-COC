// Serveur sans dépendance : fichiers statiques + proxy IA (la clé API reste côté serveur).
// Lancement : ANTHROPIC_API_KEY=sk-... node server.js
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const MODEL = process.env.MODEL || "claude-haiku-5-5";
const KEY = process.env.ANTHROPIC_API_KEY;
const PUB = path.join(__dirname, "public");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json",
  ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".wav": "audio/wav", ".png": "image/png", ".svg": "image/svg+xml" };

async function claude(system, messages, maxTokens = 800) {
  if (!KEY) throw Object.assign(new Error("ANTHROPIC_API_KEY manquante côté serveur"), { status: 503 });
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "content-type": "application/json", "x-api-key": KEY, "anthropic-version": "2023-06-01" },
    body: JSON.stringify({ model: MODEL, max_tokens: maxTokens, system, messages }),
  });
  const j = await r.json();
  if (!r.ok) throw Object.assign(new Error(j.error?.message || "Erreur API"), { status: 502 });
  return j.content.map((b) => b.text || "").join("");
}

const MEAL_SYS = `Tu es un nutritionniste. L'utilisateur décrit un repas (français). Estime les quantités raisonnables si absentes.
Réponds UNIQUEMENT par un JSON valide, sans texte autour :
{"items":[{"name":string,"qty":string,"kcal":number,"protein":number,"carbs":number,"fat":number}],"confidence":"haute"|"moyenne"|"faible","note":string}
kcal en kcal, macros en grammes, nombres entiers.`;

const PLAN_SYS = `Tu es un coach de musculation. Tu reçois les exercices choisis par l'utilisateur pour une séance, son profil (poids, taille, âge, sexe, niveau, objectif, matériel) et parfois une photo de son corps.
Pour CHAQUE exercice, dans le même ordre, donne séries, répétitions (nombre, fourchette "8-10" ou durée "45s") et temps de repos entre séries en secondes. Adapte au niveau, à l'objectif et au volume total de la séance (ne dépasse pas ~20 séries au total).
La photo sert uniquement à estimer grossièrement la corpulence et le niveau apparent. Ne donne aucun chiffre de masse grasse, aucun diagnostic. Si la photo est inutilisable, ignore-la. Sois prudent : en cas de doute, charge plus légère.
Réponds UNIQUEMENT par un JSON valide :
{"exercises":[{"name":string,"sets":number,"reps":string,"restSec":number,"note":string}],"restDays":string,"bodyNote":string,"confidence":"haute"|"moyenne"|"faible"}
"restDays" : conseil sur le nombre de jours de repos par semaine et la récupération (2 phrases max). "bodyNote" : une phrase sur ce que tu as retenu de la photo, vide s'il n'y en a pas. "note" : conseil technique court.`;

const route = {
  "/api/meal": async ({ text }) => {
    if (!text || text.length > 500) throw Object.assign(new Error("Description invalide"), { status: 400 });
    const out = await claude(MEAL_SYS, [{ role: "user", content: text }], 600);
    const m = out.match(/\{[\s\S]*\}/);
    if (!m) throw Object.assign(new Error("Réponse IA illisible"), { status: 502 });
    const data = JSON.parse(m[0]);
    data.total = data.items.reduce((t, i) => ({
      kcal: t.kcal + (i.kcal | 0), protein: t.protein + (i.protein | 0),
      carbs: t.carbs + (i.carbs | 0), fat: t.fat + (i.fat | 0) }), { kcal: 0, protein: 0, carbs: 0, fat: 0 });
    return data;
  },
  "/api/plan": async ({ day, exercises, profile, photo }) => {
    if (!Array.isArray(exercises) || !exercises.length || exercises.length > 20) throw Object.assign(new Error("Liste d'exercices invalide"), { status: 400 });
    const names = exercises.map((e) => String(e).slice(0, 80));
    const content = [];
    if (photo) {
      const m = /^data:image\/(jpeg|png);base64,([A-Za-z0-9+/=]+)$/.exec(photo);
      if (!m || m[2].length > 2500000) throw Object.assign(new Error("Photo invalide ou trop lourde"), { status: 400 });
      content.push({ type: "image", source: { type: "base64", media_type: "image/" + m[1], data: m[2] } });
    }
    content.push({ type: "text", text: JSON.stringify({ jour: day, exercices: names, profil: profile }) });
    const out = await claude(PLAN_SYS, [{ role: "user", content }], 1500);
    const m = out.match(/\{[\s\S]*\}/);
    if (!m) throw Object.assign(new Error("Réponse IA illisible"), { status: 502 });
    const d = JSON.parse(m[0]);
    d.exercises = names.map((n, i) => { const e = (d.exercises || [])[i] || {}; return { name: n, sets: Math.min(10, Math.max(1, e.sets | 0 || 3)), reps: String(e.reps || "10"), restSec: Math.min(600, Math.max(15, e.restSec | 0 || 90)), note: String(e.note || "") }; });
    return d;
  },
  "/api/coach": async ({ messages, context }) => {
    if (!Array.isArray(messages) || !messages.length || messages.length > 30) throw Object.assign(new Error("Messages invalides"), { status: 400 });
    const clean = messages.slice(-12).map((m) => ({ role: m.role === "assistant" ? "assistant" : "user", content: String(m.content).slice(0, 1500) }));
    const sys = `Tu es un coach sportif concis et factuel. Réponds en français, en 6 phrases maximum. Pas de conseil médical : en cas de douleur ou pathologie, renvoie vers un médecin.
Contexte utilisateur (JSON) : ${JSON.stringify(context || {}).slice(0, 1500)}`;
    return { reply: await claude(sys, clean, 500) };
  },
};

// Limite par IP des routes IA (elles consomment ta clé API) : 40 requêtes / heure.
const hits = new Map();
function limited(req) {
  const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress || "").split(",")[0].trim();
  const now = Date.now(), arr = (hits.get(ip) || []).filter((t) => now - t < 3600e3);
  arr.push(now); hits.set(ip, arr);
  return arr.length > 40;
}

http.createServer(async (req, res) => {
  const send = (code, body, type = "application/json") => { res.writeHead(code, { "content-type": type }); res.end(typeof body === "string" || Buffer.isBuffer(body) ? body : JSON.stringify(body)); };
  const url = new URL(req.url, "http://x");
  if (req.method === "POST" && route[url.pathname]) {
    if (limited(req)) return send(429, { error: "Trop de requêtes, réessaie plus tard" });
    let raw = ""; for await (const c of req) { raw += c; if (raw.length > 3000000) return send(413, { error: "Trop gros" }); }
    try { send(200, await route[url.pathname](JSON.parse(raw || "{}"))); }
    catch (e) { send(e.status || 500, { error: e.message }); }
    return;
  }
  let p = path.normalize(path.join(PUB, url.pathname === "/" ? "index.html" : decodeURIComponent(url.pathname)));
  if (!p.startsWith(PUB)) return send(403, "Interdit", "text/plain");
  fs.readFile(p, (err, data) => err ? send(404, "Introuvable", "text/plain") : send(200, data, TYPES[path.extname(p)] || "application/octet-stream"));
}).listen(PORT, process.env.HOST || "127.0.0.1", () => console.log(`http://localhost:${PORT}  (IA ${KEY ? "active, modèle " + MODEL : "désactivée : ANTHROPIC_API_KEY absente"})`));
