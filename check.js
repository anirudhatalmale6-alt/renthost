/* Assertions on the RentHost rules.  node check.js
   The brief states in three separate places that the commercial models must
   never be mixed together. That is the rule most of this file exists for. */

var RH = require('/var/lib/freelancer/projects/40333782/renthost/renthost.js');
var D  = require('/var/lib/freelancer/projects/40333782/renthost/data.js');

var checks = 0, fails = [];
function ok(name, cond, got) {
  checks++;
  if (!cond) fails.push(name + (got === undefined ? '' : '  (got ' + JSON.stringify(got) + ')'));
}
function eq(name, a, b) { ok(name + '  expected ' + JSON.stringify(b), JSON.stringify(a) === JSON.stringify(b), a); }

var NOW = new Date(D.NOW);
function prop(id) { return D.PROPERTIES.filter(function (p) { return p.id === id; })[0]; }
function keys(fields) { return fields.map(function (f) { return f.key; }); }

/* ===================================================================
   1. THE MODELS MUST NOT MIX
   =================================================================== */

var gr = RH.proposalFor('guaranteed');
var ch = RH.proposalFor('cohosting');

ok('a guaranteed rent proposal asks for a monthly rent', keys(gr.fields).indexOf('rentOffered') >= 0, keys(gr.fields));
ok('a guaranteed rent proposal NEVER asks for commission',
  keys(gr.fields).indexOf('commissionPct') < 0, keys(gr.fields));
ok('a guaranteed rent proposal never asks for a fixed fee or services',
  !keys(gr.fields).some(function (k) { return RH.COHOSTING_ONLY.indexOf(k) >= 0; }), keys(gr.fields));

ok('a co-hosting proposal asks for commission', keys(ch.fields).indexOf('commissionPct') >= 0, keys(ch.fields));
ok('a co-hosting proposal NEVER asks for guaranteed rent',
  keys(ch.fields).indexOf('rentOffered') < 0, keys(ch.fields));
ok('a co-hosting proposal never asks for a term or a start date',
  !keys(ch.fields).some(function (k) { return RH.GUARANTEED_ONLY.indexOf(k) >= 0; }), keys(ch.fields));

/* the two field sets must be genuinely disjoint apart from the message */
var shared = keys(gr.fields).filter(function (k) { return keys(ch.fields).indexOf(k) >= 0; });
eq('the only field the two models share is the message', shared, ['message']);

/* ===================================================================
   2. OPEN TO EITHER — the host must choose first
   =================================================================== */

var either = RH.proposalFor('either');
ok('open to either asks the host to choose before showing anything', either.mustChoose === true);
eq('and offers exactly the two real models', either.choices.map(function (c) { return c.key; }), ['guaranteed', 'cohosting']);
eq('with no fields until they have chosen', either.fields, []);

var chose = RH.proposalFor('either', 'cohosting');
ok('once chosen, it stops asking', chose.mustChoose === false);
eq('and behaves exactly like that model', keys(chose.fields), keys(ch.fields));
eq('choosing guaranteed rent likewise', keys(RH.proposalFor('either', 'guaranteed').fields), keys(gr.fields));
ok('"either" is not itself a choosable proposal', RH.proposalFor('either', 'either').mustChoose === true);
ok('a nonsense choice falls back to asking again', RH.proposalFor('either', 'nonsense').mustChoose === true);

/* ===================================================================
   3. VALIDATION — including rejecting fields that should not be there
   =================================================================== */

ok('a complete guaranteed rent proposal validates',
  RH.validate('guaranteed', { rentOffered: 11000, currency: 'AED', termMonths: 36, startDate: '2026-10-01' }).ok);
ok('a guaranteed proposal missing the rent does not',
  !RH.validate('guaranteed', { currency: 'AED', termMonths: 36, startDate: '2026-10-01' }).ok);
ok('zero rent is rejected',
  !RH.validate('guaranteed', { rentOffered: 0, currency: 'AED', termMonths: 36, startDate: '2026-10-01' }).ok);

/* the important one: a payload carrying the other model's field */
var leak = RH.validate('cohosting', { commissionPct: 15, services: ['Guest communication'], rentOffered: 2000 });
ok('a co-hosting proposal carrying a guaranteed rent is REJECTED', !leak.ok, leak.errors);
ok('and says so plainly', /must not carry rentOffered/.test(leak.errors.join(' ')), leak.errors);

var leak2 = RH.validate('guaranteed', { rentOffered: 2000, currency: 'GBP', termMonths: 12, startDate: 'x', commissionPct: 15 });
ok('a guaranteed proposal carrying a commission is REJECTED', !leak2.ok, leak2.errors);

ok('a complete co-hosting proposal validates',
  RH.validate('cohosting', { commissionPct: 15, services: ['Guest communication'] }).ok);
ok('commission over 100% is rejected',
  !RH.validate('cohosting', { commissionPct: 140, services: ['x'] }).ok);
ok('commission of zero is rejected',
  !RH.validate('cohosting', { commissionPct: 0, services: ['x'] }).ok);
ok('you cannot submit against "open to either" itself', !RH.validate('either', {}).ok);

/* ===================================================================
   4. WHAT THE PAGE AND THE CARD SAY
   =================================================================== */

function sumOf(p) { return RH.commercialSummary(p).map(function (r) { return r.label + ': ' + r.value; }).join(' | '); }

var s1 = sumOf(prop('p1'));   // guaranteed, AED 11,500
ok('a guaranteed page shows the rent requested', /Guaranteed Rent Requested: AED 11,500\/month/.test(s1), s1);
ok('a guaranteed page says the host manages it', /Managed by the Host/.test(s1), s1);
ok('a guaranteed page never says commission', !/Commission/.test(s1), s1);

var s2 = sumOf(prop('p2'));   // co-hosting, 15%
ok('a co-hosting page shows the commission', /Commission: 15%/.test(s2), s2);
ok('a co-hosting page says the OWNER still manages it', /Managed by Property Owner \/ Agent/.test(s2), s2);
/* the brief asks for this line explicitly rather than silence */
ok('a co-hosting page states guaranteed rent is not applicable',
  /Guaranteed Rent: Not applicable/.test(s2), s2);

var s5 = sumOf(prop('p5'));   // co-hosting, no commission set
ok('a co-hosting page with no figure says open to proposals', /Commission: Open to proposals/.test(s5), s5);

eq('a guaranteed card', RH.cardLine(prop('p1')),
   { label: 'GUARANTEED RENT + FULL MANAGEMENT', detail: 'AED 11,500/month requested' });
eq('a co-hosting card', RH.cardLine(prop('p2')),
   { label: 'CO-HOSTING', detail: '15% commission offered' });
eq('a card with no figure', RH.cardLine(prop('p12')),
   { label: 'GUARANTEED RENT + FULL MANAGEMENT', detail: 'Open to proposals' });
eq('an open-to-either card names both', RH.cardLine(prop('p3')),
   { label: 'OPEN TO EITHER', detail: 'Guaranteed Rent or Co-Hosting' });

/* ===================================================================
   5. EARLY ACCESS — configurable, never hard-coded to seven days
   =================================================================== */

var fresh = prop('p6');       // listed 09-09 06:00, "now" is 09-09 09:00
var old   = prop('p8');       // listed 20 Aug

var ea = RH.earlyAccess(fresh, NOW);
ok('a listing from this morning is in early access', ea.active === true);
eq('the default window is 7 days expressed in hours', ea.windowHours, 168);
ok('an old listing is out of early access', RH.earlyAccess(old, NOW).active === false);

/* the point of the requirement: an administrator can change it */
ok('a 24-hour window is respected', RH.earlyAccess(fresh, NOW, 24).active === true);
ok('a 2-hour window has already expired for a 3-hour-old listing',
  RH.earlyAccess(fresh, NOW, 2).active === false);
/* The requirement in one assertion: the SAME listing flips state purely
   because an administrator changed the setting. p9 is 240h old — outside the
   7-day default, inside a 30-day window. */
ok('seven days is a default, not a rule',
  RH.earlyAccess(prop('p9'), NOW).active === false &&
  RH.earlyAccess(prop('p9'), NOW, 24 * 30).active === true);

/* p4 is 166h old against a 168h window — two hours inside. Worth pinning
   because an off-by-one in the boundary would hide everywhere else. */
ok('a listing 2 hours short of the window is still in early access',
  RH.earlyAccess(prop('p4'), NOW).active === true);
ok('and 2 hours later it is not',
  RH.earlyAccess(prop('p4'), NOW, 164).active === false);

var freeHost = { pro: false }, proHost = { pro: true };
ok('a free host cannot apply during early access', RH.canApply(fresh, freeHost, NOW).allowed === false);
eq('and is told why', RH.canApply(fresh, freeHost, NOW).reason, 'early-access');
ok('a pro host can apply immediately', RH.canApply(fresh, proHost, NOW).allowed === true);
eq('for the right reason', RH.canApply(fresh, proHost, NOW).reason, 'pro');
ok('once early access ends, everyone can apply', RH.canApply(old, freeHost, NOW).allowed === true);
eq('and that is the open state', RH.canApply(old, freeHost, NOW).reason, 'open');
/* the marketplace is not behind a paywall — free hosts still SEE everything */
ok('early access never hides a listing, it only delays applying',
  RH.search(D.PROPERTIES, {}).length === D.PROPERTIES.length);

/* ===================================================================
   6. SEARCH
   =================================================================== */

eq('filtering by city', RH.search(D.PROPERTIES, { city: 'Dubai' }).map(function (p) { return p.id; }), ['p1', 'p11']);
eq('filtering by country',
   RH.search(D.PROPERTIES, { country: 'Portugal' }).map(function (p) { return p.id; }), ['p3', 'p7']);
eq('bedroom minimum', RH.search(D.PROPERTIES, { bedroomsMin: 4 }).map(function (p) { return p.id; }), ['p2', 'p7']);
eq('listed by an agent',
   RH.search(D.PROPERTIES, { listedBy: 'agent' }).map(function (p) { return p.id; }), ['p3', 'p4', 'p9', 'p11']);

/* An "open to either" listing must appear under BOTH specific filters,
   or the owner's most flexible listings become the least findable. */
var grResults = RH.search(D.PROPERTIES, { arrangement: 'guaranteed' }).map(function (p) { return p.id; });
var chResults = RH.search(D.PROPERTIES, { arrangement: 'cohosting' }).map(function (p) { return p.id; });
ok('open-to-either shows under the guaranteed rent filter', grResults.indexOf('p3') >= 0, grResults);
ok('open-to-either shows under the co-hosting filter too', chResults.indexOf('p3') >= 0, chResults);
ok('a pure co-hosting listing does NOT show under guaranteed rent', grResults.indexOf('p2') < 0, grResults);
ok('a pure guaranteed listing does NOT show under co-hosting', chResults.indexOf('p1') < 0, chResults);

/* A budget filter must not silently delete co-hosting listings, which have
   no monthly rent to compare against. */
var budget = RH.search(D.PROPERTIES, { budgetMax: 1500 }).map(function (p) { return p.id; });
ok('a budget filter excludes a guaranteed listing above it', budget.indexOf('p9') < 0, budget);
ok('a budget filter keeps a guaranteed listing below it', budget.indexOf('p6') >= 0, budget);
ok('a budget filter does not delete co-hosting listings', budget.indexOf('p2') >= 0, budget);

eq('free-text search', RH.search(D.PROPERTIES, { q: 'marina' }).map(function (p) { return p.id; }), ['p1']);
eq('an empty filter returns everything', RH.search(D.PROPERTIES, {}).length, D.PROPERTIES.length);

/* ===================================================================
   7. PRIVACY — area, never the street
   =================================================================== */

eq('public location is area, city, country', RH.publicLocation(prop('p1')), 'Dubai Marina, Dubai, United Arab Emirates');
ok('no property in the fixture carries a street address',
  !D.PROPERTIES.some(function (p) { return /\b\d+\s+\w+\s+(Street|Road|Avenue|Lane)\b/i.test(JSON.stringify(p)); }));

/* ===================================================================
   8. DOCUMENTS
   =================================================================== */

var dp = RH.docProgress(D.DEAL.docs);
eq('two of four documents received', [dp.received, dp.total], [2, 4]);
eq('which is 50%', dp.pct, 50);
ok('and the set is not complete', dp.complete === false);
ok('an all-received set is complete',
  RH.docProgress([{ status: 'received' }, { status: 'received' }]).complete === true);
ok('an empty set is not "complete"', RH.docProgress([]).complete === false);

/* ===================================================================
   9. MONEY + DETERMINISM
   =================================================================== */

eq('pounds', RH.money(2500, 'GBP'), '£2,500');
eq('dirhams', RH.money(11500, 'AED'), 'AED 11,500');
eq('euros', RH.money(1400, 'EUR'), '€1,400');
ok('the rules are deterministic',
  JSON.stringify(RH.search(D.PROPERTIES, { city: 'Dubai' })) === JSON.stringify(RH.search(D.PROPERTIES, { city: 'Dubai' })));

/* every seeded property must be renderable by every surface */
D.PROPERTIES.forEach(function (p) {
  ok('card line for ' + p.id, !!RH.cardLine(p).label, p.id);
  ok('commercial summary for ' + p.id, RH.commercialSummary(p).length >= 3, p.id);
  ok('known arrangement for ' + p.id, !!RH.ARRANGEMENTS[p.arrangement], p.arrangement);
  ok('known status for ' + p.id, !!RH.PROPERTY_STATUS[p.status], p.status);
});

/* ===================================================================
   10. LISTING A PROPERTY — the landlord's journey
   The brief: step by step, not a long form, conditional questions, and
   an agent must confirm authority to market the property.
   =================================================================== */

var baseDraft = { role: 'owner', country: 'United Kingdom', city: 'Leeds', area: 'Headingley',
                  type: 'House', bedrooms: 3, bathrooms: 1, furnished: 'Furnished',
                  arrangement: 'guaranteed', currency: 'GBP', rentRequested: 1400,
                  photos: ['img/w1.jpg'], availableFrom: 'Immediately' };

var ownerSteps = RH.listingSteps({ role: 'owner' }).map(function (s) { return s.key; });
var agentSteps = RH.listingSteps({ role: 'agent' }).map(function (s) { return s.key; });
ok('an owner is never asked to confirm authority', ownerSteps.indexOf('authority') < 0, ownerSteps);
ok('an agent IS asked to confirm authority', agentSteps.indexOf('authority') >= 0, agentSteps);
eq('and it is asked early, right after the role', agentSteps[1], 'authority');
eq('the agent flow is exactly one step longer', agentSteps.length, ownerSteps.length + 1);
ok('every step has a question as its title',
  RH.listingSteps({}).every(function (s) { return s.title && s.key; }));

/* the terms step is the branch that matters */
var gTerms = RH.listingTerms('guaranteed').map(function (f) { return f.key; });
var cTerms = RH.listingTerms('cohosting').map(function (f) { return f.key; });
ok('listing under guaranteed rent asks what rent you WANT', gTerms.indexOf('rentRequested') >= 0, gTerms);
ok('and never asks for a commission', gTerms.indexOf('commissionPct') < 0, gTerms);
ok('listing under co-hosting asks what commission you OFFER', cTerms.indexOf('commissionPct') >= 0, cTerms);
ok('and never asks for a rent', cTerms.indexOf('rentRequested') < 0, cTerms);
ok('open to either may give both, as guides', RH.listingTerms('either').length === 3);
ok('both figures are optional when listing — an owner may want proposals',
  RH.listingTerms('guaranteed').concat(RH.listingTerms('cohosting'))
    .filter(function (f) { return f.key === 'rentRequested' || f.key === 'commissionPct'; })
    .every(function (f) { return f.required === false; }));

/* the listing side asks a different question from the proposal side */
ok('the owner is asked what they WANT, the host what they OFFER',
  gTerms.indexOf('rentRequested') >= 0 &&
  RH.proposalFor('guaranteed').fields.map(function (f) { return f.key; }).indexOf('rentOffered') >= 0);

/* what is still missing */
eq('a complete owner draft is ready to publish', RH.listingMissing(baseDraft), []);
var m1 = RH.listingMissing({});
ok('an empty draft lists what is missing', m1.length >= 5, m1.length);
ok('and each item points at the step that fixes it',
  m1.every(function (x) { return x.step && x.text; }), m1);
ok('an agent draft without authority is not ready',
  RH.listingMissing(Object.assign({}, baseDraft, { role: 'agent' }))
    .some(function (x) { return x.step === 'authority'; }));
ok('and with it, it is',
  RH.listingMissing(Object.assign({}, baseDraft, { role: 'agent', authority: true })).length === 0);
ok('no photograph means not ready',
  RH.listingMissing(Object.assign({}, baseDraft, { photos: [] }))
    .some(function (x) { return x.step === 'photos'; }));
ok('no arrangement means not ready',
  RH.listingMissing(Object.assign({}, baseDraft, { arrangement: null }))
    .some(function (x) { return x.step === 'arrangement'; }));

/* --- a published draft becomes a normal property ---------------------- */
var made = RH.draftToProperty(baseDraft, 'new1', NOW);
ok('a new listing renders through the same card code', !!RH.cardLine(made).label);
eq('and says what it should', RH.cardLine(made),
   { label: 'GUARANTEED RENT + FULL MANAGEMENT', detail: '£1,400/month requested' });
ok('it is findable by the same search', RH.search([made], { city: 'Leeds' }).length === 1);
ok('an owner listing is marked owner listed', made.listedBy === 'owner');
eq('an agent listing is marked agent listed',
   RH.draftToProperty(Object.assign({}, baseDraft, { role: 'agent' }), 'x', NOW).listedBy, 'agent');
ok('a new listing starts in early access', RH.earlyAccess(made, NOW).active === true);

/* the no-mixing rule again, this time on the way IN.
   An owner who types a rent, then changes their mind and picks co-hosting,
   must not publish a co-hosting listing carrying a guaranteed rent. */
var switched = RH.draftToProperty(
  Object.assign({}, baseDraft, { arrangement: 'cohosting', commissionPct: 15 }), 'x', NOW);
ok('switching to co-hosting drops the rent that was typed earlier',
  switched.rentRequested === undefined, switched);
ok('and keeps the commission', switched.commissionPct === 15);
var switched2 = RH.draftToProperty(
  Object.assign({}, baseDraft, { arrangement: 'guaranteed', commissionPct: 15 }), 'x', NOW);
ok('switching to guaranteed rent drops a commission that was typed earlier',
  switched2.commissionPct === undefined, switched2);
ok('open to either may carry both figures',
  (function () {
    var e = RH.draftToProperty(Object.assign({}, baseDraft, { arrangement: 'either', commissionPct: 18 }), 'x', NOW);
    return e.rentRequested === 1400 && e.commissionPct === 18;
  })());
/* and the page rendering of that switched listing must agree */
ok('a switched listing never shows a rent on its page',
  !/Guaranteed Rent Requested/.test(sumOf(switched)), sumOf(switched));

console.log('checks: ' + checks);
console.log('PROBLEMS: ' + (fails.length ? '\n  - ' + fails.join('\n  - ') : 'none'));
process.exit(fails.length ? 1 : 0);
