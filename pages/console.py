import time
import streamlit as st
import json


with open('main_data/data.json', 'r', encoding="UTF-8") as f:
    data = json.loads(f.read())
with open('hist/hist.json', 'r', encoding="UTF-8") as f:
    hist = json.loads(f.read())

if 'default' not in st.session_state:
    st.session_state.default = None

st.title("**Console**")
main_container = st.container()
system = (lambda text: main_container.chat_message("System").write(text))
user = (lambda text: main_container.chat_message("user").write(text))
if prompt := st.chat_input("Comando aqui"):
    prompt = prompt.strip().lower()
    if data['prefix'] == prompt[0]:
        prompt = prompt.replace(data['prefix'], '')
    comando = prompt.split()[0]
    arg = (prompt[len(comando):] if prompt[len(comando):] else '').strip()
    erro = f'Erro no uso do comando "{data['prefix']}{comando} {arg}". Verifique uso usando {data['prefix']}help'
    with st.spinner("Aguarde"):
        if comando in data['commands']:
            system(f"**Comando**\n\n\t{data['prefix']}{comando} {arg}")
            if comando in ["help", "?", "h", "ajuda"]:
                system(
                    f"**Menu de ajuda**\n\n{data["menu"].replace("{prefix}", data['prefix'])}")
            elif comando == "load":
                try:
                    int(arg)
                    if arg not in hist:
                        st.warning(f"O chat {arg} não está registrado")
                    else:
                        st.warning(f"Iniciando chat {arg}")
                        st.session_state.default = int(arg)-1
                        time.sleep(0.5)
                        st.switch_page('main.py')
                except ValueError:
                    st.warning(erro)
            elif comando in ['settings', 'setting', 'config', 'configuracoes']:
                st.warning("Mudando para configurações...")
                time.sleep(0.5)
                st.switch_page("pages/settings.py")
            elif comando == 'new':
                st.warning("Iniciando novo chat...")
                time.sleep(0.5)
                st.switch_page("pages/new_chat.py")
            elif comando == "home":
                st.session_state.default = None
                st.switch_page("main.py")
        else:
            main_container.warning(
                f'Comando "{data['prefix']}{comando}" não registrado, digite {data['prefix']}help para obter ajuda!')
