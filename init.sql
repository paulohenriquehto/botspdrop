-- ============================================
-- TABELAS ESSENCIAIS PARA O BOT FUNCIONAR
-- ============================================

-- Tabela de Clientes/Empreendedores
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Conversas (OBRIGATÓRIA para customer_manager.py)
CREATE TABLE IF NOT EXISTS conversas (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id VARCHAR(100)
);

-- Tabela de Usuários Admin (para API)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Performance
CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_conversas_customer ON conversas(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversas_timestamp ON conversas(timestamp);

-- ============================================
-- TABELAS ADICIONAIS (OPCIONAIS)
-- ============================================

-- Tabela de Sessões
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- Histórico de Conversação
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    customer_id INTEGER,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_type VARCHAR(50)
);

-- Preferências do Cliente
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    interested_services TEXT,
    preferred_time_slot VARCHAR(50),
    last_interaction TIMESTAMP,
    conversation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contexto do Cliente (adaptado para dropshipping)
CREATE TABLE customer_context (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    business_niche VARCHAR(255), -- nicho de negócio (moda, eletrônicos, etc)
    experience_level VARCHAR(50), -- iniciante, intermediário, avançado
    current_situation VARCHAR(255), -- CLT, desempregado, autônomo, etc
    financial_situation VARCHAR(100), -- orçamento apertado, flexível, etc
    plans_purchased TEXT,
    last_purchase_date DATE,
    total_spent DECIMAL(10, 2) DEFAULT 0.00,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Planos de Assinatura SPDrop
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    duration_months INTEGER NOT NULL,
    payment_link VARCHAR(500),
    features TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Produtos do Catálogo
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    supplier_id INTEGER,
    cost_price DECIMAL(10, 2),
    suggested_price DECIMAL(10, 2),
    stock_status VARCHAR(50) DEFAULT 'available',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fornecedores
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pedidos dos Empreendedores
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER DEFAULT 1,
    total_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scripts de Conversação
CREATE TABLE conversation_scripts (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER,
    profile_name VARCHAR(100),
    stage VARCHAR(100),
    speaker VARCHAR(50),
    content TEXT,
    script_type VARCHAR(50), -- 'normal' ou 'promocao'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuários em Teste Grátis 7 Dias
CREATE TABLE trial_users (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    full_name VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    trial_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trial_end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'converted', 'cancelled'
    notes TEXT,
    converted_to_plan VARCHAR(100),
    conversion_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Métricas de Atendimentos (Analytics)
CREATE TABLE attendance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_conversations INT DEFAULT 0,
    total_trials_requested INT DEFAULT 0,
    total_conversions INT DEFAULT 0,
    total_messages_sent INT DEFAULT 0,
    total_messages_received INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log Completo de Mensagens
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    direction VARCHAR(10), -- 'inbound' ou 'outbound'
    message TEXT,
    from_number VARCHAR(50),
    to_number VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuários Admin do Dashboard
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Auditoria de Ações Admin
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admin_users(id),
    action VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para Performance
CREATE INDEX idx_sessions_customer_id ON sessions(customer_id);
CREATE INDEX idx_sessions_session_id ON sessions(session_id);
CREATE INDEX idx_conversation_session_id ON conversation_history(session_id);
CREATE INDEX idx_conversation_customer_id ON conversation_history(customer_id);
CREATE INDEX idx_user_preferences_customer_id ON user_preferences(customer_id);
CREATE INDEX idx_customer_context_customer_id ON customer_context(customer_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_conversation_scripts_profile ON conversation_scripts(profile_name);
CREATE INDEX idx_trial_users_customer ON trial_users(customer_id);
CREATE INDEX idx_trial_users_status ON trial_users(status);
CREATE INDEX idx_trial_users_end_date ON trial_users(trial_end_date);
CREATE INDEX idx_attendance_metrics_date ON attendance_metrics(date);
CREATE INDEX idx_message_logs_customer ON message_logs(customer_id);
CREATE INDEX idx_message_logs_timestamp ON message_logs(timestamp);
CREATE INDEX idx_message_logs_direction ON message_logs(direction);
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_audit_log_admin ON audit_log(admin_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);

-- Dados Iniciais: Planos de Assinatura SPDrop - BLACK FRIDAY
INSERT INTO subscription_plans (name, description, price, duration_months, payment_link, features) VALUES
('Plano Básico (Black Friday)', 'Promoção limitada - 10 vagas apenas! 30% OFF', 69.00, 1, 'https://pay.kiwify.com.br/USULsyi', 'Acesso completo, Catálogo +1000 produtos, Integração com marketplaces, Suporte básico'),
('Plano Semestral (Black Friday)', 'MAIS VENDIDO - 40% OFF - Apenas 10 vagas!', 447.00, 6, 'https://pay.kiwify.com.br/HdCYhLa', 'Acesso completo, Catálogo +1000 produtos, Integração com marketplaces, Suporte prioritário, Mentoria de integração, Análises de mercado'),
('Plano Anual (Black Friday)', 'MELHOR CUSTO-BENEFÍCIO - 45% OFF - Apenas 10 vagas!', 897.00, 12, 'https://pay.kiwify.com.br/DKCDNQf', 'Acesso completo, Catálogo +1000 produtos, Integração com marketplaces, Suporte VIP 24/7, Mentoria exclusiva, Análises avançadas, Acesso antecipado a novos recursos');

-- Dados Iniciais: Fornecedores Verificados
INSERT INTO suppliers (name, contact, verified, rating) VALUES
('Fornecedor Premium Mix', 'contato@premiummix.com.br', TRUE, 4.8),
('Mega Distribuidora Nacional', 'vendas@megadistribuidora.com.br', TRUE, 4.9),
('Top Quality Imports', 'sac@topquality.com.br', TRUE, 4.7),
('Brasil Atacado Plus', 'comercial@brasilatacado.com.br', TRUE, 4.6),
('Fast Supply Chain', 'suporte@fastsupply.com.br', TRUE, 4.8);

-- Dados Iniciais: Categorias de Produtos Populares
INSERT INTO products (name, category, supplier_id, cost_price, suggested_price, description) VALUES
('Kit Beleza Completo', 'Beleza e Cosméticos', 1, 45.00, 89.90, 'Kit com produtos de beleza profissional'),
('Fone Bluetooth Premium', 'Eletrônicos', 2, 35.00, 79.90, 'Fone sem fio com cancelamento de ruído'),
('Conjunto Fitness Feminino', 'Moda e Fitness', 3, 55.00, 129.90, 'Conjunto completo para academia'),
('Organizador de Gavetas', 'Casa e Decoração', 4, 25.00, 59.90, 'Kit organizador multi-compartimento'),
('Brinquedo Educativo Infantil', 'Brinquedos', 5, 30.00, 69.90, 'Brinquedo didático para crianças 3-8 anos'),
('Bolsa Feminina Executiva', 'Moda', 1, 68.00, 149.90, 'Bolsa de couro sintético premium'),
('Relógio Smartwatch', 'Eletrônicos', 2, 89.00, 199.90, 'Smartwatch com monitor cardíaco'),
('Kit Cozinha Completo', 'Utilidades', 3, 42.00, 99.90, 'Conjunto de utensílios de cozinha'),
('Mochila Notebook Premium', 'Acessórios', 4, 52.00, 119.90, 'Mochila impermeável para notebook 15.6"'),
('Kit Skincare Facial', 'Beleza', 5, 38.00, 89.90, 'Kit completo para cuidados faciais');
