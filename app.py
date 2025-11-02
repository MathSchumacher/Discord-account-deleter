import streamlit as st
from delete_discord_account import process_account  # Importe sua função principal (ajuste se o nome do arquivo for diferente)

# --- 1. Configurações da página ---
st.set_page_config(
    page_title="Discord Account Deleter",
    page_icon="img/discord.svg",  # Mantém como favicon também
    layout="wide"
)

# --- 2. CSS customizado ---
# CSS customizado para botões mais modernos (arredondados, sombras, hover)
st.markdown("""
    <style>
    .stButton > button {
        background-color: #5865F2;  /* Azul do Discord */
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
    /* Estilos de log */
    .success-log { color: green; }
    .error-log { color: red; }
    .warning-log { color: orange; }
    </style>
""", unsafe_allow_html=True)

# --- 3. Título e Separador ---
col_icon, col_title = st.columns([1, 6])
with col_icon:
    # Verifique o caminho da sua imagem; se não existir, use um emoji: st.markdown("🗑️", unsafe_allow_html=True)
    st.image("img/discord.svg", width=50)  
with col_title:
    st.markdown("<h1 style='margin: 0;'>Discord Account Deleter</h1>", unsafe_allow_html=True)

st.markdown("---")  # Linha separadora

# --- 4. Inicializa estado da sessão ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

# --- 5. Formulário (st.form) para Enter to Submit ---
# O uso de st.form() permite que, ao apertar Enter no último campo (Senha), 
# o st.form_submit_button seja acionado.
with st.form("account_submission_form"):
    col1, col2 = st.columns([3, 1])  # Layout para email e senha lado a lado
    
    with col1:
        email = st.text_input("📧 Email:", placeholder="exemplo@discord.com", key="email_input")
    with col2:
        old_password = st.text_input("🔑 Senha Atual:", type="password", placeholder="Sua senha atual", key="password_input")

    new_password = "deletingsoon123"  # Fixa, mas pode tornar editável se quiser
    st.info(f"**Nova senha será definida como:** `{new_password}`")

    # Botão de submissão DO FORMULÁRIO. 'submitted' será True se o botão for clicado OU Enter for pressionado.
    submitted = st.form_submit_button(
        "🚀 Processar Conta", 
        type="primary", 
        help="Inicia o processo de mudança de senha e exclusão", 
        disabled=st.session_state.processing
    )

# --- 6. Lógica de Processamento (Acionada pelo 'submitted') ---
if submitted:
    if not email or not old_password:
        st.warning("⚠️ Preencha email e senha para continuar.")
    else:
        st.session_state.processing = True
        st.session_state.logs = []  # Limpa logs antigos
        
        with st.spinner("🔄 Processando... Aguarde enquanto fazemos login e alteramos a conta."):
            try:
                # Chama a função e captura logs retornados
                # Certifique-se de que a função 'process_account' existe e está importada corretamente.
                returned_logs = process_account(email, old_password, new_password)
                
                # Converte para lista de dicts se necessário
                if isinstance(returned_logs, list):
                    st.session_state.logs = returned_logs
                else:
                    st.session_state.logs = [{"message": str(returned_logs), "level": "info"}]
                st.success("✅ Concluído! Verifique os logs abaixo para detalhes.")
                
            except Exception as e:
                error_log = {"message": f"❌ Erro geral: {str(e)}", "level": "error"}
                st.session_state.logs.append(error_log)
                st.error(f"❌ Falha no processamento: {str(e)}")
                
            finally:
                st.session_state.processing = False
                st.rerun()  # Recarrega para mostrar logs novos

# --- 7. Exibe Logs ---
if st.session_state.logs:
    st.subheader("📋 Logs do Processo")
    for log_entry in st.session_state.logs:
        msg = log_entry.get("message", "Log sem mensagem")
        level = log_entry.get("level", "info")
        
        # Lógica de feedback e limpeza de campos
        if "Wrong Email" in msg or "Wrong Login" in msg:
            st.warning(msg)
            st.session_state.email_input = ""
            st.session_state.password_input = ""
        elif "Wrong Password" in msg:
            st.error(msg)
            st.session_state.password_input = ""
        elif level == "success":
            st.success(msg)
        elif level == "error":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)
        else:
            st.info(msg)

# --- 8. Botões de reiniciar e limpar ---
if not st.session_state.processing and st.session_state.logs:
    col_restart, col_clear = st.columns(2)
    with col_restart:
        if st.button("🔄 Reiniciar Processo"):
            st.session_state.logs = []
            st.session_state.processing = False
            st.rerun()
    with col_clear:
        # Se 'clear' for clicado, limpa o estado da sessão completamente
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.clear()
            st.rerun()