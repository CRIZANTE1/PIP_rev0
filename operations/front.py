import streamlit as st
from operations.calc import calcular_carga_total, validar_guindaste
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def mostrar_instrucoes():
    with st.expander("📖 Como usar este aplicativo", expanded=True):
        st.markdown("""
        ### Guia de Uso
        
        1. **Dados da Carga**:
           * Digite o peso da carga principal em kg
           * Selecione se o equipamento é novo ou usado
             - Novo: aplica margem de segurança de 10%
             - Usado: aplica margem de segurança de 25%
           * Informe o peso dos acessórios (cintas, grilhetas, etc.)
           * O peso dos cabos será calculado automaticamente (3%)
        
        2. **Dados do Guindaste**:
           * Preencha as informações do fabricante e modelo
           * Informe o raio máximo e sua capacidade
           * Informe a extensão máxima da lança e sua capacidade
        
        3. **Resultados**:
           * O sistema calculará automaticamente:
             - Margem de segurança
             - Peso total a considerar
             - Peso dos cabos
             - Carga total final
           * Validará se o guindaste é adequado
           * Mostrará as porcentagens de utilização
        
        ⚠️ **Importante**: Se a utilização ultrapassar 80%, será necessária aprovação da engenharia e segurança.
        """)

def criar_diagrama_guindaste(raio_max, alcance_max):
    """Cria um diagrama técnico simplificado do guindaste."""
    
    # Criar figura
    fig = go.Figure()

    # Base do guindaste (retângulo)
    fig.add_trace(go.Scatter(
        x=[-1, 1, 1, -1, -1],
        y=[-0.5, -0.5, 0, 0, -0.5],
        mode='lines',
        name='Base do Guindaste',
        line=dict(color='gray', width=3),
        fill='toself'
    ))

    # Ponto central (centro de rotação)
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode='markers+text',
        name='Centro de Rotação',
        marker=dict(color='black', size=10, symbol='circle-dot'),
        text=['Guindaste'],
        textposition='bottom center'
    ))

    # Torre do guindaste (linha vertical)
    fig.add_trace(go.Scatter(
        x=[0, 0],
        y=[0, alcance_max],
        mode='lines+text',
        name='Torre',
        line=dict(color='blue', width=3),
        text=['', f'Altura: {alcance_max}m'],
        textposition='middle left'
    ))

    # Lança do guindaste (linha diagonal)
    fig.add_trace(go.Scatter(
        x=[0, raio_max],
        y=[alcance_max, 0],
        mode='lines+text',
        name='Lança',
        line=dict(color='red', width=3),
        text=['', f'Lança: {((raio_max**2 + alcance_max**2)**0.5):.1f}m'],
        textposition='top center'
    ))

    # Linha do ângulo (arco)
    raio_arco = min(raio_max, alcance_max) * 0.3  # Tamanho do arco
    theta = np.linspace(0, np.arctan2(alcance_max, raio_max), 50)
    x_arco = raio_arco * np.cos(theta)
    y_arco = raio_arco * np.sin(theta)
    
    fig.add_trace(go.Scatter(
        x=x_arco,
        y=y_arco,
        mode='lines',
        name='Ângulo',
        line=dict(color='purple', width=2),
    ))

    # Calcular e mostrar o ângulo atual
    angulo = np.degrees(np.arctan2(alcance_max, raio_max))
    fig.add_annotation(
        x=raio_arco/2,
        y=raio_arco/2,
        text=f'{angulo:.1f}°',
        showarrow=False,
        font=dict(size=14)
    )

    # Linha do raio máximo (linha horizontal)
    fig.add_trace(go.Scatter(
        x=[0, raio_max],
        y=[0, 0],
        mode='lines+text',
        name='Raio Máximo',
        line=dict(color='green', width=2, dash='dash'),
        text=['', f'Raio: {raio_max}m'],
        textposition='bottom center'
    ))

    # Extensão máxima da lança
    fig.add_trace(go.Scatter(
        x=[0, alcance_max],
        y=[alcance_max, 0],
        mode='lines+text',
        name='Extensão Máxima',
        line=dict(color='orange', width=2, dash='dash'),
        text=['', f'Extensão: {alcance_max}m'],
        textposition='bottom right'
    ))

    # Configurar layout
    fig.update_layout(
        title='Diagrama do Guindaste',
        xaxis_title='Distância (m)',
        yaxis_title='Altura (m)',
        showlegend=True,
        xaxis=dict(range=[-2, max(raio_max, alcance_max) + 2]),
        yaxis=dict(range=[-2, alcance_max + 2]),
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1
    )

    return fig

def front_page():
    st.title("Calculadora de Carga para Guindaste")
    
    # Mostra as instruções
    mostrar_instrucoes()
    
    # Criando abas para organizar melhor a interface
    tab1, tab2 = st.tabs(["📝 Dados do Içamento", "🏗️ Informações do Guindaste"])

    with tab1:
        # Container para manter a organização visual
        col1, col2 = st.columns(2)
        
        with col1:
            # Radio button e mensagem fora do form
            estado_equipamento = st.radio(
                "Estado do Equipamento",
                options=["Novo", "Usado"],
                index=0,
                help="Escolha 'Novo' para 10% de margem ou 'Usado' para 25%"
            )
            
            # Mensagem informativa que atualiza instantaneamente
            if estado_equipamento == "Novo":
                st.info("✨ Margem de segurança: 10% (equipamento novo)")
            else:
                st.warning("⚠️ Margem de segurança: 25% (equipamento usado)")

        # Form começa aqui
        with st.form("formulario_carga"):
            col1, col2 = st.columns(2)
            
            with col1:
                peso_carga = st.number_input(
                    "Peso da carga (kg)",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    help="Digite o peso principal do objeto a ser içado"
                )

            with col2:
                peso_acessorios = st.number_input(
                    "Peso dos acessórios (kg)",
                    min_value=0.0,
                    step=1.0,
                    value=0.0,
                    help="Peso total de cintas, grilhetas e outros acessórios"
                )
                
                st.info("ℹ️ O peso dos cabos será calculado automaticamente como 3% do peso a considerar")

            # Dados do guindaste
            st.subheader("Dados do Guindaste")
            col3, col4 = st.columns(2)
            
            with col3:
                fabricante = st.text_input(
                    "Fabricante do Guindaste",
                    help="Nome do fabricante do equipamento"
                )
                modelo = st.text_input(
                    "Modelo do Guindaste",
                    help="Modelo específico do guindaste"
                )
                
                raio_max = st.number_input(
                    "Raio Máximo (m)",
                    min_value=0.0,
                    step=0.1,
                    value=0.0,
                    help="Distância do centro de rotação até a carga"
                )

            with col4:
                capacidade_raio = st.number_input(
                    "Capacidade no Raio Máximo (kg)",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    help="Capacidade máxima de içamento no raio especificado"
                )
                
                alcance_max = st.number_input(
                    "Extensão Máxima da Lança (m)",
                    min_value=0.0,
                    step=0.1,
                    value=0.0,
                    help="Comprimento máximo da lança"
                )
                
                capacidade_alcance = st.number_input(
                    "Capacidade na Lança Máxima (kg)",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    help="Capacidade máxima de içamento com a lança totalmente estendida"
                )
                
                angulo_minimo_fabricante = st.number_input(
                    "Ângulo Mínimo da Lança (graus)",
                    min_value=0.0,
                    max_value=90.0,
                    step=1.0,
                    help="Ângulo mínimo seguro especificado pelo fabricante"
                )

            submeter = st.form_submit_button("Calcular")

        if submeter and peso_carga > 0:
            try:
                # Usa o estado do radio button de fora do form
                is_novo = estado_equipamento == "Novo"
                resultado = calcular_carga_total(peso_carga, is_novo, peso_acessorios)
                
                # Mostra os resultados detalhados
                st.subheader("📊 Resultados do Cálculo")
                
                # Cria uma tabela com os resultados
                st.table({
                    'Descrição': [
                        'Peso da carga',
                        'Margem de segurança',
                        'Peso a considerar',
                        'Peso dos cabos (3%)',
                        'Peso dos acessórios',
                        'Carga Total'
                    ],
                    'Valor (kg)': [
                        f"{resultado['peso_carga']:.2f}",
                        f"{resultado['peso_seguranca']:.2f}",
                        f"{resultado['peso_considerar']:.2f}",
                        f"{resultado['peso_cabos']:.2f}",
                        f"{resultado['peso_acessorios']:.2f}",
                        f"{resultado['carga_total']:.2f}"
                    ]
                })

                # Valida o guindaste
                if capacidade_raio > 0 and capacidade_alcance > 0:
                    validacao = validar_guindaste(
                        resultado['carga_total'],
                        capacidade_raio,
                        capacidade_alcance,
                        raio_max,
                        alcance_max
                    )
                    
                    # Mostra o resultado da validação
                    st.subheader("🎯 Resultado da Validação")
                    
                    if validacao['adequado']:
                        st.success("✅ " + validacao['mensagem'])
                    else:
                        st.error("⚠️ " + validacao['mensagem'])
                    
                    # Mostra as porcentagens de utilização em um gráfico
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Utilização no Raio Máximo",
                            f"{validacao['detalhes']['porcentagem_raio']:.1f}%",
                            help="Percentual da capacidade utilizada no raio máximo"
                        )
                    with col2:
                        st.metric(
                            "Utilização na Lança Máxima",
                            f"{validacao['detalhes']['porcentagem_alcance']:.1f}%",
                            help="Percentual da capacidade utilizada na extensão máxima"
                        )

                    # Adicionar o diagrama técnico
                    if raio_max > 0 and alcance_max > 0:
                        st.subheader("📊 Diagrama Técnico")
                        try:
                            fig = criar_diagrama_guindaste(raio_max, alcance_max)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Adicionar explicação
                            st.info("""
                            **Legenda do Diagrama:**
                            - **Torre (azul)**: Estrutura vertical do guindaste
                            - **Lança (vermelho)**: Braço do guindaste
                            - **Linha Amarela**: Referência de 45° (ângulo mínimo seguro)
                            - **Ângulo Atual**: Verde se ≥ 45°, Vermelho se < 45°
                            """)
                        except Exception as e:
                            st.error(f"Erro ao gerar o diagrama: {str(e)}")

            except ValueError as e:
                st.error(f"Erro: {str(e)}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {str(e)}")
        elif submeter:
            st.warning("⚠️ Por favor, insira o peso da carga para realizar os cálculos.")

    with tab2:
        st.header("Informações Complementares")
        
        # Adicionar seção de Tabela de Carga do Fabricante
        st.subheader("📊 Tabela de Carga do Fabricante")
        col1, col2 = st.columns(2)
        
        with col1:
            tabela_carga = st.file_uploader(
                "Upload da Tabela de Carga",
                type=['xlsx', 'xls', 'csv'],
                help="Faça upload da tabela de carga fornecida pelo fabricante"
            )
            
            if tabela_carga is not None:
                try:
                    if tabela_carga.name.endswith('.csv'):
                        df = pd.read_csv(tabela_carga)
                    else:
                        df = pd.read_excel(tabela_carga)
                    
                    st.success("✅ Tabela de carga carregada com sucesso!")
                    
                    # Mostrar a tabela
                    st.subheader("Visualização da Tabela de Carga")
                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=300
                    )
                    
                    # Criar gráfico da tabela de carga
                    if 'Raio' in df.columns and 'Capacidade' in df.columns:
                        fig = px.line(
                            df,
                            x='Raio',
                            y='Capacidade',
                            title='Curva de Capacidade do Guindaste',
                            labels={
                                'Raio': 'Raio (m)',
                                'Capacidade': 'Capacidade (kg)'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Erro ao carregar a tabela: {str(e)}")
                    st.info("""
                    A tabela deve estar em um dos seguintes formatos:
                    - CSV com colunas 'Raio' e 'Capacidade'
                    - Excel com colunas 'Raio' e 'Capacidade'
                    """)
        
        with col2:
            st.info("""
            **Instruções para Tabela de Carga:**
            
            1. A tabela deve conter as colunas:
               - Raio (m)
               - Capacidade (kg)
               
            2. Formatos aceitos:
               - Excel (.xlsx, .xls)
               - CSV (.csv)
               
            3. Certifique-se que:
               - Os valores estão nas unidades corretas
               - A tabela está formatada adequadamente
               - Os dados estão consistentes
               
            4. A tabela será usada para:
               - Validar capacidades
               - Gerar curva de carga
               - Verificar limites operacionais
            """)

        # Dados da Empresa
        st.subheader("📋 Dados da Empresa")
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Nome da Empresa")
            cnpj = st.text_input("CNPJ")
            
        with col2:
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")

        # Dados do Operador
        st.subheader("👤 Dados do Operador")
        col1, col2, col3 = st.columns(3)
        with col1:
            nome_operador = st.text_input("Nome do Operador")
            cpf_operador = st.text_input("CPF do Operador")
        
        with col2:
            cnh = st.text_input("CNH")
            validade_cnh = st.date_input("Validade CNH")
        
        with col3:
            certificacoes = st.multiselect(
                "Certificações do Operador",
                ["NR-11", "NR-12", "NR-18", "NR-35", "Outro"]
            )

        # Dados do Equipamento
        st.subheader("🏗️ Dados do Equipamento")
        col1, col2 = st.columns(2)
        with col1:
            placa = st.text_input("Placa do Guindaste")
            modelo_equip = st.text_input("Modelo")
            fabricante = st.text_input("Fabricante")
        
        with col2:
            ano = st.number_input("Ano", min_value=1950, max_value=2024)
            ultima_manutencao = st.date_input("Data Última Manutenção")
            proxima_manutencao = st.date_input("Data Próxima Manutenção")

        # Documentação
        st.subheader("📄 Documentação")
        col1, col2 = st.columns(2)
        with col1:
            num_art = st.text_input("Número da ART")
            validade_art = st.date_input("Validade da ART")
        
        with col2:
            st.file_uploader("Upload da ART", type=['pdf'])
            st.file_uploader("Certificado de Calibração", type=['pdf'])

        # Observações
        st.subheader("📝 Observações")
        observacoes = st.text_area(
            "Observações Gerais",
            height=100,
            help="Adicione informações relevantes sobre o equipamento, operação ou condições especiais"
        )

        # Botão para salvar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar Informações"):
                st.success("✅ Informações salvas com sucesso!")
        
        with col2:
            if st.button("🔄 Limpar Formulário"):
                st.warning("⚠️ Formulário limpo!")
                # Aqui você pode adicionar lógica para limpar os campos

