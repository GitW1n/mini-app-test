const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 3000 });

let clients = [];

wss.on('connection', (ws) => {
  console.log('Новое подключение');
  clients.push(ws);

  ws.send(JSON.stringify({ message: 'Добро пожаловать! Вы подключены к серверу для получения уведомлений.' }));

  ws.on('message', (message) => {
    console.log('Получено сообщение от клиента:', message);
  });

  ws.on('close', () => {
    console.log('Клиент отключился');
    clients = clients.filter(client => client !== ws);
  });

  ws.on('error', (error) => {
    console.error('Ошибка WebSocket:', error);
  });
});

console.log('Сервер запущен на ws://localhost:3000');
