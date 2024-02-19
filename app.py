import streamlit as st
import pandas as pd
import hmac
from supabase import create_client
import datetime




def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


# Initialize connection.
st.title("Manunuzi ya Bidhaa")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query():
    return supabase.table("productpurchases").select("productname, quantity, unitprice, totalamount, record_date, sales_price").execute()

def display_data(rows):
    table_placeholder = st.empty()
    df = pd.DataFrame(rows.data)
    df = df.rename(columns={
    'productname': 'Jina la Bidhaa',
    'quantity': 'Idadi',
    'unitprice': 'Bei ya Kila Bidhaa',
    'totalamount': 'Jumla ya Bei ',
    'record_date': 'Tarehe ya Ununuzi',
    'sales_price': 'Bei ya Kuuza'
    # Add more columns here if needed
    })
    df_sorted = df.sort_values(by="Tarehe ya Ununuzi", ascending=False)
    df_sorted.index = range(1, len(df_sorted) + 1)  # Resetting the index to start from 1
    table_placeholder.table(df_sorted)



def add_new_purchase(form_placeholder):
    with form_placeholder:
        with st.form(key="add_purchase_form"):
            product_name = st.text_input("Jina la Bidhaa", key="product_name")
            purchase_date = st.date_input("Tarehe ya Ununuzi", value=datetime.date.today(), key="purchase_date")
            quantity = st.number_input("Idadi", min_value=1, key="quantity")
            totalamount = st.number_input("Jumla ya Bei", min_value=1.00, key="totalamount")
            st.form_submit_button("Submit", on_click=lambda: st.session_state.update(submitted=True))

def insert_new_purchase():
    supabase.table("productpurchases").insert({
        "productname": st.session_state.product_name,
        "quantity": st.session_state.quantity,
        "unitprice": st.session_state.totalamount / st.session_state.quantity if st.session_state.quantity else 0,
        "totalamount": st.session_state.totalamount,
        "record_date": st.session_state.purchase_date.strftime("%Y-%m-%d")
    }).execute()

def delete_purchase(selected_record_date, selected_product_name):
    supabase.table("productpurchases").delete().match({"record_date": selected_record_date, "productname": selected_product_name}).execute()

rows = run_query()

form_placeholder = st.empty()
add_button = form_placeholder.button("Ongeza Manunuzi", on_click=lambda: st.session_state.update(submitted=False), key="add_button")

if add_button:
    add_new_purchase(form_placeholder)

if st.session_state.get("submitted"):
    insert_new_purchase()
    form_placeholder.empty()
    st.session_state.update(submitted=False)
    st.rerun()

if not add_button:
    delete_prod = pd.DataFrame(rows.data)[['record_date', 'productname']].drop_duplicates().values.tolist()
    selected_product = st.selectbox("Chagua Bidhaa", [f"{date}  , {product}" for date, product in delete_prod], key="selected_product")

    if selected_product:
        selected_record_date, selected_product_name = selected_product.split(",")
        selected_rows = pd.DataFrame(rows.data)
        selected_rows = selected_rows[(selected_rows['record_date'] == selected_record_date.strip()) & (selected_rows['productname'] == selected_product_name.strip())]
        if not selected_rows.empty:
            st.table(selected_rows)
            delete_button = st.button("Futa Bidhaa", key="delete_button")
            if delete_button:
                delete_purchase(selected_record_date, selected_product_name)
                st.rerun()
            st.stop()

    display_data(rows)