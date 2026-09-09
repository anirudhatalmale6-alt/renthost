# RentHost — MVP1 prototype

A clickable prototype of the core marketplace journey from the brief:

**Discover → Apply → Connect → Negotiate → Exchange Documents → Agree**

Open `index.html`. Nothing to install, no accounts, no keys, no network calls.

## What is here

| file | what it is |
|---|---|
| `renthost.js` | The marketplace rules. Pure — no DOM, no network, no randomness. |
| `data.js` | Twelve seeded properties, six hosts, one deal in progress. |
| `index.html` | The whole interface. Reads every rule out of `renthost.js`. |
| `check.js` | 123 assertions on the rules. `node check.js` |
| `ui_check.py` | 108 assertions driving the real page. `python3 ui_check.py` |

Both suites must print `PROBLEMS: none`.

## Why the rules are a separate pure file

The brief says in Part 2, Part 3 **and** Part 4 that the three commercial
models must never be mixed: a Co-Hosting opportunity must never show a
Guaranteed Rent field, and a Guaranteed Rent opportunity must never ask for a
commission. That same rule has to hold in the listing form, the card, the
detail page, the search filters, the application, the messages, the emails,
the admin screen and later a mobile app.

If it lives in the markup it gets retyped eight times and drifts on the third.
So it lives in `renthost.js` once, as data, and every surface reads it. That is
what makes it assertable:

- `check.js` proves the two field sets are disjoint apart from the message.
- `ui_check.py` proves the co-hosting form has no guaranteed-rent input **in
  the DOM at all**, not merely hidden.
- `validate()` rejects a payload carrying a field its arrangement should never
  have had — if one ever arrives, something upstream is broken and saving it
  quietly would hide that.

## What is built

- Home, with the proposition and how it works for owners, hosts and agents
- Property search — country, city, type, arrangement, bedrooms, listed-by
- Property cards, one commercial line each, exactly as the brief words them
- Property detail with the commercial block that changes shape per arrangement
- **Apply** — conditional by arrangement, one question per screen, progress bar
- **Open to Either** — the host picks the model first, then gets that form only
- Early Access gating, Pro versus Free
- Host search and Invite Host, so the marketplace runs both ways
- Deal area — conversation, proposal, document requests with status
- RentHost Pro pricing
- Mobile-first throughout; a bottom tab bar replaces the header nav on phones

## What is deliberately not built

No accounts, no database, no messaging server, no file storage, no Stripe. This
is a prototype of the *journey and the rules*, so those decisions can be
corrected before anything is built on top of them. Nothing here persists — a
refresh resets it.

The "Free host / Pro host" button in the header is a prototype switch so the
Early Access behaviour can be seen from both sides without signing up.

## Notes on the model

- **Early Access is configurable.** `earlyAccess(p, now, hours)` takes the
  window as a parameter with a default of 168 hours. Seven days is a default,
  not a rule, and there is a test asserting the same listing flips state purely
  because the setting changed.
- **Open to Either surfaces under both filters.** Otherwise an owner's most
  flexible listings become the least findable.
- **A budget filter never deletes co-hosting listings**, which have no monthly
  rent to compare against.
- **Only the area is ever published**, never the street.

## Photographs

Placeholders from Wikimedia Commons, credited in the footer and in
`img/credits-used.json` as their licences require. Replace them with real
property photography before launch.
