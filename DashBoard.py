import streamlit as st
import requests as rq
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo}{valor:.2f}{unidade}'
        valor /=1000
    return f'{prefixo}{valor:.2f} milhões'


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

anoInicial = 2020
anoFinal = 2023

todos_anos = st.sidebar.checkbox('Dados de todos os anos', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', anoInicial, anoFinal)

query_string = {'regiao':regiao.lower(), 'ano':ano}
response = rq.get(url, params = query_string)

dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

#agora que tem buscou o dado filtrado, fazer o filtro de vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]
    
##Tabelas
###Tabelas aba Receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

###Tabela aba Quantidade de Vendas
#Construir um gráfico de mapa com a quantidade de vendas por estado.
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

#Construir um gráfico de linhas com a quantidade de vendas mensal.
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending = False)

#Construir um gráfico de barras com os 5 estados com maior quantidade de vendas.


###Tabela aba Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

##Gráficos
fig_mapa_receita = px.scatter_geo(receita_estados,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Preço',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat' : False, 'lon' : False},
                                 title = 'Receita por Estado')

fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Preço',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat' : False, 'lon' : False},
                                 title = 'Vendas por Estado')

fig_receita_mensal = px.line(receita_mensal, 
                            x = 'Mes',
                            y = 'Preço',
                            markers = True,
                            range_y = (0,receita_mensal.max()),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_vendas_mensal = px.line(vendas_mensal, 
                            x = 'Mes',
                            y = 'Preço',
                            markers = True,
                            range_y = (0,vendas_mensal.max()),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Quantidade de Vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_receita_estados = px.bar(receita_estados.head(), 
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_vendas_estados = px.bar(vendas_estados.head(), 
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto= True,
                             title = 'Top estados (vendas)')
fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_receita_categorias = px.bar(receita_categorias,
                               text_auto = True,
                               title = 'Receita por categorias')
fig_receita_categorias.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_categorias = px.bar(vendas_categorias,
                               text_auto = True,
                               title = 'Vendas por categorias')
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de Vendas')

##Visualização no streamlit

#criar abas
tab1, tab2, tab3 = st.tabs(['Receitas', 'Quantidade de Vendas', 'Vendedores'])

with tab1:
    #dividir em coluna 
    col1, col2 = st.columns(2)
    with col1:
        #soma a coluna Preço do dataframe
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width= True)
        #dados.shape[0] - conta o número de linhas
    with col2:
        st.metric('Quantidade de Vendas YYY', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width= True)

with tab2:
    #dividir em coluna 
    col1, col2 = st.columns(2)
    with col1:
        #conta a coluna Preço do dataframe
        st.metric('Receita', formata_numero(dados['Preço'].sum()))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width= True)
        #dados.shape[0] - conta o número de linhas
    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width= True)

with tab3:
    #interatividade
    quantidade_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)

    #dividir em coluna 
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(quantidade_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(quantidade_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {quantidade_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores, use_container_width = True )

    with col2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(quantidade_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(quantidade_vendedores).index,
                                        text_auto= True,
                                        title= f'Top {quantidade_vendedores} vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores, use_container_width = True )

st.dataframe(dados)

