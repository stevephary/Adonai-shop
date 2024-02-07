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

# Load data.    
rows = run_query()

# Display data.
def display_data():
    table_placeholder = st.empty()
    df = pd.DataFrame(rows.data)
    table_placeholder.table(df)

# Add new purchase.
form_placeholder = st.empty()
table_placeholder = st.empty()

def submitted():
    st.session_state.submitted = True
def reset():
    st.session_state.submitted = False

add_button = form_placeholder.button("Add new purchase", on_click=reset, key="add_button")
if add_button:
    with form_placeholder:
        with st.form(key="add_purchase_form"):
            product_name = st.text_input("Product Name", key="product_name")
            purchase_date = st.date_input("Purchase Date", value=datetime.date.today(), key="purchase_date")
            quantity = st.number_input("Quantity", min_value=1, key="quantity")
            totalamount = st.number_input("Total Amount", min_value=1.00, key="totalamount")
            # st.session_state.unitprice = (totalamount / quantity if quantity else 0)

            st.form_submit_button("Submit", on_click=submitted)

if "submitted" in st.session_state:
    if st.session_state.submitted == True:
        # # Print or log the form data for inspection
        # print("Form Data:")
        # print("Product Name:", st.session_state.product_name)
        # print("Purchase Date:", st.session_state.purchase_date)
        # print("Quantity:", st.session_state.quantity)
        # print("Total Amount:", st.session_state.totalamount)
        # print("Unit Price:", st.session_state.totalamount / st.session_state.quantity if st.session_state.quantity else 0)

        supabase.table("productpurchases").insert({
            "productname": st.session_state.product_name,
            "quantity": st.session_state.quantity,
            "unitprice": st.session_state.totalamount / st.session_state.quantity if st.session_state.quantity else 0,
            "totalamount": st.session_state.totalamount,
            "record_date": st.session_state.purchase_date
        }).execute()
        form_placeholder.empty()
        reset()
        st.rerun()



delete_prod = pd.DataFrame(rows.data)[['record_date', 'productname']].drop_duplicates().values.tolist()
# Create a dropdown menu with the record dates and product names
selected_product = st.selectbox("Select a product", delete_prod, key="selected_product")

# Delete product
delete_button = st.button("Delete Product")
if delete_button:
    # Delete the product from the database
    supabase.table("productpurchases").delete().match({"record_date": selected_product[0], "productname": selected_product[1]}).execute()
    st.rerun()

if not add_button:
    display_data()

