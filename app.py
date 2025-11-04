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

# --- 3. Título e Ícone Alinhados Lado a Lado (corrigido com base64) ---
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
if 'current_email' not in st.session_state:
    st.session_state.current_email = ""
if 'current_password' not in st.session_state:
    st.session_state.current_password = ""
if 'email_password' not in st.session_state:
    st.session_state.email_password = ""
if 'step' not in st.session_state:
    st.session_state.step = "initial"  # initial, running, need_captcha, waiting_captcha, need_2fa, waiting_2fa, need_email_pass, waiting_email_pass, manual_email_verify, waiting_manual_verify, done
if 'result' not in st.session_state:
    st.session_state.result = None
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'new_password' not in st.session_state:
    st.session_state.new_password = "deletingsoon123"

# --- 5. Formulário Principal COMPACTO ---
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

    st.info(f"**Nova senha será definida como:** `{st.session_state.new_password}`")

    submitted = st.form_submit_button(
        "🚀 Processar Conta", 
        type="primary", 
        disabled=st.session_state.processing
    )

# --- 6. Lógica de Processamento Principal ---
if submitted and not st.session_state.processing:
    if not email or not old_password:
        st.warning("⚠️ Preencha email e senha para continuar.")
    else:
        st.session_state.processing = True
        st.session_state.current_email = email
        st.session_state.current_password = old_password
        st.session_state.logs = []
        st.session_state.step = "running"
        st.session_state.result = None
        st.session_state.generator = process_account(
            st.session_state.current_email,
            st.session_state.current_password,
            st.session_state.new_password
        )
        st.rerun()

# --- 7. Gerenciamento de Passos Interativos (Generator Handling) ---
if st.session_state.processing:
    if st.session_state.step == "running":
        with st.spinner("🔄 Processando..."):
            try:
                # Advance generator one step at a time
                yielded = next(st.session_state.generator)
                st.session_state.logs = st.session_state.generator.gi_frame.f_locals.get('logs', st.session_state.logs)  # Sync logs from generator locals if possible
                if isinstance(yielded, dict):
                    msg_type = yielded.get("type")
                    if msg_type == "need_captcha":
                        st.session_state.step = "need_captcha"
                    elif msg_type == "waiting_captcha":
                        st.session_state.step = "waiting_captcha"
                    elif msg_type == "need_2fa":
                        st.session_state.step = "need_2fa"
                    elif msg_type == "waiting_2fa":
                        st.session_state.step = "waiting_2fa"
                    elif msg_type == "need_email_pass":
                        st.session_state.step = "need_email_pass"
                    elif msg_type == "waiting_email_pass":
                        st.session_state.step = "waiting_email_pass"
                    elif msg_type == "manual_email_verify":
                        st.session_state.step = "manual_email_verify"
                    elif msg_type == "waiting_manual_verify":
                        st.session_state.step = "waiting_manual_verify"
                    elif msg_type == "log":
                        # Log already appended in generator; just rerun to update UI
                        pass
                    else:
                        # Continue running
                        st.session_state.step = "running"
                else:
                    # Non-dict yield (e.g., email password from send)
                    st.session_state.step = "running"
                st.rerun()
            except StopIteration as e:
                # Generator finished: capture return value
                st.session_state.result, final_logs = e.value
                st.session_state.logs = final_logs or st.session_state.logs
                st.session_state.step = "done"
                st.session_state.processing = False
                st.rerun()
            except Exception as e:
                error_log = {"message": f"❌ Erro geral: {str(e)}", "level": "error"}
                st.session_state.logs.append(error_log)
                st.session_state.step = "done"
                st.session_state.processing = False
                st.session_state.result = "ERROR"
                st.rerun()

    # Handle interactive steps: Send signal back on button click and resume
    def resume_with_signal(signal):
        try:
            yielded = st.session_state.generator.send(signal)
            st.session_state.logs = st.session_state.generator.gi_frame.f_locals.get('logs', st.session_state.logs)
            if isinstance(yielded, dict):
                msg_type = yielded.get("type")
                if "waiting" in msg_type:
                    st.session_state.step = msg_type.replace("waiting_", "need_")
                else:
                    st.session_state.step = "running"
            st.rerun()
        except StopIteration as e:
            st.session_state.result, final_logs = e.value
            st.session_state.logs = final_logs or st.session_state.logs
            st.session_state.step = "done"
            st.session_state.processing = False
            st.rerun()
        except Exception as e:
            error_log = {"message": f"❌ Erro ao retomar: {str(e)}", "level": "error"}
            st.session_state.logs.append(error_log)
            st.session_state.step = "done"
            st.session_state.processing = False
            st.session_state.result = "ERROR"
            st.rerun()

    # Passo: Need CAPTCHA (show warning + button)
    if st.session_state.step == "need_captcha":
        st.warning("🛡️ CAPTCHA detectado! Resolva manualmente no navegador aberto.")
        if st.button("✅ CAPTCHA Finalizado", type="primary", use_container_width=True):
            resume_with_signal("captcha_done")

    # Passo: Waiting CAPTCHA (should not show; internal)
    if st.session_state.step == "waiting_captcha":
        st.info("Aguardando confirmação do CAPTCHA...")
        st.rerun()  # Loop until signal

    # Passo: Need 2FA
    if st.session_state.step == "need_2fa":
        st.warning("🔐 2FA detectado! Insira o código no navegador.")
        if st.button("✅ 2FA Finalizado", type="primary", use_container_width=True):
            resume_with_signal("2fa_done")

    # Passo: Need Email Password
    if st.session_state.step == "need_email_pass":
        st.warning("📧 Verificação de email detectada! Digite a senha do seu email.")
        with st.form("email_form"):
            email_pwd = st.text_input("🔑 Senha do Email:", type="password", key="email_pwd")
            col_email1, col_email2 = st.columns([1, 1])
            with col_email1:
                if st.form_submit_button("✅ Confirmar Senha", type="primary", use_container_width=True):
                    if email_pwd:
                        st.session_state.email_password = email_pwd
                        # Send the password back to generator
                        try:
                            yielded = st.session_state.generator.send(email_pwd)
                            st.session_state.logs = st.session_state.generator.gi_frame.f_locals.get('logs', st.session_state.logs)
                            st.session_state.step = "running"
                            st.rerun()
                        except StopIteration as e:
                            st.session_state.result, final_logs = e.value
                            st.session_state.logs = final_logs or st.session_state.logs
                            st.session_state.step = "done"
                            st.session_state.processing = False
                            st.rerun()
                        except Exception as e:
                            error_log = {"message": f"❌ Erro na verificação: {str(e)}", "level": "error"}
                            st.session_state.logs.append(error_log)
                            st.session_state.step = "done"
                            st.session_state.processing = False
                            st.session_state.result = "ERROR"
                            st.rerun()
                    else:
                        st.error("Digite a senha do email.")
            with col_email2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.processing = False
                    st.session_state.step = "done"
                    st.session_state.result = "CANCELLED"
                    st.rerun()

    # Passo: Manual Email Verify
    if st.session_state.step == "manual_email_verify":
        st.warning("📧 Não foi possível automatizar a verificação. Verifique manualmente no email e no navegador.")
        if st.button("✅ Verificação Finalizada", type="primary", use_container_width=True):
            resume_with_signal("manual_verify_done")

    # Passo final: Done
    if st.session_state.step == "done":
        st.session_state.processing = False
        if st.session_state.result == "SUCCESS":
            st.success("✅ Processo concluído com sucesso!")
        else:
            st.error(f"❌ Processo finalizado com status: {st.session_state.result}")
        st.session_state.step = "initial"

# --- 8. Exibe Logs em Tempo Real ---
if st.session_state.logs:
    st.subheader("📋 Logs do Processo")
    for log_entry in st.session_state.logs:
        msg = log_entry.get("message", "Log sem mensagem")
        level = log_entry.get("level", "info")
        
        if "Wrong Email" in msg or "Wrong Login" in msg:
            st.warning(msg)
        elif "Wrong Password" in msg:
            st.error(msg)
        elif level == "success":
            st.success(msg)
        elif level == "error":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)
