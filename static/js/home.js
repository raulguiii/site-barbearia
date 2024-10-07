document.querySelectorAll('nav ul li a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

const burger = document.querySelector('.burger');
const nav = document.querySelector('.nav-links');
const navLinks = document.querySelectorAll('.nav-links li');

burger.addEventListener('click', () => {
    nav.classList.toggle('nav-active');

    navLinks.forEach((link, index) => {
        if (link.style.animation) {
            link.style.animation = '';
        } else {
            link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`;
        }
    });

    burger.classList.toggle('toggle');
});

window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    header.classList.toggle('sticky', window.scrollY > 0);
});

document.querySelector('#schedule-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.querySelector('#name').value.trim();
    const phone = document.querySelector('#phone').value.trim();
    const service = document.querySelector('#service').value;
    const date = document.querySelector('#date').value;
    const time = document.querySelector('#time').value;
    const message = document.querySelector('.form-message');

    // Obter a data de hoje
    const today = new Date().toISOString().split('T')[0];

    // Função para validar o nome completo (mínimo duas palavras)
    const isFullNameValid = (name) => {
        const nameParts = name.split(' ');
        return nameParts.length >= 2 && nameParts.every(part => /^[A-Za-zÀ-ÖØ-öø-ÿ]+$/.test(part));
    };

    // Validação
    if (name === "" || phone === "" || date === "" || time === "") {
        message.textContent = "Por favor, preencha todos os campos.";
        message.style.color = "red";
    } else if (!isFullNameValid(name)) {
        message.textContent = "Por favor, insira o nome completo (pelo menos nome e sobrenome).";
        message.style.color = "red";
    } else if (phone.length !== 11) {
        message.textContent = "O número de telefone deve ter 11 dígitos.";
        message.style.color = "red";
    } else if (date < today) {
        message.textContent = "A data do agendamento deve ser a de hoje ou futura.";
        message.style.color = "red";
    } else {
        message.textContent = "Agendamento enviado com sucesso!";
        message.style.color = "green";
        
        // Aqui você pode adicionar a lógica para enviar os dados ao backend
    }
});


