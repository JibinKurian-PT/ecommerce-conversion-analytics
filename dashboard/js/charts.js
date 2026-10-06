/* CHART CONFIGURATION: interactive line charts drawn from data. Size comes from the container, never hard-coded. */
window.Charts = (function () {
  var mounted = [], C = window.Calc;
  var niceMax = function (m) { if (!m) return 1; var p = Math.pow(10, Math.floor(Math.log10(m / 4))), s = [1, 2, 2.5, 5, 10].map(function (x) { return x * p; }).filter(function (x) { return x * 4 >= m; })[0]; return { step: s, max: Math.ceil(m / s) * s }; };
  function draw(el, cfg) {
    var n = cfg.labels.length, W = Math.max(280, el.clientWidth), Ht = 250, m = { l: 48, r: 12, t: 10, b: 28 };
    if (!n) { el.innerHTML = '<p class="na">No days fall inside the selected date range.</p>'; return; }
    var all = [].concat.apply([], cfg.series.map(function (s) { return s.values; })), nm = niceMax(Math.max.apply(null, all));
    var iw = W - m.l - m.r, ih = Ht - m.t - m.b;
    var x = function (i) { return m.l + (n < 2 ? iw / 2 : i * iw / (n - 1)); }, y = function (v) { return m.t + ih - v / nm.max * ih; };
    var s = '<div class="lg">' + cfg.series.map(function (z) { return '<span><i style="background:' + z.color + '"></i>' + z.name + '</span>'; }).join('') + '</div>' +
      '<svg width="' + W + '" height="' + Ht + '" viewBox="0 0 ' + W + ' ' + Ht + '" role="img" aria-label="' + cfg.title + ', ' + C.dDate(cfg.labels[0]) + ' to ' + C.dDate(cfg.labels[n - 1]) + '">';
    for (var v = 0; v <= nm.max + 1e-9; v += nm.step) s += '<line x1="' + m.l + '" x2="' + (W - m.r) + '" y1="' + y(v) + '" y2="' + y(v) + '" class="gl"/><text x="' + (m.l - 6) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + cfg.yFmt(v) + '</text>';
    var k = Math.max(1, Math.ceil(n / Math.max(1, Math.floor(iw / 80))));
    for (var i = 0; i < n; i += k) s += '<text x="' + x(i) + '" y="' + (Ht - 8) + '" text-anchor="middle">' + C.dShort(cfg.labels[i]) + '</text>';
    cfg.series.forEach(function (z) {
      s += n > 1 ? '<path class="ln" stroke="' + z.color + '" d="' + z.values.map(function (v, i) { return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(v).toFixed(1); }).join('') + '"/>' : '<circle r="3" fill="' + z.color + '" cx="' + x(0) + '" cy="' + y(z.values[0]) + '"/>';
    });
    s += '<line class="cx" y1="' + m.t + '" y2="' + (m.t + ih) + '" x1="0" x2="0" style="display:none"/>' + cfg.series.map(function (z, j) { return '<circle class="dot" r="4" fill="' + z.color + '" style="display:none" data-j="' + j + '"/>'; }).join('') + '<rect class="hit" x="' + m.l + '" y="' + m.t + '" width="' + iw + '" height="' + ih + '" fill="transparent"/></svg><div class="tip" role="status" hidden></div>';
    el.innerHTML = s;
    var svg = el.querySelector('svg'), cx = svg.querySelector('.cx'), tip = el.querySelector('.tip'), dots = svg.querySelectorAll('.dot');
    var show = function (e) {
      var r = svg.getBoundingClientRect(), i = Math.round((e.clientX - r.left - m.l) / iw * (n - 1)); i = Math.max(0, Math.min(n - 1, n < 2 ? 0 : i));
      cx.setAttribute('x1', x(i)); cx.setAttribute('x2', x(i)); cx.style.display = '';
      dots.forEach(function (d, j) { d.setAttribute('cx', x(i)); d.setAttribute('cy', y(cfg.series[j].values[i])); d.style.display = ''; });
      tip.hidden = false; tip.innerHTML = '<b>' + C.dLong(cfg.labels[i]) + '</b>' + cfg.series.map(function (z) { return '<div><i style="background:' + z.color + '"></i>' + z.name + ': ' + z.fmt(z.values[i]) + '</div>'; }).join('');
      var tw = tip.offsetWidth; tip.style.left = Math.max(0, Math.min(W - tw, x(i) + (x(i) > W / 2 ? -tw - 10 : 10))) + 'px'; tip.style.top = '34px';
    };
    var hide = function () { cx.style.display = 'none'; dots.forEach(function (d) { d.style.display = 'none'; }); tip.hidden = true; };
    svg.addEventListener('pointermove', show); svg.addEventListener('pointerdown', show); svg.addEventListener('pointerleave', hide);
  }
  var t; addEventListener('resize', function () { clearTimeout(t); t = setTimeout(function () { mounted.forEach(function (c) { if (document.body.contains(c.el)) draw(c.el, c.cfg); }); }, 120); });
  return { line: function (el, cfg) { mounted = mounted.filter(function (c) { return c.el !== el && document.body.contains(c.el); }); mounted.push({ el: el, cfg: cfg }); draw(el, cfg); } };
})();
