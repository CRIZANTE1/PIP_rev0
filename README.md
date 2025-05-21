# Calculadora de Movimentação de Carga (PIP_rev0)

Este projeto é uma aplicação Streamlit para auxiliar no cálculo e validação de cargas para operações de içamento com guindastes e guindautos. Ele incorpora funcionalidades de login OIDC para controle de acesso.

## Funcionalidades

*   **Cálculo de Carga:** Calcula a carga total a ser içada, considerando o peso da carga principal, acessórios, cabos e margens de segurança (diferentes para equipamentos novos e usados).
*   **Validação do Guindaste:** Verifica se o guindaste é adequado para a operação com base na carga total e nas capacidades do equipamento (raio e alcance).
*   **Diagrama Ilustrativo:** Gera um diagrama visual da operação de içamento, mostrando a posição da lança e zonas de segurança/perigo.
*   **Informações Complementares:** Permite registrar dados da empresa, operador, equipamento e documentação relevante (ART, certificado de calibração).
*   **Login OIDC:** Integração com OpenID Connect para autenticação de usuários.

## Requisitos

*   Python 3.7+
*   Streamlit (versão 1.44.0 ou superior para OIDC)
*   Authlib (versão 1.3.2 ou superior para OIDC)
*   Outras dependências listadas em `requirements.txt`

## Instalação

1.  Consultar dev.
   

## Configuração de Login OIDC

Para habilitar o login OIDC, crie um arquivo `.streamlit/secrets.toml` na raiz do projeto com as suas credenciais OIDC. Exemplo:

```toml
[oauth.google]
client_id = "SEU_CLIENT_ID_GOOGLE"
client_secret = "SEU_CLIENT_SECRET_GOOGLE"
redirect_uri = "http://localhost:8501" # Ou a URL de redirecionamento configurada
```

Você também precisa gerar um `cookie_secret` forte e aleatório no mesmo arquivo `secrets.toml`:

```toml
cookie_secret = "SEU_SEGREDO_FORTE_E_ALEATORIO"
```

Consulte a documentação do Streamlit para mais detalhes sobre a configuração OIDC.

## Como Executar

Após a instalação e configuração, execute o aplicativo com o seguinte comando:

```bash
streamlit run main.py
```

O aplicativo será aberto no seu navegador padrão em `http://localhost:8501`.

## Estrutura do Projeto

*   `main.py`: Ponto de entrada da aplicação, configura a página e gerencia o fluxo de login/aplicativo principal.
*   `auth/`: Contém módulos relacionados à autenticação OIDC.
    *   `auth_utils.py`: Funções utilitárias para verificar status de login e obter informações do usuário.
    *   `login_page.py`: Funções para exibir a página de login, cabeçalho do usuário e botão de logout.
    *   `__init__.py`: Facilita a importação dos módulos de autenticação.
*   `operations/`: Contém módulos relacionados à lógica da calculadora de carga.
    *   `calc.py`: Funções para cálculo de carga e validação do guindaste.
    *   `front.py`: Interface do usuário (frontend) da calculadora de carga.
*   `requirements.txt`: Lista das dependências do projeto.
*   `README.md`: Este arquivo.
*   `.gitignore`: Arquivos e pastas a serem ignorados pelo Git.
*   `LICENSE.txt`: Informações sobre a licença do projeto.

## Licença

Este projeto está sob a licença restrita. Veja o arquivo `LICENSE.txt` para mais detalhes.

## Contato

Desenvolvido por Cristian Ferreira Carlos.
LinkedIn: https://www.linkedin.com/in/cristian-ferreira-carlos-256b19161/

Copyright 2024, Cristian Ferreira Carlos, Todos os direitos reservados.
