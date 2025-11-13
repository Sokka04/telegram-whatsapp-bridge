import os
import requests
import time
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WHATSAPP_PHONE = os.getenv('WHATSAPP_PHONE')

def get_telegram_messages():
    """Récupère les nouveaux messages Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            messages = response.json().get('result', [])
            new_messages = []
            
            for msg in messages:
                if 'message' in msg and 'text' in msg['message']:
                    text = msg['message']['text']
                    if 'tiktok.com' in text or 'instagram.com' in text:
                        new_messages.append(text)
            
            return new_messages
        return []
    except Exception as e:
        print(f"Erreur Telegram: {e}")
        return []

def send_whatsapp_message(message):
    """Envoie un message sur WhatsApp"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # Ouvrir WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        # Attendre la connexion (30 secondes pour scanner le QR code)
        print("Scannez le QR code WhatsApp Web dans les 30 secondes...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )
        
        # Ouvrir la conversation
        driver.get(f"https://web.whatsapp.com/send?phone={WHATSAPP_PHONE}&text={message}")
        
        # Attendre que le champ de texte soit prêt
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
        )
        
        # Attendre un peu et envoyer
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "button[data-tab='11']").click()
        
        print(f"Message envoyé à {WHATSAPP_PHONE}")
        time.sleep(5)
        driver.quit()
        return True
        
    except Exception as e:
        print(f"Erreur WhatsApp: {e}")
        return False

def main():
    print("Démarrage du bridge Telegram-WhatsApp...")
    
    # Récupérer les messages Telegram
    messages = get_telegram_messages()
    
    for message in messages:
        print(f"Message reçu: {message}")
        # Envoyer vers WhatsApp
        success = send_whatsapp_message(message)
        if success:
            print("✓ Message transféré avec succès!")
        else:
            print("✗ Erreur lors du transfert")

if __name__ == "__main__":
    main()
