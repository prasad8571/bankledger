import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Bank Ledger Mapper", layout="wide")

st.title("🏦 Bank Statement → Ledger Mapping")
st.text("with this tool you can map yor bank statement to Tally Ledger")
st.text("Please feel free to Reach out to  {bangaruca@gmail.com} for any sugessions/feedback")
# ---------------------------
# Excel Template Generator
# ---------------------------
st.subheader("📄 Download Excel Templates")

def generate_bank_template():
    df = pd.DataFrame({
        "Date": [],
        "Narration": [],
        "Withdrawal": [],
        "Deposit": []
    })
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Bank_Statement")
    return buffer.getvalue()

def generate_rules_template():
    df = pd.DataFrame({
        "Keyword": [],
        "Ledger_Name": []
    })
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Rules")
    return buffer.getvalue()

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "⬇ Download Bank Statement Template",
        data=generate_bank_template(),
        file_name="Bank_Statement_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    st.download_button(
        "⬇ Download Rules Template",
        data=generate_rules_template(),
        file_name="Ledger_Rules_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------
# File Uploads
# ---------------------------
bank_file = st.file_uploader(
    "Upload Bank Statement (Excel)",
    type=["xlsx"]
)

rules_file = st.file_uploader(
    "Upload Mapping Rules (Excel)",
    type=["xlsx"]
)

# ---------------------------
# Processing
# ---------------------------
if bank_file and rules_file:
    try:
        bank_df = pd.read_excel(bank_file)
        rules_df = pd.read_excel(rules_file)

        # Standardize columns
        bank_df.columns = bank_df.columns.str.strip()
        rules_df.columns = rules_df.columns.str.strip()

        # Validate required columns
        required_bank_cols = {"Narration"}
        required_rule_cols = {"Keyword", "Ledger_Name"}

        if not required_bank_cols.issubset(bank_df.columns):
            st.error("Bank statement must contain 'Narration' column.")
            st.stop()

        if not required_rule_cols.issubset(rules_df.columns):
            st.error("Rules file must contain 'Keyword' and 'Ledger Name' columns.")
            st.stop()

        # ---------------------------
        # Mapping Logic
        # ---------------------------
        def map_ledger(narration, rules):
            narration = str(narration).upper()
            for _, rule in rules.iterrows():
                if rule["Keyword"].upper() in narration:
                    return rule["Ledger_Name"]
            return "Suspense Bank"

        bank_df["Ledger"] = bank_df["Narration"].apply(
            lambda x: map_ledger(x, rules_df)
        )

        # ---------------------------
        # Preview
        # ---------------------------
        st.subheader("Mapped Transactions Preview")
        st.dataframe(bank_df, width="content")

        # ---------------------------
        # Excel Download (FIXED BUFFER ISSUE)
        # ---------------------------
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            bank_df.to_excel(writer, index=False, sheet_name="Mapped Data")
            
        st.download_button(
            label="⬇ Download Mapped Excel",
            data=buffer.getvalue(),
            file_name="Bank_Ledger_Mapped.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("Processing failed")
        st.exception(e)

else:
    st.info("Please upload both Bank Statement and Rules file.")

st.text(" if you want to create tally vouchers xml file please use https://bank2tallyvoucher.streamlit.app/") 
