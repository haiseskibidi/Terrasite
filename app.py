from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

app = Flask(__name__, static_folder='.')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

EMAIL_CONFIG = {
    'smtp_host': 'smtp.yandex.ru',
    'smtp_port': 465,
    'smtp_user': 'team.terrasite@yandex.ru',
    'smtp_password': 'lncsiaezbmfjaltp',
    'from_email': 'team.terrasite@yandex.ru',
    'to_email': 'team.terrasite@yandex.ru'
}

LEADS_FILE = 'leads.json'

def is_duplicate_submission(data, contact_method):
    try:
        if not os.path.exists(LEADS_FILE):
            return False
            
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        contact_value = ""
        if contact_method == 'whatsapp':
            contact_value = data.get('phone', '')
        elif contact_method == 'telegram':
            contact_value = data.get('telegram', '')
        elif contact_method == 'phone':
            contact_value = data.get('phone_number', '')
        elif contact_method == 'email':
            contact_value = data.get('email', '')
        
        if not contact_value:
            return False
            
        current_time = datetime.now()
        for lead in leads:
            try:
                lead_time = datetime.fromisoformat(lead.get('timestamp', ''))
                time_diff = (current_time - lead_time).total_seconds()
                
                if time_diff < 300:
                    lead_contact_method = lead.get('contact_method', '')
                    if lead_contact_method == contact_method:
                        lead_contact_value = ""
                        if contact_method == 'whatsapp':
                            lead_contact_value = lead.get('phone', '')
                        elif contact_method == 'telegram':
                            lead_contact_value = lead.get('telegram', '')
                        elif contact_method == 'phone':
                            lead_contact_value = lead.get('phone_number', '')
                        elif contact_method == 'email':
                            lead_contact_value = lead.get('email', '')
                        
                        if lead_contact_value.lower().strip() == contact_value.lower().strip():
                            return True
            except (ValueError, TypeError):
                continue
                
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки дубликатов: {e}")
        return False

def save_lead(lead_data):
    try:
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        else:
            leads = []
        
        lead_data['timestamp'] = datetime.now().isoformat()
        lead_data['id'] = len(leads) + 1
        leads.append(lead_data)
        
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Заявка #{lead_data['id']} сохранена успешно")
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения заявки: {e}")
        return False

def send_notification_email(lead_data):
    try:
        services_text = ", ".join(lead_data.get('services', []))
        budget_map = {
            '30-50k': '30-50 тыс',
            '50-150k': '50-150 тыс',
            '150-300k': '150-300 тыс',
            '300-500k': '300-500 тыс',
            '500k+': '500+ тыс'
        }
        budget_text = budget_map.get(lead_data.get('budget', ''), lead_data.get('budget', ''))
        
        contact_method = lead_data.get('contact_method', '')
        
        if contact_method == 'whatsapp':
            contact_value = lead_data.get('phone', '')
        elif contact_method == 'telegram':
            contact_value = lead_data.get('telegram', '')
        elif contact_method == 'phone':
            phone_number = lead_data.get('phone_number', '')
            call_time = lead_data.get('call_time', '')
            contact_value = f"{phone_number}, время: {call_time}"
        elif contact_method == 'email':
            contact_value = lead_data.get('email', '')
        else:
            contact_value = ''
        
        contact_method_text = {
            'whatsapp': 'WhatsApp',
            'telegram': 'Telegram', 
            'phone': 'Звонок',
            'email': 'Email'
        }.get(contact_method, contact_method)
        
        subject = f"Новая заявка с сайта Terrasite от {lead_data.get('name', '')}"
        
        body = f"""
Новая заявка с сайта Terrasite!

Контактная информация:
Имя: {lead_data.get('name', '')}
Способ связи: {contact_method_text}
Контакт: {contact_value}

Детали проекта:
Услуги: {services_text}
Бюджет: {budget_text}

Описание проекта:
{lead_data.get('description', '')}

Время подачи заявки: {datetime.now().strftime('%d.%m.%Y %H:%M')}

---
Отправлено автоматически с сайта Terrasite
        """.strip()
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = EMAIL_CONFIG['to_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_password'])
            server.send_message(msg)
        
        logging.info(f"Уведомление о заявке #{lead_data.get('id', 'N/A')} отправлено")
        return True
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления: {e}")
        return False

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        logging.info(f"Получены данные формы: {data}")
        
        required_fields = ['name', 'services', 'description', 'budget', 'contact_method']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Поле {field} обязательно для заполнения'
                }), 400
        
        contact_method = data.get('contact_method')
        if contact_method == 'whatsapp':
            if not data.get('phone'):
                return jsonify({
                    'success': False,
                    'error': 'Введите номер WhatsApp'
                }), 400
        elif contact_method == 'telegram':
            if not data.get('telegram'):
                return jsonify({
                    'success': False,
                    'error': 'Введите Telegram username'
                }), 400
        elif contact_method == 'phone':
            if not data.get('phone_number') or not data.get('call_time'):
                return jsonify({
                    'success': False,
                    'error': 'Введите номер телефона и время для звонка'
                }), 400
        elif contact_method == 'email':
            if not data.get('email'):
                return jsonify({
                    'success': False,
                    'error': 'Введите email адрес'
                }), 400
        
        if is_duplicate_submission(data, contact_method):
            return jsonify({
                'success': False,
                'error': 'Заявка с такими контактными данными уже была отправлена недавно'
            }), 400
        
        if not isinstance(data['services'], list) or len(data['services']) == 0:
            return jsonify({
                'success': False,
                'error': 'Выберите как минимум одну услугу'
            }), 400
        
        if len(data['description'].strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Описание должно содержать минимум 10 символов'
            }), 400
        
        if not save_lead(data):
            return jsonify({
                'success': False,
                'error': 'Ошибка сохранения заявки'
            }), 500
        
        send_notification_email(data)
        
        contact_info = ""
        if contact_method == 'whatsapp':
            contact_info = f"WhatsApp: {data.get('phone', '')}"
        elif contact_method == 'telegram':
            contact_info = f"Telegram: {data.get('telegram', '')}"
        elif contact_method == 'phone':
            contact_info = f"Звонок: {data.get('phone_number', '')} в {data.get('call_time', '')}"
        elif contact_method == 'email':
            contact_info = f"Email: {data.get('email', '')}"
        
        logging.info(f"Новая заявка обработана: {data['name']} ({contact_info})")
        
        return jsonify({
            'success': True,
            'message': 'Заявка успешно отправлена'
        })
        
    except Exception as e:
        logging.error(f"Ошибка обработки заявки: {e}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@app.route('/admin/leads')
def get_leads():
    try:
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
            return jsonify(leads)
        else:
            return jsonify([])
    except Exception as e:
        logging.error(f"Ошибка получения заявок: {e}")
        return jsonify({'error': 'Ошибка получения данных'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    if not os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
