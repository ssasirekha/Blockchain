import streamlit as st
import hashlib, json, time
from datetime import datetime

st.set_page_config(page_title="Blockchain vs Conventional Database", page_icon="⛓️", layout="wide")

def sha(x): return hashlib.sha256(str(x).encode()).hexdigest()
def init():
    if "db" not in st.session_state:
        st.session_state.db=[
            {"ID":101,"Name":"Anu","Balance":5000},
            {"ID":102,"Name":"Bala","Balance":6500},
            {"ID":103,"Name":"Charan","Balance":4200},
        ]
    if "chain" not in st.session_state:
        st.session_state.chain=[]
        add_block("Genesis Block")
    if "step" not in st.session_state: st.session_state.step=1
    if "db_server" not in st.session_state: st.session_state.db_server=True
    if "nodes" not in st.session_state: st.session_state.nodes=[True,True,True]
    if "messages" not in st.session_state: st.session_state.messages=[]

def add_block(data):
    prev=st.session_state.chain[-1]["hash"] if st.session_state.chain else "0"*64
    block={"index":len(st.session_state.chain),"time":datetime.now().strftime("%H:%M:%S"),
           "data":data,"previous_hash":prev}
    block["hash"]=sha(json.dumps(block,sort_keys=True))
    st.session_state.chain.append(block)

init()

st.markdown("""
<style>
.bigtitle {font-size:2.15rem;font-weight:800}
.card {border:1px solid #ddd;border-radius:14px;padding:16px;margin:7px 0;background:#fff}
.step {border-left:5px solid #777;padding:10px 14px;background:#f7f7f7;border-radius:8px}
.small {font-size:.88rem;color:#666}
div[data-testid="stMetric"] {border:1px solid #ddd;padding:12px;border-radius:12px}
</style>
""",unsafe_allow_html=True)

st.markdown('<div class="bigtitle">⛓️ Blockchain vs Conventional Database</div>',unsafe_allow_html=True)
st.write("An interactive, self-guided experiment. Follow the numbered steps; the application explains what happens after every action.")

with st.sidebar:
    st.header("Experiment Navigator")
    sections=["1 · Understand","2 · Modify Data","3 · Verify Immutability","4 · Test Decentralization","5 · Compare Performance","6 · Conclusion & Quiz"]
    selected=st.radio("Progress",sections,index=min(st.session_state.step-1,5))
    st.progress(min(st.session_state.step/6,1.0))
    st.caption(f"Recommended progress: Step {st.session_state.step} of 6")
    if st.button("↻ Restart experiment"):
        for k in ["db","chain","step","db_server","nodes","messages"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

if selected.startswith("1"):
    st.header("Step 1 — Understand the Two Systems")
    st.info("🎯 **Learning goal:** Identify the fundamental difference between a conventional database and a blockchain.")
    c1,c2=st.columns(2)
    with c1:
        st.subheader("🗄️ Conventional Database")
        st.markdown("""A conventional database stores records in tables. An authorized application can **create, read, update or delete** records.

**Simple idea:** when a row is updated, the old value may be replaced by the new value.""")
        st.dataframe(st.session_state.db,use_container_width=True,hide_index=True)
        st.caption("Think of this as a centrally managed bank/customer table.")
    with c2:
        st.subheader("⛓️ Blockchain")
        st.markdown("""A blockchain stores records as **linked blocks**. Each block contains its own hash and the previous block's hash.

**Simple idea:** instead of silently replacing history, a new transaction can be appended to the ledger.""")
        for b in st.session_state.chain:
            st.markdown(f"""<div class="card"><b>Block {b['index']}</b><br>
            Data: {b['data']}<br><span class="small">Hash: {b['hash'][:20]}…<br>
            Previous: {b['previous_hash'][:20]}…</span></div>""",unsafe_allow_html=True)
    st.success("💡 Key idea: Database → records can be updated. Blockchain → history is represented as linked records.")
    if st.button("I understand — Continue →",type="primary"):
        st.session_state.step=max(st.session_state.step,2); st.rerun()

elif selected.startswith("2"):
    st.header("Step 2 — Perform the Same Update in Both Systems")
    st.info("🎯 Change Anu's balance from ₹5,000 to a new value and observe how each system records it.")
    newbal=st.number_input("Enter Anu's new balance",min_value=0,value=7000,step=500)
    c1,c2=st.columns(2)
    with c1:
        st.subheader("A. Update conventional database")
        st.dataframe(st.session_state.db,use_container_width=True,hide_index=True)
        if st.button("UPDATE database row",use_container_width=True):
            old=st.session_state.db[0]["Balance"]; st.session_state.db[0]["Balance"]=newbal
            st.success(f"Updated: ₹{old:,} → ₹{newbal:,}. The displayed row now contains the new value.")
            st.session_state.messages.append("db")
    with c2:
        st.subheader("B. Record update on blockchain")
        st.write("The blockchain simulation will append a transaction instead of editing the Genesis Block.")
        if st.button("ADD transaction as new block",use_container_width=True):
            add_block({"Account":101,"Action":"Balance Update","New Balance":newbal})
            st.success(f"New Block {len(st.session_state.chain)-1} appended.")
            st.session_state.messages.append("bc")
        for b in st.session_state.chain[-3:]:
            st.code(f"BLOCK {b['index']}\nData: {b['data']}\nHash: {b['hash'][:24]}...\nPrev: {b['previous_hash'][:24]}...")
    if "db" in st.session_state.messages and "bc" in st.session_state.messages:
        st.warning("🔎 **Observe:** the database exposes the latest row value. The blockchain shows the original block plus a newly appended update.")
        if st.button("Observation complete — Continue →",type="primary"):
            st.session_state.step=max(st.session_state.step,3); st.rerun()

elif selected.startswith("3"):
    st.header("Step 3 — Why Hash Linking Makes Tampering Detectable")
    st.info("🎯 Change a historical block locally and see what happens to its hash relationship.")
    if len(st.session_state.chain)<2:
        st.warning("Create a blockchain update in Step 2 first.")
    else:
        b=st.session_state.chain[1]
        st.write("Current Block 1")
        st.code(json.dumps(b,indent=2))
        fake=st.text_input("Try changing its stored data","Tampered balance = 999999")
        original=b["hash"]; changed=sha(json.dumps({**b,"data":fake,"hash":original},sort_keys=True))
        if st.button("Recalculate after tampering"):
            st.metric("Original hash",original[:18]+"…")
            st.metric("Hash after changing data",changed[:18]+"…")
            if changed!=original:
                st.error("Hash mismatch detected. Changing historical content changes the block fingerprint.")
                st.success("This is why hash linking helps make unauthorized historical changes detectable.")
        if st.button("Continue to decentralization →"):
            st.session_state.step=max(st.session_state.step,4); st.rerun()

elif selected.startswith("4"):
    st.header("Step 4 — Centralized vs Distributed Availability")
    st.info("🎯 Simulate failures and observe whether each system still has an available copy.")
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Central Database")
        st.session_state.db_server=st.toggle("Central server ON",value=st.session_state.db_server)
        if st.session_state.db_server:
            st.success("Server available → application can access the database.")
        else:
            st.error("Server unavailable → this simplified centralized service cannot answer requests.")
    with c2:
        st.subheader("Blockchain Network")
        for i in range(3):
            st.session_state.nodes[i]=st.toggle(f"Node {i+1} online",value=st.session_state.nodes[i],key=f"n{i}")
        active=sum(st.session_state.nodes)
        if active:
            st.success(f"{active} replica node(s) remain available.")
        else:
            st.error("All nodes are offline.")
    st.markdown("""**What should you notice?**  
A centralized design can have a central service dependency. A distributed ledger maintains replicated copies across participating nodes. Real systems may use redundancy, clusters and consensus rules, so this is a conceptual comparison rather than a claim that every database has a single server.""")
    if st.button("Continue to performance →"):
        st.session_state.step=max(st.session_state.step,5); st.rerun()

elif selected.startswith("5"):
    st.header("Step 5 — Compare Transaction Processing")
    st.info("🎯 Observe why consensus/validation can add processing overhead compared with a simple centralized write.")
    n=st.slider("Transactions to simulate",1,100,20)
    consensus=st.slider("Blockchain validation overhead per transaction (ms)",20,300,100)
    if st.button("▶ Run simulation",type="primary"):
        db_ms=n*5
        bc_ms=n*(5+consensus)
        st.session_state.perf=(db_ms,bc_ms,n)
    if "perf" in st.session_state:
        db_ms,bc_ms,n=st.session_state.perf
        st.bar_chart({"Milliseconds":{"Conventional DB":db_ms,"Blockchain":bc_ms}})
        c1,c2=st.columns(2)
        c1.metric("Conventional DB",f"{db_ms} ms")
        c2.metric("Blockchain simulation",f"{bc_ms} ms")
        st.warning("Do not interpret these numbers as real benchmarks. They demonstrate the *concept* that validation/consensus introduces additional work.")
        st.success("💡 Trade-off: blockchain may accept extra coordination cost to obtain shared, verifiable transaction history.")
        if st.button("Go to conclusion →"):
            st.session_state.step=6; st.rerun()

else:
    st.header("Step 6 — Conclusion & Self-Check")
    st.success("""### Experiment conclusion
You demonstrated three major differences:

**1. Data modification:** a conventional database can directly update a record; a blockchain-style ledger appends transaction history.

**2. Integrity:** hash-linked blocks make historical modification detectable.

**3. Architecture:** conventional applications are often centrally administered, while blockchains replicate a ledger across participating nodes.

Neither technology is universally “better.” The correct choice depends on the application, trust model, performance requirements and need for shared verifiability.""")
    st.subheader("🧠 Check your understanding")
    q1=st.radio("1. What happens in our blockchain simulation when account data changes?",
                ["The old block is silently overwritten","A new block is appended","All blocks are deleted"],index=None)
    q2=st.radio("2. Why does modifying block data matter?",
                ["It changes the block hash","It increases RAM automatically","It hides the block"],index=None)
    q3=st.radio("3. Which is the best conclusion?",
                ["Blockchain is always better","Databases are always better","The suitable technology depends on system requirements"],index=None)
    if st.button("Submit answers",type="primary"):
        score=sum([q1=="A new block is appended",q2=="It changes the block hash",q3=="The suitable technology depends on system requirements"])
        st.metric("Score",f"{score}/3")
        if score==3: st.balloons(); st.success("Excellent. You have completed the experiment.")
        else: st.info("Review the relevant steps and try again.")
    st.subheader("📝 Student Observation")
    obs=st.text_area("Write what you learned in 2–3 sentences")
    report=f"""VIRTUAL LAB RECORD
Experiment: Blockchain vs Conventional Database
Date: {datetime.now().strftime("%d-%m-%Y")}

Student Observation:
{obs}

Key Result:
A conventional database supports direct record updates, while the blockchain simulation appends hash-linked transaction history. Distributed replication and validation introduce different availability and performance characteristics.
"""
    st.download_button("⬇️ Download Lab Record",report,"blockchain_vs_database_lab_record.txt","text/plain")

st.divider()
st.caption("Self-contained educational simulation. No real blockchain account, cryptocurrency, private key or external database is required.")
