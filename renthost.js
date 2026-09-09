/* ===========================================================================
   RentHost — the marketplace rules, in one pure file.

   No DOM, no network, no randomness. Same input, same output, in a browser
   or in node. check.js asserts it head-on; index.html renders whatever it
   returns and never decides anything itself.

   Why this file exists at all:

   The brief says, in Part 2, Part 3 and Part 4, that the three commercial
   models must never be mixed together — a Co-Hosting opportunity must never
   show a Guaranteed Rent field, and Guaranteed Rent must never ask for a
   commission. That rule has to hold in the listing form, the card, the
   detail page, the search filters, the application, the messages, the admin
   screen and later a mobile app. If it lives in the markup it will be
   retyped eight times and it will drift on the third. So it lives here once,
   as data, and every surface reads it.
   =========================================================================== */

(function (root) {
  'use strict';

  /* ---------- the three commercial models ------------------------------
     `fields` is the whole of the proposal form for that model. Nothing
     outside this table decides what a host is asked for. */

  var ARRANGEMENTS = {
    guaranteed: {
      key: 'guaranteed',
      label: 'Guaranteed Rent + Full Management',
      short: 'Guaranteed Rent',
      blurb: 'The host operates and manages everything, and pays the owner an agreed fixed rent.',
      hostRole: 'Full operation and management',
      managedBy: 'Host',
      fields: [
        { key: 'rentOffered',  label: 'Guaranteed monthly rent offered', type: 'money',  required: true },
        { key: 'currency',     label: 'Currency',                        type: 'currency', required: true },
        { key: 'termMonths',   label: 'Proposed agreement length',       type: 'term',   required: true },
        { key: 'startDate',    label: 'Proposed start date',             type: 'date',   required: true },
        { key: 'message',      label: 'Short message to the owner',      type: 'text',   required: false }
      ]
    },
    cohosting: {
      key: 'cohosting',
      label: 'Co-Hosting',
      short: 'Co-Hosting',
      blurb: 'The owner keeps managing the property. The co-host provides agreed hosting services for a commission or fee.',
      hostRole: 'Agreed hosting services',
      managedBy: 'Property Owner / Agent',
      fields: [
        { key: 'commissionPct', label: 'Proposed commission',        type: 'percent', required: true },
        { key: 'fixedFee',      label: 'Proposed fixed fee, if any', type: 'money',   required: false },
        { key: 'services',      label: 'Services included',          type: 'services', required: true },
        { key: 'message',       label: 'Short message to the owner', type: 'text',    required: false }
      ]
    },
    either: {
      key: 'either',
      label: 'Open to Either',
      short: 'Open to Either',
      blurb: 'The owner will consider proposals under either arrangement.',
      hostRole: 'Depends on the proposal',
      managedBy: 'Depends on the proposal',
      /* deliberately empty: "Open to Either" is not a thing you can propose.
         The host picks a real model first — see proposalFor(). */
      fields: []
    }
  };

  /* Fields that belong to exactly one model. Used by the tests to prove the
     two never bleed into each other, and by validate() to reject a payload
     that carries a field it has no business carrying. */
  var GUARANTEED_ONLY = ['rentOffered', 'termMonths', 'startDate'];
  var COHOSTING_ONLY  = ['commissionPct', 'fixedFee', 'services'];

  var SERVICES = [
    'Listing creation and copy', 'Photography', 'Pricing management',
    'Guest communication', 'Check-in and check-out', 'Cleaning coordination',
    'Linen and consumables', 'Maintenance coordination', 'Review management',
    'Monthly owner reporting'
  ];

  var PROPERTY_STATUS = {
    available:    { key: 'available',    label: 'Available',          tone: 'good' },
    discussion:   { key: 'discussion',   label: 'Under Discussion',   tone: 'warn' },
    selected:     { key: 'selected',     label: 'Host Selected',      tone: 'off'  },
    unavailable:  { key: 'unavailable',  label: 'No Longer Available',tone: 'off'  },
    expired:      { key: 'expired',      label: 'Expired',            tone: 'off'  }
  };

  var DOC_STATUS = {
    requested: { key: 'requested', label: 'Requested',        tone: 'warn' },
    awaiting:  { key: 'awaiting',  label: 'Awaiting Upload',  tone: 'warn' },
    received:  { key: 'received',  label: 'Received',         tone: 'good' }
  };

  /* ---------- small helpers -------------------------------------------- */

  function num(v, d) { v = parseFloat(v); return isFinite(v) ? v : (d || 0); }
  function has(v) { return v !== undefined && v !== null && String(v).trim() !== ''; }

  var SYMBOL = { GBP: '£', USD: '$', EUR: '€', AED: 'AED ', SAR: 'SAR ', PKR: 'Rs ' };
  function money(amount, currency) {
    var s = SYMBOL[currency] || ((currency || '') + ' ');
    return s + Math.round(num(amount, 0)).toLocaleString('en-GB');
  }

  /* ---------- what a host is asked for --------------------------------
     `chosen` only matters when the listing is Open to Either: the host
     picks a real model and from that point everything behaves exactly as if
     the listing had been that model all along. */

  function proposalFor(arrangement, chosen) {
    var a = ARRANGEMENTS[arrangement];
    if (!a) return null;
    if (a.key !== 'either') {
      return { arrangement: a.key, mustChoose: false, choices: null, fields: a.fields.slice() };
    }
    var pick = ARRANGEMENTS[chosen];
    if (!pick || pick.key === 'either') {
      /* Part 2, item 8: the host chooses which proposal they are submitting
         BEFORE the form appears. No fields until they have. */
      return {
        arrangement: null, mustChoose: true,
        choices: [ARRANGEMENTS.guaranteed, ARRANGEMENTS.cohosting],
        fields: []
      };
    }
    return { arrangement: pick.key, mustChoose: false, choices: null, fields: pick.fields.slice() };
  }

  /* ---------- the commercial block on a property page ------------------ */

  function commercialSummary(p) {
    var a = ARRANGEMENTS[p.arrangement];
    if (!a) return [];
    var rows = [{ label: 'Arrangement', value: a.label }];

    if (a.key === 'guaranteed') {
      rows.push({ label: 'Guaranteed Rent Requested',
                  value: has(p.rentRequested) ? money(p.rentRequested, p.currency) + '/month' : 'Open to proposals' });
      rows.push({ label: 'Host Role', value: a.hostRole });
      rows.push({ label: 'Property Management', value: 'Managed by the Host' });
    } else if (a.key === 'cohosting') {
      rows.push({ label: 'Commission',
                  value: has(p.commissionPct) ? p.commissionPct + '%' : 'Open to proposals' });
      rows.push({ label: 'Property Management', value: 'Managed by ' + a.managedBy });
      /* Stated explicitly rather than omitted. The brief spells this line
         out, and a co-hosting page that simply stays silent about
         guaranteed rent is how somebody assumes there is one. */
      rows.push({ label: 'Guaranteed Rent', value: 'Not applicable' });
    } else {
      rows.push({ label: 'Owner will consider', value: 'Guaranteed Rent + Full Management, or Co-Hosting' });
      rows.push({ label: 'Property Management', value: 'Depends on the arrangement agreed' });
    }
    return rows;
  }

  /* ---------- the one commercial line on a search card ------------------
     Part 2 item 2: keep cards clean. One label, one figure, nothing else. */

  function cardLine(p) {
    var a = ARRANGEMENTS[p.arrangement];
    if (!a) return { label: '', detail: '' };
    if (a.key === 'guaranteed') {
      return { label: 'GUARANTEED RENT + FULL MANAGEMENT',
               detail: has(p.rentRequested) ? money(p.rentRequested, p.currency) + '/month requested' : 'Open to proposals' };
    }
    if (a.key === 'cohosting') {
      return { label: 'CO-HOSTING',
               detail: has(p.commissionPct) ? p.commissionPct + '% commission offered' : 'Open to proposals' };
    }
    return { label: 'OPEN TO EITHER', detail: 'Guaranteed Rent or Co-Hosting' };
  }

  /* ---------- Early Access ---------------------------------------------
     Part 2 item 22: duration is configurable and must NOT be hard-coded to
     seven days, so it is a parameter with a default rather than a literal
     buried below. `now` is passed in — a rules file that reads the clock
     cannot be tested. */

  function earlyAccess(p, now, hours) {
    var windowHours = num(hours, 168);          // 7 days as a DEFAULT, not a rule
    var listed = new Date(p.listedAt).getTime();
    var ends = listed + windowHours * 3600 * 1000;
    var t = (now instanceof Date ? now.getTime() : num(now, 0));
    var active = t < ends;
    return {
      active: active,
      endsAt: new Date(ends),
      hoursLeft: active ? Math.max(0, (ends - t) / 3600000) : 0,
      windowHours: windowHours
    };
  }

  /* Can this host act on this listing right now? Pro hosts always can.
     Free hosts can see it either way — the brief is explicit that the
     marketplace is not behind a paywall — but must wait to APPLY. */
  function canApply(p, host, now, hours) {
    var ea = earlyAccess(p, now, hours);
    if (!ea.active) return { allowed: true, reason: 'open', early: ea };
    if (host && host.pro) return { allowed: true, reason: 'pro', early: ea };
    return { allowed: false, reason: 'early-access', early: ea };
  }

  /* ---------- search ---------------------------------------------------- */

  function matches(p, f) {
    f = f || {};
    if (f.country  && p.country !== f.country) return false;
    if (f.city     && p.city !== f.city) return false;
    if (f.type     && p.type !== f.type) return false;
    if (f.arrangement) {
      /* An "Open to Either" listing genuinely is available under both, so it
         must surface when a host filters for either specific model —
         otherwise the owner's most flexible listings are the ones nobody
         finds. */
      if (f.arrangement !== p.arrangement && p.arrangement !== 'either') return false;
    }
    if (f.listedBy && p.listedBy !== f.listedBy) return false;
    if (f.status   && p.status !== f.status) return false;
    if (has(f.bedroomsMin) && num(p.bedrooms) < num(f.bedroomsMin)) return false;
    if (has(f.bedroomsMax) && num(p.bedrooms) > num(f.bedroomsMax)) return false;
    if (has(f.furnished) && String(p.furnished) !== String(f.furnished)) return false;
    if (f.currency && p.currency !== f.currency) return false;

    if (has(f.budgetMax)) {
      /* Only meaningful against a guaranteed rent figure. A co-hosting
         listing has no monthly rent to compare, so a budget filter must not
         silently delete it from the results. */
      if (p.arrangement === 'guaranteed' && has(p.rentRequested) && num(p.rentRequested) > num(f.budgetMax)) return false;
    }
    if (f.q) {
      var hay = [p.title, p.area, p.city, p.country, p.type].join(' ').toLowerCase();
      if (hay.indexOf(String(f.q).toLowerCase()) < 0) return false;
    }
    return true;
  }

  function search(properties, f) { return (properties || []).filter(function (p) { return matches(p, f); }); }

  /* ---------- validating a proposal ------------------------------------
     Two jobs. The obvious one is required fields. The one that matters is
     rejecting a field the arrangement should never have carried: if a
     Co-Hosting proposal arrives with a guaranteed rent in it, something
     upstream is wrong and quietly saving it would hide the bug. */

  function validate(arrangement, values) {
    var a = ARRANGEMENTS[arrangement];
    var errors = [];
    if (!a || a.key === 'either') {
      return { ok: false, errors: ['Choose Guaranteed Rent or Co-Hosting first.'] };
    }
    values = values || {};

    a.fields.forEach(function (f) {
      if (f.required && !has(values[f.key])) errors.push(f.label + ' is required.');
    });
    if (a.key === 'guaranteed' && has(values.rentOffered) && num(values.rentOffered) <= 0) {
      errors.push('Guaranteed monthly rent offered must be more than zero.');
    }
    if (a.key === 'cohosting' && has(values.commissionPct)) {
      var c = num(values.commissionPct);
      if (c <= 0 || c > 100) errors.push('Commission must be between 0 and 100%.');
    }

    var forbidden = a.key === 'guaranteed' ? COHOSTING_ONLY : GUARANTEED_ONLY;
    forbidden.forEach(function (k) {
      if (has(values[k])) errors.push('A ' + a.label + ' proposal must not carry ' + k + '.');
    });

    return { ok: errors.length === 0, errors: errors };
  }

  /* ---------- document requests ----------------------------------------- */

  var DOC_TYPES = [
    'Proof of identity', 'Company registration', 'Public liability insurance',
    'Professional indemnity insurance', 'References', 'Evidence of previous operating experience',
    'Business information', 'Licences or permits'
  ];

  function docProgress(docs) {
    var list = docs || [];
    var received = list.filter(function (d) { return d.status === 'received'; }).length;
    return { received: received, total: list.length,
             pct: list.length ? Math.round(received / list.length * 100) : 0,
             complete: list.length > 0 && received === list.length };
  }

  /* ---------- privacy ---------------------------------------------------
     Part 3 item 2: show the area, never the street. Building this as a
     function rather than trusting each template to remember is the
     difference between a rule and a hope. */

  function publicLocation(p) {
    return [p.area, p.city].filter(Boolean).join(', ') + (p.country ? ', ' + p.country : '');
  }

  var api = {
    ARRANGEMENTS: ARRANGEMENTS, SERVICES: SERVICES, PROPERTY_STATUS: PROPERTY_STATUS,
    DOC_TYPES: DOC_TYPES, DOC_STATUS: DOC_STATUS,
    GUARANTEED_ONLY: GUARANTEED_ONLY, COHOSTING_ONLY: COHOSTING_ONLY,
    proposalFor: proposalFor, commercialSummary: commercialSummary, cardLine: cardLine,
    earlyAccess: earlyAccess, canApply: canApply,
    matches: matches, search: search, validate: validate,
    docProgress: docProgress, publicLocation: publicLocation, money: money
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.RH = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
