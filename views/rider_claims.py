"""Rider app — claims: raise one, track it, see history."""
from __future__ import annotations

import time
from datetime import datetime

import pandas as pd
import streamlit as st

from shared import (html, topbar, h, kpi, inr, rows, badge, tracker, MUTED, PRIMARY,
                    OK, BAD, CLAIM_BADGE, empty, note)
from engine import store

r = store.rider()
pols = store.active_policies()
m = store.claim_metrics()

topbar("Rider app", f"{r.name} · {r.rider_id}")

h("Claims", "One tap. We already know where you were and what happened to your "
  "phone, so most claims are paid before you finish explaining them.")

k = st.columns(4)
kpi(k[0], "Claims made", str(m["total"]))
kpi(k[1], "Paid out to you", inr(m["paid_amount"]))
kpi(k[2], "Open right now", str(m["open"]))
kpi(k[3], "Typical settlement",
    "under a minute" if m["instant_share"] > 0.5 else "under a day")

st.write("")
tab_new, tab_track, tab_hist = st.tabs(
    ["Raise a claim", "Track", f"History ({m['total']})"])

# ------------------------------------------------------------------ raise
with tab_new:
    if not pols:
        empty("You need active cover before you can claim. "
              "Go to <b>Buy cover</b>.")
    else:
        st.markdown("**What happened?**")
        c = st.columns(3)
        inc_list = list(store.INCIDENTS.keys())
        if "sel_inc" not in st.session_state:
            st.session_state["sel_inc"] = inc_list[0]

        for i, name in enumerate(inc_list):
            with c[i % 3]:
                sel = st.session_state["sel_inc"] == name
                if st.button(name, key=f"inc{i}", width="stretch",
                             type="primary" if sel else "secondary"):
                    st.session_state["sel_inc"] = name
                    st.rerun()

        inc = st.session_state["sel_inc"]
        spec = store.INCIDENTS[inc]

        st.write("")
        d1, d2 = st.columns([1, 1])
        with d1:
            _rows1 = rows([
              ('You selected', f"<b>{inc}</b>"),
              ('Pays under', spec['head']),
              ('We need from you', spec['evidence']),
              ('Expected settlement',
               'Under 60 seconds' if spec['tier'] == 1 else '24–48 hours'),
            ])
            st.markdown(f"""<div class='card'>{_rows1}</div>""", unsafe_allow_html=True)

            st.write("")
            st.file_uploader("Add a photo (optional — we usually don't need one)",
                             type=["png", "jpg", "jpeg"], key="claimphoto")

        with d2:
            st.markdown("**What our system already knows**")
            live = st.toggle("Cover was live at the time", value=True,
                             help="Turn this off to see how the anti-selection "
                                  "control behaves")
            impact = st.toggle("Your phone recorded an impact", value=True,
                               help="A real crash reads as a deceleration spike "
                                    "followed by the phone going still")
            st.markdown(
                html(f"<div style='color:{MUTED};font-size:.85rem;line-height:1.6;"
                f"margin-top:.5rem'>We hold the last five minutes of movement "
                "data from your phone, your GPS trail and whether a shift was "
                "declared. That is what lets us pay in seconds instead of "
                "asking you for documents.</div>"), unsafe_allow_html=True)

        st.write("")
        if st.button("Submit claim", type="primary", width="stretch"):
            with st.status("Sending…", expanded=True) as status:
                st.write("Capturing location, timestamp and movement trail…")
                time.sleep(0.4)
                c_ = store.raise_claim(inc, cover_live=live,
                                       telematics_impact=impact)
                st.write("Checking cover was live…")
                time.sleep(0.35)
                st.write("Matching to your benefit schedule…")
                time.sleep(0.35)
                store.adjudicate(c_)
                status.update(label=f"Claim {c_.claim_id} — {c_.status}",
                              state="complete")

            if c_.status == "Paid":
                st.success(f"**{inr(c_.amount_approved)} is on its way to your "
                           f"UPI.** Claim {c_.claim_id} settled. You should see "
                           "it within a minute.")
                st.balloons()
            elif c_.status == "Approved":
                st.success(f"**Approved — {inr(c_.amount_approved)}.** Claim "
                           f"{c_.claim_id}. A Claim Saathi will call you within "
                           "15 minutes and the money follows within 48 hours.")
            elif c_.status == "Investigating":
                st.warning(f"**Claim {c_.claim_id} needs a look from a person.** "
                           "Your phone did not record an impact, so we are "
                           "checking rather than declining. Someone will call "
                           "you today.")
            else:
                st.error(f"**Claim {c_.claim_id} declined.** {c_.decline_reason}")
                st.caption("If you think this is wrong, our grievance officer "
                           "sits outside the claims team and you can escalate "
                           "to the Insurance Ombudsman. We publish every "
                           "rejection reason monthly.")

# ------------------------------------------------------------------ track
with tab_track:
    open_c = store.open_claims()
    recent = [c for c in store.claims() if c.settled][:2]
    watch = open_c + [c for c in recent if c not in open_c]

    if not watch:
        empty("Nothing in progress.")
    for c_ in watch[:4]:
        stage = {"Submitted": 0, "Verifying": 1, "Investigating": 1,
                 "Approved": 2, "Paid": 3, "Declined": 1}.get(c_.status, 0)
        when = datetime.fromisoformat(c_.submitted).strftime("%d %b, %H:%M")
        st.markdown(html(f"""<div class='pol' style='margin-bottom:.4rem'>
          <div class='h'>
            <span class='hl'><span class='t'>{c_.incident}</span><br>
              <span class='n'>{c_.claim_id} · raised {when}</span></span>
            <span class='hr'>
              {badge(c_.status, CLAIM_BADGE.get(c_.status, 'mute'))}<br>
              <span style='font-weight:800;font-size:1.05rem'>
              {inr(c_.amount_approved or c_.amount_claimed)}</span></span>
          </div></div>"""), unsafe_allow_html=True)
        tracker(stage, declined=(c_.status == "Declined"))
        if c_.status == "Declined":
            st.caption(f"Reason given: {c_.decline_reason}")
        elif c_.turnaround_hours is not None:
            secs = c_.turnaround_hours * 3600
            st.caption("Settled in %s." % (f"{secs:.0f} seconds" if secs < 120
                                           else f"{c_.turnaround_hours:.1f} hours"))

# ------------------------------------------------------------------ history
with tab_hist:
    cs = store.claims()
    if not cs:
        empty("No claims yet.")
    else:
        df = pd.DataFrame([{
            "Claim": c_.claim_id,
            "What happened": c_.incident,
            "Raised": datetime.fromisoformat(c_.submitted).strftime("%d %b %Y"),
            "Asked for": inr(c_.amount_claimed),
            "Paid": inr(c_.amount_approved) if c_.amount_approved else "—",
            "Status": c_.status,
            "Settled in": (
                "—" if c_.turnaround_hours is None
                else (f"{c_.turnaround_hours*3600:.0f} sec"
                      if c_.turnaround_hours < 0.05
                      else f"{c_.turnaround_hours:.1f} hrs")),
        } for c_ in cs])
        st.dataframe(df, width="stretch", hide_index=True)

        note("We publish our settlement ratio, median turnaround and the reason "
             "for every rejection each month. In a market where nobody trusts "
             "an insurer to pay, that is the whole product.")
