"""Drive the RentHost prototype and assert what it actually renders.

The brief's hardest rule is that the two commercial models must never be
mixed. check.js proves that of the rules; this proves it of the screen,
which is where it would actually hurt somebody.
"""
import re, sys
from playwright.sync_api import sync_playwright

URL = "https://anirudhatalmale6-alt.github.io/renthost/index.html"
OUT = "/var/lib/freelancer/projects/40333782/renthost/shots"
problems, checks = [], 0


def ok(name, cond, got=None):
    global checks
    checks += 1
    if not cond:
        problems.append("%s%s" % (name, "" if got is None else "  (got %r)" % (got,)))


def set_pro(pg, want):
    """Set the prototype's host to Pro or Free deterministically.

    Navigating by hash does NOT reload the page, so the prototype's state
    survives a goto. Blindly clicking the toggle therefore flips whatever it
    happened to be, which is how this suite ended up asserting against a Free
    host on one page and a Pro host on the next. Read, then act.
    """
    label = pg.inner_text("#whoBtn").strip().lower()
    is_pro = label.startswith("pro")
    if is_pro != want:
        pg.click("#whoBtn")
        pg.wait_for_timeout(420)
    assert pg.inner_text("#whoBtn").strip().lower().startswith("pro" if want else "free"), \
        "could not set pro=%s (button says %r)" % (want, pg.inner_text("#whoBtn"))


with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1280, "height": 800})
    pg = ctx.new_page()
    errs, failed = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("requestfailed", lambda r: failed.append(r.url))
    pg.goto(URL, wait_until="load", timeout=30000)
    pg.wait_for_timeout(900)

    ok("no javascript errors", not errs, errs)
    ok("every local asset loaded", not [u for u in failed if u.startswith("https://anirudhatalmale6-alt.github.io")], failed)

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

    # --- home ---
    ok("hero states the proposition",
       "professional hosts" in pg.inner_text("h1").lower(), pg.inner_text("h1"))
    ok("home shows property cards", pg.eval_on_selector_all("#homeGrid .card", "e=>e.length") == 6)
    ok("it says plainly it is not a booking site",
       "not a guest booking site" in pg.inner_text("footer").lower())

    # role switcher on How It Works
    ok("owner steps show first", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 5)
    pg.click('[data-role="host"]')
    pg.wait_for_timeout(250)
    ok("host has six steps", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 6)
    pg.click('[data-role="agent"]')
    pg.wait_for_timeout(250)
    ok("agent has four steps", pg.eval_on_selector_all("#steps .step", "e=>e.length") == 4)
    ok("agents must confirm authority", "authority" in pg.inner_text("#steps").lower())

    # --- search ---
    pg.goto(URL + "#/properties", wait_until="load", timeout=30000)
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
    ok("cards use the brief's exact wording",
       "GUARANTEED RENT + FULL MANAGEMENT" in line and "CO-HOSTING" in line, list(set(line)))

    # --- a CO-HOSTING property page must never mention guaranteed rent as a figure ---
    pg.goto(URL + "#/property/p2", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    rows = pg.inner_text("#commRows")
    ok("co-hosting page shows the commission", "15%" in rows, rows)
    ok("co-hosting page says the owner still manages it", "Managed by Property Owner" in rows, rows)
    ok("co-hosting page states guaranteed rent is NOT APPLICABLE", "Not applicable" in rows, rows)
    ok("co-hosting page never shows a guaranteed rent figure",
       "Guaranteed Rent Requested" not in rows, rows)

    # --- a GUARANTEED property page must never mention commission ---
    pg.goto(URL + "#/property/p1", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    rows1 = pg.inner_text("#commRows")
    ok("guaranteed page shows the rent requested", "AED 11,500/month" in rows1, rows1)
    ok("guaranteed page says the host manages it", "Managed by the Host" in rows1, rows1)
    ok("guaranteed page never mentions commission", "Commission" not in rows1, rows1)
    ok("the address is never published",
       "Dubai Marina, Dubai" in pg.inner_text("main") and not re.search(r"\b\d+\s+\w+ Street\b", pg.inner_text("main")))

    # --- EARLY ACCESS: free host blocked, Pro not ---
    ok("free host sees the early access banner", "Early access property" in pg.inner_text("main"),
       pg.inner_text("main")[:200])
    ok("and the apply button is disabled",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is True)
    set_pro(pg, True)
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
    pg.goto(URL + "#/property/p10", wait_until="load", timeout=30000)   # co-hosting, out of early access
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
    pg.goto(URL + "#/property/p7", wait_until="load", timeout=30000)    # open to either
    pg.wait_for_timeout(600)
    # p7 was listed 89 hours ago, so it is still inside the 168-hour early
    # access window and a free host genuinely cannot apply. Reloading the page
    # resets the prototype to a free host, so switch to Pro before applying —
    # the gate is doing its job, not misbehaving.
    set_pro(pg, False)
    ok("p7 is still in early access, so a free host cannot apply",
       pg.eval_on_selector("#applyBtn", "e=>e.disabled") is True)
    set_pro(pg, True)
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
    pg.goto(URL + "#/property/p8", wait_until="load", timeout=30000)    # Host Selected
    pg.wait_for_timeout(600)
    ok("a Host Selected listing shows its status", "Host Selected" in pg.inner_text("main"))
    ok("and offers no apply button", pg.locator("#applyBtn").count() == 0)

    # --- saving ---
    pg.goto(URL + "#/properties", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    pg.eval_on_selector("#results .card .savebtn", "e=>e.click()")
    pg.wait_for_timeout(400)
    ok("saving a property marks it", pg.eval_on_selector_all("#results .savebtn.on", "e=>e.length") == 1)

    # --- hosts ---
    pg.goto(URL + "#/hosts", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    ok("host profiles render", pg.eval_on_selector_all(".hostcard", "e=>e.length") == 6)
    ok("each host can be invited", pg.eval_on_selector_all("[data-invite]", "e=>e.length") == 6)
    ok("pro hosts are marked", pg.eval_on_selector_all(".pro", "e=>e.length") == 3)
    pg.click("[data-invite]")
    pg.wait_for_timeout(300)
    ok("inviting confirms", "Invitation sent" in pg.inner_text(".hostcard"))

    # --- deal area ---
    pg.goto(URL + "#/deal", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
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
    pg.goto(URL + "#/pro", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    ok("three plans", pg.eval_on_selector_all("[data-plan]", "e=>e.length") == 3)
    ok("listing stays free for owners", "free" in pg.inner_text("main").lower())
    ok("free hosts still get real value",
       "Everyone" in pg.inner_text("main"), pg.inner_text("main")[:200])
    ok("pricing is described as configurable",
       "settings, not code" in pg.inner_text("main"))

    # --- responsive: no sideways scroll anywhere ---
    for tag, w, h in (("desktop", 1280, 800), ("tablet", 820, 900), ("phone", 390, 780)):
        pg.set_viewport_size({"width": w, "height": h})
        for route in ("", "#/properties", "#/property/p1", "#/hosts", "#/deal", "#/pro"):
            pg.goto(URL + route, wait_until="load", timeout=30000)
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
        pg.goto(URL + route, wait_until="load", timeout=30000)
        pg.wait_for_timeout(700)
        pg.evaluate("window.scrollTo(0,0)")
        pg.wait_for_timeout(200)
        pg.screenshot(path="%s/%s.png" % (OUT, name))
    # the apply flow, which is the thing worth looking at
    pg.goto(URL + "#/property/p7", wait_until="load", timeout=30000)
    pg.wait_for_timeout(600)
    # the responsive loop above navigated to the bare URL, which unlike a hash
    # change really does reload and resets the prototype to a Free host
    set_pro(pg, True)
    pg.click("#applyBtn"); pg.wait_for_timeout(500)
    pg.screenshot(path="%s/apply-choose.png" % OUT)
    pg.click('[data-choose="cohosting"]'); pg.wait_for_timeout(500)
    pg.screenshot(path="%s/apply-cohost.png" % OUT)
    pg.set_viewport_size({"width": 390, "height": 780})
    pg.goto(URL + "#/properties", wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    pg.screenshot(path="%s/phone-search.png" % OUT)
    pg.goto(URL + "#/property/p2", wait_until="load", timeout=30000)
    pg.wait_for_timeout(700)
    pg.screenshot(path="%s/phone-detail.png" % OUT)

    ok("still no js errors after all that", not errs, errs)
    br.close()

print("checks: %d" % checks)
print("PROBLEMS: %s" % ("\n  - " + "\n  - ".join(problems) if problems else "none"))
sys.exit(1 if problems else 0)
