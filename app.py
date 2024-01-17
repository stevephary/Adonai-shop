import streamlit as st
import pandas as pd
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

# Convert the result to a Pandas DataFrame.
df = pd.DataFrame(rows.data)

# Sidebar
st.sidebar.title("ADONAI SHOP")
show_data_button = st.sidebar.button("Manunuzi ya bidhaa")

# Display the Pandas DataFrame using Streamlit table based on the button click.
if show_data_button:
    st.write(df)