# SPDrop Admin Dashboard - Frontend

Dashboard administrativo React para gerenciar o bot SPDrop.

## 🚀 Iniciar

### Desenvolvimento

```bash
npm install
npm run dev
```

Acessar: **http://localhost:3001**

### Build para Produção

```bash
npm run build
npm run preview
```

## 📁 Estrutura

```
src/
├── components/       # Componentes reutilizáveis
│   ├── Layout.jsx    # Layout principal com sidebar
│   └── ProtectedRoute.jsx  # Proteção de rotas
├── pages/            # Páginas da aplicação
│   ├── Login.jsx     # Página de login
│   ├── Dashboard.jsx # Dashboard com métricas
│   ├── Conversations.jsx  # Histórico de conversas
│   ├── Trials.jsx    # Gestão de testes grátis
│   └── QRCode.jsx    # Gestão QR Code WhatsApp
├── contexts/         # Contextos React
│   └── AuthContext.jsx  # Contexto de autenticação
├── services/         # Serviços de API
│   └── api.js        # Cliente Axios configurado
├── App.jsx           # Componente raiz
└── main.jsx          # Entry point
```

## 🎨 Tecnologias

- **React 18** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **React Router** - Roteamento
- **Axios** - Cliente HTTP
- **Lucide React** - Ícones
- **date-fns** - Manipulação de datas

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação:

1. Login retorna um token JWT
2. Token é salvo no localStorage
3. Todas as requisições incluem o token no header
4. Token expira em 8 horas

### Credenciais Padrão

- **Username**: admin
- **Password**: Admin@123456

## 📊 Páginas

### Dashboard (/)
- Estatísticas gerais do sistema
- Métricas do dia atual
- Lista de clientes recentes
- Atualização automática a cada 30s

### Conversas (/conversations)
- Histórico completo de conversas
- Busca por nome, telefone ou mensagem
- Visualização expandida de mensagens
- Atualização automática a cada 15s

### Testes Grátis (/trials)
- Lista de todos os testes de 7 dias
- Filtros por status (ativo, expirado, convertido)
- Conversão para plano pago
- Gerenciamento de status

### QR Code (/qrcode)
- Geração de QR Code para WhatsApp
- Status da conexão em tempo real
- Desconectar WhatsApp
- Reiniciar serviço

## 🔧 Configuração

### Variáveis de Ambiente

Arquivo `.env`:

```env
VITE_API_URL=http://localhost:8000
```

### Proxy API

O Vite está configurado para fazer proxy das requisições `/api` para o backend:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 🎨 Customização

### Cores

Edite `tailwind.config.js` para customizar as cores:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',
        600: '#0284c7',
        // ...
      }
    }
  }
}
```

### Componentes

Classes utilitárias no `src/index.css`:

```css
.btn-primary { /* Botão primário */ }
.btn-secondary { /* Botão secundário */ }
.card { /* Card container */ }
.input { /* Input field */ }
```

## 📱 Responsivo

O dashboard é totalmente responsivo:

- **Desktop**: Sidebar fixa à esquerda
- **Mobile**: Sidebar em overlay, menu hambúrguer

## 🔒 Rotas Protegidas

Todas as rotas exceto `/login` requerem autenticação.

O componente `ProtectedRoute` verifica:
- Se existe token no localStorage
- Se o token é válido
- Redireciona para /login se não autenticado

## 🚨 Tratamento de Erros

Interceptor Axios configurado para:
- Adicionar token automaticamente
- Redirecionar para login se 401
- Mostrar mensagens de erro amigáveis

## 📈 Performance

- **Auto-refresh**: Dashboard (30s), Conversas (15s), QR Code (10s)
- **Code splitting**: Rotas carregadas sob demanda
- **Lazy loading**: Componentes carregados quando necessário

## 🐛 Debug

```bash
# Ver logs do console
npm run dev

# Build de desenvolvimento
npm run build

# Preview da build
npm run preview
```

## 📦 Deploy

### Build

```bash
npm run build
```

Arquivos gerados em `/dist`.

### Servir Estático

```bash
# Com qualquer servidor HTTP
python3 -m http.server -d dist 3001

# Ou com serve
npx serve dist -p 3001
```

### Docker (Futuro)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "run", "preview"]
```

## 🤝 Integração com API

Todas as requisições são feitas via `/src/services/api.js`:

```javascript
import { dashboardAPI, conversationsAPI, authAPI } from './services/api';

// Exemplo de uso
const summary = await dashboardAPI.getSummary();
const trials = await conversationsAPI.getActiveTrials();
```

## 📞 Suporte

Para dúvidas:
- Email: admin@spdrop.com
- WhatsApp: (11) 93299-4698
