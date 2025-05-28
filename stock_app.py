import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Stock Manager", layout="centered")
st.title("📦 Stock Management App")

# Load the Excel file (must be in the same repo)
try:
    df = pd.read_excel("base_stock.xlsx")
except FileNotFoundError:
    st.error("❌ base_stock.xlsx file not found.")
    st.stop()

df.columns = [col.strip() for col in df.columns]

st.subheader("📊 Current Stock")
st.dataframe(df)

# --- Stock Update Form ---
st.subheader("🔄 Update Stock")
product_code = st.text_input("Enter Product Code (optional)").strip().upper()
product_name = st.text_input("Or Enter Product Name").strip()
supplier = st.text_input("Enter Supplier").strip()
quantity = st.number_input("Quantity", min_value=1, step=1)
action = st.selectbox("Action", ["Add", "Remove"])
submitted = st.button("Update Stock")

if submitted:
    row = None

    if product_code:
        match = df[df['Product Code'].astype(str).str.upper() == product_code]
        if not match.empty:
            row = match.index[0]

    if row is None and product_name and supplier:
        match = df[(df['Product Name'].str.lower() == product_name.lower()) &
                   (df['Supplier'].str.lower() == supplier.lower())]
        if not match.empty:
            row = match.index[0]

    if row is None:
        st.warning("Product not found. Adding as new entry.")
        new_row = {
            'Product Name': product_name,
            'Product Code': product_code if product_code else "",
            'Supplier': supplier,
            'Quantity': quantity if action == 'Add' else -quantity
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        if action == 'Add':
            df.at[row, 'Quantity'] += quantity
            st.success(f"✅ Added {quantity} units.")
        else:
            if df.at[row, 'Quantity'] >= quantity:
                df.at[row, 'Quantity'] -= quantity
                st.success(f"✅ Removed {quantity} units.")
            else:
                st.error("❌ Not enough stock to remove that quantity.")

    # Display updated table
    st.subheader("📈 Updated Stock")
    st.dataframe(df)

    # Download button
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Download Updated Excel",
        data=buffer.getvalue(),
        file_name="updated_stock.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
