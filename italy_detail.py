
import streamlit as st
import pandas as pd
import os

import matplotlib
import matplotlib.pyplot as plt

import plotly.express as px

plt.style.use('ggplot')

from words import words



# translate the names of commodity groups

def translate(name):
    if name in words:
        return words[name]
    return name

# convert variation

def growth(num):
    # if (num>100):
    #     pref = '+'
    # else:
    #     pref=''
    return round(num-100,1)

# function to process the excel file into a dataframe
def process(data):
    
    """
        Returns all of the data in a dataframe.
    """
    
    # drop NA values and replace * and - with zeros
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
    
    # debug: uncomment the following line to inspect the df
    #st.write(data)
    return data


def italy_detail():
    
    # the excel file, initially set to none
    #data_file = None
    
        
    # the dataframe initially set to None
    # df_data = None
        
    

    
    # add controls
    data_file = st.sidebar.file_uploader(
        "Inserire il documento Excel",
        type=['xls'],
        help="Soltanto il documento dell'Ente statistico serbo")
    


    
    if (data_file==None):
        st.markdown("""
            ### Dettaglio del commercio Italia Serbia
            
            E' necessario selezionare l'apposito documento in formato excel per avviare il processo.
                    """)
    else:
        with open(os.path.join("tempDir","italiaDettaglio.xls"),"wb") as f: 
            f.write(data_file.getbuffer())         
            st.success("Saved File")
            
    flux = st.sidebar.selectbox("Selezionare il tipo di flusso",('Esportazioni','Importazioni','Interscambio'),
                                help="esportazioni si riferisce ad esportazioni SERBE in Italia e viceversa")
    
    top_n = st.sidebar.selectbox("Selezionare il numero di voci principali",(10,5,20,15))
    
    
    # flux dependant variations
    if flux=='Esportazioni':
        flux_var = 'Var. Export'
    elif flux=='Importazioni':
        flux_var = 'Var. Import'
    elif flux == 'Interscambio':
        flux_var = None
        
        
    
    # initialize the variables - probably unnecessary
    
    
    # process excel file
    if os.path.join("tempDir","italiaDettaglio.xls"):
        filePath=os.path.join("tempDir","italiaDettaglio.xls")

        try:
            # get the header
            header = pd.read_excel(filePath, index_col=None, usecols = "A", header = 1, nrows=0)
            
            full_header= header.columns.values[0]
            period = full_header.split('PERIOD')[1].split('-Zemlja')[0]
            st.subheader("Periodo di riferimento:"+period)
            st.write("Valori in migliaia di EURO")
        except ValueError:
            st.subheader("Documento Excel non valido!")
            
        # read the actual data
        data=pd.read_excel(filePath, 
            # sheet_name='Tabela - 2021-04-28T082613.292', 
            skiprows=2,
            usecols="B:F")
        
        df_data = process(data)
        
        totals = df_data.loc[df_data['Voce'] == 'TOTALE']
        w_totals = totals.set_index('Voce', inplace=False)
        st.dataframe(w_totals)
        
        # expander to show the entire dataframe
        with st.beta_expander("Dati completi"):
            st.subheader("Dati di commercio completi")
            df_data_reindex = df_data.set_index('Voce', inplace=False)
            st.dataframe(df_data_reindex)
            
        
        if st.button('Export excel'):
            st.write('Excell scritto')
            df_data.to_excel("Komplet.xlsx")
  
            
   
        # filter the data according to the control
        
        if flux_var:
            filtered = df_data[['Voce',flux,flux_var]].sort_values(by=flux, ascending=False).head(top_n+1)
        else:
            # if flux_var is None it means it should not be included
            filtered = df_data[['Voce',flux]].sort_values(by=flux, ascending=False).head(top_n+1)
        
        # grab the total
        total_flux = filtered.loc[0]
        
        with st.beta_expander(flux):
            st.subheader(flux+" per il periodo")
            w_filtered = filtered.set_index('Voce', inplace=False)
            st.dataframe(w_filtered, height=500)
        
        # horizontal bar chart - all the top data WITHOUT the total because it doesn't make sense
        top_no_total = filtered[filtered['Voce']!='TOTALE']
        
        # debug
        # st.write(top_no_total)
        

        
        # fix titles
        if flux=='Esportazioni':
            chart_title = 'Esportazioni serbe in Italia nel periodo '+period
        elif flux=='Importazioni':
            chart_title = "Importazioni serbe dall'Italia nel periodo "+period
        else:
            chart_title = 'Interscambio serbo con Italia nel periodo '+period
        
        

        
        # horizontal chart
        st.dataframe(top_no_total)
        hor_fig = px.bar(top_no_total.iloc[::-1], x=flux, y="Voce", orientation='h', color=flux_var,
                         color_continuous_scale=px.colors.sequential.matter)
        
        st.plotly_chart(hor_fig)
        
        # pie chart data of the top N commodity groups
        rest_sum = float(total_flux[flux])-filtered[1:][flux].sum()
        
        
   
        rest_row = {'Voce':'Le voci rimanenti',flux:float(rest_sum)}
  
        top_no_total = filtered[filtered['Voce']!='TOTALE']    

        pie_df = top_no_total.append(rest_row, ignore_index=True)[['Voce',flux]]
        
        
        
        # the ACTUAL chart
        # pie_fig, ax = plt.subplots()
        # ax.set_title("Le principali voci: "+flux)
       
        # ax.pie(pie_df[flux],labels=pie_df['Voce'],autopct='%1.2f%%')
        # with st.beta_expander("Pie chart - %"):

        #     st.pyplot(pie_fig)
    
            
        # plotly pie chart
        with st.beta_expander("Quote delle principali voci - %"):
            plotlyPie = px.pie(
                pie_df,
                values=flux,
                names='Voce',
                color_discrete_sequence=px.colors.sequential.matter,
                hover_name="Voce"
                )
            plotlyPie.update_layout(dict(
                title="{} della Serbia, periodo {}".format(flux, period)
            ))
            
            st.subheader("Quote delle principali voci")
            st.plotly_chart(plotlyPie)
        
        
