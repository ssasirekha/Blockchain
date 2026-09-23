
import streamlit as st
import hashlib, json, random, time
from datetime import date, datetime

st.set_page_config(page_title="Blockchain Virtual Lab", page_icon="⛓️", layout="wide")

def h(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()

def short(x, n=12):
    return str(x)[:n] + "…"

def init():
    defaults = {
        "chain": [{"index":0,"data":"Genesis Block","prev":"0"*64,"nonce":0}],
        "rdbms": [{"id":1,"item":"Laptop","owner":"Lab","price":50000}],
        "nodes": {"Node A":True,"Node B":True,"Node C":True},
        "mempool": [],
        "balances": {"Alice":100.0,"Bob":100.0,"Carol":100.0,"Dave":100.0},
        "wallet_balance": 5.0, "wallet_history": [],
        "contract_created": False, "contract_deployed": False, "contract_store": {},
        "medicines": [], "supply_ledger": [],
        "proxy_value": 0, "proxy_version":"V1",
        "syntax_vars": {}, "car_bookings": [], "lands": [], "kyc": {},
    }
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
    for b in st.session_state.chain:
        b["hash"] = h({k:v for k,v in b.items() if k!="hash"})

def add_block(data):
    chain=st.session_state.chain
    prev=chain[-1]["hash"] if chain else "0"*64
    b={"index":len(chain),"timestamp":datetime.now().isoformat(timespec="seconds"),
       "data":data,"prev":prev,"nonce":random.randint(0,999999)}
    b["hash"]=h(b); chain.append(b); return b

def chain_view(chain):
    for b in chain:
        st.markdown(f"""**Block {b['index']}** · `{short(b.get('hash',''))}`  
Data: `{str(b.get('data'))[:120]}`  
Prev: `{short(b.get('prev',''))}`""")
        st.caption("↓ linked by previous hash")

def reset_all():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

init()
st.title("⛓️ Blockchain & Smart Contract Virtual Lab")
st.caption("Interactive Streamlit teaching simulations based on the learning objectives of the Virtual Labs Blockchain Lab.")

EXPS = [
"1. Blockchain vs Conventional Database",
"2. Proof of Work vs Proof of Stake",
"3. Double Spending Prevention",
"4. Ethereum Wallet / MetaMask Transaction",
"5. Create & Deploy a Smart Contract",
"6. Smart Contract Automation – Pharma Supply Chain",
"7. Solidity Syntax & Coding Process",
"8. Advanced Smart Contract Writing",
"9. Proxy Contract Approach",
"10. Smart Contract Vulnerabilities",
]
with st.sidebar:
    exp=st.radio("Choose an experiment", EXPS)
    st.divider()
    st.info("Transactions are simulated locally. No real cryptocurrency or private keys are used.")
    if st.button("Reset Lab State", use_container_width=True): reset_all()

if exp.startswith("1."):
    st.header(EXPS[0])
    st.write("**Aim:** Compare immutability, decentralization and transaction-processing behaviour of a conventional database and a blockchain.")
    tab1,tab2,tab3=st.tabs(["Immutability","Decentralization","Performance"])
    with tab1:
        c1,c2=st.columns(2)
        with c1:
            st.subheader("Conventional database")
            st.dataframe(st.session_state.rdbms, use_container_width=True)
            new_owner=st.text_input("Edit owner", value=st.session_state.rdbms[0]["owner"])
            if st.button("UPDATE row"):
                st.session_state.rdbms[0]["owner"]=new_owner
                st.success("Existing row was overwritten.")
        with c2:
            st.subheader("Blockchain")
            chain_view(st.session_state.chain[-4:])
            data=st.text_input("New transaction / update", "Laptop ownership → Student")
            if st.button("ADD as new block"):
                add_block(data); st.success("History preserved; a new linked block was appended.")
        st.info("Observation: a mutable table can overwrite a row; an append-only blockchain preserves prior records and links new records by hashes.")
    with tab2:
        c1,c2=st.columns(2)
        with c1:
            st.subheader("Network nodes")
            for n,ok in list(st.session_state.nodes.items()):
                st.session_state.nodes[n]=st.toggle(n, value=ok, key="node_"+n)
            active=sum(st.session_state.nodes.values())
            st.metric("Active blockchain replicas", active)
        with c2:
            central=st.toggle("Central database server online", True)
            if st.button("Attempt transaction", key="decent_tx"):
                st.success("Central DB: transaction accepted.") if central else st.error("Central DB unavailable: central server is down.")
                st.success(f"Blockchain accepted by {active} active node(s).") if active else st.error("Blockchain: no active node.")
    with tab3:
        n=st.slider("Number of transactions",1,50,10)
        if st.button("Run comparison"):
            rdb=round(n*0.004,3); bc=round(n*0.12,3)
            st.bar_chart({"Simulated seconds":{"RDBMS":rdb,"Blockchain":bc}})
            st.write(f"RDBMS ≈ **{rdb}s**; sequential block confirmation ≈ **{bc}s**.")
            st.caption("Teaching model only; real performance depends on architecture, consensus, batching, hardware and network.")

elif exp.startswith("2."):
    st.header(EXPS[1])
    st.write("**Aim:** Compare validator/miner selection and block creation in Proof of Work and Proof of Stake.")
    mode=st.radio("Consensus",["Proof of Work","Proof of Stake"],horizontal=True)
    names=list(st.session_state.balances)
    c1,c2=st.columns([1,1.4])
    with c1:
        sender=st.selectbox("Sender",names)
        receiver=st.selectbox("Receiver",[x for x in names if x!=sender])
        amt=st.number_input("Amount",1.0,100.0,10.0)
        if mode=="Proof of Work":
            difficulty=st.slider("Difficulty",1,5,2)
        else:
            stakes={}
            st.caption("Stake weights")
            for n in names: stakes[n]=st.number_input(f"{n} stake",1,100,25,key="stake"+n)
        if st.button("Broadcast transaction"):
            if amt<=st.session_state.balances[sender]:
                st.session_state.mempool.append({"from":sender,"to":receiver,"amount":amt}); st.success("Added to mempool.")
            else: st.error("Insufficient balance.")
        if st.button("Create next block", type="primary"):
            if not st.session_state.mempool: st.warning("Add a transaction first.")
            else:
                if mode=="Proof of Work":
                    winner=random.choice(names); metric=f"Difficulty {difficulty}; simulated mining race"
                else:
                    winner=random.choices(names,weights=[stakes[n] for n in names])[0]; metric="selection weighted by stake"
                txs=st.session_state.mempool.copy()
                for t in txs:
                    st.session_state.balances[t["from"]]-=t["amount"]; st.session_state.balances[t["to"]]+=t["amount"]
                add_block({"consensus":mode,"producer":winner,"transactions":txs})
                st.session_state.mempool=[]
                st.success(f"{winner} produced the block ({metric}).")
    with c2:
        st.subheader("Mempool"); st.dataframe(st.session_state.mempool,use_container_width=True)
        st.subheader("Balances"); st.dataframe([{"participant":k,"balance":v} for k,v in st.session_state.balances.items()],use_container_width=True)
        st.subheader("Latest blocks"); chain_view(st.session_state.chain[-3:])

elif exp.startswith("3."):
    st.header(EXPS[2])
    st.write("**Aim:** Demonstrate confirmation depth and competing-chain behaviour in a simplified double-spending scenario.")
    bal=st.number_input("Sender balance",10,1000,100)
    amt=st.number_input("Attempt to pay same coins twice",1,bal,40)
    honest=st.slider("Honest miners",2,10,6); attacker=st.slider("Secret miners",1,9,2)
    confirmations=st.slider("Confirmations required",1,8,4)
    if st.button("Run double-spend simulation",type="primary"):
        honest_blocks=max(confirmations+1,int(honest*random.uniform(.7,1.3)))
        secret_blocks=max(1,int(attacker*random.uniform(.5,1.2)))
        st.write(f"Two conflicting payments of **{amt} coins** are broadcast from a balance of **{bal}**.")
        c1,c2=st.columns(2); c1.metric("Honest chain",f"{honest_blocks} blocks"); c2.metric("Secret chain",f"{secret_blocks} blocks")
        if honest_blocks>secret_blocks and honest_blocks>=confirmations+1:
            st.success("The honest history is selected in this simulation; the conflicting secret spend is rejected.")
        else: st.warning("The secret fork is competitive in this run. Try more honest mining power or confirmation depth.")
        st.caption("Conceptual model only; not a real attack-success probability calculator.")

elif exp.startswith("4."):
    st.header(EXPS[3])
    st.write("**Aim:** Learn the Ethereum wallet transaction flow without real funds or credentials.")
    st.warning("Never enter a real seed/recovery phrase or private key into this teaching app.")
    c1,c2=st.columns([1,1.2])
    with c1:
        st.metric("Demo ETH balance",f"{st.session_state.wallet_balance:.4f} ETH")
        action=st.selectbox("Wallet action",["Receive","Send","Buy / Faucet (simulated)"])
        if action=="Receive":
            st.code("0xDEMO1234567890ABCDEF1234567890ABCDEF1234")
        elif action=="Send":
            addr=st.text_input("Recipient public address","0xABCDEF...")
            amount=st.number_input("ETH",0.001,10.0,0.1,step=0.01)
            gas=st.number_input("Estimated gas fee",0.0001,0.1,0.002)
            if st.button("Confirm demo transfer"):
                if amount+gas<=st.session_state.wallet_balance:
                    st.session_state.wallet_balance-=amount+gas
                    st.session_state.wallet_history.append({"time":str(datetime.now()),"type":"SEND","to":addr,"amount":amount,"gas":gas,"status":"Confirmed","tx_hash":h([addr,amount,time.time()])})
                    st.success("Demo transaction confirmed.")
                else: st.error("Insufficient demo balance.")
        else:
            amount=st.number_input("Test funds",0.1,2.0,0.5)
            if st.button("Add test funds"):
                st.session_state.wallet_balance+=amount
                st.session_state.wallet_history.append({"time":str(datetime.now()),"type":"FAUCET","amount":amount,"status":"Confirmed"})
                st.success("Demo funds added.")
    with c2:
        st.subheader("Transaction lifecycle")
        st.markdown("**Prepare → Review → Sign → Broadcast → Validate → Confirm**")
        st.subheader("Activity"); st.dataframe(st.session_state.wallet_history[::-1],use_container_width=True)

elif exp.startswith("5."):
    st.header(EXPS[4])
    st.write("**Aim:** Create, deploy and interact with a simple data-storage smart contract.")
    solidity="""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract DataStore {
    string private value;
    function setValue(string memory v) public { value = v; }
    function getValue() public view returns (string memory) { return value; }
}"""
    c1,c2=st.columns(2)
    with c1:
        st.code(solidity,language="solidity")
        if st.button("1. Create contract"): st.session_state.contract_created=True; st.success("Contract compiled conceptually.")
        if st.button("2. Deploy contract",disabled=not st.session_state.contract_created):
            st.session_state.contract_deployed=True; st.session_state.contract_address="0x"+h(time.time())[:40]
            add_block({"type":"contract deployment","address":st.session_state.contract_address}); st.success("Deployed to simulated chain.")
    with c2:
        if st.session_state.contract_deployed:
            st.code(st.session_state.contract_address)
            key=st.text_input("Key","course"); val=st.text_input("Value","Blockchain Lab")
            if st.button("setValue"):
                st.session_state.contract_store[key]=val; add_block({"contract":st.session_state.contract_address,"set":{key:val}}); st.success("State update mined.")
            if st.button("getValue"): st.info(st.session_state.contract_store.get(key,"No value stored"))
            st.json(st.session_state.contract_store)
        else: st.info("Create and deploy the contract first.")

elif exp.startswith("6."):
    st.header(EXPS[5])
    st.write("**Aim:** Trace a medicine batch from manufacturer through distributor and pharmacy to patient using an append-only ledger.")
    stage=st.selectbox("Actor",["Manufacturer","Distributor","Pharmacy","Patient / Verification"])
    if stage=="Manufacturer":
        name=st.text_input("Medicine","DemoCure"); batch=st.text_input("Batch ID","BATCH-001"); qty=st.number_input("Quantity",1,10000,100)
        expiry=st.date_input("Expiry",value=date.today().replace(year=date.today().year+1))
        if st.button("Manufacture & record"):
            rec={"medicine":name,"batch":batch,"quantity":qty,"expiry":str(expiry),"holder":"Manufacturer","status":"Manufactured"}
            st.session_state.medicines.append(rec); st.session_state.supply_ledger.append({**rec,"time":str(datetime.now())}); st.success("Batch recorded.")
    elif stage in ["Distributor","Pharmacy"]:
        if not st.session_state.medicines: st.warning("Manufacture a batch first.")
        else:
            batch=st.selectbox("Batch",[m["batch"] for m in st.session_state.medicines])
            if st.button(f"Transfer to {stage}"):
                m=next(x for x in st.session_state.medicines if x["batch"]==batch); m["holder"]=stage; m["status"]=f"Received by {stage}"
                st.session_state.supply_ledger.append({**m,"time":str(datetime.now())}); st.success("Transfer appended.")
    else:
        batch=st.text_input("Batch ID to verify")
        if st.button("Verify"):
            rows=[x for x in st.session_state.supply_ledger if x["batch"]==batch]
            if rows: st.success("Batch found."); st.dataframe(rows,use_container_width=True)
            else: st.error("Batch not found.")
    st.subheader("Supply-chain ledger"); st.dataframe(st.session_state.supply_ledger,use_container_width=True)

elif exp.startswith("7."):
    st.header(EXPS[6])
    st.write("**Aim:** Introduce Solidity variables, functions, arrays, mappings, structs, events and validation.")
    topic=st.selectbox("Concept",["State variable","Function","Mapping","Array","Struct","Event","require / validation"])
    examples={"State variable":"uint256 public count = 0;","Function":"function increment() public { count += 1; }",
    "Mapping":"mapping(address => uint256) public balances;","Array":"address[] public members;",
    "Struct":"struct Student { uint id; string name; }","Event":"event Updated(address indexed by, uint value);",
    "require / validation":'require(msg.value > 0, "Value must be positive");'}
    st.code(examples[topic],language="solidity")
    st.markdown("### Mini execution sandbox")
    name=st.text_input("Variable name","score"); value=st.number_input("uint value",0,100000,10)
    if st.button("Execute state update"): st.session_state.syntax_vars[name]=value; st.success("State-changing function simulated.")
    st.json(st.session_state.syntax_vars)
    st.caption("A view read does not modify state; a state-changing call normally becomes a transaction and consumes gas.")

elif exp.startswith("8."):
    st.header(EXPS[7])
    st.write("**Aim:** Apply mappings, arrays and structs in small smart-contract application patterns.")
    case=st.radio("Application",["Car Rental","Land Registry","KYC"],horizontal=True)
    if case=="Car Rental":
        renter=st.text_input("Renter","Alice"); car=st.selectbox("Car",["EV-101","EV-202","EV-303"]); days=st.slider("Days",1,30,2)
        if st.button("Book car"): st.session_state.car_bookings.append({"renter":renter,"car":car,"days":days,"cost":days*50})
        st.dataframe(st.session_state.car_bookings,use_container_width=True)
    elif case=="Land Registry":
        land=st.text_input("Land ID","TN-001"); owner=st.text_input("New owner","Alice")
        if st.button("Register / transfer"):
            old=next((x["owner"] for x in st.session_state.lands if x["land"]==land),None)
            st.session_state.lands=[x for x in st.session_state.lands if x["land"]!=land]; st.session_state.lands.append({"land":land,"owner":owner,"previous":old})
        st.dataframe(st.session_state.lands,use_container_width=True)
    else:
        addr=st.text_input("Wallet address","0xDEMO"); verified=st.checkbox("KYC verified")
        if st.button("Update KYC"): st.session_state.kyc[addr]=verified
        st.json(st.session_state.kyc)
    st.info("Mappings → keyed lookup; arrays → collections; structs → grouped records.")

elif exp.startswith("9."):
    st.header(EXPS[8])
    st.write("**Aim:** Show how a proxy keeps an address/storage interface stable while logic can be upgraded.")
    c1,c2,c3=st.columns(3); c1.metric("Proxy address","0xPROXY-DEMO"); c2.metric("Implementation",st.session_state.proxy_version); c3.metric("Stored value",st.session_state.proxy_value)
    x=st.number_input("Input",0,1000,5)
    if st.button("Call setValue through proxy"):
        st.session_state.proxy_value=x if st.session_state.proxy_version=="V1" else x*2
        st.success("Delegate-style call simulated. Storage remains with proxy.")
    if st.button("Upgrade V1 → V2"): st.session_state.proxy_version="V2"; st.success("Logic upgraded; stored value retained.")
    st.code("""Proxy (stable address + storage)
    │ delegatecall
    ├── Logic V1: setValue(x) = x
    └── Logic V2: setValue(x) = x * 2""")
    st.warning("Real upgradeable contracts require careful storage-layout compatibility and access control.")

else:
    st.header(EXPS[9])
    st.write("**Aim:** Safely demonstrate common smart-contract vulnerability concepts and mitigations in a local model.")
    vuln=st.selectbox("Vulnerability",["Re-entrancy","Arithmetic overflow / underflow","'Private' on-chain data","Access control"])
    if vuln=="Re-entrancy":
        st.code("""// Vulnerable ordering (concept)
(bool ok,) = msg.sender.call{value: amount}("");
balances[msg.sender] -= amount;

// Safer ordering
balances[msg.sender] -= amount;
(bool ok,) = msg.sender.call{value: amount}("");""",language="solidity")
        bal=st.number_input("Contract balance",1,100,10)
        if st.button("Simulate vulnerable callback"):
            st.error(f"An external callback could re-enter before the balance update and attempt repeated withdrawals from {bal} units.")
            st.success("Mitigation: Checks-Effects-Interactions and/or a reentrancy guard.")
    elif vuln=="Arithmetic overflow / underflow":
        x=st.number_input("8-bit demo value",0,255,250); add=st.number_input("Add",0,255,10)
        if st.button("Compare arithmetic"):
            st.write(f"Unchecked 8-bit wraparound model: **{x} + {add} → {(x+add)%256}**")
            if x+add>255: st.success("Solidity 0.8+ checked arithmetic would revert by default rather than silently wrap.")
    elif vuln=="'Private' on-chain data":
        secret=st.text_input("Demo 'private' value","exam-answer")
        if st.button("Store demo value"):
            st.code(secret); st.warning("`private` restricts Solidity-level access; public-chain storage should not be treated as confidential.")
            st.success("Do not store secrets on a public chain; use appropriate off-chain/encryption/commitment designs.")
    else:
        owner=st.text_input("Owner","0xOWNER"); caller=st.text_input("Caller","0xALICE")
        if st.button("Attempt admin action"):
            st.success("Authorized.") if caller==owner else st.error("Rejected by owner/role check.")
        st.code('require(msg.sender == owner, "Not authorized");',language="solidity")

st.divider()
st.caption("Educational simulator. It does not reproduce Virtual Labs source code/assets and does not connect to a real blockchain by default.")
