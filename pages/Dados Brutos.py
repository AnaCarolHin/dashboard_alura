import streamlit as st
import requests as rq
import pandas as pd
import plotly.express as px
import time

@st.cache_data
def converte(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅" )
    time.sleep(5)
    sucesso.empty()


st.title('Dados Brutos')

url = 'https://labdados.com/produtos'
response = rq.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Produtos'):
    produtos = st.multiselect('Selecione os produtos', list(dados['Produto'].unique()), list(dados['Produto'].unique()))

with st.sidebar.expander('Preço'):
    # 0 = preco minimo, 5000 = preco maximo, (0,5000) = para selecionar minimo e maximo ao mesmo tempo
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

#''' isso serve para escrever multilinhas
# \ isso indica que a linha continua na seguinte
# @ isso indica que é a variavel criada anteriormente
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas.')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility= 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click= mensagem_sucesso)
