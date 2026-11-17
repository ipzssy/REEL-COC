// Bot Clash Center : bienvenue, depart, niveaux (XP) et roles de troupes.
const fs = require('fs');
const path = require('path');
const {
  Client, Events, GatewayIntentBits, AttachmentBuilder, EmbedBuilder, ApplicationCommandOptionType,
} = require('discord.js');

const TOKEN = process.env.DISCORD_TOKEN;
const GUILD_ID = '1515604769933099069';
// Message du salon staff-discussion qui contient la banniere (recopiee en local)
const BANNER_CHANNEL_ID = '1542615316629295264';
const BANNER_MESSAGE_ID = '1571514585901568010';
const BANNER_FILE = path.join(__dirname, 'banner.png');

// Niveaux : meme reglages que Koya (courbe MEE6, 15 a 25 XP par message, 1 minute entre deux gains)
const XP_RATE = 1;
const COOLDOWN_MS = 60 * 1000;
const STACK_ROLES = true; // true = on garde les anciens roles de troupes, false = seulement le plus haut
const REWARDS = [
  { level: 1, name: 'Gobelin' },
  { level: 5, name: 'Barbare' },
  { level: 10, name: 'Archère' },
  { level: 20, name: 'Géant' },
  { level: 30, name: 'Sapeur' },
  { level: 40, name: 'Sorcier' },
  { level: 50, name: 'Ballon' },
  { level: 60, name: 'Dragon' },
  { level: 80, name: 'Dragon électrique' },
  { level: 100, name: 'P.E.K.K.A' },
];
const DATA_DIR = path.join(__dirname, 'data');
const DATA_FILE = path.join(DATA_DIR, 'levels.json');

if (!TOKEN) {
  console.error('DISCORD_TOKEN manquant');
  process.exit(1);
}

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers, GatewayIntentBits.GuildMessages],
});

// ---------- Outils ----------
// Enleve accents, lettres stylisees (𝗯𝗶𝗲𝗻𝘃𝗲𝗻𝘂𝗲 -> bienvenue) et majuscules.
const plain = (s) => s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase();
const roleKey = (s) => plain(s).replace(/[^a-z0-9.]/g, '');

function findChannel(guild, envId, word) {
  if (envId && guild.channels.cache.get(envId)) return guild.channels.cache.get(envId);
  return guild.channels.cache.find((c) => c.isTextBased() && !c.isThread() && plain(c.name).includes(word));
}

// ---------- Banniere ----------
async function refreshBanner() {
  try {
    const channel = await client.channels.fetch(BANNER_CHANNEL_ID);
    const message = await channel.messages.fetch(BANNER_MESSAGE_ID);
    const att = message.attachments.first();
    if (!att) throw new Error('aucune piece jointe dans le message de la banniere');
    const res = await fetch(att.url);
    if (!res.ok) throw new Error('telechargement ' + res.status);
    fs.writeFileSync(BANNER_FILE, Buffer.from(await res.arrayBuffer()));
    console.log('Banniere mise a jour');
  } catch (e) {
    console.error('Banniere non mise a jour :', e.message);
  }
}

// ---------- Bienvenue et depart ----------
async function welcome(guild, userId) {
  const channel = findChannel(guild, process.env.WELCOME_CHANNEL_ID, 'bienvenue');
  if (!channel) return console.error('Salon de bienvenue introuvable');
  const files = fs.existsSync(BANNER_FILE) ? [new AttachmentBuilder(BANNER_FILE)] : [];
  await channel.send({
    content: 'Bienvenue <@' + userId + '> ! \u{1F389}',
    files,
    allowedMentions: { users: [userId] },
  });
  console.log('Bienvenue envoye a', userId);
}

async function goodbye(guild, userId) {
  const channel = findChannel(guild, process.env.LEAVE_CHANNEL_ID, 'departs');
  if (!channel) return console.error('Salon des departs introuvable');
  await channel.send({
    content: '\u{1F44B} <@' + userId + '> a quitté **' + guild.name + '**. Au revoir !',
    allowedMentions: { parse: [] },
  });
  console.log('Depart annonce pour', userId);
}

// ---------- Niveaux ----------
let db = { users: {} };
try {
  db = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  if (!db.users) db.users = {};
} catch (e) {
  /* premier lancement */
}
let dirty = false;
function save() {
  if (!dirty) return;
  try {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.writeFileSync(DATA_FILE + '.tmp', JSON.stringify(db));
    fs.renameSync(DATA_FILE + '.tmp', DATA_FILE);
    dirty = false;
  } catch (e) {
    console.error('Sauvegarde impossible :', e.message);
  }
}
setInterval(save, 20 * 1000);
for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    save();
    process.exit(0);
  });
}

const xpForNext = (level) => 5 * level * level + 50 * level + 100;
function levelInfo(totalXp) {
  let level = 0;
  let rest = totalXp;
  while (rest >= xpForNext(level)) {
    rest -= xpForNext(level);
    level++;
  }
  return { level, rest, need: xpForNext(level) };
}

const lastGain = new Map();

async function syncRoles(member, level) {
  const earned = REWARDS.filter((r) => r.level <= level);
  const best = earned[earned.length - 1];
  for (const r of REWARDS) {
    const role = member.guild.roles.cache.find((x) => roleKey(x.name) === roleKey(r.name));
    if (!role) continue;
    const should = STACK_ROLES ? r.level <= level : best && r.name === best.name;
    const has = member.roles.cache.has(role.id);
    try {
      if (should && !has) await member.roles.add(role, 'Niveau ' + level);
      else if (!should && has && !STACK_ROLES) await member.roles.remove(role, 'Niveau ' + level);
    } catch (e) {
      console.error('Role ' + r.name + ' impossible :', e.message);
    }
  }
}

client.on(Events.MessageCreate, async (message) => {
  try {
    if (!message.guild || message.guild.id !== GUILD_ID || message.author.bot) return;
    const now = Date.now();
    if (now - (lastGain.get(message.author.id) || 0) < COOLDOWN_MS) return;
    lastGain.set(message.author.id, now);
    const gain = Math.round((15 + Math.floor(Math.random() * 11)) * XP_RATE);
    const u = db.users[message.author.id] || (db.users[message.author.id] = { xp: 0 });
    const before = levelInfo(u.xp).level;
    u.xp += gain;
    dirty = true;
    const after = levelInfo(u.xp).level;
    if (after > before || after >= 1) {
      const member = message.member || (await message.guild.members.fetch(message.author.id));
      if (after > before) await syncRoles(member, after);
    }
  } catch (e) {
    console.error('Erreur XP :', e.message);
  }
});

// ---------- Commandes /level et /leaderboard ----------
const COMMANDS = [
  {
    name: 'level',
    description: 'Voir ton niveau (ou celui d\'un membre)',
    options: [{ name: 'membre', description: 'Le membre', type: ApplicationCommandOptionType.User, required: false }],
  },
  { name: 'leaderboard', description: 'Le top 10 des membres les plus actifs' },
];

const ranking = () => Object.entries(db.users).sort((a, b) => b[1].xp - a[1].xp);

client.on(Events.InteractionCreate, async (it) => {
  try {
    if (!it.isChatInputCommand() || !it.guild) return;
    if (it.commandName === 'level') {
      const user = it.options.getUser('membre') || it.user;
      const xp = (db.users[user.id] || { xp: 0 }).xp;
      const { level, rest, need } = levelInfo(xp);
      const rank = ranking().findIndex(([id]) => id === user.id) + 1;
      const earned = REWARDS.filter((r) => r.level <= level);
      const troop = earned.length ? earned[earned.length - 1].name : 'Aucun';
      const embed = new EmbedBuilder()
        .setColor(0xf2a900)
        .setTitle('Niveau de ' + user.username)
        .setDescription(
          '**Niveau ' + level + '** (' + troop + ')\n' + rest + ' / ' + need + ' XP vers le niveau ' + (level + 1) +
            '\nXP total : ' + xp + (rank ? '\nClassement : #' + rank : '')
        );
      await it.reply({ embeds: [embed] });
    } else if (it.commandName === 'leaderboard') {
      const top = ranking().slice(0, 10);
      const lines = top.map(([id, v], i) => '**' + (i + 1) + '.** <@' + id + '> - niveau ' + levelInfo(v.xp).level + ' (' + v.xp + ' XP)');
      const embed = new EmbedBuilder()
        .setColor(0xf2a900)
        .setTitle('Top 10 Clash Center')
        .setDescription(lines.length ? lines.join('\n') : 'Personne pour le moment.');
      await it.reply({ embeds: [embed], allowedMentions: { parse: [] } });
    }
  } catch (e) {
    console.error('Erreur commande :', e.message);
  }
});

// ---------- Demarrage ----------
client.once(Events.ClientReady || 'ready', async () => {
  console.log('Connecte en tant que', client.user.tag);
  const guild = await client.guilds.fetch(GUILD_ID);
  await guild.channels.fetch();
  await guild.roles.fetch();
  const missing = REWARDS.filter((r) => !guild.roles.cache.find((x) => roleKey(x.name) === roleKey(r.name)));
  if (missing.length) console.error('Roles de troupes introuvables :', missing.map((r) => r.name).join(', '));
  await refreshBanner();

  const testIndex = process.argv.indexOf('--test');
  if (testIndex >= 0) {
    // Mode test : node bot.js --test <id_utilisateur> -> envoie bienvenue + depart puis s'arrete
    await welcome(guild, process.argv[testIndex + 1]);
    await goodbye(guild, process.argv[testIndex + 1]);
    client.destroy();
    process.exit(0);
  }

  try {
    await guild.commands.set(COMMANDS);
    console.log('Commandes /level et /leaderboard enregistrees');
  } catch (e) {
    console.error('Commandes non enregistrees :', e.message);
  }
  setInterval(refreshBanner, 12 * 60 * 60 * 1000);
});

client.on(Events.GuildMemberAdd, async (member) => {
  try {
    if (member.guild.id !== GUILD_ID || member.user.bot) return;
    await welcome(member.guild, member.id);
  } catch (e) {
    console.error('Erreur bienvenue :', e.message);
  }
});

client.on(Events.GuildMemberRemove, async (member) => {
  try {
    if (member.guild.id !== GUILD_ID || (member.user && member.user.bot)) return;
    await goodbye(member.guild, member.id);
  } catch (e) {
    console.error('Erreur depart :', e.message);
  }
});

client.on('error', (e) => console.error('Erreur client :', e.message));
process.on('unhandledRejection', (e) => console.error('Rejet non gere :', e && e.message ? e.message : e));

client.login(TOKEN);
