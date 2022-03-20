import streamlit as st
import pandas as pd
import numpy as np
from formulation_assistant_utils import *
import time

title_con = st.container()
text_con = st.container()
inputs_con = st.container()
results_con = st.container()
button_con = st.container()
about_con = st.container()


# with open('style.css') as f:
#     st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

df_drug, df_cancer, dict_drug = get_data()
drug_list, cancer_list = get_select_box_options(df_drug, df_cancer)
with title_con:
    st.title('Formulation Assistant')

with text_con:
    st.markdown('**Drug classifaction by Type as function of  nano-particals (NPs) stability**<br /> '
                '<b><i><span style="color:#2B78FF">_Type 1_</b></i> - Drugs that formulate “Good” and stable NPs<br />'
                '<b><i><span style="color:#2B78FF">_Type 2_</b></i> - Drugs that form Good but not stable NPs<br />'
                '<b><i><span style="color:#2B78FF">_Type 3_</b></i>  - Aggregates<br />'
                '<b><i><span style="color:#2B78FF">_Type 4_</b></i>  - Drugs that failed to precipitate<br />'
                '\u2022 Particles are “Good” if size<150nm, PDI<  0.2,<br />'
                '\u2022  Particles are stable if they remain “good” after 3 days', unsafe_allow_html=True)

with button_con:
    button_col1, button_col2, button_col3 = st.columns(3)

    clear_button = button_col1.button('Clear')
    if clear_button:
        st.session_state['drug_in'] = []
        st.session_state['cancer_in'] = ''

    help_button = button_col3.button('Help')
    if help_button:
        st.markdown('_Help is on the way..._')

    with inputs_con:
        drug_in = st.multiselect('Select Drugs (optional, up to 2)', drug_list, key='drug_in')
        cancer_in = st.selectbox('Select Cancer Type (optional)', cancer_list, key='cancer_in')

with results_con:
    if len(drug_in) > 2:
        st.markdown('<b><span style="color:#AF1F22">Please select up to two drugs', unsafe_allow_html=True)
        df_results = None

    elif len(drug_in) == 2:
        if cancer_in == '':
            df_results = search_by_two_drugs(drug_in, df_cancer)
        else:
            df_results = search_by_two_drugs_and_cancer(drug_in, cancer_in, df_cancer)

    elif len(drug_in) == 1:
        if cancer_in == '':
            df_results = search_by_single_drug(drug_in[0], df_cancer)
        else:
            df_results = search_by_single_drug_and_cancer(drug_in[0], cancer_in, df_cancer)

    elif len(drug_in) == 0:
        if cancer_in == '':
            df_results = None
        else:
            df_results = search_by_cancer(cancer_in, df_cancer)

    plot_result_df(df_results, results_con, drug_in, dict_drug)

with button_con:
    csv_to_save = get_data_to_save(df_results)

    export_button = button_col2.download_button(
        label="Export",
        data=csv_to_save,
        file_name=f'Formulation_Assistant_Data_{time.strftime("%d.%m.%Y-%H:%M:%S")}.csv',
        mime='text/csv',
    )

with about_con:
    st.markdown('\xA9 Shamay\'s Lab')
