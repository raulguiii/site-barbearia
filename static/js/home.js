
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


const navLinkFade = () => {
    document.querySelectorAll('.nav-links li').forEach((link, index) => {
        link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`;
    });
};


window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    header.classList.toggle('sticky', window.scrollY > 0);
});


document.querySelector('#contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.querySelector('#name').value.trim();
    const email = document.querySelector('#email').value.trim();
    const message = document.querySelector('#message').value.trim();
    const formMessage = document.querySelector('.form-message');

    if (!name || !email || !message) {
        formMessage.textContent = 'Por favor, preencha todos os campos.';
        formMessage.style.color = 'red';
        return;
    }

    if (!validateEmail(email)) {
        formMessage.textContent = 'Por favor, insira um email válido.';
        formMessage.style.color = 'red';
        return;
    }

    formMessage.textContent = 'Mensagem enviada com sucesso!';
    formMessage.style.color = 'green';

    // Talvez de para adicionar outra tecnologia e linkar com BD
});

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

