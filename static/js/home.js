function enableEditing(cell) {
    if (!cell.hasAttribute("data-edited")) {
        let originalValue = cell.innerHTML;
        cell.innerHTML = `<input type="text" value="${originalValue}" />`;
        cell.setAttribute("data-edited", "true");
    }
}

function saveEdits() {
    const editedCells = document.querySelectorAll("td[data-edited='true']");
    const updatedData = [];

    editedCells.forEach(cell => {
        const input = cell.querySelector("input");
        const newValue = input.value;
        cell.innerHTML = newValue;
        cell.removeAttribute("data-edited");

        const row = cell.closest("tr");
        const id = row.querySelector("td").innerText;

        updatedData.push({
            id: id,
            column: cell.cellIndex, 
            value: newValue
        });
    });

    fetch("/editar_financeiro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ updatedData })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Dados atualizados:', data);
        alert('Dados atualizados com sucesso!');
    })
    .catch(error => {
        console.error('Erro ao salvar:', error);
        alert('Erro ao salvar os dados!');
    });
}

function addNewRow() {
    const table = document.querySelector(".finance-table tbody");
    const newRow = document.createElement("tr");

    newRow.innerHTML = `
        <td></td>
        <td><input type="text" placeholder="Nome do Funcionário" /></td>
        <td><input type="text" placeholder="Horário de Trabalho" /></td>
        <td><input type="text" placeholder="Salário" /></td>
        <td><input type="text" placeholder="Status" /></td>
        <td><button onclick="saveNewRow(this)">Salvar</button></td>
    `;
    table.appendChild(newRow);
}

function saveNewRow(button) {
    const row = button.closest("tr");
    const inputs = row.querySelectorAll("input");

    const newData = {
        nome_funcionario: inputs[0].value,
        horario_trabalho: inputs[1].value,
        salario: inputs[2].value,
        status_pagamento: inputs[3].value
    };

    fetch("/adicionar_financeiro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(newData)  
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "sucesso") {
            row.querySelector("td").innerText = data.id;  
            inputs.forEach(input => {
                input.disabled = true;  
            });
            button.innerText = "Salvo";
            button.setAttribute("disabled", true); 
        } else {
            alert('Erro ao adicionar a linha: ' + data.message);  
        }
    })
    .catch(error => {
        console.error('Erro ao adicionar:', error);
        alert('Erro ao adicionar a linha!');
    });
}
