
import streamlit as st

import pandas as pd

import plotly.express as px

from words import words

import matplotlib
import matplotlib.pyplot as plt

import plotly.graph_objects as go

import seaborn as sns 
sns.set_style("darkgrid")

matplotlib.use("Agg")

st.set_page_config(layout="wide")

# translation function
def translate(name):
    if name in words:
        return words[name]
    return name

# convert variation
def growth(num):
    if (num>100):
        pref = '+'
    else:
        pref=''
    return pref+str(round(num-100,1))+'%'

print(growth(134.36))

st.header("Serbia - Italia Commercio")

data_file = st.file_uploader("Upload Excel file",type=['xls'])


filtered = None

flux_var = 'Var. Export'


flux = st.sidebar.selectbox("Selezionare il flusso",('Esportazioni','Importazioni','Interscambio'))
if flux=='Esportazioni':
    flux_var = 'Var. Export'
elif flux=='Importazioni':
    flux_var = 'Var. Import'
elif flux == 'Interscambio':
    flux_var ='Var. Interscambio'

top_n = st.sidebar.selectbox("Selezionare il numero di voci principali",(20,10,5))


if data_file:

    try:
        # get the header
        header = pd.read_excel(data_file, index_col=None, usecols = "A", header = 1, nrows=0)
        
        full_header= header.columns.values[0]
        part = full_header.split('PERIOD')[1].split('-Zemlja')[0]
        st.header("Periodo di riferimento:"+part)
    except ValueError:
        st.subheader("Documento Excel non valido!")
        
        
    data=pd.read_excel(data_file, 
        # sheet_name='Tabela - 2021-04-28T082613.292', 
        skiprows=2,
        usecols="B:F")

        
    # process data file
    
    

    data.dropna(inplace=True)
    data.replace('*',0, inplace=True)
    data.replace('-',0, inplace=True)
    data['Voce'] = data['Naziv'].str.strip()

    data['Voce'] = data['Voce'].apply(lambda x:translate(x))

  

    data['Var. Export'] = pd.to_numeric(data['Indeks - izvoz'])
    data['Var. Import'] = pd.to_numeric(data['Indeks - uvoz'])
    
    data['Var. Export'] = data['Var. Export'].apply(lambda x:growth(x))
    data['Var. Import'] = data['Var. Import'].apply(lambda x:growth(x))

    data['Esportazioni'] = pd.to_numeric(data['Izvoz'], downcast='integer')
    data['Importazioni'] = pd.to_numeric(data['Uvoz'], downcast='integer')
    data['Interscambio'] = data['Esportazioni']+data['Importazioni']
    data['Surplus'] = data['Esportazioni']-data['Importazioni']
    

    data = data[['Voce','Esportazioni','Importazioni','Var. Export','Var. Import','Interscambio','Surplus']]
    totals = data.loc[data['Voce'] == 'TOTALE']
    st.subheader("Valori complessivi in migliaia di EURO")
    st.write("Tutte le voci")
    st.write(totals)

    filtered = data[['Voce',flux,flux_var]].sort_values(by=flux, ascending=False).head(top_n+1)

    # grab the total
    total_flux = filtered.loc[0]

    st.subheader("Valori totali per il periodo")
    st.write(filtered)
    

    # remove from the rest of top N
    rest_sum = filtered[1:][flux].sum()
    rest_row = {'Voce':'Le voci rimanenti',flux:float(rest_sum)}
  
    top_no_total = filtered[filtered['Voce']!='TOTALE']    

    pie_df = top_no_total.append(rest_row, ignore_index=True) 

    plt_fig, ax = plt.subplots()
    top_no_total = top_no_total.iloc[::-1]
    ax.barh(top_no_total['Voce'],top_no_total[flux])



    # plot the value
    # fig = px.bar(filtered[1:],
    #                 x='Naziv',
    #                 y=flux,
    #                 hover_name=flux,
                    
    #                 title=f'Values in EUR {flux}')

    # st.plotly_chart(fig)

    st.pyplot(plt_fig)



        
    pie_chart = px.pie(pie_df,
        title="Pie Chart",
        values=flux,
        names="Voce")
    
    with st.beta_expander("Pie Chart"):
        st.subheader("Struttura delle "+flux+" serbe")

        st.plotly_chart(pie_chart)
    
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    
    
    
    table = go.Figure(data=[go.Table(
    header=dict(values=list(filtered.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[filtered.Voce, filtered[flux],filtered[flux_var]],
               fill_color='lavender',
               align=['center','right']))
                            
                                  
                            
])
    
    st.dataframe(filtered)