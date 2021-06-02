import streamlit as st 
st.set_page_config(layout="wide")

#import mini apps
from italy_detail import italy_detail

from world_trade import world_trade

def main():

    st.image('logo.png', width=160)

    st.title('Interscambio commerciale della Serbia')
    st.subheader('by freethrow')
  
    
    # main app navigation
    navigation = ["Serbia-Italia", "Serbia-Mondo","Economia"]
    
    choice = st.sidebar.selectbox("Menu", navigation)
    
    # navigate
    if choice == "Serbia-Italia":
        #st.subheader("Serbia - Italia") - debug
        italy_detail()
    elif choice == "Serbia-Mondo":
        #st.subheader("Serbia-Mondo")
        world_trade()
    elif choice == "Economia":
      st.subheader("Economia")
      

if __name__ == '__main__':
    main()
