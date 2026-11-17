// Bot de bienvenue Clash Center : poste un message + la banniere des qu'un membre arrive.
const fs = require('fs');
const path = require('path');
const { Client, Events, GatewayIntentBits, AttachmentBuilder } = require('discord.js');

const TOKEN = process.env.DISCORD_TOKEN;
const GUILD_ID = '1515604769933099069';
// Message du salon staff-discussion qui contient la banniere (on la recopie en local)
const BANNER_CHANNEL_ID = '1542615316629295264';
const BANNER_MESSAGE_ID = '1571514585901568010';
const BANNER_FILE = path.join(__dirname, 'banner.png');

if (!TOKEN) {
  console.error('DISCORD_TOKEN manquant');
  process.exit(1);
}

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers] });

// Telecharge la banniere depuis le message d'origine et la garde sur le disque.
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

// Trouve le salon de bienvenue (le nom contient des lettres stylisees, on les normalise).
function findWelcomeChannel(guild) {
  if (process.env.WELCOME_CHANNEL_ID) return guild.channels.cache.get(process.env.WELCOME_CHANNEL_ID);
  return guild.channels.cache.find(
    (c) => c.isTextBased() && !c.isThread() && c.name.normalize('NFKC').toLowerCase().includes('bienvenue')
  );
}

async function welcome(guild, userId) {
  const channel = findWelcomeChannel(guild);
  if (!channel) {
    console.error('Salon de bienvenue introuvable');
    return;
  }
  const files = fs.existsSync(BANNER_FILE) ? [new AttachmentBuilder(BANNER_FILE)] : [];
  await channel.send({
    content: 'Bienvenue <@' + userId + '> ! \u{1F389}',
    files,
    allowedMentions: { users: [userId] },
  });
  console.log('Bienvenue envoye a', userId);
}

client.once(Events.ClientReady || 'ready', async () => {
  console.log('Connecte en tant que', client.user.tag);
  await refreshBanner();
  const testIndex = process.argv.indexOf('--test');
  if (testIndex >= 0) {
    // Mode test : node bot.js --test <id_utilisateur> -> envoie un message puis s'arrete
    const guild = await client.guilds.fetch(GUILD_ID);
    await guild.channels.fetch();
    await welcome(guild, process.argv[testIndex + 1]);
    client.destroy();
    process.exit(0);
  }
  setInterval(refreshBanner, 12 * 60 * 60 * 1000);
});

client.on('guildMemberAdd', async (member) => {
  try {
    if (member.guild.id !== GUILD_ID || member.user.bot) return;
    await welcome(member.guild, member.id);
  } catch (e) {
    console.error('Erreur bienvenue :', e.message);
  }
});

client.on('error', (e) => console.error('Erreur client :', e.message));
process.on('unhandledRejection', (e) => console.error('Rejet non gere :', e && e.message ? e.message : e));

client.login(TOKEN);
