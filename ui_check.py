"""Drive the RentHost prototype and assert what it actually renders.

The brief's hardest rule is that the two commercial models must never be
mixed. check.js proves that of the rules; this proves it of the screen,
which is where it would actually hurt somebody.
"""
import re, sys
from playwright.sync_api import sync_playwright

URL = "file:///var/lib/freelancer/projects/40333782/renthost/index.html"
DEVURL = URL + "?dev=1"
OUT = "/var/lib/freelancer/projects/40333782/renthost/shots"
problems, checks = [], 0


def ok(name, cond, got=None):
    global checks
    checks += 1
    if not cond:
        problems.append("%s%s" % (name, "" if got is None else "  (got %r)" % (got,)))


DEV = "?dev=1"


def view_as(pg, who):
    """Set who is looking, absolutely.

    This used to click a toggle, which flips whatever the state happened to
    be — and because hash navigation does not reload, the state survived a
    goto and the toggle went the wrong way. A select takes a value, so it
    cannot drift.
    """
    pg.select_option("#asWho", who)
    pg.wait_for_timeout(450)
    assert pg.input_value("#asWho") == who, "could not view as %r" % who


def set_pro(pg, want):
    view_as(pg, "pro" if want else "free")


with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1280, "height": 800})
    pg = ctx.new_page()
    errs, failed = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("requestfailed", lambda r: failed.append(r.url))
    pg.goto(DEVURL, wait_until="load", timeout=30000)
    pg.wait_for_timeout(900)

    ok("no javascript errors", not errs, errs)
    ok("every local asset loaded", not [u for u in failed if u.startswith("file:")], failed)

    # --- her palette, exactly as specified ---
    for var, want in (("--forest", "#164A3A"), ("--fresh", "#20A66A"),
                      ("--cream", "#FAF8F3"), ("--ink", "#222222"), ("--grey", "#E9E9E6")):
        got = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('%s').trim()" % var)
        ok("palette %s is %s" % (var, want), got == want, got)
    ff = pg.evaluate("getComputedStyle(document.querySelector('h1')).fontFamily")
    ok("Inter is applied", "Inter" in ff, ff)
    bg = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    ok("cream is the page background", bg == "rgb(250, 248, 243)", bg)

    # the wordmark, not a house icon
    ok("the wordmark reads renthost", pg.inner_text(".logo").strip().lower().startswith("renthost"),
       pg.inner_text(".logo"))
    ok("rent and host are differentiated", pg.eval_on_selector_all(".logo b, .logo i", "e=>e.length") >= 2)

    # --- the navigation she asked for ---
    nav = pg.eval_on_selector_all("#nav a:not([hidden])", "e=>e.map(x=>x.textContent.trim())")
    ok("public navigation is exactly the five items requested",
       nav == ["Find Properties", "Find Hosts", "List a Property", "How It Works", "Pricing"], nav)
    ok("the deal area is now called the Deal Room",
       "Deal Room" in pg.eval_on_selector("#navDeal", "e=>e.textContent"),
       pg.eval_on_selector("#navDeal", "e=>e.textContent"))
    ok("Deal Area is NOT in the public navigation when signed out",
       pg.eval_on_selector("#navDeal", "e=>e.hidden") is True)
    ok("Sign In is offered", pg.eval_on_selector("#signInBtn", "e=>!e.hidden") is True)
    ok("Join RentHost is offered", pg.inner_text("#joinBtn").strip() == "Join RentHost",
       pg.inner_text("#joinBtn"))

    # signing in reveals the private area and swaps the buttons
    view_as(pg, "free")
    ok("signed in, the Deal Area appears", pg.eval_on_selector("#navDeal", "e=>e.hidden") is False)
    ok("and Sign In goes away", pg.eval_on_selector("#signInBtn", "e=>e.hidden") is True)
    ok("Join becomes My account", pg.inner_text("#joinBtn").strip() == "My account")
    view_as(pg, "out")
    ok("signing out hides the Deal Area again",
       pg.eval_on_selector("#navDeal", "e=>e.hidden") is True)

    # --- home ---
    h1 = pg.inner_text("h1").lower()
    ok("hero states her proposition",
       "find professional hosts for your property" in h1 and "properties to operate" in h1, h1)
    ok("it says plainly it is not a guest booking site",
       "not a guest booking site" in pg.inner_text("main").lower())
    routes = pg.eval_on_selector_all(".routes .route b", "e=>e.map(x=>x.textContent.trim())")
    ok("both routes are offered", routes == ["I own a property", "I\u2019m a host"], routes)
    ok("the owner route goes to listing",
       pg.eval_on_selector(".routes .route", "e=>e.getAttribute('href')") == "#/list")
    # .eyebrow is uppercased by CSS and inner_text returns the rendered text
    ok("the brand name is on the page", "renthost" in pg.inner_text("main").lower())
    home = pg.inner_text("main")
    ok("both arrangements are explained in her words",
       "Guaranteed Rent Arrangement" in home and "Co-Hosting" in home)
    ok("co-hosting explicitly says there is no guaranteed rent",
       "no guaranteed rent under co-hosting" in home.lower(), home[:400])
    ok("Open to Either is offered too", "Open to Either" in home)
    ok("home shows property cards", pg.eval_on_selector_all("#homeGrid .card", "e=>e.length") == 6)

    # her three-step How It Works, for both sides, on the homepage
    steps_home = pg.eval_on_selector_all(".howsteps li b", "e=>e.map(x=>x.textContent.trim())")
    ok("owners get three steps and hosts get three", len(steps_home) == 6, steps_home)
    ok("owner step one is list your property", "List your property" in steps_home, steps_home)
    ok("host step one is create your profile",
       "Create your professional profile" in steps_home, steps_home)
    ok("Why RentHost is on the homepage", "Why RentHost" in pg.inner_text("main"))
    # .caps uppercases it; inner_text returns rendered text
    ok("trust and verification is explained",
       "trust and verification" in pg.inner_text("main").lower())
    ok("no decorative verification badges are shown yet",
       "only ever appear once that check has genuinely been completed" in pg.inner_text("main"))
    ok("there is a final call to action",
       pg.eval_on_selector_all(".finalcta .btn", "e=>e.length") == 2)

    # her item 8: the guarantee clarifier must sit BESIDE the term
    ok("the guarantee clarifier appears next to Guaranteed Rent on the homepage",
       "RentHost does not provide or guarantee rental payments" in pg.inner_text(".gnote"),
       pg.inner_text("main")[:200])

    # the landlord CTA must be prominent and free
    ctas = pg.eval_on_selector_all("a[href='#/list']", "e=>e.map(x=>x.textContent.trim())")
    ok("the big landlord CTA is present in her exact words",
       any("LIST YOUR PROPERTY" in c.upper() and "FREE" in c.upper() for c in ctas), ctas)
    ok("there is more than one route into listing", len(ctas) >= 2, ctas)
    big = pg.eval_on_selector(".owncta .btn-g", "e=>getComputedStyle(e).fontSize")
    ok("and it is set larger than body text", float(big.replace("px", "")) >= 16, big)

    # her item 11: development controls must not appear in the public interface
    pg.goto(URL, wait_until="load", timeout=30000)   # no ?dev=1
    pg.wait_for_timeout(700)
    ok("no prototype bar in the public interface",
       pg.eval_on_selector("#protobar", "e=>e.hidden") is True)
    ok("no 'viewing as' control is reachable publicly",
       pg.eval_on_selector("#asWho", "e=>e.getBoundingClientRect().height") == 0)
    body_public = pg.inner_text("body")
    for junk in ("PROTOTYPE", "Seeded content", "nothing saves", "Prototype."):
        ok("public interface does not say %r" % junk, junk not in body_public)
    # her item 20: the disclaimer must be clear, not buried
    foot = pg.inner_text("footer")
    for want in ("RentHost is a marketplace", "not the accommodation provider",
                 "not a guest booking site", "do not provide or guarantee rental payments",
                 "due diligence"):
        ok("footer states %r plainly" % want, want in foot, foot[:160])
    pg.goto(DEVURL, wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    ok("the development bar is still there behind ?dev=1",
       pg.eval_on_selector("#protobar", "e=>e.hidden") is False)
    ok("the footer repeats it and credits the photographs",
       "placeholder" in pg.inner_text("footer").lower() and "Wikimedia" in pg.inner_text("footer"))
    ok("it says plainly it is not a booking site",
       "not a guest booking site" in pg.inner_text("footer").lower())

    # --- How It Works is its own page now ---
    pg.goto(DEVURL + "#/how", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    ok("owner steps show first", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 5)
    pg.click('[data-role="host"]')
    pg.wait_for_timeout(250)
    ok("host has six steps", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 6)
    pg.click('[data-role="agent"]')
    pg.wait_for_timeout(250)
    ok("agent has four steps", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 4)
    ok("agents must confirm authority", "authority" in pg.inner_text("#steps").lower())
    ok("How It Works says RentHost does not guarantee the rent",
       "not a guarantee from RentHost" in pg.inner_text("main"))

    # --- search ---
    pg.goto(DEVURL + "#/properties", wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    total = pg.eval_on_selector_all("#results .card", "e=>e.length")
    ok("all seeded properties listed", total == 12, total)

    def ids():
        return pg.eval_on_selector_all("#results .card", "e=>e.map(x=>x.dataset.open)")

    pg.select_option("#fArr", "guaranteed")
    pg.wait_for_timeout(350)
    gr = ids()
    ok("guaranteed filter includes a guaranteed listing", "p1" in gr, gr)
    ok("guaranteed filter EXCLUDES a co-hosting listing", "p2" not in gr, gr)
    ok("open-to-either appears under guaranteed", "p3" in gr, gr)

    pg.select_option("#fArr", "cohosting")
    pg.wait_for_timeout(350)
    ch = ids()
    ok("co-hosting filter includes a co-hosting listing", "p2" in ch, ch)
    ok("co-hosting filter EXCLUDES a guaranteed listing", "p1" not in ch, ch)
    ok("open-to-either appears under co-hosting too", "p3" in ch, ch)

    pg.select_option("#fArr", "")
    pg.select_option("#fCity", "Dubai")
    pg.wait_for_timeout(350)
    ok("city filter works", sorted(ids()) == ["p1", "p11"], ids())
    ok("the count reflects the filter", "2 properties" in pg.inner_text("#count"), pg.inner_text("#count"))
    pg.click("#clearF")
    pg.wait_for_timeout(400)
    ok("clearing restores everything", pg.eval_on_selector_all("#results .card", "e=>e.length") == 12)

    # empty state
    pg.select_option("#fCity", "Bath")
    pg.select_option("#fArr", "guaranteed")
    pg.wait_for_timeout(350)
    ok("an impossible filter shows an empty state", "No properties match" in pg.inner_text("#results"))
    pg.click("#clearF")
    pg.wait_for_timeout(350)

    # cards carry one commercial line, not a wall of detail
    line = pg.eval_on_selector_all("#results .card .comm .lab", "e=>e.map(x=>x.textContent)")
    ok("every card states its arrangement", len(line) == 12 and all(l.strip() for l in line), line)
    ok("cards use her arrangement wording",
       "GUARANTEED RENT ARRANGEMENT" in line and "CO-HOSTING / MANAGEMENT" in line, list(set(line)))
    first = pg.inner_text("#results .card")
    for want in ("bed", "bath", "Available", "Listed"):
       ok("the card shows %r" % want, want in first, first[:200])
    ok("every card carries the View opportunity action",
       pg.eval_on_selector_all("#results .card .viewop", "e=>e.length") == 12)
    ok("every card can be saved",
       pg.eval_on_selector_all("#results .card .savebtn", "e=>e.length") == 12)

    # sorting
    ok("a sort control exists", pg.locator("#fSort").count() == 1)
    pg.select_option("#fSort", "low")
    pg.wait_for_timeout(450)
    def rents():
        out = []
        for t in pg.eval_on_selector_all("#results .card .det", "e=>e.map(x=>x.textContent)"):
            m = re.search(r"([\d,]+)/month", t)
            out.append(float(m.group(1).replace(",", "")) if m else None)
        return out
    lows = [r for r in rents() if r is not None]
    ok("lowest rent first", lows == sorted(lows), lows)
    pg.select_option("#fSort", "high")
    pg.wait_for_timeout(450)
    highs = [r for r in rents() if r is not None]
    ok("highest rent first", highs == sorted(highs, reverse=True), highs)
    ok("listings with no rent figure never lead a rent sort",
       rents()[0] is not None, rents()[:3])
    pg.select_option("#fSort", "new")
    pg.wait_for_timeout(450)

    # --- a CO-HOSTING property page must never mention guaranteed rent as a figure ---
    pg.goto(DEVURL + "#/property/p2", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    rows = pg.inner_text("#commRows")
    ok("co-hosting page shows the commission", "15%" in rows, rows)
    ok("co-hosting page says the owner still manages it", "Managed by Property Owner" in rows, rows)
    ok("co-hosting page states guaranteed rent is NOT APPLICABLE", "Not applicable" in rows, rows)
    ok("co-hosting page never shows a guaranteed rent figure",
       "Guaranteed Rent Requested" not in rows, rows)

    # --- a GUARANTEED property page must never mention commission ---
    pg.goto(DEVURL + "#/property/p1", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    rows1 = pg.inner_text("#commRows")
    ok("guaranteed page shows the rent requested", "AED 11,500/month" in rows1, rows1)
    ok("guaranteed page says the host manages it", "Managed by the Host" in rows1, rows1)
    ok("guaranteed page never mentions commission", "Commission" not in rows1, rows1)
    detail_text = pg.inner_text("main")
    for want in ("Deal type", "Preferred agreement length", "Deposit / security", "Bills",
                 "Short-let / SA status", "What the owner is looking for"):
        ok("the property page has %r" % want, want in detail_text, detail_text[:200])
    ok("the guarantee clarifier sits beside the arrangement on the property page",
       "RentHost does not provide or guarantee rental payments" in pg.inner_text(".arrbox"),
       pg.inner_text(".arrbox")[:200])
    ok("rent-to-rent is named as the same arrangement",
       "rent-to-rent" in pg.inner_text(".arrbox").lower())
    ok("the address is never published",
       "Dubai Marina, Dubai" in pg.inner_text("main") and not re.search(r"\b\d+\s+\w+ Street\b", pg.inner_text("main")))

    # --- EARLY ACCESS: free host blocked, Pro not ---
    ok("free host sees the early access banner", "Early access property" in pg.inner_text("main"),
       pg.inner_text("main")[:200])
    ok("and the apply button is disabled",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is True)
    view_as(pg, "pro")
    ok("a Pro host may apply immediately",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is False)
    ok("and the banner changes to say so", "you can apply now" in pg.inner_text("main").lower())

    # --- APPLY: guaranteed rent form ---
    pg.click("#applyBtn")
    pg.wait_for_timeout(450)
    sheet = pg.inner_text(".sheet")
    ok("the guaranteed proposal asks for a monthly rent",
       "Guaranteed monthly rent offered" in sheet, sheet[:300])
    ok("the guaranteed proposal NEVER asks for a commission",
       "commission" not in sheet.lower(), [l for l in sheet.split("\n") if "ommission" in l])
    ok("it does not re-ask what the profile already knows",
       "Taken from your profile" in sheet)
    ok("there is a progress indicator", pg.eval_on_selector_all(".prog i", "e=>e.length") == 3)

    # validation must refuse an empty proposal
    pg.click("#sendBtn")
    pg.wait_for_timeout(350)
    ok("an empty proposal is refused", pg.locator(".errs").count() == 1)
    ok("and names the missing field", "required" in pg.inner_text(".errs").lower())

    pg.fill('[data-k="rentOffered"]', "11000")
    pg.click('[data-val="AED"]')
    pg.wait_for_timeout(200)
    pg.click('[data-val="36"]')
    pg.wait_for_timeout(200)
    pg.fill('[data-k="startDate"]', "2026-10-01")
    pg.click("#sendBtn")
    pg.wait_for_timeout(450)
    ok("a complete proposal is accepted", "Proposal sent" in pg.inner_text(".sheet"),
       pg.inner_text(".sheet")[:200])
    pg.click("#closeX")
    pg.wait_for_timeout(300)

    # --- APPLY: co-hosting form ---
    pg.goto(DEVURL + "#/property/p10", wait_until="load", timeout=30000)   # co-hosting, out of early access
    pg.wait_for_timeout(600)
    pg.click("#applyBtn")
    pg.wait_for_timeout(450)
    sheet2 = pg.inner_text(".sheet")
    ok("the co-hosting proposal asks for a commission", "Proposed commission" in sheet2, sheet2[:300])
    ok("the co-hosting proposal NEVER asks for guaranteed rent",
       "guaranteed monthly rent" not in sheet2.lower(), [l for l in sheet2.split("\n") if "uaranteed" in l])
    ok("nor for a term or a start date",
       "agreement length" not in sheet2.lower() and "start date" not in sheet2.lower(), sheet2[:400])
    ok("it offers a service list", pg.eval_on_selector_all("[data-toggle]", "e=>e.length") >= 8)
    ok("no guaranteed-rent input exists in the DOM at all",
       pg.eval_on_selector_all('[data-k="rentOffered"]', "e=>e.length") == 0)

    pg.fill('[data-k="commissionPct"]', "140")
    pg.click("[data-toggle]")
    pg.wait_for_timeout(200)
    pg.click("#sendBtn")
    pg.wait_for_timeout(350)
    ok("commission over 100% is refused", pg.locator(".errs").count() == 1, pg.inner_text(".sheet")[:200])
    pg.fill('[data-k="commissionPct"]', "15")
    pg.click("#sendBtn")
    pg.wait_for_timeout(400)
    ok("a sensible commission is accepted", "Proposal sent" in pg.inner_text(".sheet"))
    pg.click("#closeX")
    pg.wait_for_timeout(300)

    # --- APPLY: open to either must ask first ---
    pg.goto(DEVURL + "#/property/p7", wait_until="load", timeout=30000)    # open to either
    pg.wait_for_timeout(600)
    # p7 was listed 89 hours ago, so it is still inside the 168-hour early
    # access window and a free host genuinely cannot apply. Reloading the page
    # resets the prototype to a free host, so switch to Pro before applying —
    # the gate is doing its job, not misbehaving.
    view_as(pg, "free")
    ok("p7 is still in early access, so a free host cannot apply",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is True)
    view_as(pg, "pro")
    ok("and a Pro host can",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is False)
    ok("an open-to-either page names both options",
       "Guaranteed Rent + Full Management, or Co-Hosting" in pg.inner_text("#commRows"),
       pg.inner_text("#commRows"))
    pg.click("#applyBtn")
    pg.wait_for_timeout(450)
    ok("it asks which arrangement first",
       "How would you like to work" in pg.inner_text(".sheet"), pg.inner_text(".sheet")[:200])
    ok("with exactly two choices", pg.eval_on_selector_all("[data-choose]", "e=>e.length") == 2)
    ok("and no fields yet", pg.eval_on_selector_all(".sheet [data-k]", "e=>e.length") == 0)

    pg.click('[data-choose="cohosting"]')
    pg.wait_for_timeout(400)
    s3 = pg.inner_text(".sheet")
    ok("choosing co-hosting shows the co-hosting form", "Proposed commission" in s3, s3[:250])
    ok("and still no guaranteed rent field",
       pg.eval_on_selector_all('[data-k="rentOffered"]', "e=>e.length") == 0)
    pg.click("#backBtn")
    pg.wait_for_timeout(350)
    ok("back returns to the choice", pg.eval_on_selector_all("[data-choose]", "e=>e.length") == 2)
    pg.click('[data-choose="guaranteed"]')
    pg.wait_for_timeout(400)
    s4 = pg.inner_text(".sheet")
    ok("choosing guaranteed shows the guaranteed form", "Guaranteed monthly rent offered" in s4, s4[:250])
    ok("and no commission field", pg.eval_on_selector_all('[data-k="commissionPct"]', "e=>e.length") == 0)
    pg.click("#closeX")
    pg.wait_for_timeout(300)

    # --- a closed listing cannot be applied for ---
    pg.goto(DEVURL + "#/property/p8", wait_until="load", timeout=30000)    # Host Selected
    pg.wait_for_timeout(600)
    ok("a Host Selected listing shows its status", "Host Selected" in pg.inner_text("main"))
    ok("and offers no apply button", pg.locator("#applyBtn").count() == 0)

    # --- saving ---
    pg.goto(DEVURL + "#/properties", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    pg.eval_on_selector("#results .card .savebtn", "e=>e.click()")
    pg.wait_for_timeout(400)
    ok("saving a property marks it", pg.eval_on_selector_all("#results .savebtn.on", "e=>e.length") == 1)

    # --- hosts ---
    pg.goto(DEVURL + "#/hosts", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    ok("host profiles render", pg.eval_on_selector_all(".hostcard", "e=>e.length") == 6)
    ok("each host can be invited", pg.eval_on_selector_all("[data-invite]", "e=>e.length") == 6)
    ok("pro hosts are marked", pg.eval_on_selector_all(".pro", "e=>e.length") == 3)
    pg.click("[data-invite]")
    pg.wait_for_timeout(300)
    ok("inviting confirms", "Invitation sent" in pg.inner_text(".hostcard"))

    # --- deal area is private ---
    # state survives hash navigation, so set it explicitly rather than
    # inheriting whatever the previous section left behind
    pg.goto(DEVURL + "#/deal", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    view_as(pg, "out")
    ok("signed out, the deal area is withheld",
       "private" in pg.inner_text("main").lower() and pg.locator(".msg").count() == 0,
       pg.inner_text("main")[:160])
    view_as(pg, "free")
    pg.wait_for_timeout(400)
    ok("the conversation renders", pg.eval_on_selector_all(".msg", "e=>e.length") == 3)
    ok("documents render", pg.eval_on_selector_all(".doc", "e=>e.length") == 4)
    ok("progress says 2 of 4", "2 of 4" in pg.inner_text("#docPct"), pg.inner_text("#docPct"))
    ok("it states RentHost does not certify compliance",
       "does not certify" in pg.inner_text("main").lower())
    pg.fill("#dealMsg", "Thanks, references sent this morning.")
    pg.click("#dealSend")
    pg.wait_for_timeout(350)
    ok("sending a message adds it", pg.eval_on_selector_all(".msg", "e=>e.length") == 4)

    # --- pro ---
    pg.goto(DEVURL + "#/pricing", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    ok("three plans", pg.eval_on_selector_all("[data-plan]", "e=>e.length") == 3)
    ok("listing stays free for owners", "free" in pg.inner_text("main").lower())
    ok("free hosts still get real value",
       "Everyone" in pg.inner_text("main"), pg.inner_text("main")[:200])
    ok("pricing is described as configurable",
       "settings, not code" in pg.inner_text("main"))

    # ================= LIST A PROPERTY =================
    # The journey she says matters most: a landlord arrives and can list with
    # minimal effort. Walked end to end, twice — once as an owner, once as an
    # agent, because the agent gets an extra question nobody else should see.

    def wiz_open():
        """Open the wizard at step one.

        After a successful publish the route shows the confirmation screen and
        stays there, so reopening it is not enough — reset via the same button
        a real user would use."""
        pg.goto(DEVURL + "#/list", wait_until="load", timeout=30000)
        pg.wait_for_timeout(300)
        # A hash change does not reload, so the half-filled draft from the last
        # walk would still be in memory and the wizard would resume mid-flow.
        # Reloading keeps the hash and clears the state.
        pg.reload(wait_until="load", timeout=30000)
        pg.wait_for_timeout(700)
        assert pg.locator(".wizstep").count() == 1, "wizard did not open at a step"
        assert "Step 1 of" in pg.inner_text(".wizstep"), \
            "wizard did not reset (%r)" % pg.inner_text(".wizstep")

    wiz_open()
    ok("listing starts at step one", "Step 1 of" in pg.inner_text(".wizstep"), pg.inner_text(".wizstep"))
    ok("one question per screen", pg.eval_on_selector_all(".wizq", "e=>e.length") == 1)
    ok("the first question is who you are", "owner or an agent" in pg.inner_text("#wizQ").lower(),
       pg.inner_text("#wizQ"))
    ok("there is a progress bar", pg.eval_on_selector_all(".wizbar i", "e=>e.length") >= 8)
    ok("no Back button on the first step", pg.locator("#wizBack").count() == 0)
    ok("listing is stated as free", "free" in pg.inner_text(".wiz").lower())

    steps_owner = int(re.search(r"of (\d+)", pg.inner_text(".wizstep")).group(1))
    pg.click('[data-val2="owner"]')
    pg.wait_for_timeout(400)
    ok("choosing owner selects the tile", pg.eval_on_selector_all(".tile.on", "e=>e.length") == 1)

    def qtext():
        return pg.inner_text("#wizQ").lower()

    pg.click("#wizNext"); pg.wait_for_timeout(350)
    ok("an owner is never asked to confirm authority", "authority" not in qtext(), qtext())
    ok("second question is where it is", "where" in qtext(), qtext())

    pg.select_option('[data-d="country"]', "United Kingdom")
    pg.fill('[data-d="city"]', "Leeds")
    pg.fill('[data-d="area"]', "Headingley")
    ok("it promises the address stays private", "privately" in pg.inner_text("#wizBody").lower())
    pg.click("#wizNext"); pg.wait_for_timeout(350)

    ok("then what kind of property", "kind of property" in qtext(), qtext())
    pg.click('[data-val2="House"]'); pg.wait_for_timeout(350)
    pg.click("#wizNext"); pg.wait_for_timeout(350)

    ok("then how big", "how big" in qtext(), qtext())
    beds_before = pg.inner_text("#v_bedrooms")
    pg.click('[data-bump="bedrooms"][data-by="1"]'); pg.wait_for_timeout(350)
    ok("the stepper increments", pg.inner_text("#v_bedrooms") != beds_before,
       (beds_before, pg.inner_text("#v_bedrooms")))
    pg.click('[data-set2="furnished"]'); pg.wait_for_timeout(350)
    pg.click("#wizNext"); pg.wait_for_timeout(350)

    # --- the branch that matters ---
    ok("then how you want to work with a host", "work with a host" in qtext(), qtext())
    # Nobody should be defaulted into a commercial model — it decides how they
    # get paid. Selection must be an explicit act.
    ok("no arrangement is preselected",
       pg.eval_on_selector_all("#wizBody .tile.on", "e=>e.length") == 0)
    arr = pg.inner_text("#wizBody")
    ok("all three arrangements are offered",
       "Guaranteed Rent Arrangement" in arr and "Co-Hosting" in arr and "Open to Either" in arr, arr[:300])

    # co-hosting first: the terms step must ask for commission and nothing else
    pg.click('[data-val2="cohosting"]'); pg.wait_for_timeout(400)
    pg.click("#wizNext"); pg.wait_for_timeout(400)
    terms = pg.inner_text("#wizBody")
    ok("a co-hosting listing asks what commission you OFFER",
       "commission you are offering" in terms.lower(), terms[:300])
    ok("and never asks for a guaranteed rent",
       "guaranteed rent" not in terms.lower().replace("no guaranteed rent", ""), terms[:300])
    ok("no rent input exists in the DOM",
       pg.eval_on_selector_all('[data-d="rentRequested"]', "e=>e.length") == 0)

    # switch back to guaranteed rent and the question changes direction
    pg.click("#wizBack"); pg.wait_for_timeout(350)
    pg.click('[data-val2="guaranteed"]'); pg.wait_for_timeout(400)
    pg.click("#wizNext"); pg.wait_for_timeout(400)
    terms2 = pg.inner_text("#wizBody")
    ok("a guaranteed listing asks what rent you WANT",
       "rent you want" in terms2.lower(), terms2[:300])
    ok("and never asks for a commission",
       pg.eval_on_selector_all('[data-d="commissionPct"]', "e=>e.length") == 0, terms2[:300])
    ok("the figure is optional — an owner may want to hear offers",
       "optional" in terms2.lower())
    pg.fill('[data-d="rentRequested"]', "1400")
    pg.click('[data-val2="GBP"]'); pg.wait_for_timeout(350)
    ok("choosing a currency does not wipe the typed rent",
       pg.input_value('[data-d="rentRequested"]') == "1400",
       pg.input_value('[data-d="rentRequested"]'))
    pg.click("#wizNext"); pg.wait_for_timeout(350)

    ok("then photographs", "photograph" in qtext(), qtext())
    pg.eval_on_selector_all("[data-photo]", "es=>{es[0].click()}")
    pg.wait_for_timeout(400)
    ok("a photograph can be chosen", pg.eval_on_selector_all(".photogrid button.on", "e=>e.length") == 1)
    pg.click("#wizNext"); pg.wait_for_timeout(350)

    ok("then availability", "availability" in qtext(), qtext())
    pg.click('[data-set2="availableFrom"]'); pg.wait_for_timeout(400)
    pg.click("#wizNext"); pg.wait_for_timeout(400)

    ok("last step is the review", "check and publish" in qtext(), qtext())
    review = pg.inner_text(".wiz")
    ok("the review shows the arrangement", "Guaranteed Rent Arrangement" in review, review[:400])
    ok("the review shows the rent", "1,400" in review, review[:400])
    ok("a co-hosting commission is NOT shown on a guaranteed listing",
       "Commission offered" not in review, review[:400])
    ok("nothing is outstanding", pg.locator(".todo").count() == 0, pg.inner_text(".wiz")[:300])
    ok("publish is enabled", pg.eval_on_selector("#wizPublish", "e=>e.disabled") is False)

    pg.click("#wizPublish"); pg.wait_for_timeout(600)
    ok("publishing confirms", "listed" in pg.inner_text(".wiz").lower(), pg.inner_text(".wiz")[:200])

    # and the new listing behaves like any other property
    pg.click("#seeListed"); pg.wait_for_timeout(700)
    ok("the new listing appears in the marketplace",
       pg.eval_on_selector_all("#results .card", "e=>e.length") == 13,
       pg.eval_on_selector_all("#results .card", "e=>e.length"))
    first = pg.inner_text("#results .card")
    ok("it renders through the same card", "Headingley, Leeds" in first, first[:200])
    ok("with the right commercial line", "GUARANTEED RENT" in first and "1,400" in first, first[:200])
    ok("and it is in early access, being new", "EARLY ACCESS" in first, first[:200])

    # --- the agent path gets one extra question ---
    wiz_open()
    pg.click('[data-val2="agent"]'); pg.wait_for_timeout(400)
    steps_agent = int(re.search(r"of (\d+)", pg.inner_text(".wizstep")).group(1))
    ok("the agent flow is exactly one step longer", steps_agent == steps_owner + 1,
       (steps_owner, steps_agent))
    pg.click("#wizNext"); pg.wait_for_timeout(400)
    ok("an agent must confirm authority to market the property",
       "authority" in qtext(), qtext())
    ok("and the wording says so plainly",
       "authority to market" in pg.inner_text("#wizBody").lower(), pg.inner_text("#wizBody")[:200])

    # --- an incomplete listing cannot publish ---
    wiz_open()
    pg.click('[data-val2="owner"]'); pg.wait_for_timeout(350)
    for _ in range(steps_owner - 1):
        if pg.locator("#wizNext").count():
            pg.click("#wizNext"); pg.wait_for_timeout(260)
    ok("an empty listing reaches the review", pg.locator("#wizPublish").count() == 1)
    ok("publish is disabled", pg.eval_on_selector("#wizPublish", "e=>e.disabled") is True)
    ok("and it says what is still needed", pg.locator(".todo").count() == 1)
    todo_links = pg.eval_on_selector_all(".todo a", "e=>e.length")
    ok("each outstanding item is a link back to its step", todo_links >= 4, todo_links)
    pg.click(".todo a"); pg.wait_for_timeout(400)
    ok("clicking one jumps to that step", pg.locator("#wizPublish").count() == 0)

    # --- responsive: no sideways scroll anywhere ---
    for tag, w, h in (("desktop", 1280, 800), ("tablet", 820, 900), ("phone", 390, 780)):
        pg.set_viewport_size({"width": w, "height": h})
        for route in ("", "#/properties", "#/property/p1", "#/hosts", "#/deal", "#/pro"):
            pg.goto(DEVURL + route, wait_until="load", timeout=30000)
            pg.wait_for_timeout(420)
            over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            ok("no sideways scroll at %s %s" % (tag, route or "/"), over <= 2, over)
        # The real invariant is not a breakpoint number: it is that there is
        # always exactly ONE way to navigate. Either the header nav or the
        # bottom tab bar, never both and never neither.
        topnav = pg.eval_on_selector("#nav", "e=>getComputedStyle(e).display") != "none"
        tabbar = pg.eval_on_selector("#tabbar", "e=>getComputedStyle(e).display") != "none"
        ok("exactly one navigation is visible at %s" % tag, topnav != tabbar, (topnav, tabbar))
        if tag == "phone":
            ok("the phone gets the bottom tab bar", tabbar is True)
        if tag == "desktop":
            ok("the desktop gets the header nav", topnav is True)

    # --- screenshots ---
    import os
    os.makedirs(OUT, exist_ok=True)
    pg.set_viewport_size({"width": 1280, "height": 800})
    for name, route in (("home", ""), ("search", "#/properties"), ("detail", "#/property/p1"),
                        ("hosts", "#/hosts"), ("deal", "#/deal"), ("pro", "#/pro")):
        pg.goto(DEVURL + route, wait_until="load", timeout=30000)
        pg.wait_for_timeout(700)
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(200)
        pg.screenshot(path="%s/%s.png" % (OUT, name))
    # the apply flow, which is the thing worth looking at
    pg.goto(DEVURL + "#/property/p7", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    # the responsive loop above navigated to the bare URL, which unlike a hash
    # change really does reload and resets the prototype to signed out
    view_as(pg, "pro")
    pg.click("#applyBtn"); pg.wait_for_timeout(500)
    pg.screenshot(path="%s/apply-choose.png" % OUT)
    pg.click('[data-choose="cohosting"]'); pg.wait_for_timeout(500)
    pg.screenshot(path="%s/apply-cohost.png" % OUT)
    # the listing journey, desktop and phone
    pg.goto(DEVURL + "#/list", wait_until="load", timeout=30000)
    pg.reload(wait_until="load"); pg.wait_for_timeout(700)
    pg.screenshot(path="%s/list-1.png" % OUT)
    pg.click('[data-val2="owner"]'); pg.wait_for_timeout(350)
    for _ in range(4):
        pg.click("#wizNext"); pg.wait_for_timeout(300)
    pg.mouse.move(4, 4); pg.wait_for_timeout(150)
    pg.screenshot(path="%s/list-arrangement.png" % OUT)
    pg.click('[data-val2="cohosting"]'); pg.wait_for_timeout(350)
    pg.click("#wizNext"); pg.wait_for_timeout(400)
    pg.screenshot(path="%s/list-terms-cohost.png" % OUT)

    pg.set_viewport_size({"width": 390, "height": 780})
    pg.goto(DEVURL + "#/list", wait_until="load", timeout=30000)
    pg.reload(wait_until="load"); pg.wait_for_timeout(700)
    pg.screenshot(path="%s/phone-list.png" % OUT)
    pg.goto(DEVURL, wait_until="load", timeout=30000); pg.wait_for_timeout(800)
    pg.screenshot(path="%s/phone-home.png" % OUT)

    pg.goto(DEVURL + "#/properties", wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    pg.screenshot(path="%s/phone-search.png" % OUT)
    pg.goto(DEVURL + "#/property/p2", wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    pg.screenshot(path="%s/phone-detail.png" % OUT)

    ok("still no js errors after all that", not errs, errs)
    br.close()

print("checks: %d" % checks)
print("PROBLEMS: %s" % ("\n  - " + "\n  - ".join(problems) if problems else "none"))
sys.exit(1 if problems else 0)
