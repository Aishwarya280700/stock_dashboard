import streamlit as st
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Authenticate and create PyDrive client
@st.cache_resource
def connect_to_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("token.json")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # Launch browser for login
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("token.json")
    drive = GoogleDrive(gauth)
    return drive

drive = connect_to_drive()

# Google Drive file ID of base_stock.xlsx
FILE_ID = "your-google-drive-file-id"

# Download file from Drive
downloaded = drive.CreateFile({'id': FILE_ID})
downloaded.GetContentFile("base_stock.xlsx")

# Load DataFrame
df = pd.read_excel("base_stock.xlsx")
st.title("📦 Stock Dashboard (Google Drive)")
st.dataframe(df)

# Inputs
st.subheader("Update Stock")
product_code = st.text_input("Product Code").strip().upper()
product_name = st.text_input("Product Name").strip()
supplier = st.text_input("Supplier").strip()
quantity = st.number_input("Quantity", min_value=1, step=1)
action = st.selectbox("Action", ["Add", "Remove"])
submit = st.button("Apply")

if submit:
    match_index = None
    for i, row in df.iterrows():
        if product_code and row["Product Code"].strip().upper() == product_code:
            match_index = i
            break
        elif (not product_code and
              row["Product Name"].strip().lower() == product_name.lower() and
              row["Supplier"].strip().lower() == supplier.lower()):
            match_index = i
            break

    if match_index is not None:
        current_qty = df.at[match_index, "Quantity"]
        new_qty = current_qty + quantity if action == "Add" else current_qty - quantity
        if new_qty < 0:
            st.error("Not enough stock.")
        else:
            df.at[match_index, "Quantity"] = new_qty
            st.success("Stock updated.")
    else:
        if action == "Remove":
            st.error("Product not found.")
        else:
            new_row = {
                "Product Name": product_name,
                "Product Code": product_code,
                "Supplier": supplier,
                "Quantity": quantity
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("New product added.")

    # Save changes to Excel
    df.to_excel("base_stock.xlsx", index=False)

    # Upload updated file to Drive
    uploaded = drive.CreateFile({'id': FILE_ID})
    uploaded.SetContentFile("base_stock.xlsx")
    uploaded.Upload()
    st.success("Changes saved to Google Drive.")
    st.experimental_rerun()
