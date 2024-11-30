import streamlit as st
from operations.front import front_page

def configurar_pagina():
    st.set_page_config(
        page_title="Calculadora de Guindaste",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'Get Help': 'https://www.streamlit.io/community',
            'Report a bug': "***********",
            'About': """
            ## Calculadora de Carga para Guindauto
            
            Esta aplicação calcula e valida cargas para operações de içamento de carga com guindaste e guindauto, 
            o plano rigging não deve ser descartado.
            
            * Calcula margens de segurança
            * Valida capacidades do guindaste
            * Considera pesos de acessórios e cabos
            
            Versão 1.0.0
            """
        }
    )

def main():
    configurar_pagina()
    front_page()

if __name__ == "__main__":
    main()
    st.caption ('Copyright 2024, Cristian Ferreira Carlos, Todos os direitos reservados.' )
    st.caption ('https://www.linkedin.com/in/cristian-ferreira-carlos-256b19161/')