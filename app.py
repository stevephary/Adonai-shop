import streamlit as st
from supabase import create_client, Client

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query.
def run_query():
    return supabase.table("productpurchases").select("*").execute()

rows = run_query()

# Print results.
for row in rows.data:
    st.write(f"{row['productname']}")