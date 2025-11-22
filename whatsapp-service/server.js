const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const PORT = process.env.PORT || 3000;
const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://bot:5000/webhook';

let client;
let isReady = false;
let qrCodeData = null;

// Inicializar cliente WhatsApp
function initializeClient() {
    console.log('Inicializando WhatsApp Web.js...');

    client = new Client({
        authStrategy: new LocalAuth({
            dataPath: './wwebjs_auth'
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--single-process',
                '--disable-background-networking',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-sync',
                '--disable-translate',
                '--metrics-recording-only',
                '--mute-audio',
                '--no-first-run',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        }
    });

    // QR Code
    client.on('qr', (qr) => {
        console.log('QR Code recebido! Escaneie com WhatsApp:');
        qrcodeTerminal.generate(qr, { small: true });
        qrCodeData = qr;
    });

    // Cliente pronto
    client.on('ready', () => {
        console.log('✅ WhatsApp conectado com sucesso!');
        isReady = true;
        qrCodeData = null;
    });

    // Autenticação bem-sucedida
    client.on('authenticated', () => {
        console.log('✅ Autenticação bem-sucedida!');
    });

    // Falha na autenticação
    client.on('auth_failure', (msg) => {
        console.error('❌ Falha na autenticação:', msg);
        isReady = false;
    });

    // Desconectado
    client.on('disconnected', (reason) => {
        console.log('⚠️ Cliente desconectado:', reason);
        isReady = false;
    });

    // Receber mensagens
    client.on('message', async (message) => {
        console.log('📨 Mensagem recebida:', message.from, '-', message.body);

        // Preparar payload base
        let payload = {
            from: message.from,
            body: message.body,
            timestamp: message.timestamp,
            hasMedia: message.hasMedia,
            type: message.type
        };

        // Se for áudio (PTT - Push To Talk), baixar e incluir no payload
        if (message.type === 'ptt' || message.type === 'audio') {
            console.log('🎤 Áudio detectado! Baixando...');
            try {
                const media = await message.downloadMedia();
                if (media) {
                    console.log('✅ Áudio baixado com sucesso!', {
                        mimetype: media.mimetype,
                        size: media.data.length
                    });

                    // Adicionar dados do áudio ao payload (base64)
                    payload.audioData = media.data;  // base64
                    payload.audioMimetype = media.mimetype;  // audio/ogg ou audio/mpeg
                    payload.body = '[Áudio recebido]';  // Placeholder
                } else {
                    console.error('❌ Falha ao baixar áudio (retornou null)');
                }
            } catch (error) {
                console.error('❌ Erro ao baixar áudio:', error.message);
            }
        }

        // Se for imagem, baixar e incluir no payload
        if (message.type === 'image' && message.hasMedia) {
            console.log('🖼️ Imagem detectada! Baixando...');
            try {
                const media = await message.downloadMedia();
                if (media) {
                    console.log('✅ Imagem baixada com sucesso!', {
                        mimetype: media.mimetype,
                        size: media.data.length
                    });

                    // Adicionar dados da imagem ao payload (base64)
                    payload.imageData = media.data;  // base64
                    payload.imageMimetype = media.mimetype;  // image/jpeg, image/png, etc
                    payload.body = message.body || '[Imagem recebida]';  // Caption ou placeholder
                } else {
                    console.error('❌ Falha ao baixar imagem (retornou null)');
                }
            } catch (error) {
                console.error('❌ Erro ao baixar imagem:', error.message);
            }
        }

        // Enviar para webhook do bot Python
        try {
            const fetch = (await import('node-fetch')).default;
            await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } catch (error) {
            console.error('Erro ao enviar para webhook:', error.message);
        }
    });

    client.initialize();
}

// Rotas da API

// Página HTML do QR Code
app.get('/', async (req, res) => {
    if (isReady) {
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp - Conectado</title>
                <meta charset="UTF-8">
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                    .status { color: #25D366; font-size: 24px; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>WhatsApp Web.js</h1>
                    <div class="status">✅ Conectado!</div>
                    <p>Seu WhatsApp está conectado e pronto para uso.</p>
                </div>
            </body>
            </html>
        `);
        return;
    }

    if (!qrCodeData) {
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp - Aguardando</title>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="3">
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
                    .loading { color: #666; font-size: 18px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>WhatsApp Web.js</h1>
                    <div class="loading">⏳ Aguardando QR Code...</div>
                    <p>A página será atualizada automaticamente.</p>
                </div>
            </body>
            </html>
        `);
        return;
    }

    try {
        const qrBase64 = await QRCode.toDataURL(qrCodeData, {
            errorCorrectionLevel: 'H',
            type: 'image/png',
            width: 400,
            margin: 2
        });

        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp - Escanear QR Code</title>
                <meta charset="UTF-8">
                <meta http-equiv="refresh" content="30">
                <style>
                    body { font-family: Arial; text-align: center; padding: 20px; background: #f0f0f0; }
                    .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
                    .qr-code { margin: 30px 0; }
                    img { border: 2px solid #25D366; border-radius: 10px; padding: 10px; background: white; }
                    .instructions { color: #666; margin-top: 20px; line-height: 1.6; }
                    .title { color: #25D366; font-size: 28px; margin-bottom: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="title">📱 WhatsApp Web.js</h1>
                    <p><strong>Escaneie o QR Code com seu WhatsApp</strong></p>
                    <div class="qr-code">
                        <img src="${qrBase64}" alt="QR Code WhatsApp" width="400" height="400">
                    </div>
                    <div class="instructions">
                        <p><strong>Como conectar:</strong></p>
                        <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                            <li>Abra o WhatsApp no seu celular</li>
                            <li>Vá em <strong>Configurações > Aparelhos conectados</strong></li>
                            <li>Toque em <strong>Conectar um aparelho</strong></li>
                            <li>Aponte a câmera para este QR code</li>
                        </ol>
                        <p style="margin-top: 20px; font-size: 12px; color: #999;">
                            Página atualiza automaticamente a cada 30 segundos
                        </p>
                    </div>
                </div>
            </body>
            </html>
        `);
    } catch (error) {
        res.status(500).send('Erro ao gerar QR code');
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_ready: isReady,
        has_qr: qrCodeData !== null
    });
});

// Obter QR Code
app.get('/qr', async (req, res) => {
    if (isReady) {
        return res.json({ status: 'connected', message: 'WhatsApp já está conectado' });
    }

    if (!qrCodeData) {
        return res.json({ status: 'waiting', message: 'Aguardando QR Code...' });
    }

    try {
        // Gerar QR code como imagem base64
        const qrBase64 = await QRCode.toDataURL(qrCodeData, {
            errorCorrectionLevel: 'H',
            type: 'image/png',
            width: 400,
            margin: 2
        });

        res.json({
            status: 'qr_available',
            qr: qrCodeData,
            qrImage: qrBase64
        });
    } catch (error) {
        console.error('Erro ao gerar QR code:', error);
        res.status(500).json({
            error: 'Erro ao gerar QR code',
            details: error.message
        });
    }
});

// Enviar mensagem de texto
app.post('/send', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp não está conectado' });
    }

    const { number, message } = req.body;

    if (!number || !message) {
        return res.status(400).json({ error: 'Número e mensagem são obrigatórios' });
    }

    try {
        let chatId;

        // Se já vem com @c.us ou @lid (formato serializado), usar diretamente
        if (number.includes('@c.us') || number.includes('@lid')) {
            chatId = number;
        } else {
            // Caso contrário, verificar se o número está registrado no WhatsApp
            const numberId = await client.getNumberId(number);

            if (!numberId) {
                return res.status(404).json({
                    error: 'Número não encontrado',
                    details: 'Este número não está registrado no WhatsApp'
                });
            }

            chatId = numberId._serialized;
        }

        // Enviar mensagem usando o ID verificado
        await client.sendMessage(chatId, message);

        res.json({
            status: 'success',
            message: 'Mensagem enviada com sucesso',
            to: number
        });
    } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        res.status(500).json({
            error: 'Erro ao enviar mensagem',
            details: error.message
        });
    }
});

// Status da conexão
app.get('/status', async (req, res) => {
    if (!isReady) {
        return res.json({
            connected: false,
            message: 'WhatsApp não conectado'
        });
    }

    try {
        const state = await client.getState();
        res.json({
            connected: true,
            state: state,
            ready: isReady
        });
    } catch (error) {
        res.status(500).json({
            error: 'Erro ao obter status',
            details: error.message
        });
    }
});

// Obter informações do número conectado
app.get('/info', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp não está conectado' });
    }

    try {
        const info = client.info;
        res.json({
            wid: info.wid._serialized,
            pushname: info.pushname,
            platform: info.platform
        });
    } catch (error) {
        res.status(500).json({
            error: 'Erro ao obter informações',
            details: error.message
        });
    }
});

// Logout
app.post('/logout', async (req, res) => {
    if (!client) {
        return res.status(400).json({ error: 'Cliente não inicializado' });
    }

    try {
        await client.logout();
        isReady = false;
        qrCodeData = null;
        res.json({ status: 'success', message: 'Logout realizado' });
    } catch (error) {
        res.status(500).json({
            error: 'Erro ao fazer logout',
            details: error.message
        });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 WhatsApp Service rodando na porta ${PORT}`);
    initializeClient();
});
