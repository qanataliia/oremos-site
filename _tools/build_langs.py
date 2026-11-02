"""Build br/, es/ and en/ homepages from the pt-PT index.html.

index.html (pt-PT) is the source. Every visible string is listed below with its
translation; the build fails if a pt-PT string is missing from index.html, so an
edit to the source can't silently leave the other languages stale.

Run from the site root:  python3 _tools/build_langs.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://qanataliia.github.io/oremos-site/'
PLAY = 'https://play.google.com/store/apps/details?id=com.oremos.app&amp;referrer=utm_source%3Doremos-site%26utm_medium%3Dweb%26utm_campaign%3D'

# pt-PT text → (pt-BR, es, en). Wording follows the app's own strings in each language.
T = [
    ('<html lang="pt-PT">', '<html lang="pt-BR">', '<html lang="es">', '<html lang="en">'),
    ('<title>Oremos — A Palavra de hoje, terço guiado, santos e confissão</title>',
     '<title>Oremos — A Palavra de hoje, terço guiado, santos e confissão</title>',
     '<title>Oremos — La Palabra de hoy, rosario guiado, santos y confesión</title>',
     '<title>Oremos — Verse of the Day, guided Rosary, saints and confession</title>'),
    ('Oremos é uma aplicação católica para rezar todos os dias: A Palavra de hoje em 5 minutos, o terço guiado com os mistérios do dia, a vida dos santos e a preparação para a confissão. Gratuito e sem publicidade.',
     'O Oremos é um aplicativo católico para rezar todos os dias: A Palavra de hoje em 5 minutos, o terço guiado com os mistérios do dia, a vida dos santos e a preparação para a confissão. Gratuito e sem anúncios.',
     'Oremos es una app católica para rezar cada día: La Palabra de hoy en 5 minutos, el rosario guiado con los misterios del día, la vida de los santos y la preparación para la confesión. Gratis y sin anuncios.',
     'Oremos is a Catholic app for daily prayer: the Verse of the Day in 5 minutes, the guided Rosary with today’s mysteries, the lives of the saints and preparing for confession. Free, with no ads.'),
    ('Oremos — cinco minutos com Deus, todos os dias', 'Oremos — cinco minutos com Deus, todos os dias',
     'Oremos — cinco minutos con Dios, cada día', 'Oremos — five minutes with God, every day'),
    ('A Palavra de hoje, o terço guiado, a vida dos santos e a preparação para a confissão. Gratuito e sem publicidade.',
     'A Palavra de hoje, o terço guiado, a vida dos santos e a preparação para a confissão. Gratuito e sem anúncios.',
     'La Palabra de hoy, el rosario guiado, la vida de los santos y la preparación para la confesión. Gratis y sin anuncios.',
     'The Verse of the Day, the guided Rosary, the lives of the saints and preparing for confession. Free, with no ads.'),
    ('"name": "Oremos: Oração e Terço",', '"name": "Oremos: Oração e Terço",', '"name": "Oremos: Oración y Rosario",', '"name": "Oremos: Prayer & Rosary",'),
    ('"inLanguage": ["pt-PT", "pt-BR", "es", "en"]', '"inLanguage": ["pt-BR", "pt-PT", "es", "en"]', '"inLanguage": ["es", "pt-PT", "pt-BR", "en"]', '"inLanguage": ["en", "es", "pt-PT", "pt-BR"]'),
    ('aria-label="Principal"', 'aria-label="Principal"', 'aria-label="Principal"', 'aria-label="Main"'),
    ('aria-label="Idioma"', 'aria-label="Idioma"', 'aria-label="Idioma"', 'aria-label="Language"'),
    ('>Descarregar</a>', '>Baixar</a>', '>Descargar</a>', '>Download</a>'),
    ('✦ Cinco minutos com Deus, todos os dias', '✦ Cinco minutos com Deus, todos os dias',
     '✦ Cinco minutos con Dios, cada día', '✦ Five minutes with God, every day'),
    ('<h1>Comece o dia com<br><em>A&nbsp;Palavra de&nbsp;hoje</em></h1>',
     '<h1>Comece o dia com<br><em>A&nbsp;Palavra de&nbsp;hoje</em></h1>',
     '<h1>Empieza el día con<br><em>La&nbsp;Palabra de&nbsp;hoy</em></h1>',
     '<h1>Begin the day<br>with <em>God’s&nbsp;Word</em></h1>'),
    ('Um versículo, uma reflexão e uma oração, já preparados para hoje. E, quando precisar, o terço guiado, a vida dos santos e a preparação para a confissão.',
     'Um versículo, uma reflexão e uma oração, já preparados para hoje. E, quando você precisar, o terço guiado, a vida dos santos e a preparação para a confissão.',
     'Un versículo, una reflexión y una oración, ya preparados para hoy. Y, cuando lo necesites, el rosario guiado, la vida de los santos y la preparación para la confesión.',
     'A verse, a reflection and a prayer, ready for today. And when you need them, the guided Rosary, the lives of the saints and help preparing for confession.'),
    ('Código QR para descarregar o Oremos', 'Código QR para baixar o Oremos', 'Código QR para descargar Oremos', 'QR code to download Oremos'),
    ('<small>Leia para instalar</small>', '<small>Escaneie para instalar</small>', '<small>Escanea para instalar</small>', '<small>Scan to install</small>'),
    ('<small>Disponível no</small>', '<small>Disponível no</small>', '<small>Disponible en</small>', '<small>Get it on</small>'),
    ('<small>Descarregar na</small>', '<small>Baixar na</small>', '<small>Descargar en la</small>', '<small>Download on the</small>'),
    ('Gratuito · Sem publicidade · Sem conta', 'Gratuito · Sem anúncios · Sem conta', 'Gratis · Sin anuncios · Sin cuenta', 'Free · No ads · No account'),
    ('Ainda não instalou? <a href="terco-de-hoje.html" style="color:var(--gold)">Reze já o terço de hoje no navegador →</a>',
     'Ainda não instalou? <a href="terco-de-hoje.html" style="color:var(--gold)">Reze agora o terço de hoje no navegador →</a>',
     None, None),
    ('O ecrã Início do Oremos com A Palavra de hoje e os passos Palavra, Reflexão e Oração',
     'A tela Início do Oremos com A Palavra de hoje e os passos Palavra, Reflexão e Oração',
     'La pantalla Inicio de Oremos con La Palabra de hoy y los pasos Palabra, Reflexión y Oración',
     'The Oremos Home screen with the Verse of the Day and the steps Verse, Reflection and Prayer'),
    ('<li>A Palavra de hoje em 5 minutos</li>', '<li>A Palavra de hoje em 5 minutos</li>', '<li>La Palabra de hoy en 5 minutos</li>', '<li>The Verse of the Day in 5 minutes</li>'),
    ('<li>Gratuito e sem publicidade</li>', '<li>Gratuito e sem anúncios</li>', '<li>Gratis y sin anuncios</li>', '<li>Free, with no ads</li>'),
    ('<li>Não precisa de conta</li>', '<li>Não precisa de conta</li>', '<li>No necesitas cuenta</li>', '<li>No account needed</li>'),
    ('<li>Funciona sem internet</li>', '<li>Funciona sem internet</li>', '<li>Funciona sin internet</li>', '<li>Works offline</li>'),
    ('Tudo para a sua oração', 'Tudo para a sua oração', 'Todo para tu oración', 'Everything for your prayer'),
    ('Uma aplicação, a vida de oração inteira', 'Um aplicativo, a vida de oração inteira', 'Una app, toda tu vida de oración', 'One app for your whole prayer life'),
    ('Do versículo da manhã ao exame da noite, com o terço, os santos e a confissão sempre à mão.',
     'Do versículo da manhã ao exame da noite, com o terço, os santos e a confissão sempre à mão.',
     'Del versículo de la mañana al examen de la noche, con el rosario, los santos y la confesión siempre a mano.',
     'From the morning verse to the evening Examen, with the Rosary, the saints and confession always at hand.'),
    ('<h3>A Palavra de hoje</h3><p>Um versículo e uma reflexão para cada dia.</p>',
     '<h3>A Palavra de hoje</h3><p>Um versículo e uma reflexão para cada dia.</p>',
     '<h3>La Palabra de hoy</h3><p>Un versículo y una reflexión para cada día.</p>',
     '<h3>Verse of the Day</h3><p>A verse and a reflection for every day.</p>'),
    ('<h3>Rotina diária</h3><p>Palavra, Reflexão e Oração, e o Exame à noite.</p>',
     '<h3>Rotina diária</h3><p>Palavra, Reflexão e Oração, e o Exame à noite.</p>',
     '<h3>Rutina diaria</h3><p>Palabra, Reflexión y Oración, y el Examen por la noche.</p>',
     '<h3>Daily routine</h3><p>Verse, Reflection and Prayer, and the Examen at night.</p>'),
    ('<h3>Terço guiado</h3><p>Os mistérios de hoje, conta a conta.</p>',
     '<h3>Terço guiado</h3><p>Os mistérios de hoje, conta a conta.</p>',
     '<h3>Rosario guiado</h3><p>Los misterios de hoy, cuenta a cuenta.</p>',
     '<h3>Guided Rosary</h3><p>Today’s mysteries, bead by bead.</p>'),
    ('<h3>Santos</h3><p>Conheça a vida de quem seguiu Jesus.</p>',
     '<h3>Santos</h3><p>Conheça a vida de quem seguiu Jesus.</p>',
     '<h3>Santos</h3><p>Conoce la vida de quienes siguieron a Jesús.</p>',
     '<h3>Saints</h3><p>The lives of those who followed Jesus.</p>'),
    ('<h3>Confissão</h3><p>Prepare-se com calma e em privado.</p>',
     '<h3>Confissão</h3><p>Prepare-se com calma e em particular.</p>',
     '<h3>Confesión</h3><p>Prepárate con calma y en privado.</p>',
     '<h3>Confession</h3><p>Prepare calmly and privately.</p>'),
    ('<p class="eyebrow">A Palavra de hoje</p>', '<p class="eyebrow">A Palavra de hoje</p>', '<p class="eyebrow">La Palabra de hoy</p>', '<p class="eyebrow">Verse of the Day</p>'),
    ('Um versículo para guardar no coração', 'Um versículo para guardar no coração', 'Un versículo para guardar en el corazón', 'A verse to keep in your heart'),
    ('Cada dia, uma passagem da Bíblia com uma reflexão próxima, escrita para a vida de todos os dias, e um gesto concreto para viver a Palavra.',
     'Cada dia, uma passagem da Bíblia com uma reflexão próxima, escrita para a vida de todos os dias, e um gesto concreto para viver a Palavra.',
     'Cada día, un pasaje de la Biblia con una reflexión cercana, escrita para la vida de todos los días, y un gesto concreto para vivir la Palabra.',
     'Each day, a Bible passage with a warm reflection written for everyday life, and one concrete thing to live it out.'),
    ('<li><strong>Texto bíblico completo</strong>, não só uma frase solta.</li>',
     '<li><strong>Texto bíblico completo</strong>, não só uma frase solta.</li>',
     '<li><strong>El texto bíblico completo</strong>, no solo una frase suelta.</li>',
     '<li><strong>The full passage</strong>, not just a single line.</li>'),
    ('<li><strong>“Para hoje”</strong>: uma coisa simples para fazer durante o dia.</li>',
     '<li><strong>“Para hoje”</strong>: uma coisa simples para fazer durante o dia.</li>',
     '<li><strong>“Para hoy”</strong>: algo sencillo para hacer durante el día.</li>',
     '<li><strong>“For today”</strong>: one simple thing to do during the day.</li>'),
    ('<li><strong>Partilhe</strong> o versículo com quem precisa de o ouvir.</li>',
     '<li><strong>Compartilhe</strong> o versículo com quem precisa ouvi-lo.</li>',
     '<li><strong>Comparte</strong> el versículo con quien necesita oírlo.</li>',
     '<li><strong>Share</strong> the verse with someone who needs to hear it.</li>'),
    ('A Palavra de hoje no Oremos: Salmo 139', 'A Palavra de hoje no Oremos: Salmo 139', 'La Palabra de hoy en Oremos: Salmo 139', 'The Verse of the Day in Oremos: Psalm 139'),
    ('<p class="eyebrow">Rotina diária</p>', '<p class="eyebrow">Rotina diária</p>', '<p class="eyebrow">Rutina diaria</p>', '<p class="eyebrow">Daily routine</p>'),
    ('Um pequeno ritmo, todos os dias', 'Um pequeno ritmo, todos os dias', 'Un pequeño ritmo, cada día', 'A small rhythm, every day'),
    ('Sem ter de decidir o que rezar: o Oremos prepara o dia por si.',
     'Sem precisar decidir o que rezar: o Oremos prepara o dia para você.',
     'Sin tener que decidir qué rezar: Oremos prepara el día por ti.',
     'No need to decide what to pray: Oremos gets each day ready for you.'),
    ('<h3>De manhã: a Palavra</h3><p>Palavra, Reflexão e Oração, em cerca de 5 minutos. O Início mostra o que já fez hoje.</p>',
     '<h3>De manhã: a Palavra</h3><p>Palavra, Reflexão e Oração, em cerca de 5 minutos. O Início mostra o que você já fez hoje.</p>',
     '<h3>Por la mañana: la Palabra</h3><p>Palabra, Reflexión y Oración, en unos 5 minutos. Inicio muestra lo que ya hiciste hoy.</p>',
     '<h3>Morning: the Verse</h3><p>Verse, Reflection and Prayer, in about 5 minutes. Home shows what you’ve done today.</p>'),
    ('<h3>Ao longo do dia: o terço</h3><p>Os mistérios do dia, guiados conta a conta, quando tiver um momento.</p>',
     '<h3>Ao longo do dia: o terço</h3><p>Os mistérios do dia, guiados conta a conta, quando você tiver um momento.</p>',
     '<h3>Durante el día: el rosario</h3><p>Los misterios del día, guiados cuenta a cuenta, cuando tengas un momento.</p>',
     '<h3>During the day: the Rosary</h3><p>Today’s mysteries, guided bead by bead, whenever you have a moment.</p>'),
    ('<h3>À noite: o Exame</h3><p>Reveja o dia com Deus, ao jeito de Santo Inácio: agradecer, pedir luz e pedir perdão.</p>',
     '<h3>À noite: o Exame</h3><p>Reveja o dia com Deus, ao jeito de Santo Inácio: agradecer, pedir luz e pedir perdão.</p>',
     '<h3>Por la noche: el Examen</h3><p>Repasa el día con Dios, al estilo de San Ignacio: agradecer, pedir luz y pedir perdón.</p>',
     '<h3>Night: the Daily Examen</h3><p>Look back on your day with God, in the way of Saint Ignatius: give thanks, ask for light and ask forgiveness.</p>'),
    ('Escolha a hora do lembrete diário e veja a sua árvore crescer a cada dia de oração.',
     'Escolha a hora do lembrete diário e veja sua árvore crescer a cada dia de oração.',
     'Elige la hora del recordatorio diario y mira cómo crece tu árbol con cada día de oración.',
     'Pick a time for your daily reminder and watch your tree grow with every day of prayer.'),
    ('<p class="eyebrow">Terço guiado</p>', '<p class="eyebrow">Terço guiado</p>', '<p class="eyebrow">Rosario guiado</p>', '<p class="eyebrow">Guided Rosary</p>'),
    ('O terço que já sabe os mistérios de hoje', 'O terço que já sabe os mistérios de hoje', 'El rosario que ya sabe los misterios de hoy', 'The Rosary that already knows today’s mysteries'),
    ('Gozosos, Dolorosos, Gloriosos ou Luminosos: o Oremos abre os mistérios do dia e acompanha-o conta a conta.',
     'Gozosos, Dolorosos, Gloriosos ou Luminosos: o Oremos abre os mistérios do dia e acompanha você conta a conta.',
     'Gozosos, Dolorosos, Gloriosos o Luminosos: Oremos abre los misterios del día y te acompaña cuenta a cuenta.',
     'Joyful, Sorrowful, Glorious or Luminous: Oremos opens today’s mysteries and walks with you bead by bead.'),
    ('<li><strong>Uma passagem bíblica</strong> e uma graça a pedir em cada mistério.</li>',
     '<li><strong>Uma passagem bíblica</strong> e uma graça a pedir em cada mistério.</li>',
     '<li><strong>Un pasaje bíblico</strong> y una gracia que pedir en cada misterio.</li>',
     '<li><strong>A Bible passage</strong> and a grace to ask for in each mystery.</li>'),
    ('<li><strong>Todas as orações</strong> no ecrã, para quem não as sabe de cor.</li>',
     '<li><strong>Todas as orações</strong> na tela, para quem não as sabe de cor.</li>',
     '<li><strong>Todas las oraciones</strong> en la pantalla, para quien no las sabe de memoria.</li>',
     '<li><strong>Every prayer</strong> on screen, for anyone who doesn’t know them by heart.</li>'),
    ('<li><strong>As contas avançam consigo</strong>, sem perder o fio.</li>',
     '<li><strong>As contas avançam com você</strong>, sem perder o fio.</li>',
     '<li><strong>Las cuentas avanzan contigo</strong>, sin perder el hilo.</li>',
     '<li><strong>The beads move with you</strong>, so you never lose your place.</li>'),
    ('        <p style="margin-top:22px"><a class="pill" href="terco-de-hoje.html">Rezar o terço de hoje no navegador →</a></p>\n',
     '        <p style="margin-top:22px"><a class="pill" href="terco-de-hoje.html">Rezar o terço de hoje no navegador →</a></p>\n',
     '', ''),
    ('O terço guiado no Oremos, com as contas da Avé-Maria', 'O terço guiado no Oremos, com as contas da Ave-Maria',
     'El rosario guiado en Oremos, con las cuentas del Avemaría', 'The guided Rosary in Oremos, with the Hail Mary beads'),
    ('<p class="eyebrow">Santos</p>', '<p class="eyebrow">Santos</p>', '<p class="eyebrow">Santos</p>', '<p class="eyebrow">Saints</p>'),
    ('Aprenda com quem seguiu Jesus', 'Aprenda com quem seguiu Jesus', 'Aprende de quienes siguieron a Jesús', 'Learn from those who followed Jesus'),
    ('A vida de santos como São Padre Pio, os Pastorinhos de Fátima, Santo António de Lisboa, São Carlo Acutis e Santa Teresinha, contada de forma simples.',
     'A vida de santos como São Padre Pio, os Pastorinhos de Fátima, Santo Antônio de Lisboa, São Carlo Acutis e Santa Teresinha, contada de um jeito simples.',
     'La vida de santos como San Padre Pío, los pastorcitos de Fátima, San Antonio de Padua, San Carlo Acutis y Santa Teresita, contada de forma sencilla.',
     'The lives of saints like Saint Padre Pio, the shepherd children of Fatima, Saint Anthony, Saint Carlo Acutis and Saint Thérèse, told simply.'),
    ('<li><strong>A sua vida</strong>, em poucos parágrafos.</li>', '<li><strong>Sua vida</strong>, em poucos parágrafos.</li>',
     '<li><strong>Su vida</strong>, en pocos párrafos.</li>', '<li><strong>Their life</strong>, in a few paragraphs.</li>'),
    ('<li><strong>Uma oração</strong> para rezar com cada santo.</li>', '<li><strong>Uma oração</strong> para rezar com cada santo.</li>',
     '<li><strong>Una oración</strong> para rezar con cada santo.</li>', '<li><strong>A prayer</strong> to pray with each saint.</li>'),
    ('<li><strong>Um gesto para hoje</strong>, inspirado no seu exemplo.</li>', '<li><strong>Um gesto para hoje</strong>, inspirado no seu exemplo.</li>',
     '<li><strong>Un gesto para hoy</strong>, inspirado en su ejemplo.</li>', '<li><strong>Something for today</strong>, inspired by their example.</li>'),
    ('A página de São Padre Pio no Oremos', 'A página de São Padre Pio no Oremos', 'La página de San Padre Pío en Oremos', 'Saint Padre Pio’s page in Oremos'),
    ('<p class="eyebrow">Confissão</p>', '<p class="eyebrow">Confissão</p>', '<p class="eyebrow">Confesión</p>', '<p class="eyebrow">Confession</p>'),
    ('Prepare a confissão com calma', 'Prepare a confissão com calma', 'Prepara la confesión con calma', 'Prepare for confession calmly'),
    ('Depois do Exame do dia, anote o que quer levar ao sacramento. Quando for confessar-se, tem tudo à mão.',
     'Depois do Exame do dia, anote o que quer levar ao sacramento. Quando for se confessar, você tem tudo à mão.',
     'Después del Examen del día, anota lo que quieres llevar al sacramento. Cuando vayas a confesarte, lo tienes todo a mano.',
     'After the Daily Examen, note what you want to bring to the sacrament. When you go to confession, it’s all there.'),
    ('<li><strong>Só neste telemóvel</strong>: a lista não vai para a internet.</li>',
     '<li><strong>Só neste celular</strong>: a lista não vai para a internet.</li>',
     '<li><strong>Solo en este celular</strong>: la lista no se sube a internet.</li>',
     '<li><strong>Only on this phone</strong>: the list never goes online.</li>'),
    ('<li><strong>Protegida</strong>: só quem desbloqueia o telemóvel a pode abrir.</li>',
     '<li><strong>Protegida</strong>: só quem desbloqueia o celular pode abri-la.</li>',
     '<li><strong>Protegida</strong>: solo quien desbloquea el celular puede abrirla.</li>',
     '<li><strong>Protected</strong>: only someone who can unlock the phone can open it.</li>'),
    ('<li><strong>Apagada depois</strong> de se confessar.</li>', '<li><strong>Excluída depois</strong> que você se confessa.</li>',
     '<li><strong>Se borra</strong> después de confesarte.</li>', '<li><strong>Deleted</strong> after you go to confession.</li>'),
    ('<li><strong>Guia passo a passo</strong>, num ecrã escuro e discreto.</li>',
     '<li><strong>Guia passo a passo</strong>, numa tela escura e discreta.</li>',
     '<li><strong>Guía paso a paso</strong>, en una pantalla oscura y discreta.</li>',
     '<li><strong>A step-by-step guide</strong>, on a dark, discreet screen.</li>'),
    ('O ecrã Confissão no Oremos', 'A tela Confissão no Oremos', 'La pantalla Confesión en Oremos', 'The Confession screen in Oremos'),
    ('<p class="eyebrow">O que é o Oremos?</p><h2>Uma aplicação católica para a oração diária</h2>',
     '<p class="eyebrow">O que é o Oremos?</p><h2>Um aplicativo católico para a oração diária</h2>',
     '<p class="eyebrow">¿Qué es Oremos?</p><h2>Una app católica para la oración diaria</h2>',
     '<p class="eyebrow">What is Oremos?</p><h2>A Catholic app for daily prayer</h2>'),
    ('O Oremos é uma aplicação gratuita para rezar todos os dias. Inclui A Palavra de hoje com uma reflexão, uma rotina diária com o Exame da noite, o <a href="terco-de-hoje.html">terço guiado</a> com os mistérios de cada dia (<a href="misterios-gozosos.html">Gozosos</a>, <a href="misterios-dolorosos.html">Dolorosos</a>, <a href="misterios-gloriosos.html">Gloriosos</a> e <a href="misterios-luminosos.html">Luminosos</a>), a vida dos santos e uma ajuda privada para preparar a confissão. Funciona sem conta e sem internet, em português de Portugal e do Brasil, espanhol e inglês. O Oremos + é uma subscrição opcional com conteúdo adicional.',
     'O Oremos é um aplicativo gratuito para rezar todos os dias. Inclui A Palavra de hoje com uma reflexão, uma rotina diária com o Exame da noite, o <a href="terco-de-hoje.html">terço guiado</a> com os mistérios de cada dia (<a href="misterios-gozosos.html">Gozosos</a>, <a href="misterios-dolorosos.html">Dolorosos</a>, <a href="misterios-gloriosos.html">Gloriosos</a> e <a href="misterios-luminosos.html">Luminosos</a>), a vida dos santos e uma ajuda particular para preparar a confissão. Funciona sem conta e sem internet, em português do Brasil e de Portugal, espanhol e inglês. O Oremos + é uma assinatura opcional com conteúdo adicional.',
     'Oremos es una app gratuita para rezar cada día. Incluye La Palabra de hoy con una reflexión, una rutina diaria con el Examen de la noche, el rosario guiado con los misterios de cada día (Gozosos, Dolorosos, Gloriosos y Luminosos), la vida de los santos y una ayuda privada para preparar la confesión. Funciona sin cuenta y sin internet, en español, portugués e inglés. Oremos + es una suscripción opcional con contenido adicional.',
     'Oremos is a free app for daily prayer. It includes the Verse of the Day with a reflection, a daily routine with the Daily Examen at night, the guided Rosary with each day’s mysteries (Joyful, Sorrowful, Glorious and Luminous), the lives of the saints and private help preparing for confession. It works without an account and offline, in English, Spanish and Portuguese. Oremos + is an optional subscription with extra content.'),
    ('<p class="eyebrow">Perguntas frequentes</p><h2>Tem dúvidas?</h2>', '<p class="eyebrow">Perguntas frequentes</p><h2>Tem dúvidas?</h2>',
     '<p class="eyebrow">Preguntas frecuentes</p><h2>¿Tienes dudas?</h2>', '<p class="eyebrow">FAQ</p><h2>Questions?</h2>'),
    ('<summary>O Oremos é gratuito?</summary><p>Sim. A Palavra de hoje, o terço guiado, o Exame do dia e a preparação para a confissão são gratuitos e sem publicidade. O Oremos + é uma subscrição opcional com conteúdo adicional, como mais santos e os planos de leitura.</p>',
     '<summary>O Oremos é gratuito?</summary><p>Sim. A Palavra de hoje, o terço guiado, o Exame do dia e a preparação para a confissão são gratuitos e sem anúncios. O Oremos + é uma assinatura opcional com conteúdo adicional, como mais santos e os planos de leitura.</p>',
     '<summary>¿Oremos es gratis?</summary><p>Sí. La Palabra de hoy, el rosario guiado, el Examen del día y la preparación para la confesión son gratis y sin anuncios. Oremos + es una suscripción opcional con contenido adicional, como más santos y los planes de lectura.</p>',
     '<summary>Is Oremos free?</summary><p>Yes. The Verse of the Day, the guided Rosary, the Daily Examen and confession prep are free, with no ads. Oremos + is an optional subscription with extra content, like more saints and reading plans.</p>'),
    ('<summary>O que escrevo para a confissão fica guardado onde?</summary><p>Só no seu telemóvel. A lista não é enviada para a internet, está protegida pelo desbloqueio do telemóvel e é apagada depois de se confessar.</p>',
     '<summary>Onde fica o que eu escrevo para a confissão?</summary><p>Só no seu celular. A lista não é enviada para a internet, fica protegida pelo desbloqueio do celular e é excluída depois que você se confessa.</p>',
     '<summary>¿Dónde se guarda lo que escribo para la confesión?</summary><p>Solo en tu celular. La lista no se envía a internet, está protegida por el desbloqueo del celular y se borra después de confesarte.</p>',
     '<summary>Where is what I write for confession stored?</summary><p>Only on your phone. The list is never sent online, it’s protected by your phone’s lock, and it’s deleted after you go to confession.</p>'),
    ('<summary>Preciso de criar uma conta?</summary><p>Não. Pode rezar sem conta. A conta (opcional) serve para usar a Comunidade e sincronizar o Diário entre dispositivos.</p>',
     '<summary>Preciso criar uma conta?</summary><p>Não. Você pode rezar sem conta. A conta (opcional) serve para usar a Comunidade e sincronizar o Diário entre aparelhos.</p>',
     '<summary>¿Necesito crear una cuenta?</summary><p>No. Puedes rezar sin cuenta. La cuenta (opcional) sirve para usar la Comunidad y sincronizar el Diario entre dispositivos.</p>',
     '<summary>Do I need an account?</summary><p>No. You can pray without one. An optional account lets you use Community and sync your Journal across devices.</p>'),
    ('<summary>Está disponível para Android e iPhone?</summary><p>Sim: no Google Play para Android e na App Store para iPhone. No iPhone, ainda não está disponível nos países da União Europeia.</p>',
     '<summary>Está disponível para Android e iPhone?</summary><p>Sim: no Google Play para Android e na App Store para iPhone. No iPhone, ainda não está disponível nos países da União Europeia.</p>',
     '<summary>¿Está disponible para Android y iPhone?</summary><p>Sí: en Google Play para Android y en la App Store para iPhone. En iPhone, todavía no está disponible en los países de la Unión Europea.</p>',
     '<summary>Is it on Android and iPhone?</summary><p>Yes: on Google Play for Android and the App Store for iPhone. On iPhone, it isn’t available in European Union countries yet.</p>'),
    ('<summary>Funciona sem internet?</summary><p>Sim. As orações, o terço e o conteúdo do dia funcionam offline. A Comunidade e a sincronização precisam de ligação.</p>',
     '<summary>Funciona sem internet?</summary><p>Sim. As orações, o terço e o conteúdo do dia funcionam offline. A Comunidade e a sincronização precisam de conexão.</p>',
     '<summary>¿Funciona sin internet?</summary><p>Sí. Las oraciones, el rosario y el contenido del día funcionan sin conexión. La Comunidad y la sincronización necesitan conexión.</p>',
     '<summary>Does it work offline?</summary><p>Yes. The prayers, the Rosary and each day’s content work offline. Community and sync need a connection.</p>'),
    ('<summary>Em que línguas está?</summary><p>Português de Portugal, português do Brasil, espanhol e inglês. Pode mudar em Perfil → Idioma.</p>',
     '<summary>Em quais idiomas está?</summary><p>Português do Brasil, português de Portugal, espanhol e inglês. Você pode mudar em Perfil → Idioma.</p>',
     '<summary>¿En qué idiomas está?</summary><p>Español, portugués (Brasil y Portugal) e inglés. Puedes cambiarlo en Perfil → Idioma.</p>',
     '<summary>Which languages is it in?</summary><p>English, Spanish and Portuguese (Brazil and Portugal). You can change it in Profile → Language.</p>'),
    ('<h2>Comece hoje.</h2>', '<h2>Comece hoje.</h2>', '<h2>Empieza hoy.</h2>', '<h2>Start today.</h2>'),
    ('Cinco minutos com Deus, todos os dias. Gratuito, sem publicidade e sem conta.',
     'Cinco minutos com Deus, todos os dias. Gratuito, sem anúncios e sem conta.',
     'Cinco minutos con Dios, cada día. Gratis, sin anuncios y sin cuenta.',
     'Five minutes with God, every day. Free, no ads, no account.'),
    ('<p>Cinco minutos com Deus, todos os dias. Gratuito e sem publicidade.</p>',
     '<p>Cinco minutos com Deus, todos os dias. Gratuito e sem anúncios.</p>',
     '<p>Cinco minutos con Dios, cada día. Gratis y sin anuncios.</p>',
     '<p>Five minutes with God, every day. Free, with no ads.</p>'),
    ('<h4>Aplicação</h4>', '<h4>Aplicativo</h4>', '<h4>App</h4>', '<h4>App</h4>'),
    ('<a href="privacy.html">Privacidade</a>\n      <a href="terms.html">Termos</a>',
     '<a href="privacy.html">Privacidade</a>\n      <a href="terms.html">Termos</a>',
     '<a href="privacy-en.html">Privacidad</a>\n      <a href="terms-en.html">Términos</a>',
     '<a href="privacy-en.html">Privacy</a>\n      <a href="terms-en.html">Terms</a>'),
    ('<span>Desenvolvido com oração.</span>', '<span>Desenvolvido com oração.</span>', '<span>Hecho con oración.</span>', '<span>Made with prayer.</span>'),
]

# Blocks that point to Portuguese-only pages: kept for pt-BR, replaced for es/en.
PT_ONLY = [
    ('      <a class="pill hide-sm" href="terco-de-hoje.html">Terço de hoje</a>\n      <a class="pill hide-sm" href="ajuda.html">Ajuda</a>\n',
     '      <a class="pill hide-sm" href="terco-de-hoje.html">Terço de hoje</a>\n      <a class="pill hide-sm" href="ajuda.html">Ajuda</a>\n',
     '      <a class="pill hide-sm" href="mailto:oremos.pt@gmail.com">Ayuda</a>\n',
     '      <a class="pill hide-sm" href="mailto:oremos.pt@gmail.com">Help</a>\n'),
    ('      <p class="fine" style="margin-top:16px">Ainda não instalou? <a href="terco-de-hoje.html" style="color:var(--gold)">Reze já o terço de hoje no navegador →</a></p>\n',
     None, '', ''),
    ('''    <div>
      <h4>Rezar</h4>
      <a href="terco-de-hoje.html">Terço de hoje</a>
      <a href="misterios-gozosos.html">Mistérios Gozosos</a>
      <a href="misterios-dolorosos.html">Mistérios Dolorosos</a>
      <a href="misterios-gloriosos.html">Mistérios Gloriosos</a>
      <a href="misterios-luminosos.html">Mistérios Luminosos</a>
    </div>''', None,
     '''    <div>
      <h4>Rezar</h4>
      <a href="#palavra">La Palabra de hoy</a>
      <a href="#rotina">Rutina diaria</a>
      <a href="#terco">Rosario guiado</a>
      <a href="#santos">Santos</a>
      <a href="#confissao">Confesión</a>
    </div>''',
     '''    <div>
      <h4>Pray</h4>
      <a href="#palavra">Verse of the Day</a>
      <a href="#rotina">Daily routine</a>
      <a href="#terco">Guided Rosary</a>
      <a href="#santos">Saints</a>
      <a href="#confissao">Confession</a>
    </div>'''),
    ('      <a href="ajuda.html">Ajuda e Apoio</a>\n', None,
     '      <a href="mailto:oremos.pt@gmail.com">Ayuda</a>\n', '      <a href="mailto:oremos.pt@gmail.com">Help</a>\n'),
]

LANGS = [('br', 'pt-BR', 1), ('es', 'es', 2), ('en', 'en', 3)]


def build(src: str, folder: str, tag: str, i: int) -> str:
    s = src
    for row in T:
        pt, out = row[0], row[i]
        if pt not in s:
            raise SystemExit(f'{folder}: source string not found: {pt[:70]!r}')
        if out is not None:
            s = s.replace(pt, out)
    for row in PT_ONLY:
        pt, out = row[0], row[i]
        if out is None:
            continue
        if pt not in s:
            raise SystemExit(f'{folder}: block not found: {pt[:70]!r}')
        s = s.replace(pt, out)

    # Localized screenshots and Play campaign.
    s = re.sub(r'src="img/(0\d-[a-z-]+\.jpg)"', rf'src="img/{folder}/\1"', s)
    s = s.replace('utm_campaign%3Dhome', f'utm_campaign%3Dhome-{folder}')
    # Canonical / og:url for this language.
    s = s.replace(f'<link rel="canonical" href="{BASE}">', f'<link rel="canonical" href="{BASE}{folder}/">')
    s = s.replace(f'<meta property="og:url" content="{BASE}">', f'<meta property="og:url" content="{BASE}{folder}/">')
    # Language switcher: mark this language as current.
    s = s.replace(' class="on" aria-current="page">PT</a>', '>PT</a>')
    s = s.replace(f'hreflang="{tag}">', f'hreflang="{tag}" class="on" aria-current="page">', 1)
    # Paths: the page lives one folder down. PT link in the switcher goes up to the root.
    s = s.replace('<a href="./" hreflang="pt-PT"', '<a href="../" hreflang="pt-PT"')
    s = re.sub(r'(href|src)="(?!https?:|mailto:|#|\.\./|\./|data:)([^"]+)"', r'\1="../\2"', s)
    # Pages for other languages are siblings: ../br/ etc. already correct after the rewrite.
    return s


def main() -> None:
    src = (ROOT / 'index.html').read_text()
    for folder, tag, i in LANGS:
        out = build(src, folder, tag, i)
        (ROOT / folder).mkdir(exist_ok=True)
        (ROOT / folder / 'index.html').write_text(out)
        print(f'wrote {folder}/index.html')


if __name__ == '__main__':
    main()
