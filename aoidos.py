
import pandas as pd
import streamlit as st
import os
import pickle
import numpy as np
import time
from urllib import parse


st.sidebar.image("https://www.brandfibres.com/img/bf-logo.png")
st.image("logos/aoidos_logo_light_green.png")


choose_language = st.sidebar.selectbox(
    'Language of the stories',
    ("pl", "en")
)
    

def choose_model():
    model_name = f"aoidos_{choose_language}/aoidos_{choose_language}.pkl"
    with open(model_name, 'rb') as file:
        model = pickle.load(file)
    return model


file_upload = st.sidebar.file_uploader("Filename", type=["csv", "xls", "xlsx"])
text_column_name = st.sidebar.text_input("Text column", "Treść wypowiedzi")
url_column_name = st.sidebar.text_input("URL column", "Link do wypowiedzi")


def read_data():
    try:
        return pd.read_csv(file_upload, sep=";")
    except:
        try:
            return pd.read_excel(file_upload, engine="openpyxl")
        except:
            return pd.read_csv(file_upload)


if st.sidebar.button("Find stories"):
    filename = file_upload.name.split(".")[0]
    df = read_data()
    initial_length=len(df)
    
    model = choose_model()
    df["predicted_tag"] = df[text_column_name].apply(str)\
                                              .apply(lambda x: model.predict([x]))\
                                              .apply(lambda x: str(x[0]))
    df = df[df["predicted_tag"]=="1"]
    df = df[df[text_column_name].apply(str).apply(len) > 100]
    if "Unnamed: 0" in df.columns:
        del df["Unnamed: 0"]
    
    eventual_length = len(df)

    st.write(f"## Found {eventual_length} stories in the dataset of {initial_length}")
    n=1
    while f"{filename.split('.')[0]}_stories_{n}.xlsx" in os.listdir():
        n+=1

    if eventual_length > 0:
        st.write(f'#### Exported excel with stories only')
        st.write("_"*50)

        df.to_excel(f"{filename}_stories_{n}.xlsx")
        
    cols = st.beta_columns(2)
    gen = (0 if n % 2 == 0 else 1 for n in range(len(df[text_column_name]) + 1))

    for idx, row in enumerate(df[[text_column_name, url_column_name]].values, start=1):
        col_num = next(gen)
        cols[col_num].write(f"### ({str(idx)})")
        if len(str(row[0])) < 500:
            cols[col_num].write(row[0])
        else:
            cols[col_num].markdown(row[0][:500]+"<p style='color:magenta'>... [visit the link to read the full story]</p>", unsafe_allow_html=True)
            # cols[col_num].write(row[0][:500]+"... [visit the link to read the full story]")
        url = parse.urlsplit(row[1]).netloc
        cols[col_num].markdown(f'<a href="{row[1]}" target="_blank">{url}</a>', unsafe_allow_html=True)
        cols[col_num].write("-"*50)


    
