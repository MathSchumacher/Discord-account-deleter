# app.py
import subprocess  # Para rodar xvfb se necessário (cloud auto-instala)
import streamlit as st
import base64
from delete_discord_account import process_account

# --- 1. Configurações da página ---
st.set_page_config(
    page_title="Discord Account Deleter",
    page_icon="img/discord.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS customizado RESPONSIVO ---
st.markdown("""
    <style>
    /* REMOVER espaçamento excessivo no topo */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    /* Reduzir ainda mais o padding superior */
    .stApp {
        margin-top: -2rem;
    }

    /* Container para ícone e título COLADOS */
    .header-container {
        display: flex;
        align-items: center;
        gap: 12px;
        justify-content: flex-start;
        margin-bottom: 0.5rem;
    }

    .header-title {
        font-size: 1.8rem;
        margin: 0;
        font-weight: bold;
        color: #5865F2;
    }

    @media (max-width: 768px) {
        .header-title { font-size: 1.4rem; }
        .header-container { gap: 10px; }
    }

    @media (max-width: 480px) {
        .header-title { font-size: 1.2rem; }
        .header-container { gap: 8px; }
    }

    /* Botões e inputs (restante do seu CSS) */
    .stButton > button {
        background-color: #5865F2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1rem;
    }

    .stButton > button:hover {
        background-color: #4752C4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    hr { margin: 0.5rem 0; }

    .footer {
        text-align: center;
        color: #666;
        font-size: 0.75rem;
        padding: 5px;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Título e Ícone Alinhados Lado a Lado ---
with open("img/discord.svg", "rb") as f:
    discord_icon = base64.b64encode(f.read()).decode()

st.markdown(f"""
    <div class="header-container">
        <img src="data:image/svg+xml;base64,{discord_icon}" width="40" style="margin-right:8px;">
        <h1 class="header-title">Discord Account Deleter</h1>
    </div>
    <hr>
""", unsafe_allow_html=True)

# --- 4. Inicializa estado da sessão ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'gen' not in st.session_state:
    st.session_state.gen = None
if 'current_email' not in st.session_state:
    st.session_state.current_email = ""
if 'current_password' not in st.session_state:
    st.session_state.current_password = ""
if 'email_password' not in st.session_state:
    st.session_state.email_password = ""
if 'result' not in st.session_state:
    st.session_state.result = None

# --- 5. Formulário Principal ---
with st.form("account_submission_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        email = st.text_input(
            "📧 Email:", 
            placeholder="exemplo@discord.com", 
            key="email_input"
        )
    with col2:
        old_password = st.text_input(
            "🔑 Senha Atual:", 
            type="password", 
            placeholder="Sua senha atual", 
            key="password_input"
        )

    new_password = "deletingsoon123"
    st.info(f"**Nova senha será definida como:** `{new_password}`")

    submitted = st.form_submit_button(
        "🚀 Processar Conta", 
        type="primary", 
        disabled=st.session_state.processing
    )

# --- 6. Iniciar Processamento ---
if submitted and not st.session_state.processing:
    if not email or not old_password:
        st.warning("⚠️ Preencha email e senha para continuar.")
    else:
        st.session_state.processing = True
        st.session_state.current_email = email
        st.session_state.current_password = old_password
        st.session_state.logs = []
        st.session_state.result = None
        st.session_state.gen = process_account(email, old_password, new_password)
        st.rerun()

# --- 7. Gerenciar Generator ---
if st.session_state.processing and st.session_state.gen:
    try:
        # Avançar generator
        state = next(st.session_state.gen)
        while isinstance(state, dict) and 'type' in state:
            if state['type'] == 'log':
                st.session_state.logs.append({'message': state['message'], 'level': state['level']})
                st.rerun()  # Rerun to show log immediately
            elif state['type'] == 'need_captcha':
                st.warning("🛡️ CAPTCHA detectado! Resolva manualmente no navegador.")
                if st.button("✅ Captcha Finalizado", type="primary"):
                    st.session_state.gen.send("captcha_done")
                    st.rerun()
                st.stop()
            elif state['type'] == 'need_2fa':
                st.warning("🔐 2FA detectado! Insira o código no navegador.")
                if st.button("✅ 2FA Finalizado", type="primary"):
                    st.session_state.gen.send("2fa_done")
                    st.rerun()
                st.stop()
            elif state['type'] == 'need_email_pass':
                st.warning("📧 Verificação de email detectada! Digite a senha do email.")
                with st.form("email_form"):
                    email_pwd = st.text_input("🔑 Senha do Email:", type="password")
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_email = st.form_submit_button("✅ Confirmar", type="primary")
                    with col2:
                        cancel = st.form_submit_button("❌ Cancelar")
                    if submit_email and email_pwd:
                        st.session_state.gen.send(email_pwd)
                        st.rerun()
                    if cancel:
                        st.session_state.gen.send(None)
                        st.rerun()
                st.stop()
            elif state['type'] == 'manual_email_verify':
                st.warning("📧 Verificação manual necessária. Verifique o email e clique no link de verificação no navegador Discord.")
                if st.button("✅ Verificação Finalizada", type="primary"):
                    st.session_state.gen.send("manual_verify_done")
                    st.rerun()
                st.stop()
            else:
                # Unknown state
                break
        # If we reach here, process completed
        result, final_logs = st.session_state.gen.send(None)  # End it
        st.session_state.logs.extend(final_logs)
        st.session_state.result = result
        st.session_state.processing = False
        st.session_state.gen = None
        st.rerun()
    except StopIteration:
        st.session_state.processing = False
        st.session_state.gen = None
        st.rerun()
    except Exception as e:
        st.session_state.logs.append({"message": f"Erro no generator: {e}", "level": "error"})
        st.session_state.processing = False
        st.session_state.gen = None
        st.rerun()

# --- 8. Mostrar Resultado ---
if st.session_state.result:
    if st.session_state.result == "SUCCESS":
        st.success("✅ Sucesso!")
    else:
        st.error(f"❌ {st.session_state.result}")

# --- 9. Exibe Logs ---
if st.session_state.logs:
    st.subheader("📋 Logs em Tempo Real")
    for log in st.session_state.logs:
        msg = log["message"]
        level = log["level"]
        if level == "success":
            st.success(msg)
        elif level == "error":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)
        else:
            st.info(msg)

# --- 10. Reiniciar ---
if st.button("🔄 Reiniciar"):
    for key in st.session_state.keys():
        delattr(st.session_state, key)
    st.rerun()

# --- 11. Footer ---
st.markdown("---")
st.markdown(
    '<div class="footer">Discord Account Deleter • Use com responsabilidade</div>',
    unsafe_allow_html=True
)