import time
import streamlit as st
import google.generativeai as genai
import json
from requests import get
from unidecode import unidecode as un
from google.generativeai.types import generation_types as gt


class ChatBot:
    def __init__(self, num_chat: str, hist: json, data: json, prompt=None):
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        self.container = st.container()
        self.system = (lambda text: self.container.chat_message("System").write(text))
        self.user = (lambda text: self.container.chat_message("user").write(text))
        self.bot = (lambda text: self.container.chat_message("assistant").write(text))
        self.data = data
        self.hist = hist
        self.num_chat = num_chat
        self.username = self.data['name']
        self.prefix = self.data['prefix']
        self.name = self.data['name_b']
        self.temp = self.data['temperature']
        genai.configure(api_key=st.secrets["API"]["key"])
        self.chat = genai.GenerativeModel(
            'gemini-1.5-pro-latest',
            system_instruction=self.data["main"],
            safety_settings=self.safety_settings)
        self.generator = genai.GenerativeModel(
            'gemini-pro',
            safety_settings=self.safety_settings)
        try:
            self.hist_content = self.hist[self.num_chat]['content']
            self.title = self.hist[self.num_chat]['title']
        except KeyError:
            self.new(prompt)
        self.show_hist()

    def new(self, prompt):
        self.title = (self.generator.generate_content(
            f'Gere apenas um simples titulo para uma possivel conversa com a '
            f'seguinte mensagem inicial: "{prompt}"',
            generation_config=genai.types.GenerationConfig(temperature=0.5)).text)
        self.hist[self.num_chat] = {'title': self.title,
                                    'content':
                                        [
                                            {
                                                "role": "model",
                                                "parts": [f"Olá {self.data['name']}, sou {self.data['name_b']}. "
                                                          f"Como posso te ajudar?"]
                                            },
                                            {
                                                "role": "user",
                                                "parts": [prompt]
                                            },
                                            {
                                                "role": "model",
                                                "parts": [self.chat.generate_content(prompt,
                                                                                     generation_config=genai.types.
                                                                                     GenerationConfig(
                                                                                         temperature=self.temp)).text]
                                            }
                                        ]
                                    }

        st.session_state.default = int(self.num_chat) - 1
        st.session_state.titulos_numchat.append([self.num_chat, self.title])
        self.hist_content = self.hist[self.num_chat]['content']
        self.title = self.hist[self.num_chat]['title']
        self.mudar_hist()
        st.switch_page("main.py")

    def send_message(self, prompt: str):
        self.hist_content.append({'role': 'user', 'parts': [prompt]})
        self.user(f"**{self.username}**: {prompt}")
        with st.spinner('Aguarde'):
            try:
                response = self.chat.generate_content(self.hist_content, generation_config=genai.types.GenerationConfig(
                    temperature=self.temp)).text
                self.hist_content.append({'role': 'model', 'parts': [response]})
            except gt.BlockedPromptException:
                response = self.generator.generate_content(
                    'Crie uma pequena frase falando algo do tipo: Não posso responder isso pois '
                    'sou apenas uma IA', generation_config=genai.types.GenerationConfig(temperature=0.1)).text
        self.mudar_hist()
        self.bot(f"**{self.name}**: {response}")

    def mudar_hist(self):
        with open('hist/hist.json', 'r') as f:
            hist = json.loads(f.read())
        hist[self.num_chat] = {"title": self.title, "content": self.hist_content}
        with open('hist/hist.json', 'w') as f:
            json.dump(hist, f)

    def show_hist(self, prompt=''):
        temp_hist = self.hist_content
        if prompt:
            temp_hist = self.hist_content + [{"role": "user", "parts": [prompt]}]
        for e in temp_hist:
            if e['role'] == 'user':
                self.user(f"**{self.username}**: {e['parts'][0]}")
            else:
                self.bot(f"**{self.name}**: {e['parts'][0]}")

    def command(self, prompt):
        comando = prompt.split()[0]
        arg = (prompt[len(comando):] if prompt[len(comando):] else '').strip()
        erro = f'Erro no uso do comando "{self.prefix}{comando} {arg}". Verifique uso usando {self.prefix}help'
        with st.spinner("Aguarde"):
            if comando in self.data['commands']:
                self.system(f"**Comando**\n\n\t{self.prefix}{comando} {arg}")
                if comando in ["help", "?", "h", "ajuda"]:
                    self.system(
                        f"**Menu de ajuda**\n\n{data["menu"].replace("{prefix}", self.prefix)}")
                elif comando == "load":
                    try:
                        int(arg)
                        if arg not in self.hist:
                            st.warning(f"O chat {arg} não está registrado")
                        elif arg == str(st.session_state.default + 1):
                            st.warning("Você já está nesse chat!")
                        else:
                            st.warning(f"Iniciando chat {arg}")
                            time.sleep(0.5)
                            st.session_state.default = int(arg) - 1
                            st.rerun()
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
                    st.rerun()
                elif comando in ["console", "cmd"]:
                    st.warning("Redirecionando para console")
                    time.sleep(0.5)
                    st.switch_page('pages/console.py')
            else:
                self.container.warning(
                    f'Comando "{self.prefix}{comando}" não registrado, digite {self.prefix}help para obter ajuda!')


def new_chat(prompt):
    with open('hist/hist.json', 'r') as f:
        hist = json.loads(f.read())
    with open('main_data/data.json', 'r') as f:
        data = json.loads(f.read())
    if hist:
        keys = list(hist.keys())
        st.session_state.num_chat = str(int(keys[len(keys) - 1]) + 1)
    else:
        st.session_state.num_chat = '1'
    st.session_state.bot = ChatBot(st.session_state.num_chat, hist, data, prompt=prompt)


if __name__ == "__main__":
    with open('hist/hist.json', 'r', encoding="UTF-8") as f:
        hist = json.loads(f.read())
    with open('main_data/data.json', 'r', encoding="UTF-8") as f:
        data = json.loads(f.read())
    if 'default' not in st.session_state:
        st.session_state.default = None
    if 'titulos_numchat' not in st.session_state:
        st.session_state.titulos_numchat = [[e, hist[e]['title']] for e in hist]
    if "Novo Chat!" in st.session_state.titulos_numchat:
        st.session_state.titulos_numchat.remove("Novo Chat!")
    if data['FA']:
        st.switch_page("pages/settings.py")
    if not hist:
        st.switch_page('pages/new_chat.py')
    if 'one' not in st.session_state:
        loc = get('http://ipinfo.io/json').json()
        data["main"] = (f'I am your creator and from now your name is "{data['name_b']}". You are an AI based on the '
                        f'gemini-pro and was created by Enzo Albuquerque. User´s name is {data['name']}.'
                        f'{data['name']}`s ip {loc['ip']} is and the location is: '
                        f'latitude:{float(loc['loc'].split(',')[0])} and longitude: {float(loc['loc'].split(',')[1])}. '
                        f'Here is some informations: Your version is currently: {data['version']}, you are running in '
                        f'a streamlit server, so use things thatstreamlit supports like LaTe, etc. '
                        f'\nFull user information: {loc}')
        with open('main_data/data.json', 'w') as f:
            json.dump(data, f)
        st.session_state.one = True
    st.session_state.titulos_numchat.append("Novo Chat!")
    # titulos = [f"{num}: {title}" for num, title in st.session_state.titulos_numchat][0]
    selected_titulo = st.selectbox('Selecione um historico',
                                   st.session_state.titulos_numchat,
                                   placeholder="Historico",
                                   index=st.session_state.default)
    if selected_titulo:
        if selected_titulo == "Novo Chat!":
            st.switch_page("pages/new_chat.py")
        st.session_state.num_chat = str(selected_titulo[0])
        st.session_state.bot = ChatBot(st.session_state.num_chat, hist, data)
        if prompt := st.chat_input("Digite aqui!"):
            if not prompt[0] == data['prefix']:
                st.session_state.bot.send_message(prompt)
            else:
                st.session_state.bot.command(un(prompt[1:].strip(' ').lower()))

    else:
        if st.button("Criar um novo chat!"):
            st.switch_page('pages/new_chat.py')
        st.write("Selecione um dos seus chats antigos ou crie um novo.")
