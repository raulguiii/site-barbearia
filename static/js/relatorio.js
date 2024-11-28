const servicoData = JSON.parse(document.getElementById('servicoChart').dataset.servicoData);
const servicoLabels = servicoData.map(item => item.servico);
const servicoCounts = servicoData.map(item => item.total);

const servicoChartCtx = document.getElementById('servicoChart').getContext('2d');
new Chart(servicoChartCtx, {
    type: 'pie',
    data: {
        labels: servicoLabels,
        datasets: [{
            label: 'Serviços Mais Realizados',
            data: servicoCounts,
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Serviços Mais Realizados' }
        }
    }
});

const barbeiroData = JSON.parse(document.getElementById('barbeiroChart').dataset.barbeiroData);
const barbeiroLabels = barbeiroData.map(item => item.barbeiro_nome);
const barbeiroCounts = barbeiroData.map(item => item.total);

const barbeiroChartCtx = document.getElementById('barbeiroChart').getContext('2d');
new Chart(barbeiroChartCtx, {
    type: 'pie',
    data: {
        labels: barbeiroLabels,
        datasets: [{
            label: 'Barbeiros Mais Candidatados',
            data: barbeiroCounts,
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'],
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Barbeiros Mais Candidatados' }
        }
    }
});
