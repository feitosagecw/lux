// Função para animar os números nas métricas
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const currentValue = Math.floor(progress * (end - start) + start);
        element.textContent = currentValue.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Função para adicionar efeito de hover nas tabelas
function addTableHoverEffect() {
    const tables = document.querySelectorAll('.dataframe');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.style.backgroundColor = 'rgba(241, 245, 249, 0.5)';
                row.style.transition = 'all 0.3s ease';
            });
            row.addEventListener('mouseleave', () => {
                row.style.backgroundColor = '';
            });
        });
    });
}

// Função para melhorar a visualização dos gráficos
function enhanceCharts() {
    const charts = document.querySelectorAll('.js-plotly-plot');
    charts.forEach(chart => {
        chart.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        chart.style.borderRadius = '16px';
        chart.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        chart.addEventListener('mouseenter', () => {
            chart.style.transform = 'scale(1.02)';
            chart.style.boxShadow = '0 8px 12px rgba(0,0,0,0.15)';
        });
        
        chart.addEventListener('mouseleave', () => {
            chart.style.transform = 'scale(1)';
            chart.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        });
    });
}

// Função para melhorar os botões
function enhanceButtons() {
    const buttons = document.querySelectorAll('.stButton > button');
    buttons.forEach(button => {
        button.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 6px 8px rgba(59, 130, 246, 0.3)';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 4px 6px rgba(59, 130, 246, 0.2)';
        });
        
        // Adiciona efeito de ripple
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            button.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Função para melhorar os inputs
function enhanceInputs() {
    const inputs = document.querySelectorAll('.stTextInput > div > div > input');
    inputs.forEach(input => {
        input.style.transition = 'all 0.3s ease';
        
        input.addEventListener('focus', () => {
            input.style.borderColor = '#3b82f6';
            input.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.2)';
            input.style.transform = 'translateY(-1px)';
        });
        
        input.addEventListener('blur', () => {
            input.style.borderColor = '#e2e8f0';
            input.style.boxShadow = 'none';
            input.style.transform = 'translateY(0)';
        });
    });
}

// Função para adicionar loading state nos botões
function addLoadingState() {
    const buttons = document.querySelectorAll('.stButton > button');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const originalText = button.textContent;
            button.innerHTML = '<span class="loading-spinner"></span> Carregando...';
            button.disabled = true;
            
            setTimeout(() => {
                button.textContent = originalText;
                button.disabled = false;
            }, 2000);
        });
    });
}

// Função para melhorar a barra de progresso
function enhanceProgressBar() {
    const progressBar = document.querySelector('.stProgress > div > div');
    if (progressBar) {
        progressBar.style.transition = 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        progressBar.style.background = 'linear-gradient(90deg, #3b82f6, #60a5fa)';
    }
}

// Função para adicionar scroll suave
function addSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Função para melhorar a visualização das métricas
function enhanceMetrics() {
    const metrics = document.querySelectorAll('.stMetric');
    metrics.forEach(metric => {
        metric.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        metric.addEventListener('mouseenter', () => {
            metric.style.transform = 'scale(1.05) translateY(-4px)';
            metric.style.boxShadow = '0 8px 12px rgba(0,0,0,0.1)';
        });
        
        metric.addEventListener('mouseleave', () => {
            metric.style.transform = 'scale(1) translateY(0)';
            metric.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
        });
    });
}

// Função para adicionar animações de entrada
function addEntranceAnimations() {
    const elements = document.querySelectorAll('.stMetric, .dataframe, .js-plotly-plot');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Função para melhorar a visualização das mensagens
function enhanceMessages() {
    const messages = document.querySelectorAll('.st-success, .st-error, .st-warning');
    messages.forEach(message => {
        message.style.transition = 'all 0.3s ease';
        message.style.transform = 'translateX(-20px)';
        message.style.opacity = '0';
        
        setTimeout(() => {
            message.style.transform = 'translateX(0)';
            message.style.opacity = '1';
        }, 100);
    });
}

// Função principal que inicializa todas as melhorias
function initializeEnhancements() {
    addTableHoverEffect();
    enhanceCharts();
    enhanceButtons();
    enhanceInputs();
    addLoadingState();
    enhanceProgressBar();
    addSmoothScroll();
    enhanceMetrics();
    addEntranceAnimations();
    enhanceMessages();
}

// Executa as melhorias quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', initializeEnhancements);

// Reexecuta as melhorias quando o Streamlit atualizar o conteúdo
document.addEventListener('streamlit:componentReady', initializeEnhancements); 