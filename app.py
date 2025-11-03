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
if 'email_verification_required' not in st.session_state:
    st.session_state.email_verification_required = False
if 'current_email' not in st.session_state:
    st.session_state.current_email = ""
if 'current_password' not in st.session_state:
    st.session_state.current_password = ""
if 'email_password' not in st.session_state:
    st.session_state.email_password = ""

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

    new_password = "deletingsoon123"
    st.info(f"**Nova senha será definida como:** `{new_password}`")

    submitted = st.form_submit_button(
        "🚀 Processar Conta", 
        type="primary", 
        disabled=st.session_state.processing or st.session_state.email_verification_required
    )

# --- 6. Formulário de Verificação de Email COMPACTO ---
if st.session_state.email_verification_required:
    st.markdown("---")
    st.markdown("""
        <div class='email-verification-box'>
            <h3 style='margin: 0 0 8px 0; font-size: 1.1rem;'>🔐 Verificação de Email Necessária</h3>
            <p style='margin: 4px 0; font-size: 0.9rem;'>Digite a senha do seu email para continuar automaticamente:</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("email_verification_form"):
        email_password = st.text_input(
            "📧 Senha do Email:", 
            type="password", 
            placeholder="Senha do seu email",
            key="email_password_input"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            verify_submitted = st.form_submit_button(
                "✅ Continuar Verificação",
                type="primary",
                use_container_width=True
            )
        with col2:
            cancel_verification = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if verify_submitted and email_password:
            st.session_state.email_password = email_password
            st.session_state.processing = True
            st.session_state.email_verification_required = False
            
            with st.spinner("🔄 Continuando verificação..."):
                try:
                    result, returned_logs = process_account(
                        st.session_state.current_email,
                        st.session_state.current_password,
                        new_password,
                        st.session_state.email_password,
                        st.session_state.logs
                    )
                    
                    st.session_state.logs = returned_logs
                    
                    if result == "SUCCESS":
                        st.success("✅ Processo concluído com sucesso!")
                    else:
                        st.error(f"❌ Processo finalizado com status: {result}")
                        
                except Exception as e:
                    error_log = {"message": f"❌ Erro na verificação: {str(e)}", "level": "error"}
                    st.session_state.logs.append(error_log)
                    st.error(f"❌ Falha na verificação: {str(e)}")
                    
                finally:
                    st.session_state.processing = False
                    st.session_state.email_password = ""
                    st.rerun()
        
        if cancel_verification:
            st.session_state.email_verification_required = False
            st.session_state.logs.append({"message": "❌ Verificação de email cancelada", "level": "warning"})
            st.rerun()

# --- 7. Lógica de Processamento Principal ---
if not st.session_state.email_verification_required and submitted:
    if not email or not old_password:
        st.warning("⚠️ Preencha email e senha para continuar.")
    else:
        st.session_state.processing = True
        st.session_state.current_email = email
        st.session_state.current_password = old_password
        st.session_state.logs = []
        
        with st.spinner("🔄 Processando..."):
            try:
                result, returned_logs = process_account(email, old_password, new_password)
                
                if result == "EMAIL_VERIFICATION_REQUIRED":
                    st.session_state.email_verification_required = True
                    st.session_state.logs = returned_logs
                    st.warning("🔐 Verificação de email necessária.")
                elif result == "2FA_REQUIRED":
                    st.session_state.logs = returned_logs
                    st.error("❌ 2FA detectado.")
                elif result == "SUCCESS":
                    st.session_state.logs = returned_logs
                    st.success("✅ Processo concluído com sucesso!")
                else:
                    st.session_state.logs = returned_logs
                    st.error(f"❌ Processo finalizado com status: {result}")
                    
            except Exception as e:
                error_log = {"message": f"❌ Erro geral: {str(e)}", "level": "error"}
                st.session_state.logs.append(error_log)
                st.error(f"❌ Falha no processamento: {str(e)}")
                
            finally:
                if not st.session_state.email_verification_required:
                    st.session_state.processing = False
                st.rerun()

# --- 8. Exibe Logs COMPACTOS ---
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
        else:
            st.info(msg)

# --- 9. Botões de reiniciar e limpar COMPACTOS ---
if not st.session_state.processing and st.session_state.logs:
    col_restart, col_clear = st.columns([1, 1])
    with col_restart:
        if st.button("🔄 Reiniciar Processo", use_container_width=True):
            st.session_state.logs = []
            st.session_state.processing = False
            st.session_state.email_verification_required = False
            st.session_state.email_password = ""
            st.rerun()
    with col_clear:
        if st.button("🗑️ Limpar Tudo", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --- 10. Footer compacto ---
st.markdown("---")
st.markdown(
    '<div class="footer">Discord Account Deleter • Use com responsabilidade</div>',
    unsafe_allow_html=True
)