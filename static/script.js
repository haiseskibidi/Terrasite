let currentStep = 1;
const totalSteps = 4;
let formData = {
    services: [],
    description: '',
    budget: '',
    name: '',
    contact_method: '',
    phone: '',
    telegram: '',
    phone_number: '',
    call_time: '',
    email: ''
};

function nextStep() {
    if (validateCurrentStep()) {
        if (currentStep < totalSteps) {
            hideStep(currentStep);
            currentStep++;
            showStep(currentStep);
            updateFormData();
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        hideStep(currentStep);
        currentStep--;
        showStep(currentStep);
    }
}

function hideStep(step) {
    const stepElement = document.querySelector(`[data-step="${step}"]`);
    if (stepElement) {
        stepElement.classList.remove('active');
    }
}

function showStep(step) {
    const stepElement = document.querySelector(`[data-step="${step}"]`);
    if (stepElement) {
        stepElement.classList.add('active');
    }
}

function validateCurrentStep() {
    switch (currentStep) {
        case 1:
            return validateServices();
        case 2:
            return validateDescription();
        case 3:
            return validateBudget();
        case 4:
            return validateContacts();
        default:
            return true;
    }
}

function validateServices() {
    const checkedServices = document.querySelectorAll('input[name="services"]:checked');
    if (checkedServices.length === 0) {
        showError('Выберите как минимум одну услугу');
        return false;
    }
    return true;
}

function validateDescription() {
    const description = document.querySelector('textarea[name="description"]').value.trim();
    if (description.length === 0) {
        showError('Описание проекта обязательно для заполнения');
        return false;
    }
    
    if (description.length < 50) {
        showError('Описание должно содержать минимум 50 символов для лучшего понимания проекта');
        return false;
    }
    
    if (description.length > 2000) {
        showError('Описание слишком длинное (максимум 2000 символов)');
        return false;
    }
    
    if (/^(.)\1{20,}$/.test(description) || description.split(' ').length < 8) {
        showError('Пожалуйста, опишите проект более подробно (минимум 8 слов)');
        return false;
    }
    
    return true;
}

function validateBudget() {
    const checkedBudget = document.querySelector('input[name="budget"]:checked');
    if (!checkedBudget) {
        showError('Выберите предполагаемый бюджет');
        return false;
    }
    return true;
}

function validateContacts() {
    const name = document.querySelector('input[name="name"]').value.trim();
    const selectedMethod = document.querySelector('input[name="contact_method"]:checked');
    
    if (name.length === 0) {
        showError('Имя обязательно для заполнения');
        return false;
    }
    
    if (name.length < 2) {
        showError('Имя должно содержать минимум 2 символа');
        return false;
    }
    
    if (name.length > 50) {
        showError('Имя слишком длинное (максимум 50 символов)');
        return false;
    }
    
    if (!/^[а-яёА-ЯЁa-zA-Z\s\-]+$/.test(name)) {
        showError('Имя может содержать только буквы, пробелы и дефисы');
        return false;
    }
    
    if (!selectedMethod) {
        showError('Выберите способ связи');
        return false;
    }
    
    switch(selectedMethod.value) {
        case 'whatsapp':
            const whatsapp = document.querySelector('input[name="phone"]').value.trim();
            if (whatsapp.length === 0) {
                showError('Введите номер WhatsApp');
                return false;
            }
            if (!/^(\+7|8)[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/.test(whatsapp.replace(/[\s\-()]/g, ''))) {
                showError('Введите корректный номер телефона (например: +7 999 123-45-67)');
                return false;
            }
            break;
            
        case 'telegram':
            const telegram = document.querySelector('input[name="telegram"]').value.trim();
            if (telegram.length === 0) {
                showError('Введите Telegram username');
                return false;
            }
            if (!/^@[a-zA-Z0-9_]{5,32}$/.test(telegram)) {
                showError('Введите корректный Telegram username (например: @username)');
                return false;
            }
            break;
            
        case 'phone':
            const phoneNumber = document.querySelector('input[name="phone_number"]').value.trim();
            const callTime = document.querySelector('input[name="call_time"]').value.trim();
            if (phoneNumber.length === 0) {
                showError('Введите номер телефона');
                return false;
            }
            if (!/^(\+7|8)[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/.test(phoneNumber.replace(/[\s\-()]/g, ''))) {
                showError('Введите корректный номер телефона (например: +7 999 123-45-67)');
                return false;
            }
            if (callTime.length === 0) {
                showError('Укажите удобное время для звонка');
                return false;
            }
            if (callTime.length < 5) {
                showError('Укажите время более подробно (например: 10:00-18:00 или утром)');
                return false;
            }
            break;
            
        case 'email':
            const email = document.querySelector('input[name="email"]').value.trim();
            if (email.length === 0) {
                showError('Введите email адрес');
                return false;
            }
            if (!isValidEmail(email)) {
                showError('Введите корректный email адрес');
                return false;
            }
            break;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showError(message) {
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.style.cssText = `
        background-color: #fee2e2;
        color: #dc2626;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 14px;
        border: 1px solid #fecaca;
    `;
    errorElement.textContent = message;
    
    const currentStepElement = document.querySelector('.form-step.active');
    const navigationElement = currentStepElement.querySelector('.step-navigation, .next-button');
    if (navigationElement) {
        currentStepElement.insertBefore(errorElement, navigationElement);
    } else {
        currentStepElement.appendChild(errorElement);
    }
    
    setTimeout(() => {
        if (errorElement.parentNode) {
            errorElement.remove();
        }
    }, 5000);
}

function updateFormData() {
    const checkedServices = document.querySelectorAll('input[name="services"]:checked');
    formData.services = Array.from(checkedServices).map(input => input.value);
    
    const description = document.querySelector('textarea[name="description"]');
    if (description) {
        formData.description = description.value.trim();
    }
    
    const checkedBudget = document.querySelector('input[name="budget"]:checked');
    if (checkedBudget) {
        formData.budget = checkedBudget.value;
    }
    
    const name = document.querySelector('input[name="name"]');
    const contactMethod = document.querySelector('input[name="contact_method"]:checked');
    
    if (name) formData.name = name.value.trim();
    
    if (contactMethod) {
        formData.contact_method = contactMethod.value;
        
        switch(contactMethod.value) {
            case 'whatsapp':
                const whatsapp = document.querySelector('input[name="phone"]');
                if (whatsapp) formData.phone = whatsapp.value.trim();
                break;
                
            case 'telegram':
                const telegram = document.querySelector('input[name="telegram"]');
                if (telegram) formData.telegram = telegram.value.trim();
                break;
                
            case 'phone':
                const phoneNumber = document.querySelector('input[name="phone_number"]');
                const callTime = document.querySelector('input[name="call_time"]');
                if (phoneNumber) formData.phone_number = phoneNumber.value.trim();
                if (callTime) formData.call_time = callTime.value.trim();
                break;
                
            case 'email':
                const email = document.querySelector('input[name="email"]');
                if (email) formData.email = email.value.trim();
                break;
        }
    }
}

let isSubmitting = false;

async function submitForm() {
    if (isSubmitting) {
        showError('Заявка уже отправляется, подождите...');
        return;
    }
    
    updateFormData();
    
    const submitButton = document.querySelector('.submit-button');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Отправляется...';
    isSubmitting = true;
    
    try {
        const payload = { ...formData };

        if (payload.contact_method !== 'email') delete payload.email;
        if (payload.contact_method !== 'whatsapp') delete payload.phone;
        if (payload.contact_method !== 'telegram') delete payload.telegram;
        if (payload.contact_method !== 'phone') {
            delete payload.phone_number;
            delete payload.call_time;
        }

        Object.keys(payload).forEach((key) => {
            const value = payload[key];
            if (value === '' || (Array.isArray(value) && value.length === 0)) {
                delete payload[key];
            }
        });

        const response = await fetch('/submit-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showSuccessNotification();
            
            setTimeout(() => {
                formData = {
                    services: [],
                    description: '',
                    budget: '',
                    name: '',
                    contact_method: '',
                    phone: '',
                    telegram: '',
                    phone_number: '',
                    call_time: '',
                    email: ''
                };
                resetFormFields();
            }, 1000);
        } else {
            let errorMessage = 'Ошибка при отправке формы';
            try {
                const errorData = await response.json();
                if (errorData && errorData.error) {
                    errorMessage = errorData.error;
                }
            } catch (e) {
            }
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError(error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        isSubmitting = false;
    }
}

function resetFormFields() {
    document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], textarea').forEach(input => {
        input.value = '';
    });
    
    document.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(input => {
        input.checked = false;
    });
    
    document.querySelectorAll('#whatsapp-field, #telegram-field, #phone-number-field, #call-time-field, #email-field').forEach(field => {
        field.style.display = 'none';
        field.required = false;
    });
    
    updateCharCount();
    
    currentStep = 1;
    document.querySelectorAll('.form-step').forEach(step => step.classList.remove('active'));
    document.querySelector('[data-step="1"]').classList.add('active');
}

function updateDepthEffect() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = Math.min(scrollTop / docHeight, 1);
    
    const vignetteStart = 30 - (scrollPercent * 20);
    const vignetteMidOpacity = 0.05 + (scrollPercent * 0.15);
    const vignetteEndOpacity = 0.15 + (scrollPercent * 0.35);
    
    document.body.style.setProperty('--vignette-start', `${vignetteStart}%`);
    document.body.style.setProperty('--vignette-mid-opacity', vignetteMidOpacity);
    document.body.style.setProperty('--vignette-end-opacity', vignetteEndOpacity);
}

const debouncedDepthUpdate = debounce(updateDepthEffect, 16);

function updateCharCount() {
    const textarea = document.querySelector('textarea[name="description"]');
    const counter = document.getElementById('char-count');
    const counterDiv = document.querySelector('.char-counter');
    
    if (textarea && counter) {
        const currentLength = textarea.value.length;
        counter.textContent = currentLength;
        
        counterDiv.classList.remove('warning', 'success');
        if (currentLength < 50) {
            counterDiv.classList.add('warning');
        } else if (currentLength >= 50) {
            counterDiv.classList.add('success');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateCurrentStep()) {
                submitForm();
            }
        });
    }
    
    updateCharCount();
    
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', function() {
            serviceCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            
            if (targetId === 'top') {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                return;
            }
            
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    window.addEventListener('scroll', function() {
        debouncedDepthUpdate();
    });
    
    updateDepthEffect();
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function animateOnScroll() {
    const elements = document.querySelectorAll('.service-card, .benefit');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

function updateContactField() {
    const selectedMethod = document.querySelector('input[name="contact_method"]:checked');
    const whatsappWrapper = document.getElementById('whatsapp-wrapper');
    const telegramWrapper = document.getElementById('telegram-wrapper');
    const phoneWrapper = document.getElementById('phone-wrapper');
    const timeWrapper = document.getElementById('time-wrapper');
    const emailWrapper = document.getElementById('email-wrapper');
    
    const whatsappField = document.getElementById('whatsapp-field');
    const telegramField = document.getElementById('telegram-field');
    const phoneNumberField = document.getElementById('phone-number-field');
    const callTimeField = document.getElementById('call-time-field');
    const emailField = document.getElementById('email-field');
    
    if (!selectedMethod) return;
    
    [whatsappWrapper, telegramWrapper, phoneWrapper, timeWrapper, emailWrapper].forEach(wrapper => {
        wrapper.style.display = 'none';
    });
    [whatsappField, telegramField, phoneNumberField, callTimeField, emailField].forEach(field => {
        field.required = false;
    });
    
    switch(selectedMethod.value) {
        case 'whatsapp':
            whatsappWrapper.style.display = 'block';
            whatsappField.required = true;
            break;
        case 'telegram':
            telegramWrapper.style.display = 'block';
            telegramField.required = true;
            break;
        case 'phone':
            phoneWrapper.style.display = 'block';
            timeWrapper.style.display = 'block';
            phoneNumberField.required = true;
            callTimeField.required = true;
            break;
        case 'email':
            emailWrapper.style.display = 'block';
            emailField.required = true;
            break;
    }
}

function showSuccessNotification() {
    const notification = document.getElementById('successNotification');
    notification.classList.add('show');
    
    setTimeout(() => {
        hideSuccessNotification();
    }, 5000);
}

function hideSuccessNotification() {
    const notification = document.getElementById('successNotification');
    notification.classList.remove('show');
}

document.addEventListener('click', function(e) {
    const notification = document.getElementById('successNotification');
    if (notification && notification.classList.contains('show')) {
        if (!notification.contains(e.target)) {
            hideSuccessNotification();
        }
    }
});

document.addEventListener('DOMContentLoaded', animateOnScroll);
