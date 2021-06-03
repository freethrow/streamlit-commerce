import streamlit as st
import pandas as pd

import os

import matplotlib
import matplotlib.pyplot as plt

import plotly.express as px

from countries import countries

plt.style.use('ggplot')


# translate the names of countries
def translate_country(name):
    if name in countries:
        return countries[name]
    return name


# convert variation
def growth(num):
    
    return round(num-100,1)


# function to process the excel file into a dataframe
def process(data):
    
    """
        Returns all of the data in a dataframe.
    """
    
    # drop NA values and replace * and - with zeros
    # not necessary for this file
    
    data.dropna(inplace=True)
    data.replace('*',0, inplace=True)
    data.replace('-',0, inplace=True)
    data['Paese'] = data['Naziv'].str.strip()
    data['Paese'] = data['Paese'].apply(lambda x:translate_country(x))

    data['Var. Export'] = pd.to_numeric(data['Indeks - izvoz'])
    data['Var. Import'] = pd.to_numeric(data['Indeks - uvoz'])
    
    data['Var. Export'] = data['Var. Export'].apply(lambda x:growth(x))
    data['Var. Import'] = data['Var. Import'].apply(lambda x:growth(x))

    data['Esportazioni'] = pd.to_numeric(data['Izvoz'], downcast='integer')
    data['Importazioni'] = pd.to_numeric(data['Uvoz'], downcast='integer')
    data['Interscambio'] = data['Esportazioni']+data['Importazioni']
    data['Surplus'] = data['Esportazioni']-data['Importazioni']   

    data = data[['Paese','Esportazioni','Importazioni','Var. Export','Var. Import','Interscambio','Surplus']]
    
    # debug: uncomment the following line to inspect the df

    return data




def world_trade():
  
   
    # the excel file, initially set to none
    # w_data_file = None
            
    # the dataframe initially set to None
    # w_df_data = None
        
    

    # add controls
    w_data_file = st.sidebar.file_uploader(
        "Inserire il documento Excel",
        type=['xls'],
        help="Soltanto il documento dell'Ente statistico serbo")
    
    if (w_data_file==None):
        st.markdown("""
            ### Dettaglio del commercio Italia Mondo
            
            E' necessario selezionare l'apposito documento in formato excel per avviare il processo.
                    """)
    else:
        with open(os.path.join("tempDir","italiaMondo.xls"),"wb") as f: 
            f.write(w_data_file.getbuffer())         
            st.success("Saved File")
            
    
    w_flux = st.sidebar.selectbox("Selezionare il tipo di flusso",
                                  ('Esportazioni','Importazioni','Interscambio'),
                                  help="esportazioni si riferisce ad esportazioni SERBE e viceversa")
    
    w_top_n = st.sidebar.selectbox("Selezionare il numero di Paesi partner principali",(10,15,20))
    

    # flux dependant variations
    if w_flux=='Esportazioni':
        flux_var = 'Var. Export'
    elif w_flux=='Importazioni':
        flux_var = 'Var. Import'
    elif w_flux == 'Interscambio':
        flux_var = None
        
    
    # initialize the variables - probably unnecessary
    
    
    # process excel file
    if w_data_file:
        
        try:
            # get the header
            header = pd.read_excel(w_data_file, index_col=None, usecols = "A", header = 1, nrows=0)
            
            full_header= header.columns.values[0]
            print(full_header)
            period = full_header.split('PERIOD')[1].split('-20')[0]
            st.subheader("Periodo di riferimento:"+period)
            st.write("Valori in migliaia di EURO")
        except ValueError:
            st.subheader("Documento Excel non valido!")
            
        # read the actual data
        
        # exports first
        try:
            w_data_exp=pd.read_excel(w_data_file, 
                sheet_name='izvoz', 
                skiprows=2,
                usecols="A:F").dropna()
            
            #then import
            w_data_imp=pd.read_excel(w_data_file, 
                sheet_name='uvoz', 
                skiprows=2,
                usecols="A:F").dropna()
        except ValueError:
            st.subheader("Inserire il documento excel corretto")
        # concatenate
        w_data = pd.concat([w_data_exp,w_data_imp], ignore_index=True).drop_duplicates(ignore_index=True)
        # debug
        
        # translate the data and apply simple transformations            
        w_df_data = process(w_data)
        
        totals = w_df_data.loc[w_df_data['Paese'] == 'TOTALE']
        w_totals = totals.set_index('Paese', inplace=False)
        st.dataframe(w_totals)
        
        # expander to show the entire dataframe
        with st.beta_expander("Dati di interscambio completi"):
            df_reindexed = w_df_data.set_index('Paese',inplace=False)          
            st.dataframe(df_reindexed)
            
        if st.button('Export excel'):
            st.write('Excel scritto!')
            w_df_data.to_excel("Serbia-Mondo.xlsx")
            
        # chart for selected flux
        
        # create the dataframe
        # filter the data according to the control
        
        if flux_var:
            filtered = w_df_data[['Paese',w_flux,flux_var]].sort_values(by=w_flux, ascending=False).head(w_top_n+1)
        else:
            # if flux_var is None it means it should not be included
            filtered = w_df_data[['Paese',w_flux]].sort_values(by=w_flux, ascending=False).head(w_top_n+1)
        
        # grab the total
        total_flux = filtered.loc[0]
        
        with st.beta_expander(w_flux):
            st.subheader(w_flux+" per il periodo")
            w_filtered = filtered.set_index('Paese', inplace=False)
            st.dataframe(w_filtered, height=500)
            
        # horizontal bar chart - all the top data WITHOUT the total because it doesn't make sense
        top_no_total = filtered[filtered['Paese']!='TOTALE']
        
        # debug
        # st.write(top_no_total)
        
       
        
        # for the pie chart we need the remainder
        
        rest_sum = float(total_flux[w_flux])-filtered[1:][w_flux].sum()     
   
        rest_row = {'Paese':'Paesi rimanenti',w_flux:float(rest_sum)}
  
        top_no_total = filtered[filtered['Paese']!='TOTALE']    

        pie_df = top_no_total.append(rest_row, ignore_index=True)[['Paese',w_flux]]
        
            
            
        # plotly chart
       
        plotlyChart = px.bar(
            top_no_total.iloc[::-1],
            y='Paese',
            x=w_flux,
            color=flux_var,
            color_continuous_scale=px.colors.sequential.matter)
        
        
        with st.beta_expander("Grafico dei top "+str(w_top_n)):
            st.plotly_chart(plotlyChart)
        
        # plotly pie chart
        plotlyPie = px.pie(
            pie_df,
            values=w_flux,
            names='Paese',
            color_discrete_sequence=px.colors.sequential.Sunsetdark,
            hover_name="Paese"
        )
        
        st.subheader("Quote")
        st.plotly_chart(plotlyPie)
        

