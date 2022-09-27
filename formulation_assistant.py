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
drug_list, cancer_list = get_select_box_options(dict_drug, df_cancer)
with title_con:
    # st.title('Nano Meta Synergy Finder')
    st.image('images/logo3.png')
    st.markdown('<b><i><span style=\"color:#345BAF\">Paper Link placeholder', unsafe_allow_html=True)
    # t_col1, t_col2, t_col3 = st.columns([4,1,1])
    st.video('https://www.youtube.com/watch?v=VscCpyPnI3A&ab_channel=YosiShamayLab')


with text_con:
    st.markdown("**Drug classification by Type as a function of  nano-particles (NPs) stability**<br /> "
                "<b><i><span style=\"color:#345BAF\">_Type 1_</b></i> - Drugs that formulate “Good” and stable NPs<br />"
                "<b><i><span style=\"color:#345BAF\">_Type 2_</b></i> - Drugs that formulate \"Good\" but unstable NPs<br />"
                "<b><i><span style=\"color:#345BAF\">_Type 3_</b></i>  - Drugs which aggregate into large structures <br />"
                "<b><i><span style=\"color:#345BAF\">_Type 4_</b></i>  - Drugs that do not to precipitate alone but can co-precipitate with Type 1 drugs<br />"
                "<b><i><span style=\"color:#345BAF\">_Type 5_</b></i>  - Drugs that do not precipitate alone nor co-precipitate with Type 1 drugs<br />"
                "\u2022 Particles are considered “Good” if they are of size < 150nm and have PDI < 0.2<br />"
                "\u2022 Particles are considered stable if they remain “Good” after 3 days<br />"
                "\u2022 'Pred. Type x' is the predicted type according to our model, as reviewed in the paper<br />"
                "**Fluorescence Status:**<br />"
                "\u2022 Fluorescent<br />"
                "\u2022 AIE - Aggregation-Induced Emission<br />", unsafe_allow_html=True)

with button_con:
    button_col1, button_col2, button_col3 = st.columns(3)

    clear_button = button_col1.button('Clear')
    if clear_button:
        st.session_state['drug_in'] = []
        st.session_state['cancer_in'] = ''

    help_button = button_col3.button('Help')
    if help_button:
        st.markdown('<b>NanoMetaSynergy Finder (NMSF) </b> is a search engine for anti-cancer drug combinations that can formulate ‘good’ and ‘stable’ and nanoparticles (see definition above) with synergy to specific cancer types.<br>'
                    '<br>To do so, simply choose up to two drugs from the list at the “Select Drugs” box, a single cancer type at the “Select Cancer Type” box, or any combination of them.<br>'
                    '<br>NMSF will scan its database, finding relevant combination and providing information on the anti-cancer drugs, their <b>Type</b> (see definition above), synergy to cancer types, indication if the two drugs can formulate ‘good’ and ‘stable’ and nanoparticles, a "frequency in literature” rating for each combination and even a direct link to PubMed search results.<br>'
                    '<br><br>We hope NMSF can help you in your research!<br>For support, please contact us at: b.f@campus.technion.ac.il<br><b>Enjoy!</b>', unsafe_allow_html=True)

    with inputs_con:
        drug_in = st.multiselect('Select Drugs (optional, up to 2)', drug_list, key='drug_in')
        cancer_in = st.selectbox('Select Cancer Type (optional)', cancer_list, key='cancer_in')

with results_con:
    if len(drug_in) > 2:
        st.markdown('<b><span style="color:#AF1F22">Please select up to two drugs', unsafe_allow_html=True)
        df_results = None

    elif len(drug_in) == 2:
        if cancer_in == '':
            df_results = search_by_two_drugs(drug_in, df_cancer, dict_drug)
        else:
            df_results = search_by_two_drugs_and_cancer(drug_in, cancer_in, df_cancer, dict_drug)

    elif len(drug_in) == 1:
        if cancer_in == '':
            df_results = search_by_single_drug(drug_in[0], df_cancer, dict_drug)
        else:
            df_results = search_by_single_drug_and_cancer(drug_in[0], cancer_in, df_cancer, dict_drug)

    elif len(drug_in) == 0:
        if cancer_in == '':
            df_results = None
        else:
            df_results = search_by_cancer(cancer_in, df_cancer, dict_drug)

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
    st.write("[\xA9 Shamay\'s Lab](https://www.shamaylab.com/research-1)")
