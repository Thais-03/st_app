# Importar bibliotecas de terceiros
import pandas as pd
import streamlit as st

# Importar pacotes específicos de bibliotecas
from datetime import datetime

# Carregar dados
envios_raw = pd.read_csv('data/envios_db.csv')


# Data Wrangling
envios_raw['Data'] = pd.to_datetime(envios_raw['Data'], dayfirst=True)
envios_raw['Faixa de Peso'] = envios_raw['Faixa de Peso'].astype(str)
envios_raw.loc[envios_raw['Faixa de Peso'] == 'nan', 'Faixa de Peso'] = np.nan
envios_raw = envios_raw.dropna()



envios = envios_raw[['Data', 'UF', 'CEP', 'Município', 'Valor previsto', 'Frete', 'Faixa de Peso', 'Total da Venda']]

# Desenvolver componentes

# Configuração da página
st.set_page_config(page_title='Frete B2C', page_icon=':truck:', layout='wide')

# Título do webapp e instruções
st.title('Frete B2C')
st.write('''Este dashboard oferece uma análise abrangente dos valores de frete para canais B2C, com dados históricos atualizados semanalmente. 
         Na barra lateral, é possível aplicar filtros por data, estado (UF), município e valor total do pedido.''')

# Exibir datas iniciais e finais
min_data = envios.Data.min().strftime("%d-%m-%Y")
max_data = envios.Data.max().strftime("%d-%m-%Y")
data = datetime.now().strftime("%d-%m-%Y")
st.write(f'Data Inicial: {min_data}')
st.write(f'Data Final: {max_data}')
st.write(f'Última atualização: {data}')

st.markdown('---')

# Filtro de data
st.sidebar.header('Filtros:')
min_data = envios.Data.min()
max_data = envios.Data.max()

# Filtro para data inicial e final
data_inicial = st.sidebar.date_input('Data Inicial', value=min_data, min_value=min_data, max_value=max_data, format='YYYY-MM-DD')
data_final = st.sidebar.date_input('Data Final', value=max_data, min_value=min_data, max_value=max_data, format='YYYY-MM-DD')

# Aplicar filtro de data
envios_filtrados = envios[(envios['Data'] <= pd.to_datetime(data_final)) & 
                          (envios['Data'] >= pd.to_datetime(data_inicial))]

# Filtro UF
estados = ['Todos','AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
UF_selecionada = st.sidebar.selectbox("UF:", estados, index=0)

# Aplicar filtro de UF
if UF_selecionada == 'Todos':
    envios_filtrados = envios_filtrados

else:
    envios_filtrados = envios_filtrados[envios_filtrados['UF'] == UF_selecionada]

# Filtro Valor do Pedido
valor_pedido = st.sidebar.slider("Valor do Pedido", 0, 10000, (0, 10000))
valor_pedido_min, valor_pedido_max = valor_pedido

# Aplicar filtro de valor do pedido
envios_filtrados = envios_filtrados[(envios_filtrados['Total da Venda'] >= valor_pedido_min) & (envios_filtrados['Total da Venda'] <= valor_pedido_max)]

# 11 - Título da seção - st.write()
# 12 - totalizador - Frete - st.metric()
# 13 - totalizador - Valor previsto - st.metric()
# 14 - totalizador - Frete Médio - st.metric()
# 15 - totalizador - ticket médio - st.metric()
st.header('Métricas')

# Gerar data frame com os dados
despesa = (envios_filtrados.groupby('Data')['Frete'].sum()).sum()



receita = envios_filtrados['Valor previsto'].sum()
frt_med = envios_filtrados['Frete'].mean()
tkt_med = envios_filtrados['Total da Venda'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Despesa", f"R${despesa:,.2f}")
col2.metric("Receita", f"R${receita:,.2f}")
col3.metric("Frete Médio", f"R${frt_med:,.2f}")
col4.metric("Ticket Médio", f"R${tkt_med:,.2f}")

st.markdown('---')
# 16 - Gráfico de quantidade de envios ao longo do tempo
st.header('Quantidade de Envios')

# Gerar data frame com os dados
gr_16 = envios_filtrados.groupby('Data')['Frete'].value_counts().reset_index()
gr_16.columns = ['Data', 'Frete', 'Quantidade']

#Plotar gráfico
st.line_chart(gr_16,
              x='Data',
              y='Quantidade')


# 17 - Gráfico Despesa e Receita ao longo do tempo
st.header('Ao longo do tempo')

# Gerar data frame com os dados
gr_17 = envios.groupby('Data').agg({'Frete': 'sum', 'Valor previsto': 'sum'}).reset_index()

#Plotar gráfico
st.line_chart(gr_17,
              x='Data',
              y=['Frete', 'Valor previsto'])


# 18 - Gráfico de frete grátis
st.header('Frete Grátis')

# Gerar data frame com os dados
gr_18 = envios[envios['Frete'] == 0].groupby('Data')['Frete'].value_counts().reset_index()
gr_18.columns = ['Data', 'Frete', 'Quantidade']

#Plotar gráfico
st.line_chart(gr_18,
              x='Data',
              y='Quantidade')

# 19 - Gráfico distribuiçao por UF - st.bar_chart() ***
st.header('Distrubuição por UF')

# Gerar data frame com os dados
gr_19 = envios['UF'].value_counts()

# Plotar gráfico
st.bar_chart(gr_19)

# 20 - Scatter por UF ***
st.header('Frete Médio e Quantidade por UF')

# Gerar data frame com os dados
gr_20 = envios.pivot_table(index='UF', 
                           aggfunc={'Frete': 'mean',
                                    'UF': 'size'},
                            values='Frete')

gr_20 = gr_20.rename(columns={'UF': 'Quantidade', 'Frete': 'Frete Médio'})
gr_20 = gr_20.reset_index()
gr_20 = gr_20[['UF', 'Quantidade', 'Frete Médio']]

# Plotar gráfico
st.scatter_chart(gr_20,
                 x='UF',
                 y='Quantidade',
                 size='Frete Médio',
                 color='UF')

# 21 - Gráfico em base ao peso dos envios ***
st.header('Peso dos Envios')

# Gerar data frame com os dados
gr_21 = envios['Faixa de Peso'].value_counts()
gr_21 = gr_21.dropna()

# Plotar gráfico
st.bar_chart(gr_21)
