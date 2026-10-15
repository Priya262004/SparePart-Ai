import pandas as pd
import streamlit as st
import re

# -------------------- Page setup --------------------
st.set_page_config(
    page_title="SparePart AI | Inventory Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Professional dashboard UI --------------------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --navy:#10233F; --navy2:#17385B; --cyan:#11B8C9; --ink:#182B45; --muted:#718198; --line:#E1E8F0; --page:#F4F7FB; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--page); color:var(--ink); }
.block-container { max-width:1600px; padding-top:1.5rem; padding-bottom:2.5rem; }
header[data-testid="stHeader"] { background:transparent; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--navy) !important; letter-spacing:-.025em; }
h1 { font-weight:800 !important; font-size:2rem !important; }
h2 { font-weight:800 !important; font-size:1.35rem !important; }
h3 { font-weight:700 !important; font-size:1.05rem !important; }
p, label { color:var(--ink); }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#10233F 0%,#142F50 100%); border-right:1px solid #203E5F; }
section[data-testid="stSidebar"] * { color:#EAF2FA !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label { background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:.5rem .65rem; margin:.18rem 0; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:rgba(17,184,201,.16); }
.sp-brand { font-family:'Manrope',sans-serif; font-size:1.4rem; font-weight:800; color:white; letter-spacing:-.04em; }
.sp-brand span { color:#36D6E0; }
.sp-side-note { color:#B8C9DC; font-size:.78rem; line-height:1.5; margin-top:.25rem; }
.sp-hero { background:linear-gradient(115deg,#10233F 0%,#17385B 66%,#087F91 100%); border-radius:20px; padding:1.7rem 1.9rem; color:#fff; margin-bottom:1.2rem; box-shadow:0 12px 28px rgba(16,35,63,.12); border:1px solid rgba(255,255,255,.12); }
.sp-eyebrow { color:#63E0E6; font-size:.72rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin-bottom:.45rem; }
.sp-title { color:white; font-family:'Manrope',sans-serif; font-size:2.25rem; font-weight:800; line-height:1.12; letter-spacing:-.045em; }
.sp-subtitle { color:#E0EDF6; margin-top:.55rem; max-width:850px; line-height:1.6; font-size:.95rem; }
.sp-pills { margin-top:1rem; display:flex; flex-wrap:wrap; gap:.5rem; }
.sp-pill { color:#E9FCFF; background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.20); border-radius:999px; padding:.35rem .7rem; font-size:.75rem; font-weight:600; }
.sp-section { font-family:'Manrope',sans-serif; font-size:1.16rem; font-weight:800; color:var(--navy); margin:.3rem 0 .15rem; }
.sp-caption { color:var(--muted); font-size:.86rem; margin-bottom:.8rem; }
div[data-testid="stMetric"] { background:white; border:1px solid var(--line); border-radius:15px; padding:1rem 1.05rem; min-height:105px; box-shadow:0 4px 14px rgba(16,35,63,.035); }
div[data-testid="stMetricLabel"] { color:var(--muted); font-size:.82rem; font-weight:650; }
div[data-testid="stMetricValue"] { color:var(--navy); font-family:'Manrope',sans-serif; font-weight:800; }
div[data-testid="stDataFrame"],div[data-testid="stTable"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
div[data-testid="stTextInput"] input { border:1px solid #D3DFE9; border-radius:10px; min-height:2.9rem; background:#fff; }
.stButton>button,.stDownloadButton>button { border-radius:10px; min-height:2.7rem; font-weight:700; border:1px solid #10233F; background:#10233F; color:white; }
.stButton>button:hover,.stDownloadButton>button:hover { background:#087F91; border-color:#087F91; color:white; }
div[data-testid="stAlert"] { border-radius:11px; }
div[data-testid="stExpander"] { background:white; border:1px solid var(--line); border-radius:12px; }
hr { border-color:var(--line); margin:1.3rem 0; }
.sp-panel { background:white; border:1px solid var(--line); border-radius:15px; padding:1rem 1.1rem; }
.sp-footer { text-align:center; color:#8190A5; font-size:.78rem; padding:1.5rem 0 .3rem; }
@media(max-width:700px){.block-container{padding:.9rem .8rem 2rem}.sp-hero{padding:1.3rem;border-radius:15px}.sp-title{font-size:1.75rem}}
</style>
""", unsafe_allow_html=True)

if "search_history" not in st.session_state:
    st.session_state.search_history = []

# -------------------- Data and model --------------------
@st.cache_data
def load_parts():
    return pd.read_csv("data/spare_parts.csv")

try:
    df = load_parts()
except Exception as exc:
    st.error("Could not load data/spare_parts.csv. Check that the data folder and CSV file are in the same project directory.")
    st.exception(exc)
    st.stop()

required = ["part_id", "part_name", "category", "machine_model", "stock", "location"]
missing = [col for col in required if col not in df.columns]
if missing:
    st.error("The spare-parts dataset is missing required columns: " + ", ".join(missing))
    st.stop()

df["stock"] = pd.to_numeric(df["stock"], errors="coerce").fillna(0).astype(int)
status_order = ["Available", "Low stock", "Out of stock"]
def stock_status(qty):
    return "Out of stock" if qty == 0 else ("Low stock" if qty <= 2 else "Available")

df["Stock status"] = df["stock"].apply(stock_status)
total_parts = len(df)
stock_units = int(df["stock"].sum())
out_of_stock = df[df["stock"] == 0].copy()
low_stock = df[(df["stock"] > 0) & (df["stock"] <= 2)].copy()
needs_restock = df[df["stock"] <= 2].copy()
# Always create the recommendation column, including when no parts need restocking.
# Use one exact column name everywhere to avoid pandas KeyError exceptions.
needs_restock["Recommended order quantity"] = (
    10 - needs_restock["stock"]
).clip(lower=0).astype(int)

# -------------------- Sidebar navigation --------------------
with st.sidebar:
    st.markdown('<div class="sp-brand">SparePart <span>AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sp-side-note">Inventory intelligence workspace</div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Dashboard", "Semantic Search", "Inventory", "Stock Alerts", "Restocking", "Search History"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.caption(f"Inventory records: {total_parts:,}")
    st.caption("AI-powered part matching")

# -------------------- Header --------------------
st.markdown('''<div class="sp-hero">
<div class="sp-eyebrow">Inventory intelligence · AI-powered</div>
<div class="sp-title">SparePart AI</div>
<div class="sp-subtitle">Find the right spare parts faster, monitor inventory health, and make smarter replenishment decisions from one workspace.</div>
<div class="sp-pills"><span class="sp-pill">Semantic search</span><span class="sp-pill">Live stock overview</span><span class="sp-pill">Restocking insights</span></div>
</div>''', unsafe_allow_html=True)

# -------------------- Shared metric row --------------------
def show_metrics():
    a, b, c, d = st.columns(4)
    a.metric("Total parts", f"{total_parts:,}", help="Number of spare-part records in inventory")
    b.metric("Units in stock", f"{stock_units:,}", help="Total quantity across all spare parts")
    c.metric("Out of stock", f"{len(out_of_stock):,}", help="Parts with zero units available")
    d.metric("Low stock", f"{len(low_stock):,}", help="Parts with 1–2 units remaining")

# -------------------- Page content --------------------
if page == "Dashboard":
    st.markdown('<div class="sp-section">Dashboard overview</div><div class="sp-caption">A quick operational summary of your spare-parts inventory.</div>', unsafe_allow_html=True)
    show_metrics()
    st.markdown(" ")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="sp-section">Stock distribution</div><div class="sp-caption">Parts grouped by current stock status.</div>', unsafe_allow_html=True)
        distribution = df["Stock status"].value_counts().reindex(status_order, fill_value=0)
        st.bar_chart(distribution, color="#11B8C9", height=250)
    with right:
        st.markdown('<div class="sp-section">Parts requiring attention</div><div class="sp-caption">Low-stock and out-of-stock items to review first.</div>', unsafe_allow_html=True)
        if needs_restock.empty:
            st.success("No parts currently need restocking.")
        else:
            st.dataframe(needs_restock[["part_id", "part_name", "stock", "location", "Recommended order quantity"]], use_container_width=True, hide_index=True)
    st.markdown(" ")
    st.markdown('<div class="sp-section">Inventory at a glance</div><div class="sp-caption">Current stock quantity by spare part.</div>', unsafe_allow_html=True)
    stock_chart = df[["part_name", "stock"]].set_index("part_name").sort_values("stock", ascending=False)
    st.bar_chart(stock_chart, color="#17385B", height=280)
    st.caption("Stock-status thresholds: out of stock = 0 units; low stock = 1–2 units; available = more than 2 units.")

elif page == "Semantic Search":
    st.markdown('<div class="sp-section">Find a spare part</div><div class="sp-caption">Describe what you need in everyday language. Results are ranked using the words in your query.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        query_col, button_col = st.columns([5, 1.3], vertical_alignment="bottom")
        with query_col:
            query = st.text_input(
                "Describe the part you need",
                placeholder="Example: I need a motor for machine M100",
                label_visibility="collapsed",
                key="spare_part_query",
            )
        with button_col:
            search_clicked = st.button("Search parts  →", use_container_width=True, type="primary")

    if search_clicked:
        if not query.strip():
            st.warning("Enter a short description of the spare part you need.")
        else:
            if query not in st.session_state.search_history:
                st.session_state.search_history.append(query)

            # Lightweight text matching: does not require sentence-transformers or a model download.
            query_terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
            searchable = (
                df["part_name"].fillna("").astype(str) + " " +
                df["category"].fillna("").astype(str) + " " +
                df["machine_model"].fillna("").astype(str) + " " +
                df["part_id"].fillna("").astype(str) + " " +
                df["location"].fillna("").astype(str)
            )
            stop_words = {"i", "need", "a", "an", "the", "for", "of", "to", "with", "part", "machine"}
            query_terms -= stop_words

            def text_match_score(text):
                terms = set(re.findall(r"[a-zA-Z0-9]+", str(text).lower()))
                if not query_terms:
                    return 0.0
                overlap = len(query_terms & terms) / len(query_terms)
                # Small bonus for the full query appearing in a record.
                full_query = query.lower().strip()
                phrase_bonus = 0.15 if full_query and full_query in str(text).lower() else 0.0
                return min(1.0, overlap + phrase_bonus)

            scores = searchable.apply(text_match_score).to_numpy()
            indices = scores.argsort()[::-1][:3]
            results = df.iloc[indices][["part_id", "part_name", "category", "machine_model", "stock", "location"]].copy()
            results["Similarity"] = (scores[indices] * 100).round(1).astype(str) + "%"
            results["Stock status"] = results["stock"].apply(stock_status)
            st.markdown('<div class="sp-section">Best matches</div>', unsafe_allow_html=True)
            st.dataframe(results, use_container_width=True, hide_index=True)
            st.caption("These are keyword-based matches, not AI embedding similarity. Verify part specifications and machine compatibility before ordering.")

elif page == "Inventory":
    st.markdown('<div class="sp-section">Complete inventory</div><div class="sp-caption">Search, review, and filter your spare-part records.</div>', unsafe_allow_html=True)
    show_metrics()
    filter_col, search_col = st.columns([1, 2])
    with filter_col:
        selected_status = st.selectbox("Filter by stock status", ["All statuses"] + status_order)
    with search_col:
        inventory_query = st.text_input("Search inventory", placeholder="Search part name, ID, category, machine, or location")
    view = df.copy()
    if selected_status != "All statuses":
        view = view[view["Stock status"] == selected_status]
    if inventory_query.strip():
        mask = view.astype(str).apply(lambda col: col.str.contains(inventory_query.strip(), case=False, na=False)).any(axis=1)
        view = view[mask]
    st.caption(f"Showing {len(view):,} of {len(df):,} parts")
    st.dataframe(view, use_container_width=True, hide_index=True)

elif page == "Stock Alerts":
    st.markdown('<div class="sp-section">Stock alerts</div><div class="sp-caption">Parts that may need attention before they affect operations.</div>', unsafe_allow_html=True)
    alert_a, alert_b = st.columns(2)
    with alert_a:
        st.markdown("### 🔴 Out of stock")
        if out_of_stock.empty:
            st.success("No parts are currently out of stock.")
        else:
            st.error(f"{len(out_of_stock)} part(s) have zero units available.")
            st.dataframe(out_of_stock[["part_id", "part_name", "stock", "location"]], use_container_width=True, hide_index=True)
    with alert_b:
        st.markdown("### 🟠 Low stock")
        if low_stock.empty:
            st.success("No low-stock parts found.")
        else:
            st.warning(f"{len(low_stock)} part(s) have 1–2 units remaining.")
            st.dataframe(low_stock[["part_id", "part_name", "stock", "location"]], use_container_width=True, hide_index=True)

elif page == "Restocking":
    st.markdown('<div class="sp-section">Restocking recommendations</div><div class="sp-caption">Suggested order quantities to bring low-stock items toward a target of 10 units.</div>', unsafe_allow_html=True)
    if needs_restock.empty:
        st.success("All spare parts currently have more than 2 units in stock.")
    else:
        st.dataframe(needs_restock[["part_id", "part_name", "category", "machine_model", "stock", "location", "Recommended order quantity"]], use_container_width=True, hide_index=True)
        csv_data = needs_restock[["part_id", "part_name", "stock", "location", "Recommended order quantity"]].to_csv(index=False).encode("utf-8")
        st.download_button("Download restocking report  ↓", data=csv_data, file_name="restocking_report.csv", mime="text/csv")
        st.caption("Order quantities are suggestions based on a target stock level of 10. Confirm supplier lead times and actual demand before placing orders.")

elif page == "Search History":
    st.markdown('<div class="sp-section">Recent search history</div><div class="sp-caption">Review recent semantic searches from this session.</div>', unsafe_allow_html=True)
    if st.session_state.search_history:
        for index, item in enumerate(reversed(st.session_state.search_history[-10:]), start=1):
            st.markdown(f"**{index}.** 🔎 {item}")
        if st.button("Clear search history"):
            st.session_state.search_history = []
            st.rerun()
    else:
        st.info("Your recent searches will appear here after you search for a part.")

st.markdown('<div class="sp-footer">SparePart AI · AI-assisted spare-parts search and inventory visibility</div>', unsafe_allow_html=True)
