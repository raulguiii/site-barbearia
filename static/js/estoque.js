
document.querySelectorAll('.form-editar').forEach(form => {
    form.addEventListener('submit', (e) => {
        const confirmacao = confirm("Tem certeza que deseja editar este produto?");
        if (!confirmacao) {
            e.preventDefault();
        }
    });
});


document.querySelectorAll('.btn-excluir').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const confirmacao = confirm("Tem certeza que deseja excluir este produto?");
        if (!confirmacao) {
            e.preventDefault();
        }
    });
});


document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', () => {
        input.style.borderColor = '#16a085';
        input.style.boxShadow = '0 0 10px rgba(22, 160, 133, 0.5)';
        input.style.transition = '0.3s ease';
    });

    input.addEventListener('blur', () => {
        input.style.borderColor = '#ddd';
        input.style.boxShadow = 'none';
    });
});


const adicionarButton = document.querySelector('.form-produto button');
adicionarButton.addEventListener('click', (e) => {
    e.preventDefault();

    
    adicionarButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';

    setTimeout(() => {
        document.querySelector('.form-produto').submit(); 

        // Exibir mensagem de sucesso após o envio
        const successMessage = document.createElement('div');
        successMessage.classList.add('success-message');
        successMessage.innerHTML = 'Produto adicionado com sucesso!';
        document.body.appendChild(successMessage);
        
        
        setTimeout(() => {
            successMessage.remove();
        }, 5000);  
    }, 1000);
});


const tableRows = document.querySelectorAll('table tr');
tableRows.forEach(row => {
    row.addEventListener('mouseenter', () => {
        row.style.backgroundColor = '#f0f0f0';
        row.style.transition = 'background-color 0.3s ease';
    });

    row.addEventListener('mouseleave', () => {
        row.style.backgroundColor = '';
    });
});


document.querySelectorAll('form').forEach(form => {
    form.addEventListener('mouseover', () => {
        const btnExcluir = form.querySelector('.btn-excluir');
        if (btnExcluir) {
            btnExcluir.style.opacity = '1';
            btnExcluir.style.transition = 'opacity 0.3s ease';
        }
    });

    form.addEventListener('mouseout', () => {
        const btnExcluir = form.querySelector('.btn-excluir');
        if (btnExcluir) {
            btnExcluir.style.opacity = '0.7';
        }
    });
});
