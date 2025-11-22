FROM nginx:alpine

# Copiar configuração customizada
COPY nginx.conf /etc/nginx/nginx.conf

# Criar página inicial simples
RUN echo '<!DOCTYPE html>\n\
<html lang="pt-BR">\n\
<head>\n\
    <meta charset="UTF-8">\n\
    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n\
    <title>SPDrop - Bot WhatsApp</title>\n\
    <style>\n\
        * { margin: 0; padding: 0; box-sizing: border-box; }\n\
        body {\n\
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;\n\
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n\
            min-height: 100vh;\n\
            display: flex;\n\
            align-items: center;\n\
            justify-content: center;\n\
            padding: 20px;\n\
        }\n\
        .container {\n\
            background: white;\n\
            border-radius: 20px;\n\
            padding: 60px 40px;\n\
            max-width: 500px;\n\
            width: 100%;\n\
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);\n\
            text-align: center;\n\
        }\n\
        h1 {\n\
            color: #333;\n\
            font-size: 2.5em;\n\
            margin-bottom: 20px;\n\
        }\n\
        .emoji { font-size: 4em; margin-bottom: 20px; }\n\
        .status {\n\
            display: inline-block;\n\
            background: #25D366;\n\
            color: white;\n\
            padding: 10px 20px;\n\
            border-radius: 50px;\n\
            font-weight: bold;\n\
            margin: 20px 0;\n\
        }\n\
        .links {\n\
            margin-top: 40px;\n\
            display: flex;\n\
            flex-direction: column;\n\
            gap: 15px;\n\
        }\n\
        .link {\n\
            display: block;\n\
            background: #667eea;\n\
            color: white;\n\
            text-decoration: none;\n\
            padding: 15px 30px;\n\
            border-radius: 10px;\n\
            font-weight: 500;\n\
            transition: all 0.3s;\n\
        }\n\
        .link:hover {\n\
            background: #764ba2;\n\
            transform: translateY(-2px);\n\
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);\n\
        }\n\
        .link.secondary {\n\
            background: #f0f0f0;\n\
            color: #333;\n\
        }\n\
        .link.secondary:hover {\n\
            background: #e0e0e0;\n\
        }\n\
        .info {\n\
            margin-top: 30px;\n\
            padding: 20px;\n\
            background: #f8f9fa;\n\
            border-radius: 10px;\n\
            font-size: 0.9em;\n\
            color: #666;\n\
        }\n\
    </style>\n\
</head>\n\
<body>\n\
    <div class="container">\n\
        <div class="emoji">🤖</div>\n\
        <h1>SPDrop</h1>\n\
        <p style="color: #666; font-size: 1.1em;">Bot WhatsApp Inteligente</p>\n\
        <div class="status">✅ Sistema Online</div>\n\
        \n\
        <div class="links">\n\
            <a href="/whatsapp/" class="link">📱 Conectar WhatsApp (QR Code)</a>\n\
            <a href="/api/docs" class="link">📚 Documentação da API</a>\n\
            <a href="/health" class="link secondary">💚 Health Check</a>\n\
        </div>\n\
        \n\
        <div class="info">\n\
            <strong>🔒 Arquitetura Segura</strong><br>\n\
            Todos os serviços estão isolados em rede interna.<br>\n\
            Apenas este gateway público está acessível.\n\
        </div>\n\
    </div>\n\
</body>\n\
</html>' > /usr/share/nginx/html/index.html

# Expor porta 80
EXPOSE 80

# Comando padrão do nginx
CMD ["nginx", "-g", "daemon off;"]
