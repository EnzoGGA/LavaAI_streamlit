import time

import streamlit as st
import json

with open('main_data/data.json', 'r') as f:
    data = json.loads(f.read())

version = data['version']
prefix = data['prefix']
name = data['name']
bot = data['name_b']
st.title("Settings")
st.write(f"Versão atual: {version}")
FA = data["FA"]

permitidos = ['.', '/', "!", ',', ':', '?', ';']
can_pass = True
selected_prefix = st.selectbox(label=f'Prefixo (atual "{prefix}")',
                               options=permitidos,
                               index=permitidos.index(prefix))

selected_nome = st.text_input(label="Nome",
                              help="Digite aqui seu nome",
                              max_chars=10,
                              value=name if name else None,
                              placeholder='Digite seu nome')
if not selected_nome:
    can_pass = False

selected_temp = st.selectbox(label="Preferencia da IA",
                             options=['Mais Criativa', "Mediana", "Mais objetiva"],
                             index=1)
if selected_temp == "Mais Criativa":
    temp = 1
elif selected_temp == "Mediana":
    temp = 0.5
else:
    temp = 0.1

if st.button("Aplicar", disabled=not can_pass):
    data['prefix'] = selected_prefix
    data['name'] = selected_nome
    data['FA'] = False
    with open('main_data/data.json', 'w') as f:
        json.dump(data, f)
    st.warning("Aplicado!", icon='✅')
    time.sleep(1)
    st.switch_page('main.py')

if FA:
    st.caption('Nota do desenvolvedor: "Criado por Enzo Albuquerque como projeto pessoal. Obrigado!"')
