import streamlit as st
from delete_discord_account import process_account

# --- 1. Configurações da página ---
st.set_page_config(
    page_title="Discord Account Deleter",
    page_icon="img/discord.svg",
    layout="wide"
)

# --- 2. CSS customizado ---
st.markdown("""
    <style>
    .stButton > button {
        background-color: #5865F2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4752C4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    .email-verification-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Título e Separador ---
col_icon, col_title = st.columns([1, 6])
with col_icon:
    st.image("img/discord.svg", width=50)  
with col_title:
    st.markdown("<h1 style='margin: 0;'>Discord Account Deleter</h1>", unsafe_allow_html=True)

st.markdown("---")

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

# --- 5. Formulário Principal ---
with st.form("account_submission_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email = st.text_input("📧 Email:", placeholder="exemplo@discord.com", key="email_input")
    with col2:
        old_password = st.text_input("🔑 Senha Atual:", type="password", placeholder="Sua senha atual", key="password_input")

    new_password = "deletingsoon123"
    st.info(f"**Nova senha será definida como:** `{new_password}`")

    submitted = st.form_submit_button(
        "🚀 Processar Conta", 
        type="primary", 
        help="Inicia o processo de mudança de senha e exclusão", 
        disabled=st.session_state.processing or st.session_state.email_verification_required
    )

# --- 6. Formulário de Verificação de Email (aparece apenas quando necessário) ---
if st.session_state.email_verification_required:
    st.markdown("---")
    st.markdown("""
        <div class='email-verification-box'>
            <h3>🔐 Verificação de Email Necessária</h3>
            <p>O Discord detectou um acesso de localidade diferente e requer verificação por email.</p>
            <p>Digite a senha do seu email para continuar automaticamente:</p>
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
                type="primary"
            )
        with col2:
            cancel_verification = st.form_submit_button("❌ Cancelar")
        
        if verify_submitted and email_password:
            st.session_state.email_password = email_password
            st.session_state.processing = True
            st.session_state.email_verification_required = False
            
            with st.spinner("🔄 Continuando verificação de email..."):
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
            st.session_state.logs.append({"message": "❌ Verificação de email cancelada pelo usuário", "level": "warning"})
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
        
        with st.spinner("🔄 Processando... Aguarde enquanto fazemos login e alteramos a conta."):
            try:
                result, returned_logs = process_account(email, old_password, new_password)
                
                # Verifica se precisa de verificação de email
                if result == "EMAIL_VERIFICATION_REQUIRED":
                    st.session_state.email_verification_required = True
                    st.session_state.logs = returned_logs
                    st.warning("🔐 Verificação de email necessária. Preencha o formulário abaixo.")
                elif result == "2FA_REQUIRED":
                    st.session_state.logs = returned_logs
                    st.error("❌ 2FA detectado. Esta funcionalidade ainda não está implementada.")
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

# --- 8. Exibe Logs ---
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

# --- 9. Botões de reiniciar e limpar ---
if not st.session_state.processing and st.session_state.logs:
    col_restart, col_clear = st.columns(2)
    with col_restart:
        if st.button("🔄 Reiniciar Processo"):
            st.session_state.logs = []
            st.session_state.processing = False
            st.session_state.email_verification_required = False
            st.session_state.email_password = ""
            st.rerun()
    with col_clear:
        if st.button("🗑️ Limpar Tudo"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()