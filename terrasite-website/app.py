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
    'smtp_password': 'lncsiaezbmfjaltp',  # Пароль приложения
    'from_email': 'team.terrasite@yandex.ru',
    'to_email': 'team.terrasite@yandex.ru'
}

LEADS_FILE = 'leads.json'

def save_lead(lead_data):
    try:
        # Читаем существующие заявки
        if os.path.exists(LEADS_FILE):
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        else:
            leads = []
        
        # Добавляем новую заявку
        lead_data['timestamp'] = datetime.now().isoformat()
        lead_data['id'] = len(leads) + 1
        leads.append(lead_data)
        
        # Сохраняем обратно в файл
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
        
        subject = f"Новая заявка с сайта Terrasite от {lead_data.get('name', '')}"
        
        body = f"""
Новая заявка с сайта Terrasite!

Контактная информация:
Имя: {lead_data.get('name', '')}
Email: {lead_data.get('email', '')}

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
        
        required_fields = ['name', 'email', 'services', 'description', 'budget']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Поле {field} обязательно для заполнения'
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
        
        logging.info(f"Новая заявка обработана: {data['name']} ({data['email']})")
        
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
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
