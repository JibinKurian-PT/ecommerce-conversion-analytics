/* CALCULATIONS and formatting. Rates come from the Q files; this file only formats, filters and joins. */
(function () {
  var Q = window.DASH.q, NA = 'Not provided';
  var min = function (a, k) { return Math.min.apply(null, a.map(function (r) { return r[k]; })); };
  var max = function (a, k) { return Math.max.apply(null, a.map(function (r) { return r[k]; })); };
  var sum = function (a, k) { return a.reduce(function (s, r) { return s + r[k]; }, 0); };
  // Q10 + Q11 + Q12 joined on event_date
  var d11 = {}, d12 = {};
  Q.Q11.forEach(function (r) { d11[r.event_date] = r; }); Q.Q12.forEach(function (r) { d12[r.event_date] = r; });
  var daily = Q.Q10.map(function (r) {
    var a = d11[r.event_date], b = d12[r.event_date];
    return { date: r.event_date, events: r.total_events, visitors: r.unique_visitors, views: a.views, carts: a.add_to_carts, tx: a.transactions, viewers: b.viewers, purchasers: b.purchasers, rate: b.view_to_purchase_pct };
  }).sort(function (x, y) { return x.date < y.date ? -1 : 1; });
  var D = new Date('1970-01-01T00:00:00Z');
  var fd = function (s, o) { return new Date(s + 'T00:00:00Z').toLocaleDateString('en-GB', Object.assign({ timeZone: 'UTC' }, o)); };
  window.Calc = {
    NA: NA, min: min, max: max, sum: sum, daily: daily,
    firstDate: daily[0].date, lastDate: daily[daily.length - 1].date,
    N: function (n) { return n == null ? NA : Number(n).toLocaleString('en-US'); },
    P: function (v) { return v == null ? NA : Number(v).toFixed(2) + '%'; },
    K: function (v) { return v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : v >= 1e4 ? Math.round(v / 1e3) + 'k' : v >= 1e3 ? (v / 1e3).toFixed(1) + 'k' : String(v); },
    range: function (from, to) { return daily.filter(function (d) { return d.date >= from && d.date <= to; }); },
    dShort: function (s) { return fd(s, { day: 'numeric', month: 'short' }); },
    dLong: function (s) { return fd(s, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }); },
    dDate: function (s) { return fd(s, { day: 'numeric', month: 'short', year: 'numeric' }); },
    monthSpan: function () { var f = daily[0].date, l = daily[daily.length - 1].date, m = function (s) { return fd(s, { month: 'long' }); }; return m(f) + '\u2013' + m(l) + ' ' + fd(l, { year: 'numeric' }); },
    tone: function (s) { return /^available/i.test(s) ? 'pos' : /^unavailable/i.test(s) ? 'neg' : 'neu'; },
    src: function (s) { return s.split(',').map(function (x) { x = x.trim(); return x + ': ' + (window.DASH.queries[x] || ''); }).join(' | '); }
  };
})();
