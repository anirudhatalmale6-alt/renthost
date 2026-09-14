/* Seeded marketplace content for the prototype.

   Kept separate from the rules and from the page so it is obvious that none
   of this is real, and so it can be thrown away the day a database exists.
   Dates are fixed strings rather than "now minus n days" — a fixture that
   moves with the clock makes every test flaky. */

(function (root) {
  'use strict';

  var NOW = '2026-09-09T09:00:00Z';   // the prototype's "today"

  var PROPERTIES = [
    {
      id: 'p1', preferredTerm: '36 months', deposit: "Two months' rent", bills: 'Excluded', saStatus: 'Permitted — holiday home permit held', wants: 'An experienced Dubai operator with a permit of their own.', title: '2-bed apartment, marina view', img: 'img/w5.jpg',
      country: 'United Arab Emirates', city: 'Dubai', area: 'Dubai Marina',
      type: 'Apartment', bedrooms: 2, bathrooms: 2, furnished: 'Furnished',
      currency: 'AED', arrangement: 'guaranteed', rentRequested: 11500,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-08T14:00:00Z',
      availableFrom: '1 October 2026',
      features: ['Balcony', 'Shared pool', 'Gym', 'Covered parking', 'High floor'],
      description: 'A bright two-bedroom apartment on a high floor with a full marina outlook. ' +
        'Building permits short-stay letting and has a dedicated guest entrance. Owner is looking for ' +
        'a professional operator to take the whole property on a fixed rent.',
      ownerName: 'Yusuf A.', ownerRole: 'Property Owner', ownerSince: '2026'
    },
    {
      id: 'p2', preferredTerm: '24 months', deposit: "One month's rent", bills: 'Included', saStatus: 'Already operating as a short let', wants: 'A co-host who can take over messaging and changeovers.', title: 'Georgian townhouse, 4 bed', img: 'img/w4.jpg',
      country: 'United Kingdom', city: 'Bath', area: 'Central Bath',
      type: 'House', bedrooms: 4, bathrooms: 2, furnished: 'Part furnished',
      currency: 'GBP', arrangement: 'cohosting', commissionPct: 15,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-06T09:00:00Z',
      availableFrom: 'Immediately',
      features: ['Period features', 'Courtyard garden', 'Log burner', 'Walk to centre'],
      description: 'Family townhouse a short walk from the abbey. Already listed and running, but the ' +
        'owner no longer wants to handle guest messaging and changeovers. Looking for a co-host to take ' +
        'over the day-to-day for a share of revenue.',
      ownerName: 'Helen M.', ownerRole: 'Property Owner', ownerSince: '2025'
    },
    {
      id: 'p3', preferredTerm: '12–36 months', deposit: 'To be agreed', bills: 'Excluded', saStatus: 'Licensed for short stays', wants: 'Either a fixed rent or a co-host — the owner will consider both.', title: 'Studio in the old town', img: 'img/w1.jpg',
      country: 'Portugal', city: 'Lisbon', area: 'Alfama',
      type: 'Studio', bedrooms: 1, bathrooms: 1, furnished: 'Furnished',
      currency: 'EUR', arrangement: 'either', rentRequested: 1400, commissionPct: 18,
      listedBy: 'agent', status: 'available', listedAt: '2026-09-09T07:30:00Z',
      availableFrom: '15 October 2026',
      features: ['Roof terrace', 'Air conditioning', 'Renovated 2025', 'Tram at the door'],
      description: 'Compact studio in a fully renovated building, licensed for short stays. The owner is ' +
        'open to either a fixed rent or a co-hosting arrangement and will consider both properly.',
      ownerName: 'Atlas Property', ownerRole: 'Agent', ownerSince: '2024'
    },
    {
      id: 'p4', preferredTerm: '36 months', deposit: "Two months' rent", bills: 'Excluded', saStatus: 'No restriction known', wants: 'A guaranteed monthly figure and no involvement.', title: '3-bed family home, quiet street', img: 'img/x1.jpg',
      country: 'United Kingdom', city: 'Manchester', area: 'Didsbury',
      type: 'House', bedrooms: 3, bathrooms: 2, furnished: 'Unfurnished',
      currency: 'GBP', arrangement: 'guaranteed', rentRequested: 1850,
      listedBy: 'agent', status: 'available', listedAt: '2026-09-02T11:00:00Z',
      availableFrom: '1 November 2026',
      features: ['Driveway', 'South-facing garden', 'Near hospital', 'Recently rewired'],
      description: 'Well-kept three-bedroom house in a residential street, ten minutes from the hospital ' +
        'and popular with contractors. Landlord wants a guaranteed monthly figure and no involvement.',
      ownerName: 'Northgate Lettings', ownerRole: 'Agent', ownerSince: '2023'
    },
    {
      id: 'p5', preferredTerm: 'Open', deposit: 'Not required', bills: 'Included', saStatus: 'Tourist licence held', wants: 'A co-host with Barcelona experience.', title: 'Penthouse, 3 bed with terrace', img: 'img/w8.jpg',
      country: 'Spain', city: 'Barcelona', area: 'Eixample',
      type: 'Apartment', bedrooms: 3, bathrooms: 2, furnished: 'Furnished',
      currency: 'EUR', arrangement: 'cohosting', commissionPct: null,
      listedBy: 'owner', status: 'discussion', listedAt: '2026-08-28T10:00:00Z',
      availableFrom: 'Immediately',
      features: ['Private terrace', 'Lift', 'Air conditioning', 'Tourist licence held'],
      description: 'Top-floor apartment with a large private terrace and an existing tourist licence. ' +
        'Owner is speaking with two co-hosts and is open to proposals on structure.',
      ownerName: 'Marta R.', ownerRole: 'Property Owner', ownerSince: '2025'
    },
    {
      id: 'p6', preferredTerm: '36 months', deposit: "One month's rent", bills: 'Excluded', saStatus: 'Block permits short stays', wants: 'An operator to take the whole unit on a fixed rent.', title: 'Serviced 1-bed, business district', img: 'img/w9.jpg',
      country: 'United Kingdom', city: 'Birmingham', area: 'Colmore Row',
      type: 'Apartment', bedrooms: 1, bathrooms: 1, furnished: 'Furnished',
      currency: 'GBP', arrangement: 'guaranteed', rentRequested: 1150,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-09T06:00:00Z',
      availableFrom: 'Immediately',
      features: ['Concierge', 'Corporate demand', 'Secure entry', 'Fibre broadband'],
      description: 'One-bed in a managed block with steady corporate demand midweek. Owner has run it as ' +
        'a long let for four years and wants to move to a fixed rent with an operator.',
      ownerName: 'David O.', ownerRole: 'Property Owner', ownerSince: '2026'
    },
    {
      id: 'p7', preferredTerm: '12–24 months', deposit: 'To be agreed', bills: 'Excluded', saStatus: 'Not yet confirmed', wants: "Someone who will keep it occupied outside the family's six weeks.", title: 'Villa with pool, 4 bed', img: 'img/w10.jpg',
      country: 'Portugal', city: 'Faro', area: 'Vale do Lobo',
      type: 'Villa', bedrooms: 4, bathrooms: 3, furnished: 'Furnished',
      currency: 'EUR', arrangement: 'either', rentRequested: 4200, commissionPct: 20,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-05T16:00:00Z',
      availableFrom: '1 December 2026',
      features: ['Private pool', 'Garden', 'Golf nearby', 'Air conditioning', 'Parking'],
      description: 'Detached villa used by the family for six weeks a year, empty the rest of the time. ' +
        'The owner would rather it worked than sat closed, and is genuinely open on structure.',
      ownerName: 'Sofia C.', ownerRole: 'Property Owner', ownerSince: '2025'
    },
    {
      id: 'p8', preferredTerm: '24 months', deposit: "One month's rent", bills: 'Included', saStatus: 'Already operating', wants: 'Now let — kept visible to show a closed listing.', title: 'Loft conversion, 2 bed', img: 'img/w12.jpg',
      country: 'United Kingdom', city: 'Edinburgh', area: 'Leith',
      type: 'Apartment', bedrooms: 2, bathrooms: 1, furnished: 'Furnished',
      currency: 'GBP', arrangement: 'cohosting', commissionPct: 12,
      listedBy: 'owner', status: 'selected', listedAt: '2026-08-20T12:00:00Z',
      availableFrom: 'Let',
      features: ['Exposed brick', 'Roof windows', 'Waterfront walk'],
      description: 'Converted loft near the shore. Owner has now chosen a co-host — kept visible so you ' +
        'can see how a closed listing looks.',
      ownerName: 'Callum S.', ownerRole: 'Property Owner', ownerSince: '2024'
    },
    {
      id: 'p9', preferredTerm: '36 months', deposit: "Two months' rent", bills: 'Excluded', saStatus: '90-night cap applies without planning consent', wants: 'An operator comfortable with longer corporate stays.', title: 'New-build 2 bed, river view', img: 'img/w5.jpg',
      country: 'United Kingdom', city: 'London', area: 'Canary Wharf',
      type: 'Apartment', bedrooms: 2, bathrooms: 2, furnished: 'Furnished',
      currency: 'GBP', arrangement: 'guaranteed', rentRequested: 3400,
      listedBy: 'agent', status: 'available', listedAt: '2026-08-30T09:00:00Z',
      availableFrom: '1 October 2026',
      features: ['River view', 'Gym', 'Concierge', '24h security'],
      description: 'Two-bed in a new riverside development. Note the London 90-night restriction applies ' +
        'to whole-home short lets without planning consent — the owner is aware and open to discussing ' +
        'longer corporate stays.',
      ownerName: 'Meridian Residential', ownerRole: 'Agent', ownerSince: '2022'
    },
    {
      id: 'p10', preferredTerm: '18 months', deposit: 'To be agreed', bills: 'Included', saStatus: 'Already operating with good reviews', wants: 'Help with turnarounds and the calendar, nothing more.', title: 'Cottage, 2 bed, coastal', img: 'img/x1.jpg',
      country: 'United Kingdom', city: 'Whitby', area: 'Old Town',
      type: 'House', bedrooms: 2, bathrooms: 1, furnished: 'Furnished',
      currency: 'GBP', arrangement: 'cohosting', commissionPct: 18,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-01T08:00:00Z',
      availableFrom: 'Immediately',
      features: ['Sea glimpse', 'Wood burner', 'Steps to harbour', 'Pet friendly'],
      description: 'Stone cottage two streets back from the harbour, already trading with good reviews. ' +
        'Owner wants help with the turnarounds and the calendar, nothing more.',
      ownerName: 'Jean W.', ownerRole: 'Property Owner', ownerSince: '2023'
    },
    {
      id: 'p11', preferredTerm: '24 months', deposit: "One month's rent", bills: 'Excluded', saStatus: 'Holiday-home permit held', wants: 'A co-host for guest communication and changeovers.', title: '1-bed apartment, downtown', img: 'img/w9.jpg',
      country: 'United Arab Emirates', city: 'Dubai', area: 'Downtown',
      type: 'Apartment', bedrooms: 1, bathrooms: 1, furnished: 'Furnished',
      currency: 'AED', arrangement: 'cohosting', commissionPct: 15,
      listedBy: 'agent', status: 'available', listedAt: '2026-09-04T13:00:00Z',
      availableFrom: 'Immediately',
      features: ['Fountain view', 'Pool', 'Metro nearby', 'Holiday-home permit held'],
      description: 'One-bed with a permit already in place. The owner runs it themselves and wants a ' +
        'co-host for guest communication and changeovers only.',
      ownerName: 'Gulf Key Realty', ownerRole: 'Agent', ownerSince: '2024'
    },
    {
      id: 'p12', preferredTerm: 'Open', deposit: 'To be agreed', bills: 'Excluded', saStatus: 'Not yet confirmed', wants: 'Proposals on what operators think it is worth.', title: 'Duplex, 3 bed, city centre', img: 'img/w1.jpg',
      country: 'Spain', city: 'Valencia', area: 'Ruzafa',
      type: 'Apartment', bedrooms: 3, bathrooms: 2, furnished: 'Part furnished',
      currency: 'EUR', arrangement: 'guaranteed', rentRequested: null,
      listedBy: 'owner', status: 'available', listedAt: '2026-09-07T10:00:00Z',
      availableFrom: '1 November 2026',
      features: ['Two floors', 'Balcony', 'Renovated kitchen', 'Central'],
      description: 'Duplex in a lively neighbourhood. The owner has not fixed a rent figure and would ' +
        'rather hear what operators think it is worth.',
      ownerName: 'Andres L.', ownerRole: 'Property Owner', ownerSince: '2026'
    }
  ];

  var HOSTS = [
    { id: 'h1', name: 'Northern Stay Co.', city: 'Manchester', country: 'United Kingdom',
      areas: ['Didsbury', 'Chorlton', 'City Centre'], models: ['guaranteed', 'cohosting'],
      years: 6, units: 14, types: ['Apartment', 'House'], pro: true,
      services: ['Guest communication', 'Cleaning coordination', 'Pricing management', 'Photography'],
      bio: 'Six years operating serviced accommodation across south Manchester. Fourteen units live, ' +
           'mostly on guaranteed rent agreements with private landlords.' },
    { id: 'h2', name: 'Aisha K.', city: 'Dubai', country: 'United Arab Emirates',
      areas: ['Dubai Marina', 'JBR', 'Downtown'], models: ['cohosting'],
      years: 3, units: 5, types: ['Apartment'], pro: false,
      services: ['Guest communication', 'Check-in and check-out', 'Review management'],
      bio: 'Co-host working with owners who want to keep control of their property but not the messaging ' +
           'at two in the morning.' },
    { id: 'h3', name: 'Iberia Short Lets', city: 'Lisbon', country: 'Portugal',
      areas: ['Alfama', 'Baixa', 'Príncipe Real'], models: ['guaranteed'],
      years: 8, units: 22, types: ['Apartment', 'Studio'], pro: true,
      services: ['Full operation', 'Pricing management', 'Maintenance coordination', 'Monthly owner reporting'],
      bio: 'Operator taking whole units on fixed rent across central Lisbon. All properties licensed.' },
    { id: 'h4', name: 'Coast & Cove', city: 'Whitby', country: 'United Kingdom',
      areas: ['Whitby', 'Robin Hood\'s Bay', 'Scarborough'], models: ['cohosting'],
      years: 4, units: 9, types: ['House'], pro: false,
      services: ['Cleaning coordination', 'Linen and consumables', 'Guest communication'],
      bio: 'Small local team looking after coastal cottages. Everything done in person, nothing subcontracted.' },
    { id: 'h5', name: 'Meridian Stays', city: 'London', country: 'United Kingdom',
      areas: ['Canary Wharf', 'Stratford', 'Greenwich'], models: ['guaranteed', 'cohosting'],
      years: 5, units: 18, types: ['Apartment'], pro: true,
      services: ['Full operation', 'Corporate lettings', 'Pricing management'],
      bio: 'Corporate-focused operator. Most stays are over thirty nights, which sits outside the ' +
           'London ninety-night restriction.' },
    { id: 'h6', name: 'Barcelona Host Collective', city: 'Barcelona', country: 'Spain',
      areas: ['Eixample', 'Gràcia', 'Born'], models: ['cohosting'],
      years: 7, units: 30, types: ['Apartment'], pro: false,
      services: ['Guest communication', 'Cleaning coordination', 'Review management', 'Photography'],
      bio: 'Co-hosting collective. Owners keep the licence and the relationship; we run the operation.' }
  ];

  /* One worked example of a deal in progress, for the Deal Area screen. */
  var DEAL = {
    property: 'p1',
    host: 'h1',
    stage: 'Documents',
    proposal: { arrangement: 'guaranteed', rentOffered: 11000, currency: 'AED',
                termMonths: 36, startDate: '1 October 2026' },
    docs: [
      { type: 'Public liability insurance', status: 'received', at: '7 Sep' },
      { type: 'Company registration',       status: 'received', at: '7 Sep' },
      { type: 'References',                 status: 'awaiting', at: null },
      { type: 'Proof of identity',          status: 'requested', at: null }
    ],
    messages: [
      { from: 'owner', name: 'Yusuf A.', at: '6 Sep', text: 'Thanks for the proposal. The figure works. Could you send your insurance and company details before we go further?' },
      { from: 'host',  name: 'Northern Stay Co.', at: '7 Sep', text: 'Both uploaded. References will follow tomorrow — I have asked two landlords we work with.' },
      { from: 'owner', name: 'Yusuf A.', at: '7 Sep', text: 'Received, thank you. Once the references are in I am happy to move to agreement.' }
    ]
  };

  var api = { NOW: NOW, PROPERTIES: PROPERTIES, HOSTS: HOSTS, DEAL: DEAL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.RHDATA = api;

})(typeof globalThis !== 'undefined' ? globalThis : this);
