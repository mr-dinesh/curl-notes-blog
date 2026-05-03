(function () {
  var el = document.getElementById('nf-quote');
  var refresh = document.getElementById('nf-refresh');

  var fallback = [
    "Rajnikanth doesn't read books. He stares them down until he gets the information he wants.",
    "Rajnikanth can divide by zero.",
    "Rajnikanth counted to infinity. Twice.",
    "When Rajnikanth does a pushup, he isn't lifting himself up — he's pushing the Earth down."
  ];

  function load() {
    el.classList.add('loading');
    fetch('https://api.chucknorris.io/jokes/random?category=dev,career,science,food,money,sport,travel')
      .then(function (res) {
        if (!res.ok) throw new Error('http ' + res.status);
        return res.json();
      })
      .then(function (data) {
        el.textContent = data.value.replace(/chuck norris/gi, 'Rajnikanth').replace(/chuck/gi, 'Rajni');
      })
      .catch(function () {
        el.textContent = fallback[Math.floor(Math.random() * fallback.length)];
      })
      .finally(function () {
        el.classList.remove('loading');
      });
  }

  refresh.addEventListener('click', function (e) {
    e.preventDefault();
    load();
  });

  load();
})();
