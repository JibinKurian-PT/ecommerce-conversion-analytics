/* COMPONENTS + ROUTING. Every card carries the tag of the Q output it is drawn from. */
(function () {
  var D = window.DASH, Q = D.q, C = window.Calc, H = window.Charts, N = C.N, P = C.P;
  var $ = function (s) { return document.querySelector(s); };
  var F0 = { from: C.firstDate, to: C.lastDate, cq: '', cmin: 0, pq: '', pmin: 0 }, F = Object.assign({}, F0), charts = [];
  var by = function (a, k, v) { return a.filter(function (r) { return r[k] === v; })[0]; };
  var q1 = Q.Q1[0], q2 = Q.Q2[0], q3 = Q.Q3[0], q4 = Q.Q4[0], q5 = Q.Q5[0].cart_users_without_recorded_purchase, q6 = Q.Q6[0].purchases_without_prior_recorded_cart, q7 = Q.Q7[0];
  var one = by(Q.Q8, 'visitor_type', 'One Event'), multi = by(Q.Q8, 'visitor_type', 'Multiple Events');
  var cat = by(Q.Q22, 'category_status', 'Category Matched'), catNo = by(Q.Q22, 'category_status', 'No Category Match');
  var av = by(Q.Q23, 'availability_status', 'Availability Matched'), avNo = by(Q.Q23, 'availability_status', 'No Availability Match');
  var aA = by(Q.Q17, 'availability_status', 'Available'), aU = by(Q.Q17, 'availability_status', 'Unavailable'), aK = by(Q.Q17, 'availability_status', 'Unknown / Not Matched');
  var src = function (s) { return '<span class="src" title="' + C.src(s) + '">' + s + '</span>'; };
  var kpi = function (l, v, s, q) { return '<div class="kpi"><div class="kl">' + l + ' ' + src(q) + '</div><div class="kv">' + v + '</div>' + (s ? '<div class="ks">' + s + '</div>' : '') + '</div>'; };
  var card = function (t, sub, body, note, q, cls) { return '<section class="card ' + (cls || '') + '"><div class="ch"><h3>' + t + '</h3>' + (q ? src(q) : '') + '</div>' + (sub ? '<p class="sub">' + sub + '</p>' : '') + body + (note ? '<p class="note">' + note + '</p>' : '') + '</section>'; };
  var ins = function (n, t, b, q) { return '<article class="ins"><div class="in">Insight 0' + n + ' ' + src(q) + '</div><h4>' + t + '</h4><p>' + b + '</p></article>'; };
  var table = function (head, rows) {
    return '<div class="tw"><table><thead><tr>' + head.map(function (h, i) { return '<th scope="col"' + (i ? ' class="n"' : '') + '>' + h + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.map(function (r) { return '<tr>' + r.map(function (c, i) { return i ? '<td class="n">' + c + '</td>' : '<th scope="row">' + c + '</th>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  };
  var ib = function (v, mx, c) { return '<span class="ib"><i class="' + (c || '') + '" style="width:' + (mx ? Math.max(1, 100 * v / mx) : 0).toFixed(1) + '%"></i></span>'; };
  var cb = function (t, v, mx, c) { return '<div class="cb"><span>' + t + '</span>' + ib(v, mx, c) + '</div>'; };
  var empty = '<p class="na">No rows match these filters.</p>';
  var bars = function (rows, max) {
    max = max || Math.max.apply(null, rows.map(function (r) { return r.value; }));
    return '<ul class="bars">' + rows.map(function (r) { return '<li title="' + r.label + ': ' + r.text + (r.sub ? ' (' + r.sub + ')' : '') + '"><span class="l">' + r.label + '</span><span class="t" aria-hidden="true"><span class="f ' + (r.tone || '') + '" style="width:' + Math.max(0.4, 100 * r.value / max).toFixed(2) + '%"></span></span><span class="v">' + r.text + (r.sub ? '<small>' + r.sub + '</small>' : '') + '</span></li>'; }).join('') + '</ul>';
  };
  var page = function (t, purpose, body) { return '<h2 id="ph" tabindex="-1">' + t + '</h2><p class="purpose">' + purpose + '</p>' + body; };
  var chart = function (id, fn) { charts.push({ id: id, fn: fn }); return '<div class="chart" id="c-' + id + '"></div>'; };
  var rows = function () { return C.range(F.from, F.to); };
  var period = function () { return 'Showing ' + rows().length + ' of ' + C.daily.length + ' days, ' + C.dDate(F.from) + ' to ' + C.dDate(F.to) + '.'; };
  var BLUE = '#3B5B7E', GREY = '#7A828C';
  var series = function (t, keys, fmt, yFmt) {
    return function () { var r = rows(); return { title: t, labels: r.map(function (d) { return d.date; }), yFmt: yFmt, series: keys.map(function (k) { return { name: k[0], values: r.map(function (d) { return d[k[1]]; }), color: k[2], fmt: fmt }; }) }; };
  };
  var dateBar = function () {
    return '<div class="filters" role="group" aria-label="Date range"><label>From<input type="date" data-f="from" value="' + F.from + '" min="' + C.firstDate + '" max="' + C.lastDate + '"></label><label>To<input type="date" data-f="to" value="' + F.to + '" min="' + C.firstDate + '" max="' + C.lastDate + '"></label><button type="button" data-reset>Reset filters</button></div><p class="fstate" id="dstate" aria-live="polite">' + period() + ' Date range applies to daily activity and daily conversion charts only.</p>';
  };
  var sel = function (k, vals, label) { return '<label>' + label + '<select data-f="' + k + '">' + vals.map(function (v) { return '<option value="' + v + '"' + (F[k] == v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label>'; };
  var inp = function (k, label) { return '<label>' + label + '<input type="search" data-f="' + k + '" value="' + F[k] + '" inputmode="numeric" autocomplete="off"></label>'; };
  var rng = function (a, k) { return 'Sample sizes in this list range from ' + N(C.min(a, k)) + ' to ' + N(C.max(a, k)) + '.'; };

  /* ---------- category tables ---------- */
  var catBody = function () {
    var q = F.cq.trim(), id = function (r) { return String(r.categoryid).indexOf(q) > -1; };
    var a = Q.Q13.filter(id), b = Q.Q14.filter(function (r) { return id(r) && r.viewers >= F.cmin; }), c = Q.Q15.filter(function (r) { return id(r) && r.viewers >= F.cmin; }).sort(function (x, y) { return y.viewers - x.viewers; });
    var m13 = C.max(Q.Q13, 'total_events'), m14 = C.max(Q.Q14, 'view_to_purchase_pct'), v14 = C.max(Q.Q14, 'viewers'), v15 = C.max(Q.Q15, 'viewers');
    return '<div class="grid">' + card('Top Categories by Activity', 'Showing ' + a.length + ' of ' + Q.Q13.length + ' categories, ordered by total events', a.length ? table(['Category ID', 'Total events', 'Unique visitors', 'Views', 'Add to carts', 'Transactions'], a.map(function (r) { return [r.categoryid, cb(N(r.total_events), r.total_events, m13), N(r.unique_visitors), N(r.views), N(r.add_to_carts), N(r.transactions)]; })) : empty, 'Events are recorded events, not visitors. Category IDs are shown because reliable human-readable category names are not available in the source data.', 'Q13') + '</div>' +
      '<div class="grid">' + card('Categories With Highest Observed Conversion', 'Showing ' + b.length + ' of ' + Q.Q14.length + ' categories, ordered by observed view-to-purchase rate', b.length ? table(['Category ID', 'Viewers (sample size)', 'Cart users', 'Purchasers', 'Observed view → purchase'], b.map(function (r) { return [r.categoryid, cb(N(r.viewers), r.viewers, v14, 'gy'), N(r.cart_users), N(r.purchasers), cb(P(r.view_to_purchase_pct), r.view_to_purchase_pct, m14)]; })) : empty, 'The grey bar shows sample size relative to the largest sample in this list, so a high rate on few viewers is visibly less certain. ' + rng(Q.Q14, 'viewers') + ' A high observed rate marks a category for investigation, not a proven top performer.', 'Q14') + '</div>' +
      '<div class="grid">' + card('Categories With Many Views and Few Recorded Purchases', 'Showing ' + c.length + ' of ' + Q.Q15.length + ' categories, ordered by viewers', c.length ? table(['Category ID', 'Viewers (sample size)', 'Purchasers', 'Observed view → purchase'], c.map(function (r) { return [r.categoryid, cb(N(r.viewers), r.viewers, v15, 'gy'), N(r.purchasers), P(r.view_to_purchase_pct)]; })) : empty, rng(Q.Q15, 'viewers') + ' No recorded purchase does not mean a category performs badly; it requires investigation.', 'Q15') + '</div>';
  };
  /* ---------- product tables ---------- */
  var prodBody = function () {
    var q = F.pq.trim(), id = function (r) { return String(r.itemid).indexOf(q) > -1; }, f = function (a, k) { return a.filter(function (r) { return id(r) && r[k] >= F.pmin; }); };
    var a = f(Q.Q18, 'unique_viewers'), b = f(Q.Q19, 'viewers'), c = f(Q.Q20, 'unique_viewers'), d = f(Q.Q21, 'cart_users');
    var s = function (n, t) { return 'Showing ' + n + ' of ' + Q.Q18.length + ' products' + t; };
    return '<div class="grid g2">' + card('Most Viewed Products', s(a.length, ', ordered by unique viewers'), a.length ? table(['Item ID', 'Unique viewers (sample size)', 'View events'], a.map(function (r) { return [r.itemid, cb(N(r.unique_viewers), r.unique_viewers, C.max(Q.Q18, 'unique_viewers'), 'gy'), N(r.view_events)]; })) : empty, 'Unique viewers count visitors; view events count every recorded view, so a product can have more events than viewers. Product names are not available in the source data.', 'Q18') +
      card('Products With Highest Observed Conversion', s(b.length, ', ordered by observed view-to-purchase rate'), b.length ? table(['Item ID', 'Viewers (sample size)', 'Purchasers', 'Observed view → purchase'], b.map(function (r) { return [r.itemid, cb(N(r.viewers), r.viewers, C.max(Q.Q19, 'viewers'), 'gy'), N(r.purchasers), cb(P(r.view_to_purchase_pct), r.view_to_purchase_pct, C.max(Q.Q19, 'view_to_purchase_pct'))]; })) : empty, rng(Q.Q19, 'viewers') + ' Compare each rate with its sample size; a high percentage on a small sample is not evidence of a best product.', 'Q19') + '</div>' +
      '<div class="grid g2">' + card('High-View Products With No Recorded Purchase', s(c.length, ', ordered by unique viewers'), c.length ? table(['Item ID', 'Unique viewers (sample size)', 'View events'], c.map(function (r) { return [r.itemid, cb(N(r.unique_viewers), r.unique_viewers, C.max(Q.Q20, 'unique_viewers'), 'gy'), N(r.view_events)]; })) : empty, rng(Q.Q20, 'unique_viewers') + ' These products have no recorded purchase in the data; this requires investigation and does not show that the products are poor.', 'Q20') +
      card('Strong Cart Activity With Relatively Low Cart-to-Purchase Conversion', s(d.length, ', ordered by observed cart-to-purchase rate (lowest first)'), d.length ? table(['Item ID', 'Cart users (sample size)', 'Purchasers', 'Observed cart → purchase'], d.map(function (r) { return [r.itemid, cb(N(r.cart_users), r.cart_users, C.max(Q.Q21, 'cart_users'), 'gy'), N(r.purchasers), P(r.cart_to_purchase_pct)]; })) : empty, rng(Q.Q21, 'cart_users') + ' Low observed conversion requires investigation; it does not by itself indicate a problem with the product.', 'Q21') + '</div>';
  };

  var takeaway = function () {
    return 'Observed conversion is strongest at the cart-to-purchase stage and weakest at the transition from product viewing to cart activity. Only ' + P(q2.view_to_cart_pct) + ' of viewers recorded an add-to-cart event, while the stage-based cart-to-purchase rate was ' + P(q2.cart_to_purchase_pct) + ', producing an overall stage-based view-to-purchase rate of ' + P(q2.view_to_purchase_pct) + '. The simplified sequential View \u2192 Cart \u2192 Purchase funnel completed for ' + P(q4.complete_funnel_pct) + ' of all visitors. ' +
      'Availability is also associated with a substantial difference in observed conversion (' + P(aA.view_to_purchase_pct) + ' Available, ' + P(aU.view_to_purchase_pct) + ' Unavailable, ' + P(aK.view_to_purchase_pct) + ' Unknown / Not Matched), although this relationship is observational rather than causal. In addition, incomplete historical category matching (' + P(cat.event_pct) + ' of events matched) and availability matching (' + P(av.event_pct) + ') limit the depth of segmentation. ' +
      'The main opportunities are therefore to investigate the View \u2192 Cart drop-off, availability-related browsing behaviour, high-traffic and low-conversion products and categories, and event-tracking completeness.';
  };
  var pages = [
    { id: 'overview', label: 'Executive overview', render: function () {
      var dr = C.daily.map(function (d) { return d.rate; }), lo = Math.min.apply(null, dr), hi = Math.max.apply(null, dr);
      return page('Executive overview', 'What happened, where the biggest drop is, and what deserves investigation.', dateBar() +
        '<div class="kpis">' + kpi('Unique visitors', N(q1.total_visitors), '', 'Q1') + kpi('Total events', N(q7.total_events), '', 'Q7') + kpi('View → cart', P(q2.view_to_cart_pct), 'cart users ÷ viewers', 'Q2') + kpi('Stage-based Cart → Purchase', P(q2.cart_to_purchase_pct), 'Purchasers ÷ cart users', 'Q2') + kpi('View → purchase', P(q2.view_to_purchase_pct), 'purchasers ÷ viewers', 'Q2') + '</div>' +
        '<div class="grid g2">' + card('Observed Funnel Stage Reach', 'Visitors reaching each stage (stage-based counts, not a strictly sequential journey)', bars([
          { label: 'Viewers', value: q2.viewers, text: N(q2.viewers), sub: '100% of viewers' }, { label: 'Cart users', value: q2.cart_users, text: N(q2.cart_users), sub: P(q2.view_to_cart_pct) + ' of viewers' }, { label: 'Purchasers', value: q2.purchasers, text: N(q2.purchasers), sub: P(q2.view_to_purchase_pct) + ' of viewers' }]), '', 'Q1, Q2') +
        card('Executive takeaway', '', '<p class="take">' + takeaway() + '</p>', '', 'Q2, Q4, Q17, Q22, Q23') + '</div>' +
        '<div class="grid">' + card('Key findings', '', '<ol class="findings cols">' +
          '<li>' + P(q3.view_to_cart_dropoff_pct) + ' of viewers have no recorded cart event, the largest observed drop in the funnel (Q3).</li>' +
          '<li>Stage-based Cart \u2192 Purchase is ' + P(q2.cart_to_purchase_pct) + ' (purchasers \u00f7 cart users); this is not a strictly sequential journey. The separate simplified sequential funnel completes for ' + P(q4.complete_funnel_pct) + ' of visitors (Q2, Q4).</li>' +
          '<li>Observed view-to-purchase was ' + P(aA.view_to_purchase_pct) + ' for Available, ' + P(aU.view_to_purchase_pct) + ' for Unavailable and ' + P(aK.view_to_purchase_pct) + ' for Unknown / Not Matched. Availability is associated with differences in observed conversion (Q17).</li>' +
          '<li>' + P(one.visitor_pct) + ' of visitors recorded only one event; the average is ' + q7.avg_events_per_visitor.toFixed(2) + ' events per visitor (Q7, Q8).</li>' +
          '<li>Across ' + C.daily.length + ' days, observed daily view-to-purchase conversion ranged from ' + P(lo) + ' to ' + P(hi) + ' (Q12).</li>' +
          '<li>Historical matching covers ' + P(cat.event_pct) + ' of events for category and ' + P(av.event_pct) + ' for availability (Q22, Q23).</li></ol>') + '</div>' +
        '<div class="grid g2">' + card('Observed Daily View-to-Purchase Conversion', 'Purchasers ÷ viewers for each day', chart('conv', series('Observed daily view-to-purchase conversion', [['View → purchase', 'rate', BLUE]], P, function (v) { return v.toFixed(1) + '%'; })), 'Daily rates are observed values for that day; they are not adjusted for traffic mix.', 'Q12') +
        card('Observed Conversion by Availability Status', 'View → purchase', bars(Q.Q17.map(function (r) { return { label: r.availability_status, value: r.view_to_purchase_pct, text: P(r.view_to_purchase_pct), sub: N(r.purchasers) + ' purchasers / ' + N(r.viewers) + ' viewers', tone: C.tone(r.availability_status) }; })), 'Availability is associated with differences in observed conversion; this is not a causal result. Unknown / Not Matched means no safe historical availability match was found, not that the item was unavailable.', 'Q17') + '</div>' +
        card('Recommended next actions', 'Prioritised for investigation. None of these is a forecast of revenue impact.', '<ol class="findings">' +
          '<li><b>Investigate the View → Cart drop-off.</b> ' + P(q3.view_to_cart_dropoff_pct) + ' of viewers record no cart event (Q3). Compare product-page to cart behaviour across categories and availability statuses.</li>' +
          '<li><b>Investigate availability-related conversion differences.</b> Unavailable items account for ' + N(by(Q.Q16, 'availability_status', 'Unavailable').total_events) + ' events (Q16) but only ' + P(aU.view_to_purchase_pct) + ' observed conversion (Q17). Check how much browsing lands on unavailable items.</li>' +
          '<li><b>Review high-traffic, low-conversion products and categories.</b> Q15 lists categories with at least ' + N(C.min(Q.Q15, 'viewers')) + ' viewers and no recorded purchase; Q20 lists products with at least ' + N(C.min(Q.Q20, 'unique_viewers')) + ' unique viewers and none; Q21 lists products with strong cart activity and lower cart-to-purchase rates.</li>' +
          '<li><b>Review event tracking.</b> ' + N(q6) + ' purchases have no prior recorded cart (Q6) and ' + N(q5) + ' cart users have no recorded purchase (Q5). Check whether tracking or event ordering contributes.</li>' +
          '<li><b>Improve historical attribute coverage.</b> ' + P(catNo.event_pct) + ' of events have no category match and ' + P(avNo.event_pct) + ' no availability match (Q22, Q23), which limits the segment analysis.</li></ol>', '', 'Q1 to Q23'));
    } },
    { id: 'funnel', label: 'Conversion funnel', render: function () {
      return page('Conversion funnel', 'How visitors progress from viewing to cart to purchase, measured two different ways.',
        '<div class="grid g21">' + card('Observed Funnel Stage Reach', 'Visitors reaching each stage (stage-based counts, not a strictly sequential journey)', bars([
          { label: 'Viewers', value: q2.viewers, text: N(q2.viewers), sub: '100% of viewers' }, { label: 'Cart users', value: q2.cart_users, text: N(q2.cart_users), sub: P(q2.view_to_cart_pct) + ' of viewers' }, { label: 'Purchasers', value: q2.purchasers, text: N(q2.purchasers), sub: P(q2.view_to_purchase_pct) + ' of viewers' }]),
          'Each stage counts visitors with a recorded event of that type. A purchaser is not required to have a recorded cart event, so these counts are not a strictly sequential funnel.', 'Q1, Q2') +
        card('Stage Conversion Rates and Drop-off', '', table(['Stage', 'Observed rate', 'Drop-off'], [
          ['View → cart', P(q2.view_to_cart_pct) + '<br><span class="mut">cart users ÷ viewers</span>', '<span class="neg">' + P(q3.view_to_cart_dropoff_pct) + '</span>'],
          ['Stage-based cart → purchase', P(q2.cart_to_purchase_pct) + '<br><span class="mut">purchasers ÷ cart users</span>', '<span class="neg">' + P(q3.cart_to_purchase_dropoff_pct) + '</span>'],
          ['View → purchase', P(q2.view_to_purchase_pct) + '<br><span class="mut">purchasers ÷ viewers</span>', '<span class="mut">not reported</span>']]), 'Rates from Q2, drop-off from Q3. Stage-based cart → purchase is a stage-based rate: purchasers ÷ cart users. It is not a strictly sequential journey. Q3 reports drop-off for the two adjacent stages only.', 'Q2, Q3') + '</div>' +
        '<div class="grid g3">' + card('Simplified Sequential View → Cart → Purchase Funnel', 'Separate analysis from the stage reach above', '<div class="kv">' + N(q4.completed_funnel_visitors) + '</div><p class="sub">visitors completing all three steps in order, ' + P(q4.complete_funnel_pct) + ' of ' + N(q4.total_visitors) + ' visitors</p>', 'Sequential analysis uses simplified event ordering.', 'Q4', 'seq') +
        card('Cart Users Without a Recorded Purchase', '', '<div class="kv">' + N(q5) + '</div><p class="sub">cart users without recorded purchase</p>', 'This may reflect abandonment, incomplete tracking, or other event-ordering limitations.', '', 'Q5') +
        card('Purchases Without a Preceding Recorded Cart', '', '<div class="kv">' + N(q6) + '</div><p class="sub">purchases without a preceding recorded cart event</p>', 'This may indicate missing or incomplete cart-event tracking or a different recorded event sequence.', '', 'Q6') + '</div>' +
        card('Methodology', '', '<p class="note" style="margin:0;max-width:100ch">Q2 rates are stage-based: View → cart is cart users ÷ viewers, cart → purchase is purchasers ÷ cart users, and view → purchase is purchasers ÷ viewers. The stage-based cart → purchase rate is not a strictly sequential journey. Q4 is a separate simplified sequential analysis. Because ' + N(q6) + ' purchases have no prior recorded cart (Q6), purchasers ÷ cart users is not the same as the share of cart users who purchased. For reference, ' + N(q5) + ' of ' + N(q1.cart_users) + ' cart users (' + P(100 * q5 / q1.cart_users) + ', Q5 ÷ Q1) have no recorded purchase. Sequential analysis uses simplified event ordering.</p>', '', 'Q1 to Q6'));
    } },
    { id: 'behavior', label: 'Customer behavior', render: function () {
      var top = C.sum(Q.Q9, 'total_events');
      return page('Customer behavior', 'How visitors interact with the platform, and how activity moves day to day.', dateBar() +
        '<div class="kpis">' + kpi('Average events per visitor', q7.avg_events_per_visitor.toFixed(2), N(q7.total_events) + ' events / ' + N(q7.unique_visitors) + ' visitors', 'Q7') + kpi('One-event visitors', P(one.visitor_pct), N(one.visitors) + ' visitors', 'Q8') + kpi('Multiple-event visitors', P(multi.visitor_pct), N(multi.visitors) + ' visitors', 'Q8') + '</div>' +
        '<div class="grid g2">' + card('Share of Visitors by Number of Recorded Events', '', bars([{ label: 'One event', value: one.visitor_pct, text: P(one.visitor_pct), sub: N(one.visitors) + ' visitors' }, { label: 'Multiple events', value: multi.visitor_pct, text: P(multi.visitor_pct), sub: N(multi.visitors) + ' visitors' }], 100), '', 'Q8') +
        card('Daily Event Volume and Unique Visitors', period(), chart('ev', series('Daily event volume and unique visitors', [['Total events', 'events', BLUE], ['Unique visitors', 'visitors', GREY]], N, C.K)), 'Unique visitors are counted within each day; a visitor active on several days appears on each, so daily values should not be added together.', 'Q10') + '</div>' +
        '<div class="grid g2">' + card('Daily Views', period(), chart('views', series('Daily views', [['Views', 'views', BLUE]], N, C.K)), '', 'Q11') +
        card('Daily Add-to-Carts and Transactions', period(), chart('ct', series('Daily add-to-carts and transactions', [['Add to carts', 'carts', BLUE], ['Transactions', 'tx', GREY]], N, C.K)), 'Views are shown separately because their volume would flatten these two series.', 'Q11') + '</div>' +
        card('Highest Observed Activity Visitors', 'The ' + Q.Q9.length + ' visitors with the most recorded events', table(['Visitor', 'Total events', 'Views', 'Add to carts', 'Transactions'], Q.Q9.map(function (r, i) { return ['Visitor ' + String(i + 1).padStart(2, '0'), cb(N(r.total_events), r.total_events, C.max(Q.Q9, 'total_events')), N(r.views), N(r.add_to_carts), N(r.transactions)]; })),
          'Together these ' + Q.Q9.length + ' visitors account for ' + N(top) + ' events, ' + P(100 * top / q7.total_events) + ' of all recorded events (Q9 ÷ Q7). They are listed as highest recorded activity only; no classification is made. Visitor identifiers are anonymised in the portfolio presentation; Q9 contains the underlying activity ranking.', 'Q9'));
    } },
    { id: 'categories', label: 'Category performance', render: function () {
      return page('Category performance', 'Differences between categories. Category IDs are used throughout.',
        '<div class="filters" role="group" aria-label="Category filters">' + inp('cq', 'Category ID contains') + sel('cmin', [0, 100, 200, 500, 1000], 'Minimum viewers (conversion lists)') + '<button type="button" data-reset>Reset filters</button></div><div id="cat-out">' + catBody() + '</div>');
    } },
    { id: 'products', label: 'Product performance', render: function () {
      return page('Product performance', 'Products that may deserve investigation. Sample size is shown beside every rate.',
        '<div class="filters" role="group" aria-label="Product filters">' + inp('pq', 'Item ID contains') + sel('pmin', [0, 50, 100, 500, 1000], 'Minimum sample size (viewers; cart users for Q21)') + '<button type="button" data-reset>Reset filters</button></div><div id="prod-out">' + prodBody() + '</div>');
    } },
    { id: 'quality', label: 'Availability & data quality', render: function () {
      var t16 = C.sum(Q.Q16, 'total_events');
      var match = function (a, b) { return bars([{ label: 'Matched', value: a.event_pct, text: P(a.event_pct), sub: N(a.events) + ' events' }, { label: 'Not matched', value: b.event_pct, text: P(b.event_pct), sub: N(b.events) + ' events', tone: 'neu' }], 100); };
      return page('Availability & data quality', 'How availability relates to observed conversion, and how much of the data could be matched safely.',
        '<div class="grid g2">' + card('Observed Conversion by Availability Status', 'View → purchase', bars(Q.Q17.map(function (r) { return { label: r.availability_status, value: r.view_to_purchase_pct, text: P(r.view_to_purchase_pct), sub: N(r.purchasers) + ' purchasers / ' + N(r.viewers) + ' viewers', tone: C.tone(r.availability_status) }; })),
          'Availability is associated with differences in observed conversion; this is not a causal result. Unknown / Not Matched means no safe historical availability match was found, not that the item was unavailable. Visitors can appear in more than one status, so viewers and purchasers are not additive across rows.', 'Q17') +
        card('Activity by Availability Status', '', table(['Status', 'Events', 'Share of events', 'Unique visitors'], Q.Q16.map(function (r) { return [r.availability_status, N(r.total_events), P(100 * r.total_events / t16), N(r.unique_visitors)]; })), 'Share of events is each row ÷ the three rows combined (Q16). Unique visitors overlap across statuses.', 'Q16') + '</div>' +
        '<div class="grid g2">' + card('Events With a Safe Historical Category Match', 'Share of all recorded events', match(cat, catNo), 'Not matched means no safe historical property match was found for the event. It does not mean the category is missing, the product is unavailable, or the product is poor.', 'Q22') +
        card('Events With a Safe Historical Availability Match', 'Share of all recorded events', bars([{ label: 'Matched', value: av.event_pct, text: P(av.event_pct), sub: N(av.events) + ' events' }, { label: 'Not matched', value: avNo.event_pct, text: P(avNo.event_pct), sub: N(avNo.events) + ' events', tone: 'neu' }], 100), 'These unmatched events are the events reported as Unknown / Not Matched in Q16.', 'Q23') + '</div>' +
        '<div class="grid g2">' + card('Dataset Scope', '', table(['Measure', 'Count'], [['Total events', N(q7.total_events) + ' ' + src('Q7')], ['Unique visitors', N(q1.total_visitors) + ' ' + src('Q1')], ['Unique items', N(D.validated.uniqueItems) + ' <span class="mut">earlier validated figure</span>'], ['Unique transaction IDs', N(D.validated.uniqueTransactionIds) + ' <span class="mut">earlier validated figure</span>']]), 'Unique items and transaction IDs come from the earlier validated project figures and are not part of Q1 to Q23.') +
        card('Methodology and Limitations', '', '<ul class="findings" style="margin:0"><li>Category and availability are historical item properties. An event receives a value only when a safe historical match exists; otherwise it is kept and recorded as not matched.</li><li>Availability is coded Available = 1, Unavailable = 0 and Unknown / Not Matched = NULL (no safe historical match).</li><li>The analysis is observational. Associations with category or availability are not causal.</li><li>Stage-based funnel counts (Q2) and the simplified sequential funnel (Q4) measure different things.</li><li>The Q outputs contain no revenue, price, product names or category names, so none are shown.</li><li>Duplicate-event and tracking-anomaly counts are not part of Q1 to Q23.</li></ul>') + '</div>');
    } }
  ];

  function mount() { charts.forEach(function (c) { H.line($('#c-' + c.id), c.fn()); }); }
  function render(mode) {
    var id = location.hash.replace('#/', '') || 'overview', p = by(pages, 'id', id) || pages[0]; charts = [];
    $('#nav').innerHTML = pages.map(function (x) { return '<a href="#/' + x.id + '"' + (x.id === p.id ? ' aria-current="page"' : '') + '>' + x.label + '</a>'; }).join('');
    $('#main').innerHTML = p.render(); document.title = p.label + ' | ' + D.meta.title; mount();
    if (mode === 1) { window.scrollTo(0, 0); $('#ph').focus(); }
  }
  $('#bqt').textContent = D.meta.businessQuestion; $('#bqm').textContent = 'Observational analysis of recorded e-commerce events from ' + C.monthSpan() + '.'; $('#ttl').textContent = D.meta.title; $('#desc').textContent = D.meta.description; $('#foot').textContent = D.meta.source;
  addEventListener('hashchange', function () { F = Object.assign({}, F0); render(1); });
  document.addEventListener('input', function (e) {
    var k = e.target.dataset && e.target.dataset.f; if (!k) return;
    F[k] = /min$/.test(k) ? +e.target.value : e.target.value;
    if (k === 'from' || k === 'to') {
      var ok = F.from && F.to && F.from <= F.to;
      $('#dstate').textContent = ok ? period() + ' Date range applies to daily activity and daily conversion charts only.' : 'Choose a start date that is not after the end date.';
      if (ok) { mount(); document.querySelectorAll('.card .sub').forEach(function (s) { if (/^Showing \d+ of \d+ days/.test(s.textContent)) s.textContent = period(); }); }
    } else if (k === 'cq' || k === 'cmin') $('#cat-out').innerHTML = catBody(); else $('#prod-out').innerHTML = prodBody();
  });
  document.addEventListener('click', function (e) { if (e.target.matches('[data-reset]')) { F = Object.assign({}, F0); render(2); } });
  render(0);
})();
