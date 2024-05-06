import streamlit as st
import json
import main

with open('main_data/data.json', 'r') as f:
    data = json.loads(f.read())
with st.chat_message("assistant"):
    st.write(f"**{data["name_b"]}**: Olá {data['name']}, sou {data['name_b']}. Como posso te ajudar?")
if prompt := st.chat_input("Digite aqui!"):
    if not prompt[0] == data['prefix']:
        with st.chat_message("user"):
            st.write(f"**{data['name']}**: {prompt}")
            with st.spinner('Aguarde'):
                main.new_chat(prompt)
    else:
        st.warning("Comandos não podem ser ultilizados aqui. Vá para [aqui!](./console)")
