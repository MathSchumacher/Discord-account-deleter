# delete_discord_account.py
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import shutil
import webbrowser

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
                self.imap_server = "imap.gmail.com"
        else:
            self.imap_server = imap_server
        self.mail = None
    
    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_address, self.email_password)
            return True
        except Exception as e:
            print(f"Erro ao conectar ao email: {e}")
            domain = self.email_address.lower().split('@')[-1]
            if 'gmail.com' in domain:
                print("Dica: Para Gmail, use 'App Password' se 2FA estiver ativado")
            elif 'outlook.com' in domain or 'hotmail.com' in domain:
                print("Dica: Para Outlook, gere 'App Password' em Configurações")
            return False
    
    def disconnect(self):
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
    
    def search_discord_verification_email(self, timeout=120):
        if not self.mail:
            if not self.connect():
                return None
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.mail.select("inbox")
                status, messages = self.mail.search(None, '(FROM "noreply@discord.com" SUBJECT "verif")')
                
                if status == "OK" and messages[0]:
                    latest_email_id = messages[0].split()[-1]
                    status, msg_data = self.mail.fetch(latest_email_id, "(RFC822)")
                    if status == "OK":
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        verification_url = self.extract_verification_url(msg)
                        if verification_url:
                            return verification_url
                
                time.sleep(5)
                
            except Exception as e:
                print(f"Erro ao buscar email: {e}")
                time.sleep(5)
        
        return None
    
    def extract_verification_url(self, msg):
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

def setup_driver():
    """Configura o driver do Selenium para ambiente local ou Streamlit Cloud"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1920,1080")
    
    # Detecta se está no Streamlit Cloud
    if os.path.exists('/usr/bin/chromium'):
        # Streamlit Cloud
        options.binary_location = '/usr/bin/chromium'
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # Ambiente local - tenta usar Brave, senão Chrome padrão
        brave_path = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
        if os.path.exists(brave_path):
            options.binary_location = brave_path
        
        driver = webdriver.Chrome(options=options)
    
    return driver

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
    try:
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
                
        current_url = driver.current_url
        if 'login' in current_url.lower():
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

def get_email_web_url(email):
    domain = email.lower().split('@')[-1]
    if 'gmail.com' in domain:
        return 'https://mail.google.com/mail/u/0/#inbox'
    elif 'outlook.com' in domain or 'hotmail.com' in domain:
        return 'https://outlook.live.com/mail/inbox'
    elif 'yahoo.com' in domain:
        return 'https://mail.yahoo.com'
    else:
        return None

def process_account(email, old_password, new_password, email_password=None, logs=None):
    if logs is None:
        logs = []

    def log_message(msg, level="info"):
        print(msg)
        logs.append({"message": msg, "level": level})
        yield {"type": "log", "message": msg, "level": level}

    gen = log_message("Iniciando o processo de login automático...", "info")
    next(gen)

    token = None
    verification_required = False
    current_email_password = email_password

    driver = setup_driver()

    try:
        gen = log_message("Abrindo navegador e tentando login automático. Aguarde...", "info")
        next(gen)

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

        verification_checked = False
        captcha_resolved = False
        start_time = time.time()
        login_success = False
        
        while time.time() - start_time < 600:
            current_url = driver.current_url.lower()

            if 'channels' in current_url or 'app' in current_url:
                login_success = True
                break

            if detect_captcha(driver) and not captcha_resolved:
                gen = log_message("CAPTCHA detectado! No modo headless, isso pode falhar. Tentando aguardar resolução automática...", "warning")
                next(gen)
                yield {"type": "need_captcha"}
                user_signal = yield {"type": "waiting_captcha"}
                if user_signal == "captcha_done":
                    captcha_resolved = True
                    gen = log_message("CAPTCHA resolvido! Prosseguindo...", "success")
                    next(gen)
                else:
                    gen = log_message("CAPTCHA não resolvido. Cancelando.", "error")
                    next(gen)
                    driver.quit()
                    return "CAPTCHA_FAILED", logs
                continue

            try:
                if driver.find_elements(By.NAME, "code"):
                    gen = log_message("2FA detectado. Isso requer interação manual.", "warning")
                    next(gen)
                    yield {"type": "need_2fa"}
                    user_signal = yield {"type": "waiting_2fa"}
                    if user_signal != "2fa_done":
                        gen = log_message("2FA não completado. Cancelando.", "error")
                        next(gen)
                        driver.quit()
                        return "2FA_REQUIRED", logs
            except:
                pass

            if not verification_checked:
                time.sleep(5)
                verification_required = detect_email_verification(driver)
                verification_checked = True

            if verification_required:
                if current_email_password is None:
                    gen = log_message("Verificação de email detectada! Aguardando senha do email.", "warning")
                    next(gen)
                    yield {"type": "need_email_pass"}
                    current_email_password = yield {"type": "waiting_email_pass"}
                    if current_email_password is None:
                        gen = log_message("Senha do email não fornecida. Processo não pode continuar automaticamente.", "error")
                        next(gen)
                        driver.quit()
                        return "EMAIL_PASSWORD_REQUIRED", logs
                else:
                    gen = log_message("Iniciando verificação automática de email...", "info")
                    next(gen)
                    verifier = EmailVerifier(email, current_email_password)
                    verification_url = verifier.search_discord_verification_email(timeout=60)
                    if verification_url:
                        gen = log_message("URL de verificação encontrada! Processando...", "success")
                        next(gen)
                        driver.execute_script(f"window.open('{verification_url}', '_blank');")
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(5)
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        time.sleep(3)
                        gen = log_message("Verificação de email concluída!", "success")
                        next(gen)
                        verifier.disconnect()
                    else:
                        gen = log_message("Falha na verificação automática. Use 'App Password' para o email.", "error")
                        next(gen)
                        driver.quit()
                        return "EMAIL_VERIFICATION_FAILED", logs

            time.sleep(2)

        if not login_success:
            current_url = driver.current_url
            page_source = driver.page_source.lower()

            error_type = None
            if 'login' in current_url.lower():
                if any(phrase in page_source for phrase in ['couldn\'t find an account', 'não encontramos uma conta']):
                    error_type = "Wrong Email"
                    gen = log_message("⚠️ Email não encontrado.", "error")
                    next(gen)
                elif any(phrase in page_source for phrase in ['incorrect password', 'senha incorreta']):
                    error_type = "Wrong Password"
                    gen = log_message("⚠️ Senha incorreta.", "error")
                    next(gen)
                else:
                    error_type = "Wrong Login"
                    gen = log_message("⚠️ Erro no login.", "error")
                    next(gen)

            if error_type:
                driver.quit()
                return f"{error_type}", logs

            gen = log_message("Falha no login (timeout).", "error")
            next(gen)
            driver.quit()
            return "LOGIN_TIMEOUT", logs

        start_time = time.time()
        while time.time() - start_time < 60:
            if 'channels' in driver.current_url.lower() or 'app' in driver.current_url.lower():
                login_success = True
                break
            time.sleep(2)

        if login_success:
            token = get_discord_token(driver)
            if not token:
                gen = log_message("Não foi possível obter o token.", "warning")
                next(gen)
                token = None
            else:
                gen = log_message("Token obtido com sucesso!", "success")
                next(gen)
        else:
            token = None

        driver.quit()
        time.sleep(2)

    except Exception as e:
        gen = log_message(f"Exceção geral: {e}", "error")
        next(gen)
        if 'driver' in locals():
            driver.quit()
        return "ERROR", logs

    if token:
        changer = Change()
        change_success, new_token = changer.Changer(token, old_password, email, new_password, logs)

        if change_success and new_token:
            gen = log_message("Mudança de senha bem-sucedida. Prosseguindo para exclusão...", "success")
            next(gen)
            deleter_success = changer.Deleter(new_token, new_password, logs)
            if deleter_success:
                gen = log_message("Tudo concluído!", "success")
                next(gen)
                return "SUCCESS", logs
            else:
                gen = log_message("Falha na exclusão.", "error")
                next(gen)
                return "DELETE_FAILED", logs
        else:
            gen = log_message("Falha na mudança de senha. Tentando exclusão com senha antiga...", "warning")
            next(gen)
            deleter_success = changer.Deleter(token, old_password, logs)
            if deleter_success:
                gen = log_message("Exclusão concluída com senha antiga.", "success")
                next(gen)
                return "SUCCESS", logs
            else:
                gen = log_message("Falha na exclusão.", "error")
                next(gen)
                return "DELETE_FAILED", logs
    else:
        gen = log_message("Falha ao obter token. Processo cancelado.", "error")
        next(gen)
        return "TOKEN_FAILED", logs