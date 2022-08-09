import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np


@st.cache
def get_cancer_abbreviations_dict():
    return {'GIST': 'Gastrointestinal Stromal Tumor',
            'HNSCC': 'Head And Neck Cancer',
            'HCC': 'Hepatocellular Carcinoma',
            'NSCLC': 'Non-Small Cell Lung Cancer',
            'SCLC': 'Small Cell Lung Cancer',
            'GBM': 'Glioblastoma',
            'AML': 'Acute Myeloid Leukemia',
            'MCL': 'Mantle Cell Lymphoma',
            'TNBC': 'Breast Cancer',
            'CML': 'Chronic Myelogenous Leukemia',
            '17Aag': '17-AAG',
            'DLBCL': 'Diffuse Large B-Cell Lymphoma',
            'um': 'Uveal Melanoma',
            'crc': 'Colon Cancer',
            'colorectal cancer': 'Colon Cancer',
            'dipg': 'Diffuse Intrinsic Pontine Glioma',
            'OVARIAN CANCER': 'Ovarian Cancer'}


@st.cache
def get_data():
    xls = pd.ExcelFile("Drug Classification and synergy9.0.xlsx")
    df_drug = pd.read_excel(xls, 'Types(chemistry)')
    df_cancer = pd.read_excel(xls, 'Synergy(biology)', keep_default_na=False)
    # df_cancer.replace(get_cancer_abbreviations_dict(), inplace=True)
    # # df_cancer["Fluorescence Status"].replace({'NA': 'Non-Active'}, inplace=True)
    # df_cancer["Fluorescence Status"].replace({'Non-Active': 'NA'}, inplace=True)
    #
    dict_drug = {}
    for cur_col in list(df_drug):
        for cur_drug in list(df_drug[cur_col].dropna()):
            if cur_drug.isupper():
                dict_drug[cur_drug] = cur_col
            else:
                dict_drug[cur_drug.title()] = cur_col
    # pd.options.mode.chained_assignment = None
    # all_drug_type = []
    # confidence_list = []
    # for index, row in df_cancer.iterrows():
    #     if not row['Cancers'].isupper():
    #         df_cancer['Cancers'][index] = row['Cancers'].title()
    #     if not row['TypeI'].isupper():
    #         df_cancer['TypeI'][index] = row['TypeI'].title()
    #     if not row['All drugs'].isupper():
    #         df_cancer['All drugs'][index] = row['All drugs'].title()
    #
    #     if df_cancer['All drugs'][index] in list(dict_drug.keys()):
    #         all_drug_type.append(dict_drug[df_cancer['All drugs'][index]])
    #     else:
    #         all_drug_type.append('Type NA')
    #
    #     confidence_list.append(set_confidence(row))
    #
    # df_cancer['all_drug_type'] = all_drug_type
    # df_cancer['confidence_level'] = confidence_list
    return df_drug, df_cancer, dict_drug


@st.cache
def get_select_box_options(df_drug, df_cancer):
    drug_list = []
    for cur_type in list(df_drug):
        drug_list = drug_list + df_drug[cur_type].dropna().to_list()
    drug_list = list(set(drug_list))
    # drug_list.append('')
    drug_list.sort(reverse=False)

    cancer_list = list(set(df_cancer['Cancers'].to_list()))
    cancer_list.append('')
    cancer_list.sort(reverse=False)
    return drug_list, cancer_list


def set_confidence(row, confidence_threshold=None):  # 1-3 low , 4-10 medium, >11 high #
    if confidence_threshold is None:
        confidence_threshold = [3, 10]
    if row['# of publications'] <= confidence_threshold[0]:
        return 'Rare'
    elif row['# of publications'] <= confidence_threshold[1]:
        return 'Medium'
    elif row['# of publications'] > confidence_threshold[1]:
        return 'Common'
    else:
        assert 'bad # of publications'


def get_bold_headers(results_df):
    bold_list = []
    for col in list(results_df):
        bold_list.append('<b>' + col)
    return bold_list


def get_type_5_result_str(drugs, dict_drug):
    no_results_str = ''
    if (len(drugs) == 2) and (dict_drug[drugs[0]] == 'Type 5' or dict_drug[drugs[1]] == 'Type 5'):
        no_results_str = f'<b>{drugs[0]} is a {dict_drug[drugs[0]]} drug</b><br>' \
                         f'<b>{drugs[1]} is a {dict_drug[drugs[1]]} drug</b><br>' \
                         f'<b><span style="color:#AF1F22">Type 5 drugs _cannot_ form stable NPs</b><br>'
    elif len(drugs) == 1 and dict_drug[drugs[0]] == 'Type 5':
        no_results_str = f'<b>{drugs[0]} is a {dict_drug[drugs[0]]} drug</b><br>' \
                         f'<b><span style="color:#AF1F22">Type 5 drugs _cannot_ form stable NPs</b><br>'
    return no_results_str


def get_empty_df_result_str(drugs, dict_drug, no_results_str):
    if no_results_str:
        no_results_str += f'<br><b>No additional information was found</b><br>'
    else:
        valid = False
        for drug in drugs:
            no_results_str += f"<b>{drug} is a {dict_drug[drug]} drug</b><br>"
            if len(drugs) == 2 and dict_drug[drug] == 'Type 1':
                valid = True
        if len(drugs) == 2 and valid:
            no_results_str += f'<b><span style="color:#2B78FF">{drugs[0]} and {drugs[1]} _can_ be combined to form stable NPs</b><br>'
            no_results_str += f'<br><b>No additional information was found</b><br>'
        elif len(drugs) == 2 and not valid:
            no_results_str += f'<b><span style="color:#AF1F22">{drugs[0]} and {drugs[1]} _cannot_ be combined to form stable NPs</b><br>'
            no_results_str += f'<br><b>No additional information was found</b><br>'
        else:
            no_results_str += f'<br><b><span style="color:#AF1F22">No results were found, please try to relax the constraints'

    return no_results_str


cols_to_show = ['Drug A', 'Drug B', 'Cancer Type', 'Drugs Type', 'Stable NP', 'Frequency in Literature', 'PubMed']


def get_pubmed_links(results_df):
    pubmed_links_list = []
    for index, row in results_df.iterrows():
        pubmed_links_list.append({"Link": f"https://pubmed.ncbi.nlm.nih.gov/?term=%28%28"
                                           f"{row['Drug A'].replace(' ','+')}%29+AND+%28"
                                           f"{row['Drug B'].split(' <br>')[0].replace(' ','+')}%29%29+AND+%28"
                                           f"{row['Cancer Type'].replace(' ','+')}%29&sort="})
    results_df['PubMed'] = pubmed_links_list
    results_df['PubMed'] = results_df['PubMed'].apply(
        lambda x: f'<a href="{list(x.values())[0]}">{list(x.keys())[0]}</a>')


def plot_result_df(results_df, results_filed, drugs, dict_drug):
    if results_df is None:
        results_filed.markdown('_The results will appear here..._')
        return

    get_pubmed_links(results_df)
    map_color = {"Yes": "#C6F2C9", "No": "#F2D9D5", "Unknown": "#F0F2F6"}
    results_df['Stable NP color'] = results_df['Stable NP'].map(map_color)
    fill_color = []
    n = len(results_df)
    for col in cols_to_show:
        if col != 'Stable NP':
            fill_color.append(['#F0F2F6'] * n)
        else:
            fill_color.append(results_df["Stable NP color"].to_list())

    no_results_str = get_type_5_result_str(drugs, dict_drug)

    if results_df.empty:
        no_results_str = get_empty_df_result_str(drugs, dict_drug, no_results_str)
    # D7DEEF
    if not results_df.empty:
        fig = go.Figure(data=go.Table(columnwidth = [110,110,130,125,90,120,75],
            header=dict(values=get_bold_headers(results_df[cols_to_show]),
                        fill_color='#B3BDD8',
                        font=dict(size=15),
                        align='center'),
            cells=dict(values=results_df[cols_to_show].transpose().values.tolist(),
                       fill_color=fill_color,
                       font=dict(size=14),
                       align=['left', 'left', 'left', 'left', 'center', 'center','left'])))
        # fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), width=120 * len(list(results_df[cols_to_show])), height=1000)
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))

        no_results_str += f'**{len(results_df)} results were found**'
        results_filed.markdown(f'{no_results_str}', unsafe_allow_html=True)
        results_filed.write(fig)

    else:
        results_filed.markdown(f'{no_results_str}', unsafe_allow_html=True)


def get_data_to_save(results_df):
    temp = pd.DataFrame()
    if results_df is None or results_df.empty:
        return temp.to_csv(index=False).encode('utf-8')
    else:
        return results_df[cols_to_show].to_csv(index=False).encode('utf-8')


## Search functions:
def init_result_dict():
    return {'Drug A': [], 'Drug B': [], 'Cancer Type': [], 'Drugs Type': [], 'Stable NP': [],
            'Frequency in Literature': []}


def get_stable_np_status(row):
    if row["all_drug_type"] == 'Type NA':
        return 'Unknown'
    elif row["all_drug_type"] == 'Type 5' or row["all_drug_type"] == 'Pred. Type 5' :
        return f'No'
    else:
        return f'Yes'


def add_to_result_dict(row, result_dict):
    if row["TypeI"] == row["All drugs"]:
        return result_dict
    if (row["TypeI"] in result_dict['Drug B']) and (row["All drugs"] in result_dict['Drug A']) and (row["Cancers"] in result_dict['Cancer Type']):
        return result_dict

    result_dict['Drug A'].append(f'{row["TypeI"]}')
    fs = ''
    if row["Fluorescence Status"] != 'NA':
        fs = f' <br><b>{row["Fluorescence Status"]}'
    result_dict['Drug B'].append(row["All drugs"] + fs)
    result_dict['Cancer Type'].append(row["Cancers"])
    result_dict['Drugs Type'].append(f'A:<b> Type 1</b> <br>B: <b>{row["all_drug_type"]}</b>')
    result_dict['Stable NP'].append(get_stable_np_status(row))
    result_dict['Frequency in Literature'].append(row["confidence_level"])
    return result_dict


def get_result_df(result_dict):
    result_df = pd.DataFrame.from_dict(result_dict)
    # st.write(result_df)
    # st.write(result_dict)
    result_df = result_df.sort_values(by=['Drug A', 'Drug B', 'Cancer Type'])
    return result_df


def search_by_cancer(cancer, df_cancer):
    result_dict = init_result_dict()
    for index, row in df_cancer.iterrows():
        if row['Cancers'] == cancer:
            result_dict = add_to_result_dict(row, result_dict)

    return get_result_df(result_dict)


def search_by_single_drug(drug, df_cancer):
    result_dict = init_result_dict()
    for index, row in df_cancer.iterrows():
        if row["TypeI"] == drug or row["All drugs"] == drug:
            if row["TypeI"] == row["All drugs"]:
                continue
            result_dict = add_to_result_dict(row, result_dict)
    return get_result_df(result_dict)


def search_by_two_drugs(drugs, df_cancer):
    result_dict = init_result_dict()
    for index, row in df_cancer.iterrows():
        if (row["TypeI"] == drugs[0] and row["All drugs"] == drugs[1]) or (
                row["TypeI"] == drugs[1] and row["All drugs"] == drugs[0]):
            result_dict = add_to_result_dict(row, result_dict)
    return get_result_df(result_dict)


def search_by_single_drug_and_cancer(drug, cancer, df_cancer):
    result_dict = init_result_dict()
    for index, row in df_cancer.iterrows():
        if (row["TypeI"] == drug or row["All drugs"] == drug) and (row['Cancers'] == cancer):
            result_dict = add_to_result_dict(row, result_dict)
    return get_result_df(result_dict)


def search_by_two_drugs_and_cancer(drugs, cancer, df_cancer):
    result_dict = init_result_dict()
    for index, row in df_cancer.iterrows():
        if (row["TypeI"] == drugs[0] and row["All drugs"] == drugs[1]) or (
                row["TypeI"] == drugs[1] and row["All drugs"] == drugs[0]):
            if row['Cancers'] == cancer:
                result_dict = add_to_result_dict(row, result_dict)
    return get_result_df(result_dict)


# # Offline Functions
# def add_fluorescence_status_to_df(df, aie_list, acq_list, non_active_list):
#     aie_list = [x.lower() for x in aie_list]
#     acq_list = [x.lower() for x in acq_list]
#     non_active_list = [x.lower() for x in non_active_list]
#
#     f_s_list = []
#     for i, row in df.iterrows():
#         if row['All drugs'].lower() in aie_list:
#             f_s_list.append('AIE')
#         elif row['All drugs'].lower() in acq_list:
#             f_s_list.append('Fluorescent')
#         elif row['All drugs'].lower() in non_active_list:
#             f_s_list.append('Non-Active')
#         else:
#             f_s_list.append('NA')
#     df['Fluorescence Status'] = f_s_list
#     # df.to_csv(
#     # 'C:\\Users\\benf\\OneDrive - NVIDIA Corporation\\Desktop\\Uni_stuff\\Technion\\Yosi_lab\\08-apps\\082-formulation_assistant\\fs.csv')
#     return df
#
#
# def clean_merged_df(merge_df, verbose=False, save_path=None):
#     merge_df.replace(get_cancer_abbreviations_dict(), inplace=True)
#     merge_df['Cancers'] = merge_df['Cancers'].str.lower()
#     merge_df['TypeI'] = merge_df['TypeI'].str.lower()
#     merge_df['All drugs'] = merge_df['All drugs'].str.lower()
#
#     merge_df = merge_df.sort_values(by=['# of publications'], ascending=False, ignore_index=True)
#
#     if verbose:
#         print(f'{merge_df.nunique()=}, {merge_df["# of publications"].sum()=}')
#
#     merge_df_no_dup = merge_df.drop_duplicates()
#     if verbose:
#         print(f'{merge_df_no_dup.nunique()=}, {merge_df_no_dup["# of publications"].sum()=}')
#
#     if save_path:
#         merge_df_no_dup.to_csv(save_path)
#     return merge_df_no_dup
#
#
# for DrugBank
# def get_predicted_type(mol):
#
#     if mol['experimental_logP'] and mol['experimental_logP'] < 2.5:
#         if mol['aromatic_rings'] > 1:
#             return 'Type 4'
#         else:
#             return 'Type 5'
#     else:
#         if mol['NHISS'] >= 4 and (mol['pKa_strongest_acidic'] > 7 and mol['pKa_strongest_basic'] > 7):
#             if mol['Fluorescence Status'] == 'AIE':
#                 return 'Type 1'
#             else:
#                 return 'Type 2'
#         else:
#             return 'Type 3'

