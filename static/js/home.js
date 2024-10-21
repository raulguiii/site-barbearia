
document.querySelector('.fa-user').addEventListener('click', function(e) {
    e.preventDefault();
    window.location.href = '/login';
});


// Menu hamburguer
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
    const today = new Date().toISOString().split('T')[0];

    
    const isFullNameValid = (name) => {
        const nameParts = name.split(' ');
        return nameParts.length >= 2 && nameParts.every(part => /^[A-Za-zÀ-ÖØ-öø-ÿ]+$/.test(part));
    };

   
    if (name === "" || phone === "" || date === "" || time === "") {
        showMessage("Por favor, preencha todos os campos.", "red", message);
    } else if (!isFullNameValid(name)) {
        showMessage("Por favor, insira o nome completo (pelo menos nome e sobrenome).", "red", message);
    } else if (phone.length !== 11) {
        showMessage("O número de telefone deve ter 11 dígitos.", "red", message);
    } else if (date < today) {
        showMessage("A data do agendamento deve ser a de hoje ou futura.", "red", message);
    } else {
        showMessage("Agendamento enviado com sucesso!", "green", message);
        sendAgendamento(name, phone, service, date, time, message);
    }
});


function showMessage(text, color, element) {
    element.textContent = text;
    element.style.color = color;
}


function sendAgendamento(name, phone, service, date, time, messageElement) {
    const formData = new URLSearchParams();
    formData.append('name', name);
    formData.append('phone', phone);
    formData.append('service', service);
    formData.append('date', date);
    formData.append('time', time);

    fetch('/agendar', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao realizar o agendamento');
        }
        return response.text();
    })
    .then(data => {
        console.log(data); 
       
        document.querySelector('#schedule-form').reset();
        
    })
    .catch(error => {
        console.error('Erro:', error);
        showMessage("Ocorreu um erro ao enviar o agendamento. Tente novamente.", "red", messageElement);
    });
}
