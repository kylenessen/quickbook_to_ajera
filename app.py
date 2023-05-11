import streamlit as st
import pandas as pd
import re
from ofxparse import OfxParser
import base64
from datetime import datetime

pd.options.display.float_format = '{:,.2f}'.format

def extract_name(memo_string):
    pattern = r'[A-Z][A-Z ]+'
    match = re.search(pattern, memo_string)
    if match:
        # Split the matched string into words
        words = match.group(0).split()

        # If there are at least 2 words, return the first and last one
        if len(words) >= 2:
            return "{} {}".format(words[0].capitalize(), words[-1].capitalize())
        else:
            # If there's only one word, return it
            return words[0].capitalize()
    else:
        return None

def extract_card_number(memo_string):
    pattern = r'\d{4}(?=[A-Z])'
    match = re.search(pattern, memo_string)
    return match.group(0) if match else None

def convert_ofx_to_csv(file):
    ofx = OfxParser.parse(file)
    transactions = ofx.account.statement.transactions

    data = {
        'Date': [t.date for t in transactions],
        'Amount': [t.amount for t in transactions],
        'Memo': [t.memo for t in transactions],
        'Vendor': [t.payee for t in transactions],
        'Type': [t.type for t in transactions],
        'ID': [t.id for t in transactions],
    }

    df = pd.DataFrame(data)
    df['Cardholder'] = df['Memo'].apply(extract_name)
    df['Card Number'] = df['Memo'].apply(extract_card_number)

    return df[['Date', 'Cardholder', 'Card Number', 'Vendor', 'Amount', 'Type', 'ID','Memo']]

def file_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-button">Download {filename}</a>'
    return href

def generate_filename():
    current_date = datetime.now().strftime('%Y%m%d')
    return f"CreditCard_{current_date}.csv"

st.title('QBO/QFX to CSV Converter')

uploaded_file = st.file_uploader('Upload a QBO or QFX file', type=['qbo', 'qfx'])

if uploaded_file is not None:
    with st.spinner('Converting file...'):
        df = convert_ofx_to_csv(uploaded_file)
    st.success('Conversion complete!')
    df_display = df.copy()
    df_display['Amount'] = df_display['Amount'].apply(lambda x: '{:,.2f}'.format(x))
    st.write(df_display)
    output_filename = generate_filename()
    st.markdown(file_download_link(df, output_filename), unsafe_allow_html=True)
    
# Custom CSS for the download button
st.markdown("""
<style>
.download-button {
    font-size: 20px;
    padding: 10px 20px;
    background-color: purple;
    color: white;
    border-radius: 5px;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)