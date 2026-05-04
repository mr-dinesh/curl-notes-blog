(function () {
  var el = document.getElementById('nf-quote');
  var refresh = document.getElementById('nf-refresh');

  var quotes = [
    // Physics
    "Light slows down when it passes Rajnikanth — out of respect.",
    "Rajnikanth doesn't need gravity. The Earth just tries to stay close to him.",
    "When Rajnikanth stares at the Sun, the Sun looks away first.",
    "Rajnikanth doesn't move at the speed of light. Light moves at the speed of Rajnikanth.",
    "Thermodynamics has four laws. The fifth is: Rajnikanth doesn't follow the first four.",
    "Rajnikanth once walked into a black hole. The black hole apologised and let him out.",
    "The Higgs boson gives mass to all particles except Rajnikanth — who is already beyond measure.",
    "Rajnikanth doesn't obey the uncertainty principle. He's always certain.",
    "When Rajnikanth throws a ball, it orbits.",
    "Rajnikanth's heartbeat is the standard unit of time.",
    "Friction doesn't slow Rajnikanth down. Rajnikanth slows friction down.",
    "Schrodinger's cat is alive because Rajnikanth opened the box and told it to be.",
    "Rajnikanth discovered dark matter. It's just the shadow he leaves behind when he walks.",
    "When Rajnikanth stands still, time stops to watch.",
    "The Big Bang was Rajnikanth clearing his throat.",
    // Chemistry
    "Water doesn't boil for Rajnikanth. It volunteers.",
    "Rajnikanth has memorised the periodic table — and added five elements of his own.",
    "The noble gases become excited in Rajnikanth's presence.",
    "Rajnikanth doesn't dissolve in any solvent. Solvents dissolve themselves trying.",
    "Rajnikanth's tears are the only known cure for anything. Too bad he never cries.",
    "When Rajnikanth sneezes, new compounds are created.",
    "Acids neutralise themselves when Rajnikanth enters the lab.",
    "Rajnikanth is the only human with a half-life of infinity.",
    "The activation energy for Rajnikanth is zero. He always reacts.",
    "Rajnikanth once touched a catalyst. The catalyst became more reactive out of shame.",
    "Carbon dating doesn't work on Rajnikanth — he's older than carbon.",
    "Rajnikanth's DNA has six base pairs. Scientists haven't named the extra two yet.",
    "Gold is only 24 carat because Rajnikanth took the other carats.",
    "Rajnikanth doesn't oxidise. Oxygen is too nervous to try.",
    "When Rajnikanth stirs a solution, it self-separates.",
    // Mathematics
    "Rajnikanth can divide by zero.",
    "Rajnikanth counted to infinity — twice.",
    "Rajnikanth knows the last digit of pi.",
    "Euclid's fifth postulate was originally about Rajnikanth. He asked to be removed for fairness.",
    "Rajnikanth proved Fermat's Last Theorem in the margin — of a Post-it note.",
    "The imaginary number i was invented because mathematicians needed something beyond Rajnikanth.",
    "Rajnikanth can square the circle. He just chooses not to, to keep geometry alive.",
    "When Rajnikanth says 'roughly', he means 40 decimal places.",
    "Rajnikanth's age is a prime number. It always will be.",
    "Infinity goes to infinity and beyond — but Rajnikanth was already there.",
    "Rajnikanth doesn't solve equations. Equations confess their answers.",
    "The Fibonacci sequence was supposed to start with Rajnikanth. He said it would take too long.",
    "Matrices are afraid to be singular when Rajnikanth is in the room.",
    "The Riemann Hypothesis is unsolved because Rajnikanth hasn't felt like writing it down yet.",
    "Zero was invented when someone tried to count how many times Rajnikanth has failed.",
    // Sports
    "Rajnikanth doesn't play to win. He plays to let others know what losing feels like.",
    "When Rajnikanth misses in cricket, the stumps still fall — out of respect.",
    "Rajnikanth once scored a goal from the bench. He didn't even know the match was on.",
    "Olympic medals are gold, silver, and bronze. Rajnikanth gets a fourth category.",
    "Rajnikanth's warmup routine is what other athletes call their entire career.",
    "The shot put was invented when Rajnikanth got bored throwing mountains.",
    "Rajnikanth has won every sport he's competed in. Including sports he made up on the day.",
    "When Rajnikanth referees, there are no fouls. Players are too intimidated to foul.",
    "Rajnikanth doesn't need a starting block. He was there before the race was conceived.",
    "The ball always lands where Rajnikanth intends. Sometimes it lands there before he kicks it.",
    "Chess added a new piece after Rajnikanth played once. It doesn't move — it just wins.",
    "Rajnikanth's marathon time is negative. He finishes before the race starts.",
    "When Rajnikanth swims, the water gets out of the way.",
    "Rajnikanth can bowl a no-ball that still takes the wicket.",
    "Rajnikanth holds the world record in every event. Including the ones he didn't enter.",
    // Movies
    "Rajnikanth doesn't need a stunt double. His stunt double needs a stunt double.",
    "Rajnikanth films don't have budgets — they have tributes.",
    "Rajnikanth doesn't read scripts. Scripts audition for him.",
    "The director says 'action'. Rajnikanth says 'in a minute'.",
    "Camera crews double-check their equipment before shooting Rajnikanth — not to miss a frame.",
    "Rajnikanth has won every award he's been nominated for. And several he wasn't.",
    "Rajnikanth doesn't dub his films. The other languages learn his voice.",
    "The first day of a Rajnikanth film earns more than the entire production cost — of the film industry.",
    "Rajnikanth's villain always loses. The villain knows it from the casting call.",
    "Background dancers in Rajnikanth films get standing ovations just for surviving.",
    "Rajnikanth once played a villain. The film was banned — no one could watch the hero lose.",
    "The credits in a Rajnikanth film scroll up faster so he doesn't have to wait.",
    "Rajnikanth's sunglasses have a sequel.",
    "When Rajnikanth walks in slow motion, time apologises for the inconvenience.",
    "Rajnikanth doesn't use CGI. CGI uses Rajnikanth as a benchmark.",
    // History
    "Historians date events as BR (Before Rajnikanth) and AR (After Rajnikanth).",
    "Rajnikanth was not born. He simply appeared, decided to participate, and history rearranged itself.",
    "The Great Wall of China was built to contain Rajnikanth's coolness. It failed.",
    "Rajnikanth discovered electricity. Edison wrote it down.",
    "Every empire that ever fell did so because Rajnikanth left.",
    "The invention of the wheel was inspired by watching Rajnikanth spin a coin.",
    "Napoleon was measured as short because the measuring tape was held against Rajnikanth first.",
    "Rajnikanth's autobiography is filed under History, Science, and Religious Texts.",
    "Julius Caesar's last words were not 'Et tu, Brute?' — he was asking if Rajnikanth had arrived yet.",
    "The industrial revolution was Rajnikanth's lunch break.",
    "The printing press was invented so people could write about Rajnikanth at scale.",
    "Every ancient monument was either built by Rajnikanth, or built to impress him. Most failed.",
    "Darwin's theory of evolution has an asterisk: except Rajnikanth, who was always finished.",
    "Rajnikanth wasn't in either World War. They resolved themselves out of courtesy.",
    "Cleopatra was known for her wit. Had she met Rajnikanth, she would have been known for her silence.",
    // Geography
    "When Rajnikanth sneezes, it registers on the Richter scale.",
    "The Equator was drawn because Rajnikanth told the Earth to sit straight.",
    "Mount Everest is the tallest mountain measured from sea level. It used to be measured from Rajnikanth's eye level.",
    "The Sahara was a forest until Rajnikanth looked at it.",
    "Ocean currents follow Rajnikanth's instructions.",
    "Rajnikanth once got lost. The map apologised and corrected itself.",
    "Volcanoes erupt when Rajnikanth walks nearby and they get excited.",
    "The seven continents were originally one. Rajnikanth spread them apart when he stretched.",
    "Rivers run downhill. Except near Rajnikanth, where they run uphill just to get a better view.",
    "Rajnikanth has been to every country on Earth. Some of them don't know it yet.",
    "Latitude and longitude were invented to track Rajnikanth's last known position.",
    "The Amazon rainforest produces 20% of the world's oxygen. Rajnikanth produces the rest.",
    "Rajnikanth doesn't need GPS. GPS needs Rajnikanth.",
    "The North Pole is cold because Rajnikanth hasn't visited yet.",
    "When Rajnikanth points at a map, it becomes accurate."
  ];

  function load() {
    el.classList.add('loading');
    el.textContent = quotes[Math.floor(Math.random() * quotes.length)];
    el.classList.remove('loading');
  }

  refresh.addEventListener('click', function (e) {
    e.preventDefault();
    load();
  });

  load();
})();
