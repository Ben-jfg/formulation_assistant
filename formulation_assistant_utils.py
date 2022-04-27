import pandas as pd
import streamlit as st
import plotly.graph_objects as go


@st.cache
def get_cancer_abbreviations_dict():
    return {'GIST': 'Gastrointestinal Stromal Tumor',
            'HNSCC': 'Head And Neck Cancer',
            'HCC': 'Hepatocellular Carcinoma',
            'NSCLC': 'Non-Small Cell Lung Cancer',
            'SCLC': 'Small Cell Lung Cancer',
            'OVARIAN CANCER': 'Ovarian Cancer'}


@st.cache
def get_data():
    xls = pd.ExcelFile("Drug Classification and synergy2.0.xlsx")
    df_drug = pd.read_excel(xls, 'Types(chemistry)')
    df_cancer = pd.read_excel(xls, 'Synergy(biology)')
    df_cancer.replace(get_cancer_abbreviations_dict() ,inplace=True)
    dict_drug = {}
    for cur_col in list(df_drug):
        for cur_drug in list(df_drug[cur_col].dropna()):
            if cur_drug.isupper():
                dict_drug[cur_drug] = cur_col
            else:
                dict_drug[cur_drug.title()] = cur_col

    pd.options.mode.chained_assignment = None
    all_drug_type = []
    confidence_list = []
    for index, row in df_cancer.iterrows():
        if not row['Cancers'].isupper():
            df_cancer['Cancers'][index] = row['Cancers'].title()
        if not row['TypeI'].isupper():
            df_cancer['TypeI'][index] = row['TypeI'].title()
        if not row['All drugs'].isupper():
            df_cancer['All drugs'][index] = row['All drugs'].title()

        if row['All drugs'] in list(dict_drug.keys()):
            all_drug_type.append(dict_drug[row['All drugs']])
        else:
            all_drug_type.append('Type NA')

        confidence_list.append(set_confidence(row))

    df_cancer['all_drug_type'] = all_drug_type
    df_cancer['confidence_level'] = confidence_list
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


def plot_result_df(results_df, results_filed, drugs, dict_drug):
    if results_df is None:
        results_filed.markdown('_The results will appear here..._')
        return

    if not results_df.empty:
        fig = go.Figure(data=go.Table(
            header=dict(values=get_bold_headers(results_df),
                        fill_color='#A5C2FF',
                        align='center'),
            cells=dict(values=results_df.transpose().values.tolist(),
                       fill_color='#F0F2F6',
                       align='left')))
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), width=135*len(list(results_df)), height=1000)
        results_filed.write(fig)

    elif results_df.empty:
        no_results_str = ''
        valid = 0
        for drug in drugs:
            no_results_str += f"<b>{drug} is a {dict_drug[drug]} drug</b><br>"
            if len(drugs) == 2 and dict_drug[drug] == 'Type 1':
                valid = 1
        if len(drugs) == 2 and valid:
            no_results_str += f'<b><span style="color:#2B78FF">{drugs[0]} and {drugs[1]} _can_ be combined to create stable NPs</b><br>'
            no_results_str += f'<br><b>No additional information was found</b><br>'
        elif len(drugs) == 2 and not valid:
            no_results_str += f'<b><span style="color:#AF1F22">{drugs[0]} and {drugs[1]} _cannot_ be combined to create stable NPs</b><br>'
            no_results_str += f'<br><b>No additional information was found</b><br>'
        else:
            no_results_str += f'<br><b><span style="color:#AF1F22">No results were found, please try to relax the constraints'

        results_filed.markdown(f'{no_results_str}', unsafe_allow_html=True)


def get_data_to_save(results_df):
    temp = pd.DataFrame()
    if results_df is None or results_df.empty:
        return temp.to_csv(index=False).encode('utf-8')
    else:
        return results_df.to_csv(index=False).encode('utf-8')


## Search functions:
def init_result_dict():
    return {'Drug I (type 1)': [], 'Drug II': [], 'Drug II type': [], 'Cancer Type': [], 'Frequency in Literature': []}


def add_to_result_dict(row, result_dict):
    result_dict['Drug I (type 1)'].append(row["TypeI"])
    result_dict['Drug II'].append(row["All drugs"])
    result_dict['Drug II type'].append(row["all_drug_type"])
    result_dict['Cancer Type'].append(row["Cancers"])
    result_dict['Frequency in Literature'].append(row["confidence_level"])
    return result_dict


def get_result_df(result_dict):
    result_df = pd.DataFrame.from_dict(result_dict)
    # st.write(result_df)
    # st.write(result_dict)
    result_df = result_df.sort_values(by=['Drug I (type 1)', 'Drug II', 'Cancer Type'])
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
        if (row["TypeI"] == drugs[0] and row["All drugs"] == drugs[1]) or (row["TypeI"] == drugs[1] and row["All drugs"] == drugs[0]):
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
        if (row["TypeI"] == drugs[0] and row["All drugs"] == drugs[1]) or (row["TypeI"] == drugs[1] and row["All drugs"] == drugs[0]):
            if row['Cancers'] == cancer:
                result_dict = add_to_result_dict(row, result_dict)
    return get_result_df(result_dict)
