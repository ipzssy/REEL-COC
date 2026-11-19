def CTA(say, first, extra=None, imgs=None, bg="w:clip_17h17.mp4:50"):
    lines = list(first) + [("Dis-le", "DIS-LE EN COMMENTAIRE", "w", 105), ("rejoins", "REJOINS LE DISCORD", "c", 120), ("lien", "LIEN EN BIO", "y", 170)]
    return {"say": say + " Dis-le en commentaire, et rejoins le Discord, lien en bio.", "bg": bg, "imgs": imgs or ["big:?|y"], "lines": lines}
def SC(say, bg, imgs, lines, head=None): return {"say": say, "bg": bg, "imgs": imgs, "lines": lines, "head": head}
B = "b:clip_17h06.mp4:%d"; W = "w:%s:%d"
def b(ss): return f"b:clip_17h06.mp4:{ss}"
def w(c, ss): return f"w:{c}:{ss}"
V = {}
V["hdv"] = dict(date="2026-11-21", scenes=[
 SC("Ton hôtel de ville ne tombe jamais ? Ce n'est pas ton armée, c'est ça.", b(8), ["th18"], [("Ton","TON HDV","w",200),("ne","NE TOMBE JAMAIS ?","y",150),("Ce","CE N'EST PAS","w",150),("armée","TON ARMÉE","r",190),("est","C'EST ÇA","y",230)]),
 SC("Erreur numéro un : tes troupes partent dans les coins. Ouvre un chemin vers le centre.", w("clip_17h17.mp4",20), ["king"], [("tes","TES TROUPES","w",150),("partent","PARTENT DANS LES COINS","o",120),("Ouvre","OUVRE UN CHEMIN","g",150),("vers","VERS LE CENTRE","y",150)], ("ERREUR","N°1")),
 SC("Erreur numéro deux : tu oublies que l'hôtel de ville se défend. Garde des sorts ou une capacité pour cette zone.", w("clip_17h19.mp4",40), ["th18","rage"], [("tu","L'HDV SE DÉFEND","r",130),("Garde","GARDE DES SORTS","c",130),("ou","OU UNE CAPACITÉ","p",130),("pour","POUR CETTE ZONE","y",130)], ("ERREUR","N°2")),
 SC("Résultat : le centre s'effondre, et l'étoile est à toi.", "grass", ["star"], [("le","LE CENTRE S'EFFONDRE","g",120),("et","L'ÉTOILE EST À TOI","y",140)], ("RÉSULTAT",None)),
 CTA("L'hôtel de ville, tu le prends en premier, ou en dernier ?", [("en","EN PREMIER","c",190),("ou","OU EN DERNIER ?","o",150)], imgs=["th18"]),
], loop=dict(say="Et la vraie raison, c'est que…", lines=[("Et","ET LA VRAIE RAISON,","w",140),("c'est","C'EST QUE…","y",230)]))
V["remparts"] = dict(date="2026-11-22", scenes=[
 SC("Tout le monde oublie ses remparts, et ça fait perdre des attaques entières.", b(14), ["wallb"], [("Tout","TOUT LE MONDE","w",150),("oublie","OUBLIE SES REMPARTS","y",120),("ça","ÇA FAIT PERDRE","r",150),("des","DES ATTAQUES ENTIÈRES","o",110)]),
 SC("Raison numéro un : ils ralentissent les troupes sous le feu.", w("clip_17h17.mp4",30), ["wallb"], [("ils","ILS RALENTISSENT","c",130),("les","LES TROUPES","w",160),("sous","SOUS LE FEU","o",170)], ("RAISON","N°1")),
 SC("Raison numéro deux : ils forcent l'adversaire à dépenser des sorts, ou des briseurs de murs.", w("clip_17h19.mp4",60), ["wallb","lightning"], [("ils","ILS FORCENT","w",150),("l","L'ADVERSAIRE","y",140),("dépenser","DÉPENSER DES SORTS","p",120),("ou","OU DES BRISEURS","o",130)], ("RAISON","N°2")),
 SC("Commence par ceux qui protègent le centre. Stockage plein ? Mets le surplus dans les remparts.", w("clip_17h25.mp4",30), ["th18"], [("Commence","COMMENCE PAR","w",140),("protègent","CEUX QUI PROTÈGENT","c",110),("centre","LE CENTRE","y",190),("Stockage","STOCKAGE PLEIN ?","g",130),("Mets","MÈTS LE SURPLUS","w",130),("dans","DANS LES REMPARTS","y",110)]),
 SC("Résultat : ta base devient bien plus dure à raser.", "grass", ["star"], [("ta","TA BASE","w",190),("bien","BIEN PLUS DURE","g",140),("à","À RASER","y",190)], ("RÉSULTAT",None)),
 CTA("Tes remparts, tu les montes au max, ou tu les oublies ?", [("au","AU MAX","g",230),("ou","OU OUBLIÉS ?","r",170)], imgs=["wallb"]),
], loop=dict(say="Et n'oublie jamais…", lines=[("Et","ET N'OUBLIE","w",170),("jamais","JAMAIS…","y",250)]))
V["lire_base"] = dict(date="2026-11-23", scenes=[
 SC("Prends dix secondes avant d'attaquer. Ça change tout.", b(30), ["big:10 SEC|y"], [("Prends","PRENDS 10 SECONDES","y",130),("avant","AVANT D'ATTAQUER","w",130),("Ça","ÇA CHANGE TOUT","g",160)]),
 SC("Un : trouve les défenses aériennes.", w("clip_17h17.mp4",20), ["ad"], [("trouve","TROUVE LES","w",170),("défenses","DÉFENSES AÉRIENNES","c",110)], ("ÉTAPE","N°1")),
 SC("Deux : repère les tours de l'enfer et l'aigle.", w("clip_17h19.mp4",40), ["eagle"], [("repère","REPÈRE LES","w",160),("tours","TOURS DE L'ENFER","r",120),("et","ET L'AIGLE","o",190)], ("ÉTAPE","N°2")),
 SC("Trois : devine où sont les pièges.", w("clip_17h25.mp4",30), ["giant_bomb","spring","air_mine"], [("devine","DEVINE","w",200),("où","OÙ SONT LES PIÈGES ?","o",120)], ("ÉTAPE","N°3")),
 SC("Quatre : choisis le côté le plus faible pour ton entrée.", w("clip_17h17.mp4",60), ["hog"], [("choisis","CHOISIS LE CÔTÉ","w",140),("plus","LE PLUS FAIBLE","g",150),("pour","POUR TON ENTRÉE","y",130)], ("ÉTAPE","N°4")),
 SC("Résultat : tu attaques avec un plan.", "grass", ["star"], [("tu","TU ATTAQUES","w",190),("avec","AVEC UN PLAN","g",160)], ("RÉSULTAT",None)),
 CTA("Tu prends le temps de lire la base, ou tu fonces direct ?", [("lire","LIRE LA BASE","c",160),("ou","OU FONCER ?","o",170)]),
], loop=dict(say="Et avant chaque attaque, souviens-toi…", lines=[("Et","ET AVANT CHAQUE ATTAQUE,","w",100),("souviens","SOUVIENS-TOI…","y",190)]))
V["pourcentage"] = dict(date="2026-11-24", scenes=[
 SC("Bloqué à quatre-vingt-dix pour cent ? Voici comment gratter les derniers pour cent.", b(44), ["big:90 %|r"], [("Bloqué","BLOQUÉ À 90 % ?","r",150),("gratter","GRATTE LES","w",170),("derniers","DERNIERS POUR CENT","y",110)]),
 SC("Erreur numéro un : toutes tes troupes sont posées, et il reste des bâtiments dans les coins. Garde quelques troupes rapides pour la fin.", w("clip_17h17.mp4",20), ["hog"], [("toutes","TOUTES TES TROUPES","w",120),("posées","DÉJÀ POSÉES","o",150),("bâtiments","BÂTIMENTS DANS LES COINS","r",100),("Garde","GARDE DES TROUPES","g",120),("rapides","RAPIDES","c",230)], ("ERREUR","N°1")),
 SC("Erreur numéro deux : tu ne regardes pas le chrono. Dans les trente dernières secondes, fonce sur les bâtiments restants.", w("clip_17h19.mp4",40), ["clock"], [("regardes","REGARDE LE CHRONO","o",120),("trente","30 DERNIÈRES SECONDES","y",100),("fonce","FONCE","g",250),("sur","SUR LES BÂTIMENTS","w",120)], ("ERREUR","N°2")),
 SC("Résultat : des pour cent en plus, parfois même une étoile.", "grass", ["star"], [("des","DES % EN PLUS","g",160),("parfois","PARFOIS UNE ÉTOILE","y",120)], ("RÉSULTAT",None)),
 CTA("Ton pire souvenir : quatre-vingt-dix-neuf pour cent, ou quarante-neuf ?", [("quatre","99 % ?","r",230),("ou","OU 49 % ?","o",200)], imgs=["big:% ?|y"]),
], loop=dict(say="Et si tu es bloqué…", lines=[("Et","ET SI TU ES","w",170),("bloqué","BLOQUÉ…","y",230)]))
V["lanceur"] = dict(date="2026-11-25", scenes=[
 SC("L'engin de siège le plus sous-estimé du jeu ? Le lanceur de bûches. Voici pourquoi.", b(20), ["logl"], [("engin","L'ENGIN DE SIÈGE","w",140),("plus","LE PLUS SOUS-ESTIMÉ","y",110),("lanceur","LE LANCEUR DE BÛCHES","c",100)]),
 SC("Un : ses bûches cassent les murs en ligne droite.", w("clip_17h17.mp4",20), ["logl"], [("bûches","SES BÛCHES","w",170),("cassent","CASSENT LES MURS","o",130),("en","EN LIGNE DROITE","y",140)], ("RAISON","N°1")),
 SC("Deux : il ouvre un chemin direct vers le centre.", w("clip_17h19.mp4",40), ["king"], [("ouvre","IL OUVRE UN CHEMIN","w",120),("direct","DIRECT VERS LE CENTRE","g",110)], ("RAISON","N°2")),
 SC("Trois : il transporte ton château de clan.", w("clip_17h25.mp4",30), ["clan_castle"], [("transporte","IL TRANSPORTE","w",150),("château","TON CHÂTEAU DE CLAN","c",110)], ("RAISON","N°3")),
 SC("Attention, il roule tout droit. Pose-le bien en face.", b(60), ["logl"], [("Attention","ATTENTION","r",230),("roule","IL ROULE TOUT DROIT","o",120),("Pose","POSE-LE EN FACE","y",140)]),
 CTA("Lanceur de bûches, ou briseurs de murs : tu prends lequel ?", [("Lanceur","BÛCHES","y",220),("briseurs","OU BRISEURS ?","c",160)], imgs=["logl","wallb"]),
], loop=dict(say="Et devine quel est…", lines=[("Et","ET DEVINE","w",190),("quel","QUEL EST…","y",210)]))
V["nouvel_hdv"] = dict(date="2026-11-26", scenes=[
 SC("Nouvel hôtel de ville ? N'améliore surtout pas n'importe quoi.", b(12), ["th19"], [("Nouvel","NOUVEL HDV ?","y",190),("améliore","N'AMÉLIORE PAS","r",150),("n","N'IMPORTE QUOI","w",150)]),
 SC("Priorité numéro un : le laboratoire.", w("clip_17h17.mp4",20), ["lab15"], [("le","LE LABORATOIRE","c",140)], ("PRIORITÉ","N°1")),
 SC("Numéro deux : les camps militaires et le château de clan.", w("clip_17h19.mp4",40), ["army_camp12","clan_castle"], [("les","LES CAMPS MILITAIRES","g",100),("et","LE CHÂTEAU DE CLAN","y",100)], ("PRIORITÉ","N°2")),
 SC("Numéro trois : tes héros, ils montent lentement.", w("clip_17h25.mp4",30), ["king","queen"], [("tes","TES HÉROS","w",160),("montent","ILS MONTENT LENTEMENT","o",100)], ("PRIORITÉ","N°3")),
 SC("Ensuite seulement, les défenses et le reste.", w("clip_17h17.mp4",60), ["ad","eagle"], [("Ensuite","ENSUITE SEULEMENT","w",120),("les","LES DÉFENSES","c",160),("et","ET LE RESTE","y",170)]),
 CTA("Attaque ou défense en premier, tu montes quoi ?", [("Attaque","ATTAQUE","r",230),("ou","OU DÉFENSE ?","c",190)]),
], loop=dict(say="Et si tu passes à un…", lines=[("Et","ET SI TU PASSES","w",150),("un","À UN…","y",250)]))
V["ressources"] = dict(date="2026-11-27", scenes=[
 SC("Toujours à court de ressources ? Voici trois astuces simples.", b(26), ["resources"], [("court","À COURT DE RESSOURCES ?","r",100),("trois","3 ASTUCES SIMPLES","y",120)]),
 SC("Un : un ouvrier qui dort, c'est du temps perdu.", w("clip_17h17.mp4",20), ["builder"], [("ouvrier","UN OUVRIER QUI DORT","w",120),("temps","TEMPS PERDU","r",190)], ("ASTUCE","N°1")),
 SC("Deux : les guerres et les jeux de clans rapportent gros.", w("clip_17h19.mp4",40), ["clan_castle"], [("guerres","LES GUERRES","c",160),("jeux","LES JEUX DE CLANS","p",110),("rapportent","ÇA RAPPORTE GROS","g",130)], ("ASTUCE","N°2")),
 SC("Trois : stockages pleins ? Dépense avant de te faire piller. Le surplus part dans les remparts.", w("clip_17h25.mp4",30), ["resources"], [("stockages","STOCKAGES PLEINS ?","o",120),("Dépense","DÉPENSE","g",230),("avant","AVANT LE PILLAGE","r",120),("surplus","SURPLUS = REMPARTS","y",100)], ("ASTUCE","N°3")),
 CTA("Tu manques d'or, d'élixir, ou d'élixir noir ?", [("or","D'OR ?","y",230),("élixir","D'ÉLIXIR ?","p",190),("noir","ÉLIXIR NOIR ?","w",150)], imgs=["resources"]),
], loop=dict(say="Et si tu es toujours à court…", lines=[("Et","ET SI TU ES","w",170),("toujours","TOUJOURS À COURT…","y",120)]))
V["trophees"] = dict(date="2026-11-28", scenes=[
 SC("Tu perds des trophées en boucle ? Voici trois raisons.", b(36), ["bk_ko","aq_ko"], [("perds","TU PERDS DES TROPHÉES","r",110),("en","EN BOUCLE ?","o",190),("trois","3 RAISONS","y",230)]),
 SC("Un : ton armée est incomplète.", w("clip_17h17.mp4",20), ["army_camp12"], [("armée","ARMÉE INCOMPLÈTE","o",120)], ("RAISON","N°1")),
 SC("Deux : ta base est trop facile à raser.", w("clip_17h19.mp4",40), ["th18"], [("base","TA BASE","w",190),("trop","TROP FACILE À RASER","r",110)], ("RAISON","N°2")),
 SC("Trois : tu joues trop haut pour ton niveau.", w("clip_17h25.mp4",30), ["th19"], [("joues","TU JOUES TROP HAUT","y",110),("pour","POUR TON NIVEAU","w",120)], ("RAISON","N°3")),
 SC("Attaque toujours avec une armée complète, et renforce ta défense.", w("clip_17h17.mp4",60), ["army_camp12","ad"], [("Attaque","ATTAQUE TOUJOURS","w",120),("armée","ARMÉE COMPLÈTE","g",120),("renforce","RENFORCE TA DÉFENSE","c",110)]),
 CTA("Plutôt ressources, ou trophées ?", [("Plutôt","PLUTÔT RESSOURCES ?","g",100),("ou","OU TROPHÉES ?","y",130)], imgs=["bk_ko"]),
], loop=dict(say="Et si tu perds toujours…", lines=[("Et","ET SI TU PERDS","w",150),("toujours","TOUJOURS…","y",230)]))
V["clan"] = dict(date="2026-11-29", scenes=[
 SC("Ton clan est mort ? Voici comment en trouver un qui te fait progresser.", b(16), ["clan_castle"], [("Ton","TON CLAN EST MORT ?","r",120),("trouver","TROUVE-EN UN","w",150),("fait","QUI TE FAIT PROGRESSER","g",100)]),
 SC("Un : il fait des guerres régulièrement.", w("clip_17h17.mp4",20), ["king"], [("guerres","DES GUERRES","c",170),("régulièrement","RÉGULIÈREMENT","y",110)], ("CRITÈRE","N°1")),
 SC("Deux : ses membres donnent vite des troupes.", w("clip_17h19.mp4",40), ["dragon"], [("ses","SES MEMBRES","w",150),("donnent","DONNENT VITE","g",150),("des","DES TROUPES","y",150)], ("CRITÈRE","N°2")),
 SC("Trois : ils partagent des conseils. Et pour aller plus vite, il y a le Discord.", w("clip_17h25.mp4",30), ["healer"], [("partagent","ILS PARTAGENT","w",150),("conseils","DES CONSEILS","y",150),("Discord","LE DISCORD","c",190)], ("CRITÈRE","N°3")),
 CTA("Ton clan, actif ou mort ?", [("actif","ACTIF","g",230),("mort","OU MORT ?","r",200)], imgs=["clan_castle"]),
], loop=dict(say="Et si c'est ton cas…", lines=[("Et","ET SI","w",200),("c'est","C'EST TON CAS…","y",120)]))
V["pieges"] = dict(date="2026-11-30", scenes=[
 SC("Ton attaque part bien, puis tout s'écroule d'un coup ? C'est un piège.", b(52), ["giant_bomb"], [("part","TON ATTAQUE PART BIEN","g",110),("puis","PUIS TOUT S'ÉCROULE","r",110),("piège","C'EST UN PIÈGE","o",160)]),
 SC("Un : la bombe géante, contre tes troupes au sol groupées.", w("clip_17h17.mp4",20), ["giant_bomb"], [("bombe","LA BOMBE GÉANTE","o",130),("contre","CONTRE TES TROUPES","w",110),("sol","AU SOL GROUPÉES","y",120)], ("PIÈGE","N°1")),
 SC("Deux : la mine aérienne, contre tes troupes volantes.", w("clip_17h19.mp4",40), ["air_mine"], [("mine","LA MINE AÉRIENNE","c",120),("volantes","TROUPES VOLANTES","y",110)], ("PIÈGE","N°2")),
 SC("Trois : le piège à ressort, qui éjecte tes troupes.", w("clip_17h25.mp4",30), ["spring"], [("piège","LE PIÈGE À RESSORT","p",110),("éjecte","ÉJECTE TES TROUPES","r",110)], ("PIÈGE","N°3")),
 SC("Envoie une troupe en éclaireur pour les déclencher.", w("clip_17h17.mp4",60), ["hog"], [("troupe","UNE TROUPE","w",190),("éclaireur","EN ÉCLAIREUR","g",170)]),
 CTA("Quel piège t'a fait le plus rager : la bombe, ou la mine ?", [("bombe","LA BOMBE ?","o",190),("mine","OU LA MINE ?","c",190)], imgs=["giant_bomb","air_mine"]),
], loop=dict(say="Et si ton attaque…", lines=[("Et","ET SI","w",200),("attaque","TON ATTAQUE…","y",170)]))
V["defenses"] = dict(date="2026-12-01", scenes=[
 SC("Toutes les défenses ne se valent pas. Celles-ci, tu les détruis en premier.", b(66), ["eagle"], [("Toutes","TOUTES LES DÉFENSES","w",110),("valent","NE SE VALENT PAS","r",110),("détruis","DÉTRUIS-LES EN PREMIER","y",100)]),
 SC("Un : les tours de l'enfer, elles font fondre tes héros.", w("clip_17h17.mp4",20), ["king","queen"], [("tours","TOURS DE L'ENFER","r",120),("font","ELLES FONT FONDRE","o",110),("héros","TES HÉROS","w",190)], ("DÉFENSE","N°1")),
 SC("Deux : l'aigle d'artillerie, qui frappe sur une grande partie de la base.", w("clip_17h19.mp4",40), ["eagle"], [("aigle","L'AIGLE D'ARTILLERIE","o",100),("frappe","FRAPPE TRÈS LARGE","y",120)], ("DÉFENSE","N°2")),
 SC("Trois : les défenses aériennes, si tu attaques par les airs.", w("clip_17h25.mp4",30), ["ad","dragon"], [("défenses","DÉFENSES AÉRIENNES","c",110),("attaques","SI TU ATTAQUES PAR LES AIRS","w",90)], ("DÉFENSE","N°3")),
 SC("Utilise tes sorts ou tes héros pour les neutraliser tôt.", w("clip_17h17.mp4",60), ["rage","queen"], [("sorts","SORTS OU HÉROS","p",130),("neutraliser","NEUTRALISE TÔT","g",140)]),
 CTA("La pire défense, la tour de l'enfer, ou l'aigle ?", [("tour","TOUR DE L'ENFER ?","r",110),("ou","OU L'AIGLE ?","o",150)], imgs=["eagle"]),
], loop=dict(say="Et n'oublie pas…", lines=[("Et","ET N'OUBLIE","w",170),("pas","PAS…","y",260)]))
V["phases"] = dict(date="2026-12-02", scenes=[
 SC("Une bonne attaque, c'est trois phases. Rate-en une, et tes étoiles s'envolent.", b(4), ["big:3 PHASES|y"], [("bonne","UNE BONNE ATTAQUE","w",120),("trois","3 PHASES","y",230),("Rate","RATE-EN UNE","r",170),("étoiles","TES ÉTOILES S'ENVOLENT","o",100)]),
 SC("Phase un : l'entrée. Ouvre un côté de la base.", w("clip_17h17.mp4",20), ["hog"], [("entrée","L'ENTRÉE","c",210),("Ouvre","OUVRE UN CÔTÉ","w",140)], ("PHASE","N°1")),
 SC("Phase deux : le cœur. Les héros sortent vers le centre.", w("clip_17h19.mp4",40), ["king","queen"], [("cœur","LE CŒUR","p",210),("héros","HÉROS VERS LE CENTRE","y",100)], ("PHASE","N°2")),
 SC("Phase trois : le nettoyage des derniers bâtiments.", w("clip_17h25.mp4",30), ["dragon"], [("nettoyage","LE NETTOYAGE","g",160),("derniers","DERNIERS BÂTIMENTS","w",110)], ("PHASE","N°3")),
 SC("Résultat : une attaque propre, du début à la fin.", "grass", ["star"], [("une","UNE ATTAQUE PROPRE","g",110),("du","DU DÉBUT À LA FIN","y",110)], ("RÉSULTAT",None)),
 CTA("Tu rates plutôt l'entrée, ou la fin ?", [("entrée","L'ENTRÉE ?","c",200),("ou","OU LA FIN ?","o",190)]),
], loop=dict(say="Et n'oublie pas…", lines=[("Et","ET N'OUBLIE","w",170),("pas","PAS…","y",260)]))
V["base"] = dict(date="2026-12-03", scenes=[
 SC("Ta base se fait raser à chaque attaque ? Regarde ces trois erreurs.", b(72), ["th18"], [("base","TA BASE SE FAIT RASER","r",100),("trois","3 ERREURS","y",230)]),
 SC("Erreur numéro un : ton hôtel de ville est sur le bord. Mets-le au centre, entouré de défenses.", w("clip_17h17.mp4",20), ["th18"], [("bord","HDV SUR LE BORD","r",130),("Mets","MÈTS-LE AU CENTRE","g",120),("entouré","ENTOURÉ DE DÉFENSES","c",100)], ("ERREUR","N°1")),
 SC("Erreur numéro deux : tes défenses aériennes sont collées. Écarte-les, un seul combo ne les détruit plus toutes.", w("clip_17h19.mp4",40), ["ad"], [("collées","DÉFENSES COLLÉES","r",110),("Écarte","ÉCARTE-LES","g",190),("plus","PLUS TOUTES DÉTRUITES","w",100)], ("ERREUR","N°2")),
 SC("Erreur numéro trois : tu copies une base sans rien changer. Modifie quelques bâtiments pour surprendre.", w("clip_17h25.mp4",30), ["king"], [("copies","TU COPIES UNE BASE","o",110),("sans","SANS RIEN CHANGER","r",110),("Modifie","MODIFIE QUELQUES BÂTIMENTS","g",90)], ("ERREUR","N°3")),
 CTA("Ta base, tu l'as faite toi-même, ou copiée ?", [("faite","FAITE PAR TOI ?","c",130),("ou","OU COPIÉE ?","o",170)], imgs=["th18"]),
], loop=dict(say="Et si ta base…", lines=[("Et","ET SI","w",200),("base","TA BASE…","y",220)]))
