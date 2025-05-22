const messages = [
    "Por favor, aguarde o download finalizar...",
    "Quase lá, continue aguardando...",
    "Estamos preparando seu arquivo...",
    "Quase pronto, mais um instante..."
];

let currentIndex = 0;
let messageInterval;

function showMessage() {
    const msgDiv = document.getElementById('message');
    msgDiv.textContent = messages[currentIndex];
    currentIndex = (currentIndex + 1) % messages.length;
}

document.getElementById('download-form').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('download-link').innerHTML = '';
    showMessage();
    clearInterval(messageInterval);
    messageInterval = setInterval(showMessage, 30000); // muda a cada 30 segundos

    fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `url=${encodeURIComponent(document.getElementById('url').value)}&format=${encodeURIComponent(document.getElementById('format').value)}`
    })
    .then(res => res.json())
    .then(data => {
        if (!data.task_id) {
            alert('Erro ao iniciar o download.');
            clearInterval(messageInterval);
            document.getElementById('message').textContent = '';
            return;
        }
        checkProgress(data.task_id);
    })
    .catch(() => {
        alert('Erro na requisição.');
        clearInterval(messageInterval);
        document.getElementById('message').textContent = '';
    });
});

function checkProgress(task_id) {
    fetch(`/progress/${task_id}`)
    .then(res => res.json())
    .then(data => {
        if (data.status === 'done') {
            clearInterval(messageInterval);
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = 'Download concluído!';

            const downloadDiv = document.getElementById('download-link');
            downloadDiv.innerHTML = '';

            const link = document.createElement('a');
            link.textContent = "Clique aqui para baixar seu arquivo";
            link.href = `/downloaded/${encodeURIComponent(data.filename)}`;
            link.download = data.filename;

            downloadDiv.appendChild(link);
        } else if (data.status === 'error') {
            clearInterval(messageInterval);
            document.getElementById('message').textContent = `Erro: ${data.message}`;
        } else {
            setTimeout(() => checkProgress(task_id), 2000);
        }
    })
    .catch(() => {
        clearInterval(messageInterval);
        document.getElementById('message').textContent = 'Erro ao verificar o progresso.';
    });
}
