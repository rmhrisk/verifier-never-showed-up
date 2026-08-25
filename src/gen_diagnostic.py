# Single source of truth for the diagnostic. Emits static HTML into part4.html
# so the questions exist in the document; JS only attaches scoring behaviour.
import re, html

Q = [
 ("Can you name the anchor tenant?",
  "A specific verifier, named, whose participation is committed rather than hoped for.",
  [("Named and committed",0),("Named, not committed",1),("Not yet",2)], "noverifier"),
 ("Would that verifier still need to solve this problem if your program did not exist?",
  "A motive your program created disappears when your funding does.",
  [("Yes, it predates us",0),("Partly",1),("No",2)], "noverifier"),
 ("If a mandate is part of the plan, what exactly is being mandated?",
  "Compelling a transaction people need works. Compelling possession of a credential moves the issuance number and not the acceptance one.",
  [("A transaction, by the body that must make it work",0),("A transaction, by somebody else",1),("Holding the credential",2)], "political"),
 ("What will acceptance cost the verifier, and who pays it?",
  "Integration, training, support, and the ongoing cost of accepting.",
  [("Quantified and funded",0),("Estimated",1),("Not analysed",2)], "integration"),
 ("Who remains liable when a credential turns out to be wrong?",
  "If the verifier does, and regulation says it must, the credential cannot reduce its risk.",
  [("Risk genuinely transfers",0),("Shared or unclear",1),("It keeps all of it",2)], "liability"),
 ("If liability is meant to transfer, who absorbs the loss and what are they paid?",
  "A transfer capped below the harm, on per-verification fees, has not moved the risk. It has moved the paperwork.",
  [("Capacity and price match the exposure",0),("Transfer written, cap below the harm",1),("Not worked out",2)], "liability"),
 ("Is an institutional override, meaning revoke or freeze or suspend, legally required here?",
  "Court orders, sanctions, safeguarding. Holder-controlled architectures limit this by design.",
  [("Not required",0),("Possibly",1),("Required",2)], "liability"),
 ("Who pays for the credential, and who benefits from it?",
  "Systems where the holder pays and the verifier benefits stall.",
  [("Beneficiary pays",0),("Split",1),("Holder pays",2)], "misaligned"),
 ("What must the holder obtain, install or visit before first use?",
  "The nPA asked for an office visit, middleware and a purchased reader. Passkeys ask for nothing.",
  [("Nothing beyond a device they own",0),("One additional step",1),("An in-person visit or bought hardware",2)], "friction"),
 ("Which populations cannot complete enrolment as designed?",
  "Evidence and device assumptions, degraded biometrics in older users, children, and anyone acting under a power of attorney or guardianship.",
  [("Modelled, with alternate routes",0),("Identified, unresolved",1),("Not analysed",2)], "exclusion"),
 ("Is assurance set per transaction, or once for the whole system?",
  "A single IAL/AAL posture across every use is not a risk decision, it is eleven decisions avoided.",
  [("Per transaction",0),("Two or three tiers",1),("One level for everything",2)], "exclusion"),
 ("Which architectural choices were made for political acceptability rather than function?",
  "Verify's federated design existed to avoid a central database. That choice created its coordination problem.",
  [("None, or consequences accepted",0),("Some, unexamined",1),("The core design",2)], "political"),
 ("If this is a new standard, what stops being used, and what makes it stop?",
  "A mandate with consequences, a buyer too large to refuse, or default platform distribution. Not that yours is better.",
  [("Named mechanism and timeline",0),("Expect voluntary migration",1),("Ours is better",2)], "coordination"),
 ("If two implementations disagree, who decides and who is bound?",
  "Conformance testing, certification, and a consequence for failing it.",
  [("Named authority with teeth",0),("Testing, no consequence",1),("Nobody",2)], "enforcement"),
 ("How many independent parties must converge for this to work?",
  "And what forces them to, absent a mandate or an anchor tenant?",
  [("One, or a mandate exists",0),("Few, aligned",1),("Many, voluntary",2)], "coordination"),
 ("Who was in the room before the design was fixed?",
  "Volume, habit and breadth. One department specifying alone will encode that department, and every other will find the fit wrong.",
  [("All three roles, more than one org",0),("Some, consulted late",1),("One body, or a desk survey",2)], "lockin"),
 ("What is the annual operating budget, as a share of build cost?",
  "Security review, supplier verification, protocol migration, conformance testing.",
  [("10% or more",0),("Under 10%",1),("Not budgeted",2)], "governance"),
 ("Which security properties are load-bearing by accident?",
  "Mechanisms borrowed for a property they were not designed to provide, where the party being relied on never agreed to it. SMS one-time passwords are the standing example.",
  [("Identified, and the reliance is designed",0),("Some known, not written down",1),("Not asked",2)], "governance"),
 ("Which of today's choices will be unfixable at scale?",
  "Identifier format, revocation model, algorithm agility, trust-anchor update.",
  [("Identified, with migration paths",0),("Identified only",1),("Not considered",2)], "lockin"),
 ("What is the primary success metric?",
  "Credentials issued measures the half you control. Completed transactions measures the half that decides.",
  [("Transactions completed",0),("Both",1),("Credentials issued",2)], "governance"),
]

rows=[]
for i,(q,s,opts,c) in enumerate(Q):
    o="".join(
      f'<button class="sc-opt" type="button" data-q="{i}" data-v="{v}" aria-pressed="false">{html.escape(l, quote=False)}</button>'
      for l,v in opts)
    rows.append(
      f'<div class="sc-q" data-mode="{c}">\n'
      f'  <p class="qt">{html.escape(q, quote=False)}</p>\n'
      f'  <p class="qs">{html.escape(s, quote=False)}</p>\n'
      f'  <div class="sc-opts">{o}</div>\n'
      f'</div>')
static="\n".join(rows)

f='part5.html'; src=open(f).read()
a=src.index('<div id="sc-questions">') if '<div id="sc-questions">' in src else src.index('<div id="sc-questions"')
b=src.index('>',a)+1
end=src.index('<div class="sc-result"', b)
new=f'<div id="sc-questions">\n{static}\n</div>\n  '
src = src[:a] + new + src[end:]
open(f,'w').write(src)
print(f"emitted {len(Q)} questions as static HTML")

# JS no longer builds the DOM; it reads it
f='part7_js.html'; j=open(f).read()
a=j.index('const scq=document.getElementById') if 'const scq=document.getElementById' in j else j.index('const SCQ=[')
b=j.index('const STRUCTURAL=')
newjs = '''const scq=document.getElementById("sc-questions");
const SCQ=[...scq.querySelectorAll(".sc-q")].map(el=>({c:el.dataset.mode}));
const scState=new Array(SCQ.length).fill(null);
scq.addEventListener("click",e=>{
  const b=e.target.closest(".sc-opt"); if(!b) return;
  const i=+b.dataset.q; scState[i]=+b.dataset.v;
  [...scq.querySelectorAll('.sc-opt[data-q="'+i+'"]')].forEach(x=>
    x.setAttribute("aria-pressed",String(x===b)));
  scoreCard();
});
'''
j = j[:a] + newjs + j[b:]
open(f,'w').write(j); print("JS now reads the markup instead of generating it")
