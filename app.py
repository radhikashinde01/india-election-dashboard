import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="India Election Dashboard", layout="wide")
st.title(" India Election Dashboard")
st.write("Upload an election dataset (CSV) to explore insights interactively.")

# Upload CSV
uploaded_file = st.file_uploader("📂 Upload your election CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    st.success("✅ File loaded successfully!")
    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head())

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    if "year" in df.columns:
        year = st.sidebar.selectbox("Select Year", sorted(df['year'].dropna().unique()))
        df = df[df['year'] == year]
    if "st_name" in df.columns:
        state = st.sidebar.selectbox("Select State", sorted(df['st_name'].dropna().unique()))
        df = df[df['st_name'] == state]

    st.subheader(f"📈 Analysis for {state if 'st_name' in df.columns else ''} {year if 'year' in df.columns else ''}")

    # Turnout distribution
    if "turnout_pct" in df.columns:
        fig1 = px.histogram(df, x="turnout_pct", nbins=20, title="Turnout Distribution (%)")
        st.plotly_chart(fig1, use_container_width=True)

    # Top parties by votes
    if "partyname" in df.columns and "totvotpoll" in df.columns:
        party_votes = df.groupby('partyname')['totvotpoll'].sum().sort_values(ascending=False).head(10)
        fig2 = px.bar(party_votes.reset_index(), x="partyname", y="totvotpoll",
                      title="Top 10 Parties by Votes", labels={'partyname':'Party','totvotpoll':'Votes'})
        st.plotly_chart(fig2, use_container_width=True)

    # Candidate gender distribution
    if "cand_sex" in df.columns:
        fig3 = px.pie(df, names="cand_sex", title="Candidate Gender Distribution")
        st.plotly_chart(fig3, use_container_width=True)

    # ✅ Winning Party per Constituency
    if "pc_name" in df.columns and "totvotpoll" in df.columns and "partyname" in df.columns:
        winners = df.loc[df.groupby('pc_name')['totvotpoll'].idxmax()]
        fig4 = px.bar(winners, x='pc_name', y='totvotpoll', color='partyname',
                      title="Winning Party per Constituency",
                      labels={'pc_name':'Constituency','totvotpoll':'Votes','partyname':'Party'})
        st.plotly_chart(fig4, use_container_width=True)

    # Summary metrics
    st.subheader("📌 Key Insights")
    if "totvotpoll" in df.columns:
        st.metric("Total Votes Polled", f"{df['totvotpoll'].sum():,}")
    if "electors" in df.columns:
        st.metric("Total Electors", f"{df['electors'].sum():,}")
    if "turnout_pct" in df.columns:
        st.metric("Average Turnout (%)", f"{df['turnout_pct'].mean():.2f}")

    # Download filtered dataset
    st.subheader("📥 Download Filtered Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="filtered_election_data.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload a CSV file to start analysis.")
