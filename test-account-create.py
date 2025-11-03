import os
import random
import string
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DiscordAccountCreator:
    def __init__(self):
        self.accounts_file = "test_accounts.json"
        self.load_existing_accounts()
        self.setup_valid_domains()
    
    def setup_valid_domains(self):
        """Domínios de email que o Discord aceita"""
        self.valid_domains = [
            "gmail.com", "outlook.com", "yahoo.com", "hotmail.com",
            "icloud.com", "protonmail.com", "aol.com", "zoho.com"
        ]
    
    def load_existing_accounts(self):
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = json.load(f)
        else:
            self.accounts = []
    
    def save_accounts(self):
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
    
    def generate_plausible_email(self):
        """Gera emails que parecem reais"""
        first_names = ["alex", "mike", "chris", "jordan", "taylor", "casey", "jamie"]
        last_names = ["smith", "johnson", "williams", "brown", "jones", "miller"]
        
        patterns = [
            lambda: f"{random.choice(first_names)}.{random.choice(last_names)}{random.randint(100, 999)}",
            lambda: f"{random.choice(first_names)}_{random.choice(last_names)}{random.randint(100, 999)}",
        ]
        
        username = random.choice(patterns)()
        domain = random.choice(self.valid_domains)
        return f"{username}@{domain}"
    
    def generate_strong_password(self):
        """Gera senha forte"""
        upper = random.choices(string.ascii_uppercase, k=2)
        lower = random.choices(string.ascii_lowercase, k=6)
        digits = random.choices(string.digits, k=3)
        special = random.choices("!@#$%&*", k=1)
        
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)
    
    def generate_username(self):
        """Gera username plausível"""
        adjectives = ["Cool", "Happy", "Swift", "Brave", "Clever", "Mighty"]
        nouns = ["Wolf", "Dragon", "Tiger", "Eagle", "Phoenix", "Lion"]
        numbers = ''.join(random.choices(string.digits, k=4))
        
        return f"{random.choice(adjectives)}{random.choice(nouns)}{numbers}"
    
    def setup_browser_with_captcha_support(self):
        """Configura navegador com suporte para captcha"""
        options = Options()
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-US")
        
        return options
    
    def wait_for_captcha_and_manual_solve(self, driver):
        """Aguarda e permite resolver captcha manualmente"""
        print("\n🎯 AGUARDANDO CAPTCHA...")
        print("="*50)
        print("1. Resolva o captcha na página")
        print("2. O script aguardará até 5 MINUTOS")
        print("3. Após resolver, o processo continuará automaticamente")
        print("="*50)
        
        start_time = time.time()
        captcha_timeout = 300  # 5 minutos
        
        try:
            while time.time() - start_time < captcha_timeout:
                current_url = driver.current_url.lower()
                page_source = driver.page_source.lower()
                
                if "captcha" not in page_source and "challenge" not in page_source:
                    print("✅ Captcha resolvido! Continuando...")
                    return True
                
                if any(url in current_url for url in ["/app", "/channels", "verify"]):
                    print("✅ Redirecionado após captcha!")
                    return True
                
                time.sleep(5)
                
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0:
                    print(f"⏰ Aguardando há {elapsed} segundos...")
            
            print("❌ Tempo esgotado para captcha.")
            return False
            
        except Exception as e:
            print(f"⚠️  Erro durante captcha: {e}")
            return False
    
    def fill_registration_form(self, driver, email, username, password):
        """Preenche formulário de registro COMPLETAMENTE automático"""
        try:
            print("📝 Preenchendo formulário automaticamente...")
            
            # Campo email
            email_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "email"))
            )
            email_field.clear()
            for char in email:
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            time.sleep(1)
            
            # Campo username
            username_field = driver.find_element(By.NAME, "username")
            username_field.clear()
            for char in username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            time.sleep(1)
            
            # Campo senha
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            for char in password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.1))
            time.sleep(1)
            
            # Data de nascimento - AGORA AUTOMÁTICO
            print("🎂 Preenchendo data de nascimento automaticamente...")
            self.fill_birth_date_auto(driver)
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao preencher formulário: {e}")
            return False
    
    def fill_birth_date_auto(self, driver):
        """Preenche data de nascimento automaticamente - 05/02/1997"""
        try:
            # Mês - Fevereiro (2)
            print("📅 Selecionando mês: Fevereiro")
            month_dropdown = driver.find_element(By.NAME, "month")
            month_dropdown.click()
            time.sleep(1)
            
            # Seleciona Fevereiro
            feb_option = driver.find_element(By.XPATH, "//div[contains(text(), 'Feb') or contains(text(), 'Fevereiro')]")
            feb_option.click()
            time.sleep(1)
            
            # Dia - 5
            print("📅 Inserindo dia: 5")
            day_field = driver.find_element(By.NAME, "day")
            day_field.clear()
            day_field.send_keys("5")
            time.sleep(1)
            
            # Ano - 1997
            print("📅 Inserindo ano: 1997")
            year_field = driver.find_element(By.NAME, "year")
            year_field.clear()
            year_field.send_keys("1997")
            time.sleep(1)
            
            print("✅ Data de nascimento preenchida: 05/02/1997")
            
        except Exception as e:
            print(f"⚠️  Erro ao preencher data: {e}")
    
    def submit_form_and_handle_captcha(self, driver):
        """Submete formulário e lida com captcha"""
        try:
            print("✅ Submetendo formulário...")
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            time.sleep(5)
            
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            if any(indicator in page_source for indicator in ["captcha", "challenge", "robot", "verify"]):
                print("🎯 CAPTCHA DETECTADO!")
                return self.wait_for_captcha_and_manual_solve(driver)
            else:
                print("✅ Sem captcha detectado, continuando...")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao submeter: {e}")
            return False
    
    def handle_phone_verification(self, driver):
        """Lida com verificação de telefone - GUIA PRÁTICO"""
        print("\n📱 VERIFICAÇÃO DE TELEFONE REQUERIDA!")
        print("="*60)
        print("🎯 SIGA ESTES PASSOS:")
        print("1. Abra em outra aba: https://receive-sms.com/")
        print("2. Escolha um número americano (+1)")
        print("3. VOLTE AQUI e cole o número no Discord")
        print("4. Clique em 'Send' para receber SMS")
        print("5. VOLTE para https://receive-sms.com/")
        print("6. Espere o SMS chegar e copie o código")
        print("7. VOLTE AQUI e cole o código no Discord")
        print("="*60)
        
        input("👆 Pressione Enter quando estiver pronto para começar...")
        
        try:
            # Aguarda campo de telefone
            print("⏳ Aguardando campo de telefone aparecer...")
            phone_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "phone"))
            )
            
            print("✅ Campo de telefone detectado!")
            print("💡 COLE o número do Receive-SMS.com no campo acima...")
            
            # Aguarda usuário inserir número manualmente
            input("👆 Pressione Enter após COLAR o número de telefone...")
            
            # Encontra e clica no botão de enviar SMS
            print("📨 Procurando botão 'Send'...")
            send_sms_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send') or contains(text(), 'Enviar') or contains(text(), 'SMS')]"))
            )
            send_sms_btn.click()
            
            print("✅ SMS enviado! Aguardando código...")
            print("💡 VERIFIQUE https://receive-sms.com/ para ver o SMS...")
            time.sleep(10)
            
            # Aguarda campo de código
            print("⏳ Aguardando campo de código...")
            code_field = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.NAME, "code"))
            )
            
            print("✅ Campo de código detectado!")
            print("💡 COLE o código do SMS no campo acima...")
            input("👆 Pressione Enter após COLAR o código do SMS...")
            
            # Aguarda verificação ser processada
            print("⏳ Processando verificação...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na verificação de telefone: {e}")
            return False
    
    def create_single_account(self):
        """Cria uma única conta com suporte completo"""
        print("🚀 Iniciando criação de conta...")
        
        driver = webdriver.Chrome(options=self.setup_browser_with_captcha_support())
        
        try:
            # Acessa página de registro
            print("🌐 Acessando Discord...")
            driver.get("https://discord.com/register")
            
            # Aguarda carregamento inicial
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            time.sleep(3)
            
            # Gera dados
            email = self.generate_plausible_email()
            username = self.generate_username()
            password = self.generate_strong_password()
            
            print(f"📧 Email: {email}")
            print(f"👤 Username: {username}")
            print(f"🔑 Senha: {password}")
            
            # Preenche formulário COMPLETAMENTE automático
            if not self.fill_registration_form(driver, email, username, password):
                return "FORM_ERROR"
            
            # Submete e lida com captcha
            if not self.submit_form_and_handle_captcha(driver):
                return "CAPTCHA_TIMEOUT"
            
            # Aguarda resultado
            print("⏳ Aguardando resultado...")
            time.sleep(10)
            
            # Verifica se precisa de telefone
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            if "phone" in page_source:
                print("📱 Discord está pedindo verificação por telefone...")
                if self.handle_phone_verification(driver):
                    print("✅ Verificação de telefone concluída!")
                    time.sleep(10)
            
            # Verifica resultado final
            result = self.check_final_result(driver, email, username, password)
            return result
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return "ERROR"
        finally:
            print("\n⚠️  O navegador permanecerá aberto para você ver o resultado.")
            print("💡 Feche manualmente quando terminar.")
            input("👆 Pressione Enter para voltar ao menu...")
            driver.quit()
    
    def check_final_result(self, driver, email, username, password):
        """Verifica o resultado final"""
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        
        if any(indicator in page_source for indicator in ["verify", "check your email", "verification"]):
            print("🎯 Verificação de EMAIL solicitada!")
            self.save_account(email, username, password, True)
            return "EMAIL_VERIFICATION_REQUIRED"
        
        elif any(url in current_url for url in ["/app", "/channels", "@me"]):
            print("✅ CONTA CRIADA COM SUCESSO!")
            self.save_account(email, username, password, False)
            return "SUCCESS"
        
        elif "phone" in page_source:
            print("📱 Ainda precisa de verificação de telefone")
            return "PHONE_VERIFICATION_NEEDED"
        
        else:
            print("⚠️  Resultado indeterminado")
            return "UNKNOWN"
    
    def save_account(self, email, username, password, verification_required):
        """Salva conta"""
        account_data = {
            "email": email,
            "username": username,
            "password": password,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "verification_required": verification_required,
            "verified": not verification_required
        }
        
        self.accounts.append(account_data)
        self.save_accounts()
        
        print("\n" + "="*50)
        print("📋 CONTA SALVA!")
        print(f"📧 Email: {email}")
        print(f"👤 Username: {username}")
        print(f"🔑 Senha: {password}")
        print(f"🔐 Status: {'VERIFICAÇÃO REQUERIDA' if verification_required else 'CONTA PRONTA'}")
        print("="*50)
    
    def list_accounts(self):
        """Lista contas criadas"""
        if not self.accounts:
            print("📭 Nenhuma conta criada ainda.")
            return
        
        print(f"\n📋 CONTAS CRIADAS ({len(self.accounts)}):")
        print("="*60)
        
        for i, account in enumerate(self.accounts, 1):
            status = "🔐 VERIFICAÇÃO REQUERIDA" if account.get("verification_required", False) else "✅ PRONTA"
            print(f"{i}. {account['email']}")
            print(f"   👤: {account['username']}")
            print(f"   🔑: {account['password']}")
            print(f"   📅: {account['created_at']} | {status}")
            print("-" * 40)
    
    def show_menu(self):
        """Menu principal"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🎯 DISCORD ACCOUNT CREATOR - VERSÃO CORRIGIDA")
            print("="*50)
            print("1. 🚀 Criar conta (data automática + guia telefone)")
            print("2. 📋 Listar contas")
            print("3. 🧪 Testar no app principal")
            print("4. ❌ Sair")
            print("="*50)
            
            choice = input("\n🔢 Escolha: ").strip()
            
            if choice == "1":
                self.create_account_flow()
            elif choice == "2":
                self.list_accounts()
                input("\n📝 Enter para continuar...")
            elif choice == "3":
                self.test_with_main_app()
                input("\n📝 Enter para continuar...")
            elif choice == "4":
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida")
                time.sleep(1)
    
    def create_account_flow(self):
        """Fluxo de criação de conta"""
        print("\n🚀 INICIANDO CRIAÇÃO DE CONTA...")
        print("💡 Funcionalidades:")
        print("   ✅ Preenchimento AUTOMÁTICO da data (05/02/1997)")
        print("   ✅ Tempo para resolver CAPTCHA")
        print("   ✅ Guia passo a passo para TELEFONE")
        print("   ✅ Navegador não fecha sozinho")
        
        result = self.create_single_account()
        print(f"\n🎯 Resultado final: {result}")
    
    def test_with_main_app(self):
        """Testa conta no app principal"""
        self.list_accounts()
        
        if not self.accounts:
            return
        
        try:
            choice = int(input("\n🔢 Número da conta para testar (0=cancelar): "))
            if choice == 0:
                return
            
            if 1 <= choice <= len(self.accounts):
                account = self.accounts[choice - 1]
                print(f"\n🎯 Use no app principal:")
                print(f"📧 Email: {account['email']}")
                print(f"🔑 Senha: {account['password']}")
            else:
                print("❌ Número inválido.")
        
        except ValueError:
            print("❌ Digite um número válido.")

def main():
    print("🔧 Inicializando Discord Account Creator...")
    creator = DiscordAccountCreator()
    creator.show_menu()

if __name__ == "__main__":
    main()