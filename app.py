# app.py
import streamlit as st
import pandas as pd
import snowflake.connector
import matplotlib.pyplot as plt

# --- Funksjon for å hente data ---
#def get_data(call):
#    snowflakecon = snowflake.connector.connect(
#        user="ABO_SERVICE_USER",
#        password='!7wHQT9VD0nF^wzSdgHv20sK',
#        account='schibsted.eu-west-1',
#        warehouse='shared_wh_medium',
#        database='',
#        schema='HALJOHNS',
#        role='SUBSCRIPTION_NORWAY_RED'
    )
#    cursor = snowflakecon.cursor()
#    result = cursor.execute(call).fetchall()
#    hdrs = pd.DataFrame(cursor.description)
#    df_ready = pd.DataFrame.from_records(result)
#    df_ready.columns = hdrs['name']
#    cursor.close()
#    snowflakecon.close()
#    return df_ready

# --- Streamlit starter her ---
st.title("Analyse av Fordelsdata fra Snowflake")

#query = """
#select * from subs_sandbox.haljohns.fordel 
#where object_id not like ('%preview%') 
#and object_id not like ('%benefit%')
#and product_tag in ('sabenefits', 'btbenefits', 'apbenefits')
#"""

#fordelsdata = get_data(query)

csv_path = "fordelsdata.csv"  # Endre stien hvis filen ligger et annet sted
fordelsdata = pd.read_csv(csv_path)


# Hent data automatisk hvis det ikke finnes i session_state
if "fordelsdata" not in st.session_state:
    fordelsdata = get_data(query)
    fordelsdata = fordelsdata.dropna(subset=[
        "ARTICLE_TEXT_ALL", 
        "SECTION_PARENT_TITLE", 
        "SECTION_TITLE", 
        "SECTION_FULL_TITLE"
    ]).copy()
    st.session_state["fordelsdata"] = fordelsdata

# Mulighet for å oppdatere data manuelt med knapp
if st.button("Oppdater data"):
    fordelsdata = get_data(query)
    fordelsdata = fordelsdata.dropna(subset=[
        "ARTICLE_TEXT_ALL", 
        "SECTION_PARENT_TITLE", 
        "SECTION_TITLE", 
        "SECTION_FULL_TITLE"
    ]).copy()
    st.session_state["fordelsdata"] = fordelsdata

# Sjekk om data er lastet inn
if "fordelsdata" in st.session_state:
    fordelsdata = st.session_state["fordelsdata"]

    st.subheader("📦 Antall artikler per product_tag")
    if "PRODUCT_TAG" in fordelsdata.columns:
        product_tag_counts = fordelsdata["PRODUCT_TAG"].value_counts()
        st.bar_chart(product_tag_counts)
        st.dataframe(product_tag_counts)
    else:
        st.warning("❗ Kolonnen 'PRODUCT_TAG' finnes ikke i datasettet.")

    st.subheader("📊 Antall av hver SECTION_TITLE per PRODUCT_TAG")
    if "PRODUCT_TAG" in fordelsdata.columns and "SECTION_TITLE" in fordelsdata.columns:
        pivot = pd.pivot_table(
            fordelsdata, 
            index="SECTION_TITLE", 
            columns="PRODUCT_TAG", 
            values="ARTICLE_TEXT_ALL", 
            aggfunc="count",
            fill_value=0
        )
        st.dataframe(pivot)
    else:
        st.warning("❗ Kolonnene 'PRODUCT_TAG' og/eller 'SECTION_TITLE' finnes ikke i datasettet.")

    # Velg product_tag og vis antall artikler per SECTION_TITLE for valgt tag
    if "PRODUCT_TAG" in fordelsdata.columns and "SECTION_TITLE" in fordelsdata.columns:
        st.subheader("📈 Antall artikler per SECTION_TITLE for valgt PRODUCT_TAG")
        valgt_tag = st.selectbox(
            "Velg PRODUCT_TAG",
            sorted(fordelsdata["PRODUCT_TAG"].unique())
        )
        filtered = fordelsdata[fordelsdata["PRODUCT_TAG"] == valgt_tag]
        section_counts = filtered["SECTION_TITLE"].value_counts()
        
        # Horisontal bar chart med matplotlib
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(6, max(4, len(section_counts) * 0.4)))
        section_counts.sort_values().plot.barh(
            ax=ax,
            color="#1f77b4"  # Streamlit sin standard blåfarge
            )
        ax.set_xlabel("Antall artikler")
        ax.set_ylabel("SECTION_TITLE")
        st.pyplot(fig)
        
        st.dataframe(section_counts)
