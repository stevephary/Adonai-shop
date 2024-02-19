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


def page_display_products():
    st.title("Manunuzi Ya Bidhaa")

    @st.cache_resource
    def init_connection():
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)

    supabase = init_connection()

    def run_query():
        return supabase.table("productpurchases").select("productname, quantity, unitprice, totalamount, record_date, sales_price").execute()

    def display_data(rows):
        df = pd.DataFrame(rows.data)
        df = df.rename(columns={
        'productname': 'Jina la Bidhaa',
        'quantity': 'Idadi',
        'unitprice': 'Bei ya Kila Bidhaa',
        'totalamount': 'Jumla ya Bei ',
        'record_date': 'Tarehe ya Ununuzi',
        'sales_price': 'Bei ya Kuuza Bidhaa',
        # Add more columns here if needed
        })
        df_sorted = df.sort_values(by="Tarehe ya Ununuzi", ascending=False)
        df_sorted.index = range(1, len(df_sorted) + 1)  # Resetting the index to start from 1
        st.table(df_sorted)

    rows = run_query()
    display_data(rows)

def page_add_product():
    st.title("Ongeza Bidhaa")

    @st.cache_resource
    def init_connection():
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)

    supabase = init_connection()

    def insert_new_product(product_name, quantity, totalamount, purchase_date):
        supabase.table("productpurchases").insert({
            "productname": product_name,
            "quantity": quantity,
            "unitprice": totalamount / quantity if quantity else 0,
            "totalamount": totalamount,
            "record_date": purchase_date.strftime("%Y-%m-%d")
        }).execute()

    with st.form(key="add_product_form"):
        product_name = st.text_input("Jina la Bidhaa")
        purchase_date = st.date_input("Tarehe ya Ununuzi", value=datetime.date.today())
        quantity = st.number_input("Idadi", min_value=1)
        totalamount = st.number_input("Jumla ya Bei", min_value=1.00)
        submitted = st.form_submit_button("Ongeza Bidhaa")

        if submitted:
            insert_new_product(product_name, quantity, totalamount, purchase_date)
            st.success("Bidhaa imeongezwa kwa mafanikio!")
            st.session_state.runpage = page_display_products  # Set the page to display products
            # st.experimental_rerun()  # Redirect to display page after adding product

def page_add_selling_price():
    st.title("Ongeza Bei ya Kuuza")

    @st.cache_resource
    def init_connection():
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)

    supabase = init_connection()

    # Get the list of product names from the purchases table
    def get_product_names():
        rows = supabase.table("productpurchases").select("productname, record_date").execute()
        return [f"{row['productname']}  ,   {row['record_date']}" for row in rows.data]

    product = get_product_names()

    # Dropdown to select the product
    selected_product = st.selectbox("Chagua Jina la Bidhaa", product)

    if selected_product:
        new_price = st.number_input("Bei ya Kuuza", min_value=0.00)
        if st.button("Weka Bei ya Kuuza"):
            supabase.table("productpurchases").update({
                "sales_price": new_price
            }).eq("productname" , selected_product).execute()
            st.success(f"Bei ya Kuuza ya '{selected_product}' imeongezwa kwa mafanikio!")

 
def main():
    pages = {
        "Onyesha Bidhaa": page_display_products,
        "Ongeza Bidhaa": page_add_product,
        "Ongeza Bei ya Kuuza": page_add_selling_price,
    }

    st.sidebar.title("ADONAI SHOP")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    page = pages[selection]
    page()

if __name__ == "__main__":
    if not check_password():
        st.stop()
    main()
