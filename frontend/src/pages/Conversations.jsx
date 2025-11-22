import { useState, useEffect, useRef } from 'react';
import { conversationsAPI } from '../services/api';
import {
  Search,
  MoreVertical,
  Phone,
  Paperclip,
  Send,
  Smile,
  Mic,
  ArrowLeft,
  CheckCheck,
  Users,
  Briefcase,
  MessageSquare,
  RefreshCw
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export default function Conversations() {
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const messagesEndRef = useRef(null);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const response = await conversationsAPI.getGroupedConversations(100);
      setConversations(response.data.conversations);
    } catch (error) {
      console.error('Erro ao carregar conversas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
    // Atualizar a cada 15 segundos
    const interval = setInterval(loadConversations, 15000);
    return () => clearInterval(interval);
  }, []);

  const activeConversation = conversations.find(c => c.customer.id === selectedCustomerId);
  const activeMessages = activeConversation?.messages || [];

  // Efeito para rolar para o fim das mensagens
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeMessages, selectedCustomerId]);

  // Responsividade: Controle de visualização Mobile
  const handleContactClick = (customerId) => {
    setSelectedCustomerId(customerId);
    if (window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  };

  const handleBackToContacts = () => {
    setIsSidebarOpen(true);
    setSelectedCustomerId(null);
  };

  // Filtro de contatos
  const filteredConversations = conversations.filter(conv =>
    conv.customer.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.customer.phone?.includes(searchTerm) ||
    conv.messages.some(msg =>
      msg.text?.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  // Função para obter iniciais do nome
  const getInitials = (name) => {
    if (!name) return '?';
    const words = name.trim().split(' ');
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Cores para avatares usando CSS variables
  const avatarColors = [
    { bg: 'var(--accent-500)' },
    { bg: 'var(--success-500)' },
    { bg: '#8B5CF6' }, // purple
    { bg: '#EC4899' }, // pink
    { bg: '#6366F1' }, // indigo
    { bg: 'var(--error-500)' },
    { bg: 'var(--warning-500)' },
    { bg: '#14B8A6' } // teal
  ];

  const getAvatarColor = (id) => {
    return avatarColors[id % avatarColors.length];
  };

  // Formatar horário da última mensagem
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return format(date, 'HH:mm');
    } else if (diffDays === 1) {
      return 'Ontem';
    } else if (diffDays < 7) {
      return format(date, 'EEEE', { locale: ptBR });
    } else {
      return format(date, 'dd/MM/yy');
    }
  };

  if (loading && conversations.length === 0) {
    return (
      <div className="flex items-center justify-center h-[600px]" style={{ background: 'var(--bg-surface)' }}>
        <div className="w-12 h-12 border-4 rounded-full animate-spin" style={{ borderColor: 'var(--accent-500)', borderTopColor: 'transparent' }} />
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'var(--bg-base)' }}>
      {/* --- SIDEBAR (Lista de Contatos) --- */}
      <div className={`${isSidebarOpen ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-[400px]`} style={{ borderRight: '2px solid var(--border-light)', background: 'var(--bg-base)' }}>

        {/* Header Sidebar */}
        <div className="flex items-center justify-between px-6 py-4" style={{ background: 'var(--bg-surface)', borderBottom: '2px solid var(--border-light)' }}>
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-full overflow-hidden flex items-center justify-center" style={{ background: 'var(--accent-500)', boxShadow: 'var(--shadow-md)' }}>
              <span className="font-bold text-base" style={{ color: 'var(--text-inverse)' }}>SP</span>
            </div>
            <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>SPDrop Admin</div>
          </div>
          <div className="flex gap-5" style={{ color: 'var(--text-secondary)' }}>
            <button onClick={loadConversations} className="transition-colors p-1 rounded-full refresh-btn">
              <RefreshCw className="w-5 h-5" />
            </button>
            <MoreVertical className="w-5 h-5 cursor-pointer transition-colors more-btn" />
          </div>
          <style>{`
            .refresh-btn:hover, .more-btn:hover {
              color: var(--accent-500) !important;
              background: var(--gray-100) !important;
            }
          `}</style>
        </div>

        {/* Search Bar */}
        <div className="px-4 py-3" style={{ background: 'var(--bg-base)', borderBottom: '1px solid var(--border-light)' }}>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4" style={{ color: 'var(--text-secondary)' }} />
            </div>
            <input
              type="text"
              className="text-sm rounded-xl w-full pl-10 p-3 focus:outline-none transition-all search-input"
              style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
              placeholder="Pesquisar conversa..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <style>{`
              .search-input::placeholder {
                color: var(--text-tertiary);
              }
              .search-input:focus {
                outline: none;
                box-shadow: 0 0 0 2px var(--accent-500);
              }
            `}</style>
          </div>
        </div>

        {/* Contact List */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-10 py-8" style={{ color: 'var(--text-secondary)' }}>
              <MessageSquare className="w-20 h-20 mb-6" style={{ color: 'var(--gray-300)' }} />
              <p className="text-base font-medium">{searchTerm ? 'Nenhuma conversa encontrada' : 'Nenhuma conversa ainda'}</p>
            </div>
          ) : (
            filteredConversations.map((conv) => {
              const lastMessage = conv.messages[conv.messages.length - 1];

              return (
                <div
                  key={conv.customer.id}
                  onClick={() => handleContactClick(conv.customer.id)}
                  className={`flex items-center gap-4 px-5 py-4 cursor-pointer transition-all duration-200 contact-item ${selectedCustomerId === conv.customer.id ? 'contact-item-active' : ''}`}
                  style={{
                    borderBottom: '1px solid var(--border-light)',
                    borderLeft: selectedCustomerId === conv.customer.id ? '4px solid var(--accent-500)' : '4px solid transparent',
                    background: selectedCustomerId === conv.customer.id ? 'rgba(59, 130, 246, 0.08)' : 'transparent'
                  }}
                >
                  <div className="w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center font-bold" style={{ background: getAvatarColor(conv.customer.id).bg, color: 'var(--text-inverse)', boxShadow: 'var(--shadow-md)' }}>
                    {getInitials(conv.customer.name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline mb-1.5">
                      <h3 className="font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{conv.customer.name || 'Cliente'}</h3>
                      <span className="text-xs ml-2" style={{ color: 'var(--text-secondary)' }}>
                        {formatTime(conv.last_message_time)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center mb-1.5">
                      <p className="text-sm truncate pr-2" style={{ color: 'var(--text-secondary)' }}>
                        {lastMessage?.sender === 'agent' && '✓ '}
                        {lastMessage?.text || 'Sem mensagens'}
                      </p>
                    </div>
                    <span className="inline-block mt-1 text-[10px] px-2.5 py-1 rounded-full uppercase tracking-wide" style={{ background: 'var(--gray-100)', color: 'var(--text-secondary)' }}>
                      {conv.customer.phone}
                    </span>
                  </div>
                  <style>{`
                    .contact-item:hover:not(.contact-item-active) {
                      background: var(--bg-hover) !important;
                    }
                  `}</style>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* --- MAIN CHAT AREA --- */}
      <div className={`${!isSidebarOpen ? 'flex' : 'hidden'} md:flex flex-col flex-1 relative`} style={{ background: '#efeae2' }}>
        {selectedCustomerId && activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="px-6 py-4 flex items-center justify-between z-10" style={{ background: 'var(--bg-surface)', borderBottom: '2px solid var(--border-light)', boxShadow: 'var(--shadow-sm)' }}>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleBackToContacts}
                  className="md:hidden mr-1 p-1 rounded-full transition-colors back-btn"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  <ArrowLeft className="w-6 h-6" />
                </button>
                <div className="w-11 h-11 rounded-full flex items-center justify-center font-bold" style={{ background: getAvatarColor(activeConversation.customer.id).bg, color: 'var(--text-inverse)', boxShadow: 'var(--shadow-md)' }}>
                  {getInitials(activeConversation.customer.name)}
                </div>
                <div className="flex flex-col">
                  <span className="font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>{activeConversation.customer.name || 'Cliente'}</span>
                  <span className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                    {activeConversation.customer.phone}
                  </span>
                </div>
              </div>
              <div className="flex gap-5" style={{ color: 'var(--text-secondary)' }}>
                <Search className="w-5 h-5 cursor-pointer transition-colors chat-icon" />
                <Phone className="w-5 h-5 cursor-pointer transition-colors hidden sm:block chat-icon" />
                <MoreVertical className="w-5 h-5 cursor-pointer transition-colors chat-icon" />
              </div>
              <style>{`
                .back-btn:hover, .chat-icon:hover {
                  color: var(--accent-500) !important;
                  background: var(--gray-100);
                }
              `}</style>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 sm:p-10 bg-[url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png')] bg-repeat bg-opacity-30">
              {/* Aviso de Criptografia */}
              <div className="flex justify-center mb-8">
                <div className="text-xs px-4 py-2 rounded-lg text-center max-w-md" style={{ background: 'var(--warning-100)', color: 'var(--text-primary)', border: '1px solid var(--warning-500)', boxShadow: 'var(--shadow-sm)' }}>
                  🔒 As mensagens são criptografadas de ponta a ponta
                </div>
              </div>

              {activeMessages.map((msg) => {
                const isUser = msg.sender === 'user';

                return (
                  <div
                    key={msg.id}
                    className={`flex mb-3 ${isUser ? 'justify-start' : 'justify-end'}`}
                  >
                    <div
                      className={`relative max-w-[85%] sm:max-w-[65%] px-4 py-3 rounded-xl text-sm sm:text-[15px] leading-relaxed ${
                        isUser ? 'rounded-tl-none' : 'rounded-tr-none'
                      }`}
                      style={{
                        background: isUser ? 'var(--bg-base)' : '#d9fdd3',
                        border: isUser ? '1px solid var(--border-light)' : '1px solid #b9f5d0',
                        boxShadow: 'var(--shadow-md)'
                      }}
                    >
                      <p className="mr-2 pb-2 whitespace-pre-wrap break-words" style={{ color: 'var(--text-primary)' }}>{msg.text}</p>
                      <div className="flex justify-end items-center gap-1 absolute bottom-2 right-3">
                        <span className="text-[10px] mt-1 block text-right min-w-[40px]" style={{ color: 'var(--text-secondary)' }}>
                          {format(new Date(msg.timestamp), 'HH:mm')}
                        </span>
                        {!isUser && (
                          <CheckCheck className="w-3 h-3" style={{ color: '#53bdeb' }} />
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area - Apenas visual, sem funcionalidade de envio */}
            <div className="px-5 py-4 flex items-center gap-4 z-10" style={{ background: 'var(--bg-surface)', borderTop: '1px solid var(--border-light)' }}>
              <Smile className="w-6 h-6 cursor-not-allowed hidden sm:block transition-colors input-icon" style={{ color: 'var(--text-tertiary)' }} />
              <Paperclip className="w-6 h-6 cursor-not-allowed transition-colors input-icon" style={{ color: 'var(--text-tertiary)' }} />

              <div className="flex-1 rounded-xl flex items-center" style={{ background: 'var(--bg-base)', boxShadow: 'var(--shadow-sm)', border: '1px solid var(--border-light)' }}>
                <input
                  type="text"
                  className="w-full px-5 py-3 rounded-xl focus:outline-none cursor-not-allowed input-field"
                  style={{ background: 'var(--bg-base)', color: 'var(--text-primary)' }}
                  placeholder="Visualização somente leitura"
                  disabled
                />
              </div>

              <Mic className="w-6 h-6 cursor-not-allowed transition-colors input-icon" style={{ color: 'var(--text-tertiary)' }} />

              <style>{`
                .input-icon:hover {
                  color: var(--text-secondary) !important;
                }
                .input-field::placeholder {
                  color: var(--text-tertiary);
                }
              `}</style>
            </div>
          </>
        ) : (
          /* Empty State (No chat selected) */
          <div className="flex flex-col items-center justify-center h-full text-center px-12 py-10" style={{ background: 'var(--bg-surface)', borderBottom: '8px solid var(--success-500)' }}>
            <div className="mb-10 relative">
              <div className="w-64 h-64 rounded-full flex items-center justify-center" style={{ background: 'var(--gray-100)', boxShadow: 'var(--shadow-inner)' }}>
                <Briefcase className="w-32 h-32" style={{ color: 'var(--gray-300)' }} />
              </div>
            </div>

            <h1 className="text-3xl font-light mb-5" style={{ color: 'var(--text-primary)' }}>SPDrop Web</h1>
            <p className="text-sm leading-7 max-w-md px-4" style={{ color: 'var(--text-secondary)' }}>
              Gerencie todas as conversas com seus clientes em um só lugar. Histórico completo de mensagens com a Gabi.
            </p>
            <div className="mt-12 flex items-center gap-3 text-xs px-4 py-2 rounded-full" style={{ background: 'var(--bg-base)', color: 'var(--text-tertiary)', boxShadow: 'var(--shadow-sm)' }}>
              <Users className="w-4 h-4" />
              <span>Visualização de conversas do banco de dados</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
