import streamlit as st
import pandas as pd
from supabase import create_client, Client
import datetime


# Initialize connection.
# Uses st.cache_resource to only run once.
st.title("Product Purchase Tracker")

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
df = pd.DataFrame(rows.data)