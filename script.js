// Переменные состояния формы
let currentStep = 1;
const totalSteps = 4;
let formData = {
    services: [],
    description: '',
    budget: '',
    name: '',
    email: ''
};

// Функции навигации по шагам
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

// Валидация шагов
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
    if (description.length < 10) {
        showError('Описание должно содержать минимум 10 символов');
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
    const email = document.querySelector('input[name="email"]').value.trim();
    
    if (name.length === 0) {
        showError('Имя обязательно для заполнения');
        return false;
    }
    
    if (email.length === 0) {
        showError('Email обязателен для заполнения');
        return false;
    }
    
    if (!isValidEmail(email)) {
        showError('Введите корректный email адрес');
        return false;
    }
    
    return true;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Функция показа ошибок
function showError(message) {
    // Удаляем предыдущие ошибки
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Создаем новое сообщение об ошибке
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
    
    // Вставляем перед кнопками навигации
    const currentStepElement = document.querySelector('.form-step.active');
    const navigationElement = currentStepElement.querySelector('.step-navigation, .next-button');
    if (navigationElement) {
        currentStepElement.insertBefore(errorElement, navigationElement);
    } else {
        currentStepElement.appendChild(errorElement);
    }
    
    // Удаляем ошибку через 5 секунд
    setTimeout(() => {
        if (errorElement.parentNode) {
            errorElement.remove();
        }
    }, 5000);
}

// Обновление данных формы
function updateFormData() {
    // Услуги
    const checkedServices = document.querySelectorAll('input[name="services"]:checked');
    formData.services = Array.from(checkedServices).map(input => input.value);
    
    // Описание
    const description = document.querySelector('textarea[name="description"]');
    if (description) {
        formData.description = description.value.trim();
    }
    
    // Бюджет
    const checkedBudget = document.querySelector('input[name="budget"]:checked');
    if (checkedBudget) {
        formData.budget = checkedBudget.value;
    }
    
    // Контакты
    const name = document.querySelector('input[name="name"]');
    const email = document.querySelector('input[name="email"]');
    if (name) formData.name = name.value.trim();
    if (email) formData.email = email.value.trim();
}

// Отправка формы
async function submitForm() {
    updateFormData();
    
    try {
        const response = await fetch('/submit-form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showStep('success');
            // Сброс формы
            formData = {
                services: [],
                description: '',
                budget: '',
                name: '',
                email: ''
            };
        } else {
            throw new Error('Ошибка при отправке формы');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Произошла ошибка при отправке формы. Попробуйте еще раз.');
    }
}

// Обработчики событий
document.addEventListener('DOMContentLoaded', function() {
    // Обработка отправки формы
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (validateCurrentStep()) {
                submitForm();
            }
        });
    }
    
    // Обработка кликов по карточкам услуг в главной секции
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', function() {
            // Убираем активный класс у всех карточек
            serviceCards.forEach(c => c.classList.remove('active'));
            // Добавляем активный класс к выбранной
            this.classList.add('active');
        });
    });
    
    // Плавная прокрутка для якорных ссылок
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
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
    
    // Обработка скролла для фиксированной шапки
    let lastScrollTop = 0;
    const header = document.querySelector('.header');
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Скролл вниз - скрываем шапку
            header.style.transform = 'translateY(-100%)';
        } else {
            // Скролл вверх - показываем шапку
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Добавляем transition для плавного скрытия/показа шапки
    header.style.transition = 'transform 0.3s ease-in-out';
});

// Дебаунс функция для оптимизации обработчиков
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

// Функция для анимации появления элементов при скролле
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

// Запускаем анимацию после загрузки DOM
document.addEventListener('DOMContentLoaded', animateOnScroll);
