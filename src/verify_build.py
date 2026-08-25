# Fail loudly on any edit that silently did not apply. Run after every change.
import re, sys
h = open('/home/claude/site/index.html').read()
fails = []

MUST_BE_GONE = [
    "2006 ID card scheme</text>",
    "scheme was defeated",
 'The mode counts are uneven','One mode is much thinner than the others','weigh it accordingly',
 'earlier draft','until I checked','I first assumed','version of this analysis',
 'A late fact-check moved several classifications',
 'The obvious objection','An objection worth taking seriously','There is a case on the other side',
 'The tempting reading','The tempting lesson','It would be convenient to','I am tempted to file',
 'and it is a good one','The obvious rebuttal',
 '&#x27;','programme',
 'The pattern generalises','the operating model was underfunded.','more than half than to three in ten',
 'The new number is not better',
 'The point is not that','None of that makes the model wrong','nobody serious claims it is',
 'This is not to say','I am not saying this',
 'low-cost alternative to PIV','Cheaper than government-mandated PIV',
 'Too early','marked <em>too early</em>',
 'Acceptance sits with parties it cannot compel',
 'no conformance regime, no mutual recognition','with no reciprocity requirement',
 'fill="#4A6B4F">Restored</text>',
 'seven to eleven per cent of detected identity-fraud attempts',
 'cross-tenant vulnerabilities disclosed in 2025',
 "incorporated Stefan Brands' minimal-disclosure work",
 'Stalled outside government','no platform integration and no developer incentive',
 'Distribution beat specification, consistently',
 'If a reader keeps five things from this post',
 'Twenty-seven integrated services','around 10 million users','$56 billion','237 of 500',
 'lost DIATF certification in May 2025','and got ten per cent activation',
 'the careless version is easy to attack','confirm against the NAO 2019',
 '52% first-attempt','a a 48 per cent',
 'ceiling of about &pound;18 million','cost the United Kingdom nine months .',
 'is midway through a record-by-record','Every successful program eventually picks up',
 'Across all 31','the whole record of 31','Show all 31 rows','>All 31<',
 'twenty-nine programs','zero out of thirty-one',
 'Not one program in thirty years failed',
 'Where liability cannot move, no credential helps',
 'privileges that dissolve it','Smartphone NFC arrived in 2021',
 'x[0]==="crypto"',
 'and largely faltered',
]
MUST_BE_PRESENT = [
    "ID-card scheme abolished",
    "in 2010, limited rollout",
    "abolished in 2010 after a limited rollout",
    "reviewable by a parliament.</p>",
 'In this sample, I did not identify weak cryptography as the primary cause',
 'Residual responsibility sets the value ceiling',
 '48 per cent single-attempt verification success',
 'completed a record-by-record national recheck in December 2023',
 'combined potential value of about &pound;18 million',
 'marked <em>uncertain</em> rather than failed','o:"uncertain"',
 'GENERATED:category-chart','Availability and use are different measures',
 'cannot establish by itself that the credential','kept a working national login off its trust-framework register',

 'I am an author of the GIDS specification and I contributed to PIV',
 'NOT FOR IDENTIFICATION','a shared identifier used as a secret is a credential with no revocation',
 'stated scope does not bind the parties who find the thing convenient',
 'There is a second floor underneath the legal one','who is going to carry this, can they, and what are they being paid',
 'Then ask where the kiosk goes','federation, arrived at by elimination rather than preference',
 'Across the world it is not a plan',
 'Both figures come from biased samples pointing opposite ways','undone by the part that runs afterwards',
 'it did eventually get fixed','retrofitted interoperability is not impossible',
 'enrolled their fingerprints on their mother','load-bearing by design and which are load-bearing by accident',
 'The property was borrowed, the assumption was never written down',
 'A minor can be emancipated by court order','age and capacity are different questions',
 'No credential presented has at least two causes','converts a privacy preference into a disability',
 'no verifier has yet been named whose need to check identity predates',
 'an ecosystem to be built and enabled','Enabling is what NSTIC did',
 'Enabling is the passive half of the job',
 'The browser is called a user agent for a reason','celebrate it in Stockholm and be uneasy about it in Cupertino',
 'The pattern has a fourth member',
 'designed for remote deployment','I am an author of one of them',
 'are not properly separable','The harder case was e-passports','that is a weaker reason than I would like',
 'This began as a talk','I put the failure rate at roughly seven in ten',
 'The three entries marked <em>in flight</em>','No outcome to classify yet',
 'not an exception to this claim but a payment plan',
 'Why It Keeps Happening','Two mandates, two different bills','Reasoned, not demonstrated',
 
 'Standards Do Not Converge By Themselves','apparent authority becomes something an unrelated party can manufacture',
 'the blast radius is bounded',
 'a limited form of mutual recognition for qualified signatures','Europe Is Running the Same Sequence Twice',
 'without a special arrangement having been made for that corridor',
 'restored to the specification and have yet to be restored to the deployments',
 'useless advice about architecture','It will work, and it may be the only thing that ever works','Three roles have to be present','because Conway\'s law applies to credentials','Enrollment is not adoption',
 'The house is not the one buying the detector','changing the question from detection to provenance',
 'the first plausible source of genuinely new verifier demand','Verify the adults, and treat the absence of verification as the signal',
 'A failure to plan is a plan to fail',
 'the argument of xkcd 927','xkcd 927</a>','which existing thing stops being used, by what mechanism','became options rather than replacements',
 'The Lifecycle Nobody Designs For','the direction of authority reverses across a lifetime',
 'a corner you cannot reach from inside','The binding model is the one most often mistaken for a detail',
 'The record supports five moves','Every available lever is economic, institutional or legal',
 'invisible by construction in any measure of completed transactions',
 'Write specifications for clarity rather than for flexibility',
 'whose failure can break the security policy','trusted but not trustworthy',
 'a party that can betray you','to trust something is to be vulnerable to it',
 'political capital to reopen the question','single electoral cycle','hybrid operation is not a transition state',
 'PayPal and Verizon among them','19.5 million authentications',
 'Distribution is necessary and it is not sufficient','inbox with every Windows from 7 SP1',
 'The argument in five claims','failing both is close to decisive','Would some verifier still need to solve this problem',
 'The objection lands on the word','The harder case is passkeys',
 'The opening of this post listed five claims','deferred and repriced',
 'Protocols and frameworks die on the demand side','deferred and repriced','k:"national"',
 'Delegated authority is the same collision','power of attorney','court-appointed deputy',
 'capacity or delegation requirements',
 'non-cash releasing','Seven departments were invoiced','nineteen services had connected',
 'ninety-seven per cent of cards by administrative decree','Recovery took nine months',
 '$100 billion and $135 billion','Reader and validation estates told the same story',
 'clearest natural experiment in this record','Investigation into Verify</i></a>, March 2019',
]
for x in MUST_BE_GONE:
    if x in h: fails.append("STALE STILL PRESENT: "+x)
for x in MUST_BE_PRESENT:
    if x not in h: fails.append("EDIT DID NOT LAND: "+x)

if h.count('&mdash;') or h.count('\u2014'): fails.append("em dash present")
rr=set(re.findall(r'href="#(r\d+)"',h)); ri=set(re.findall(r'id="(r\d+)"',h))
if rr-ri: fails.append("broken citations "+str(rr-ri))
if ri-rr: fails.append("orphan sources "+str(ri-rr))
ids=set(re.findall(r'id="(s\d+)"',h)); refs=set(re.findall(r'href="#(s\d+)"',h))
if refs-ids: fails.append("broken anchors "+str(refs-ids))
if h.count('<div')!=h.count('</div>'): fails.append("div mismatch")

dupids=[i for i,c in __import__("collections").Counter(re.findall(r'<marker id="([^"]+)"',h)).items() if c>1]
if dupids: fails.append("DUPLICATE MARKER ID: "+",".join(dupids))

for m in re.finditer(r'href="#s(\d+)">&sect;(\d+)</a>', h):
    if m.group(1)!=m.group(2):
        fails.append("POINTER LABEL WRONG: links to s%s but reads §%s" % (m.group(1), m.group(2)))
# 17 SVG diagrams + 4 photographic artifacts in the section 1 strip
if h.count('<svg')!=19: fails.append("SVG LOST OR ADDED: %d, expected 19" % h.count('<svg'))
if h.count('<figure')!=25: fails.append("FIGURE COUNT: %d, expected 25" % h.count('<figure'))
if h.count('<figure')!=h.count('</figure>'): fails.append("figure tag mismatch")
if h.count('<img')!=6: fails.append("IMG COUNT: %d, expected 6" % h.count('<img'))
if h.count('src="assets/'): fails.append("IMAGE NOT INLINED: external asset path present")
if 'loading="lazy"' in h: fails.append("lazy loading on inlined data URIs defers decode for no benefit")
if h.count('src="data:image/jpeg;base64,')!=6: fails.append("inlined image count wrong")
# the diagnostic must exist in the document, not only after JS runs
body=re.sub(r'<script.*?</script>','',h,flags=re.S)
if body.count('class="sc-q"')!=20: fails.append("DIAGNOSTIC NOT STATIC: %d questions in markup, expected 20" % body.count('class="sc-q"'))
if body.count('class="sc-opt"')!=60: fails.append("diagnostic option count wrong in markup")
if 'anchor verifier' in h: fails.append("non-standard term 'anchor verifier' present")
import collections
persec={}
for m in re.finditer(r'<section id="(s\d+)"', h):
    nxt=h.find('<section', m.end()); nxt=nxt if nxt>0 else len(h)
    persec[m.group(1)]=h[m.start():nxt].count('<figure')
empty=[k for k,v in persec.items() if v==0 and k not in ('s19','s20','s21','s22')]
if empty: fails.append("section without a figure: "+",".join(empty))
if h.count('<section')!=h.count('</section>'): fails.append("section mismatch")

# no duplicated paragraphs
paras=[re.sub(r'<[^>]+>','',p).strip() for p in re.findall(r'<p>.*?</p>', h, re.S)]
seen={}
for p in paras:
    if len(p)>120:
        if p in seen: fails.append("DUPLICATE PARAGRAPH: "+p[:70])
        seen[p]=1

# static markup is necessary but not sufficient: JS must not diverge from it
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br=pw.chromium.launch(); pg=br.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("file:///home/claude/site/index.html"); pg.wait_for_timeout(2500)
        live=pg.evaluate("()=>[...document.querySelectorAll('.sc-q .qt')].map(e=>e.textContent.trim())")
        rows=pg.evaluate("()=>document.querySelectorAll('#record-rows tr').length")
        br.close()
    if errs: fails.append("PAGE JS ERROR: "+"; ".join(errs))
    if not rows: fails.append("RECORD TABLE DID NOT RENDER")
    src=[re.sub(r'&#x27;',"'",re.sub(r'<[^>]+>','',m)).strip()
         for m in re.findall(r'<p class="qt">(.*?)</p>', body, re.S)]
    if live!=src:
        fails.append("RENDERED DIAGNOSTIC DIVERGES FROM MARKUP: %d rendered vs %d in source"%(len(live),len(src)))
        for a,b_ in zip(live,src):
            if a!=b_: fails.append("   first divergence: rendered %r vs source %r"%(a[:50],b_[:50])); break
except Exception as e:
    fails.append("could not verify rendered output: %s"%e)

print("\n".join(fails) if fails else "build clean: no stale text, no missing edits, no duplicates, rendered output matches source")
sys.exit(1 if fails else 0)
