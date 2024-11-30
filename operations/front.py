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

def criar_diagrama_guindaste(raio_max, alcance_max, carga_total=None, capacidade_raio=None, angulo_minimo=45):
    """Cria um diagrama técnico do guindaste com simulação de içamento."""
    
    fig = go.Figure()

    # Calcula o comprimento real da lança
    comprimento_lanca = min(np.sqrt(raio_max**2 + alcance_max**2), raio_max)
    
    # Calcula o ângulo atual da lança
    angulo_atual = np.degrees(np.arctan2(alcance_max, raio_max))
    
    # Define o ângulo máximo seguro (para evitar que a carga fique sobre o guindaste)
    angulo_maximo = 80  # Limita o ângulo máximo a 80 graus
    
    # Calcula o raio de trabalho seguro baseado na carga
    if carga_total and capacidade_raio:
        raio_trabalho_seguro = min((capacidade_raio/carga_total) * raio_max, raio_max)
        # Garante que o raio de trabalho não seja menor que 20% do raio máximo
        raio_trabalho_seguro = max(raio_trabalho_seguro, raio_max * 0.2)
    else:
        raio_trabalho_seguro = raio_max

    # Calcula o ângulo seguro baseado no raio de trabalho
    angulo_trabalho = np.degrees(np.arctan2(
        np.sqrt(comprimento_lanca**2 - raio_trabalho_seguro**2),
        raio_trabalho_seguro
    ))
    
    # Define o ângulo seguro final (entre o mínimo do fabricante e máximo seguro)
    angulo_seguro = min(max(angulo_minimo, angulo_trabalho), angulo_maximo)
    
    # Adiciona a posição atual da lança
    x_atual = min(raio_max, comprimento_lanca * np.cos(np.radians(angulo_atual)))
    y_atual = min(alcance_max, comprimento_lanca * np.sin(np.radians(angulo_atual)))
    
    # Adiciona a posição segura recomendada
    x_seguro = min(raio_max, comprimento_lanca * np.cos(np.radians(angulo_seguro)))
    y_seguro = min(alcance_max, comprimento_lanca * np.sin(np.radians(angulo_seguro)))
    fig.add_trace(go.Scatter(
        x=[0, x_seguro],
        y=[0, y_seguro],
        mode='lines',
        name=f'Posição Segura ({angulo_seguro:.1f}°)',
        line=dict(color='green', width=2, dash='dash'),
        hovertemplate=f'<b>Ângulo Seguro:</b> {angulo_seguro:.1f}°<extra></extra>'
    ))
    
    # Desenha a base do guindaste
    fig.add_trace(go.Scatter(
        x=[-2, 2, 2, -2, -2],
        y=[-1, -1, 0, 0, -1],
        mode='lines',
        name='Base do Guindaste',
        line=dict(color='darkgray', width=3),
        fill='toself'
    ))
    
    # Desenha a lança na posição atual
    cor_atual = 'blue' if angulo_minimo <= angulo_atual <= angulo_maximo else 'red'
    fig.add_trace(go.Scatter(
        x=[0, x_atual],
        y=[0, y_atual],
        mode='lines',
        name=f'Posição Atual ({angulo_atual:.1f}°)',
        line=dict(color=cor_atual, width=3),
        hovertemplate=f'Ângulo: {angulo_atual:.1f}°<extra></extra>'
    ))
    
    # Adiciona zona de perigo (sobre o guindaste)
    theta = np.linspace(np.radians(angulo_maximo), np.pi/2, 50)
    x_zona = np.minimum(raio_max, comprimento_lanca * np.cos(theta))
    y_zona = np.minimum(alcance_max, comprimento_lanca * np.sin(theta))
    fig.add_trace(go.Scatter(
        x=np.concatenate([[0], x_zona, [0]]),
        y=np.concatenate([[0], y_zona, [0]]),
        fill='toself',
        fillcolor='rgba(255,0,0,0.1)',
        name='Zona de Perigo (Sobre o Guindaste)',
        line=dict(color='red', width=1, dash='dot'),
        hovertemplate='<b>Zona de Perigo</b><br>Ângulo > 80°<extra></extra>'
    ))

    # Adiciona anotação para o ângulo da zona de perigo
    fig.add_annotation(
        x=raio_max * 0.3,  # 30% do raio máximo
        y=alcance_max * 0.8,  # 80% da altura máxima
        text=f"Ângulo de Perigo: {angulo_maximo}°",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        arrowsize=1,
        arrowwidth=2,
        ax=50,  # Ajuste horizontal da seta
        ay=-30,  # Ajuste vertical da seta
        font=dict(
            color="red",
            size=12
        ),
        align="left"
    )

    # Adiciona linha do ângulo mínimo do fabricante
    x_min = min(raio_max, comprimento_lanca * np.cos(np.radians(angulo_minimo)))
    y_min = min(alcance_max, comprimento_lanca * np.sin(np.radians(angulo_minimo)))
    fig.add_trace(go.Scatter(
        x=[0, x_min],
        y=[0, y_min],
        mode='lines',
        name=f'Ângulo Mínimo ({angulo_minimo}°)',
        line=dict(color='orange', width=2, dash='dash'),
        hovertemplate=f'<b>Ângulo Mínimo:</b> {angulo_minimo}°<extra></extra>'
    ))

    # Atualiza o layout
    fig.update_layout(
        title=dict(
            text='Diagrama do Guindaste',
            x=0.5,
            y=0.95,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis_title='Distância (m)',
        yaxis_title='Altura (m)',
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(0,0,0,0)',  # Legenda sem fundo
            bordercolor='rgba(0,0,0,0)',  # Sem borda
            font=dict(
                size=12,
                color='white'  # Texto branco para melhor contraste
            )
        ),
        xaxis=dict(
            range=[-2, raio_max + 1],
            dtick=1,
            tick0=0,
            title=dict(
                text='Distância (m)',
                font=dict(size=14),
                standoff=10
            ),
            gridcolor='rgba(128, 128, 128, 0.2)',
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(0, 0, 0, 0.5)',
            zerolinewidth=1
        ),
        yaxis=dict(
            range=[-2, alcance_max + 2],
            title=dict(
                text='Altura (m)',
                font=dict(size=14),
                standoff=10
            ),
            gridcolor='rgba(128, 128, 128, 0.2)',
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(0, 0, 0, 0.5)',
            zerolinewidth=1
        ),
        yaxis_scaleanchor="x",
        yaxis_scaleratio=1,
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0)",
            font_size=12,
            font_family="Arial"
        ),
        margin=dict(t=100, l=80, r=80, b=80),
        width=800,
        height=600
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
                st.info("⚠️ Margem de segurança: 10% (equipamento novo)")
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
                    help=" Peso do objeto principal a ser içado, sem incluir acessórios ou cabos"
                )

            with col2:
                peso_acessorios = st.number_input(
                    "Peso dos acessórios (kg)",
                    min_value=0.0,
                    step=1.0,
                    value=0.0,
                    help="Peso total de todos os equipamentos auxiliares como cintas, grilhetas, manilhas, etc."
                )
                
                st.info("ℹ️ O peso dos cabos será calculado automaticamente como 3% do peso a considerar")

            # Dados do guindaste
            st.subheader("Dados do Guindaste")
            col3, col4 = st.columns(2)
            
            with col3:
                fabricante = st.text_input(
                    "Fabricante do Guindaste",
                    help=" Nome da empresa que fabricou o guindaste (ex: Liebherr, Manitowoc, etc.)"
                )
                modelo = st.text_input(
                    "Modelo do Guindaste",
                    help=" Código ou nome do modelo específico do guindaste (ex: LTM 1100, GMK 5220)"
                )
                
                raio_max = st.number_input(
                    "Raio Máximo (m)",
                    min_value=0.0,
                    step=0.1,
                    value=0.0,
                    help=" Distância horizontal máxima do centro do guindaste até o ponto de içamento"
                )

            with col4:
                capacidade_raio = st.number_input(
                    "Capacidade no Raio Máximo (kg)",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    help=" Peso máximo que o guindaste pode levantar na distância horizontal especificada"
                )
                
                alcance_max = st.number_input(
                    "Extensão Máxima da Lança (m)",
                    min_value=0.0,
                    step=0.1,
                    value=0.0,
                    help=" Comprimento total da lança quando totalmente estendida"
                )
                
                capacidade_alcance = st.number_input(
                    "Capacidade na Lança Máxima (kg)",
                    min_value=0.0,
                    step=100.0,
                    value=0.0,
                    help=" Peso máximo que o guindaste pode levantar com a lança totalmente estendida"
                )
                
                angulo_minimo_fabricante = st.number_input(
                    "Ângulo Mínimo da Lança (graus)",
                    min_value=0.0,
                    max_value=90.0,
                    step=1.0,
                    help=" Menor ângulo permitido entre a lança e o solo, conforme manual do fabricante"
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
                        st.subheader("📊 Simulação do Içamento")
                        try:
                            fig = criar_diagrama_guindaste(
                                raio_max, 
                                alcance_max,
                                resultado['carga_total'],
                                capacidade_raio,
                                angulo_minimo_fabricante
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            st.info(f"""
                            **Legenda do Diagrama:**
                            - **Linha Laranja**: Ângulo mínimo do fabricante ({angulo_minimo_fabricante}°)
                            - **Linha Azul**: Posições seguras da lança
                            - **Linha Vermelha**: Posições abaixo do ângulo mínimo
                            - **Linha Pontilhada Vermelha**: Limite de capacidade
                            
                            ⚠️ **Importante:**
                            - Mantenha a operação acima do ângulo mínimo do fabricante
                            - Observe o limite de capacidade indicado
                            - Considere as condições do local e do tempo
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
        
        # Seção do Gráfico de Carga do Fabricante
        st.subheader("📊 Gráfico de Carga do Fabricante")
        
        grafico_carga = st.file_uploader(
            "Upload do Gráfico de Carga",
            type=['png', 'jpg', 'jpeg'],
            help="Faça upload da imagem do gráfico de carga do fabricante"
        )
        
        if grafico_carga is not None:
            st.image(
                grafico_carga,
                caption="Gráfico de Carga do Fabricante",
                use_column_width=True
            )

        st.info("""
        **Instruções para o Gráfico de Carga:**
        
        1. O gráfico deve:
           - Ser a imagem oficial do manual do fabricante
           - Estar legível e completo
           - Corresponder ao modelo do guindaste
        
        2. Formatos aceitos:
           - PNG
           - JPG/JPEG
        
        3. Certifique-se que:
           - As informações estão atualizadas
           - Os dados correspondem ao modelo específico do equipamento
        """)

        # Dados da Empresa
        st.subheader("📋 Dados da Empresa")
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input(
                "Nome da Empresa",
                help=" Nome da empresa responsável pela operação"
            )
            cnpj = st.text_input(
                "CNPJ",
                help=" CNPJ da empresa (formato: XX.XXX.XXX/XXXX-XX)"
            )
            
        with col2:
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")

        # Dados do Operador
        st.subheader("👤 Dados do Operador")
        col1, col2, col3 = st.columns(3)
        with col1:
            nome_operador = st.text_input(
                "Nome do Operador",
                help="Nome completo do operador certificado do guindaste"
            )
            cpf_operador = st.text_input("CPF do Operador")
        
        with col2:
            cnh = st.text_input("CNH")
            validade_cnh = st.date_input("Validade CNH")
        
        with col3:
            certificacoes = st.multiselect(
                "Certificações do Operador",
                ["NR-11", "NR-12", "NR-18", "NR-35", "Outro"],
                help=" Normas regulamentadoras que o operador possui certificação"
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
            num_art = st.text_input(
                "Número da ART",
                help="Número da Anotação de Responsabilidade Técnica do engenheiro responsável"
            )
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

