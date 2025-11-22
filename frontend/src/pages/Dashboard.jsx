import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import {
  LayoutDashboard,
  Users,
  RefreshCw,
  MessageSquare,
  TrendingUp,
  Clock,
  Send,
  Inbox,
  UserPlus,
  CheckCircle,
  Activity
} from 'lucide-react';

const Card = ({ children, className = "" }) => (
  <div
    className={`rounded-xl p-6 transition-all duration-300 ${className}`}
    style={{
      background: 'var(--bg-base)',
      border: '1px solid var(--border-light)',
      boxShadow: 'var(--shadow-sm)'
    }}
  >
    {children}
  </div>
);

const StatCard = ({ title, value, subtext, icon: Icon, colorClass }) => {
  const colorMap = {
    'text-blue-400': { bg: 'rgba(59, 130, 246, 0.1)', icon: 'var(--accent-500)' },
    'text-yellow-400': { bg: 'rgba(245, 158, 11, 0.1)', icon: 'var(--warning-500)' },
    'text-green-400': { bg: 'rgba(16, 185, 129, 0.1)', icon: 'var(--success-500)' },
    'text-purple-400': { bg: 'rgba(139, 92, 246, 0.1)', icon: '#8B5CF6' }
  };

  const colors = colorMap[colorClass] || { bg: 'var(--gray-100)', icon: 'var(--gray-600)' };

  return (
    <div
      className="flex flex-col justify-between rounded-xl p-6 transition-all duration-300 stat-card"
      style={{
        background: 'var(--bg-base)',
        border: '1px solid var(--border-light)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 style={{ color: 'var(--text-secondary)' }} className="text-sm font-medium uppercase tracking-wider">{title}</h3>
          <p style={{ color: 'var(--text-primary)' }} className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="p-3 rounded-lg" style={{ background: colors.bg }}>
          <Icon className="w-6 h-6" style={{ color: colors.icon }} />
        </div>
      </div>
      {subtext && (
        <div className="flex items-center text-xs mt-2">
          <span className="px-2 py-1 rounded" style={{ background: 'var(--gray-100)', color: 'var(--text-secondary)' }}>{subtext}</span>
        </div>
      )}
      <style>{`
        .stat-card:hover {
          border-color: var(--accent-500) !important;
          box-shadow: var(--shadow-md) !important;
          transform: translateY(-2px);
        }
      `}</style>
    </div>
  );
};

const MiniStat = ({ label, value, icon: Icon, trend }) => (
  <div
    className="rounded-lg p-4 flex items-center justify-between transition-colors mini-stat"
    style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-light)'
    }}
  >
    <div className="flex items-center gap-3">
      <div className="p-2 rounded-md" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-500)' }}>
        <Icon size={18} />
      </div>
      <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{label}</span>
    </div>
    <div className="text-right">
      <span className="block text-xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</span>
      {trend !== undefined && (
        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>Hoje</span>
      )}
    </div>
    <style>{`
      .mini-stat:hover {
        background: var(--gray-100) !important;
      }
    `}</style>
  </div>
);

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [todayMetrics, setTodayMetrics] = useState(null);
  const [lastUpdated, setLastUpdated] = useState("");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setIsRefreshing(true);
    try {
      const [summaryRes, todayRes] = await Promise.all([
        dashboardAPI.getSummary(),
        dashboardAPI.getTodayMetrics(),
      ]);

      setSummary(summaryRes.data);
      setTodayMetrics(todayRes.data);

      const now = new Date();
      setLastUpdated(now.toLocaleTimeString('pt-BR'));
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadData();
  };

  useEffect(() => {
    loadData();
    // Atualizar a cada 30 segundos
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !summary) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: 'var(--bg-surface)' }}>
        <div className="w-12 h-12 border-4 rounded-full animate-spin" style={{ borderColor: 'var(--accent-500)', borderTopColor: 'transparent' }} />
      </div>
    );
  }

  const generalStats = [
    {
      title: "Total de Clientes",
      value: summary?.total_customers || 0,
      subtext: "Base ativa",
      icon: Users,
      colorClass: "text-blue-400"
    },
    {
      title: "Testes Ativos",
      value: summary?.active_trials || 0,
      subtext: "7 dias grátis",
      icon: Clock,
      colorClass: "text-yellow-400"
    },
    {
      title: "Conversões",
      value: summary?.total_conversions || 0,
      subtext: "Total acumulado",
      icon: CheckCircle,
      colorClass: "text-green-400"
    },
    {
      title: "Mensagens 24h",
      value: summary?.messages_last_24h || 0,
      subtext: "Ciclo atual",
      icon: MessageSquare,
      colorClass: "text-purple-400"
    },
  ];

  const todaysMetrics = [
    { label: "Conversas Iniciadas", value: todayMetrics?.metrics?.total_conversations || 0, icon: MessageSquare },
    { label: "Trials Solicitados", value: todayMetrics?.metrics?.total_trials_requested || 0, icon: UserPlus },
    { label: "Conversões (Dia)", value: todayMetrics?.metrics?.total_conversions || 0, icon: TrendingUp },
    { label: "Msgs Enviadas", value: todayMetrics?.metrics?.total_messages_sent || 0, icon: Send },
    { label: "Msgs Recebidas", value: todayMetrics?.metrics?.total_messages_received || 0, icon: Inbox },
  ];

  const hasActivity = todaysMetrics.some(m => m.value > 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Dashboard</h1>
          <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
            Visão geral do sistema • {new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all text-sm font-medium active:scale-95 disabled:opacity-50 refresh-btn"
          style={{
            background: 'var(--accent-500)',
            color: 'var(--text-inverse)',
            boxShadow: 'var(--shadow-sm)'
          }}
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">{isRefreshing ? 'Atualizando...' : 'Atualizar'}</span>
        </button>
        <style>{`
          .refresh-btn:hover:not(:disabled) {
            background: var(--accent-600) !important;
            box-shadow: var(--shadow-md) !important;
          }
        `}</style>
      </div>

      {/* Last Update Info */}
      {lastUpdated && (
        <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          <Clock className="w-4 h-4" />
          Última atualização: <span className="font-mono" style={{ color: 'var(--text-primary)' }}>{lastUpdated}</span>
        </div>
      )}

      {/* Status Bar */}
      <div className="flex items-center justify-between rounded-lg px-4 py-3 text-sm" style={{ background: 'var(--success-100)', border: '1px solid var(--success-600)' }}>
        <div className="flex items-center gap-2" style={{ color: 'var(--success-600)' }}>
          <Activity className="w-4 h-4" />
          <span className="font-semibold">Status do Sistema: Operacional</span>
        </div>
      </div>

      {/* Big Stats Grid */}
      <section>
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
          Métricas Principais
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {generalStats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>
      </section>

      {/* Today's Metrics Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Column: Today's Breakdown */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>Métricas de Hoje</h2>
            <span className="text-xs px-2 py-1 rounded font-medium" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-600)', border: '1px solid var(--accent-500)' }}>
              Tempo real
            </span>
          </div>

          <Card>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {todaysMetrics.map((metric, index) => (
                  <MiniStat key={index} {...metric} trend={0} />
                ))}
              </div>

            {/* Empty State Visual Placeholder when no activity */}
            {!hasActivity && (
              <div className="mt-6 p-6 border border-dashed rounded-lg flex flex-col items-center justify-center text-center" style={{ borderColor: 'var(--border-default)', background: 'var(--bg-surface)' }}>
                <div className="w-12 h-12 rounded-full flex items-center justify-center mb-3" style={{ background: 'var(--gray-200)', color: 'var(--text-tertiary)' }}>
                  <TrendingUp size={24} />
                </div>
                <p className="font-medium" style={{ color: 'var(--text-primary)' }}>Aguardando atividade</p>
                <p className="text-sm max-w-md mt-1" style={{ color: 'var(--text-secondary)' }}>
                  As métricas diárias aparecerão aqui assim que houver interação com os leads ou disparos ativos.
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Team & Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>Equipe & Status</h2>

          <Card className="h-full">
            <h3 className="text-sm font-medium uppercase tracking-wider mb-4" style={{ color: 'var(--text-secondary)' }}>Agentes Ativos</h3>
            <div className="space-y-4">
              {/* Paulo */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: 'var(--accent-500)', color: 'var(--text-inverse)' }}>P</div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Paulo</p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Estratégia</p>
                  </div>
                </div>
                <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--success-500)' }}></div>
              </div>
              {/* Kaique */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: 'var(--gray-600)', color: 'var(--text-inverse)' }}>K</div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Kaique</p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Suporte</p>
                  </div>
                </div>
                <div className="w-2 h-2 rounded-full" style={{ background: 'var(--success-500)' }}></div>
              </div>
              {/* Eduarda */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: 'var(--gray-600)', color: 'var(--text-inverse)' }}>E</div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Eduarda</p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Prospecção</p>
                  </div>
                </div>
                <div className="w-2 h-2 rounded-full" style={{ background: 'var(--gray-400)' }}></div>
              </div>
              {/* David */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: 'var(--gray-600)', color: 'var(--text-inverse)' }}>D</div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>David</p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Prospecção</p>
                  </div>
                </div>
                <div className="w-2 h-2 rounded-full" style={{ background: 'var(--gray-400)' }}></div>
              </div>
            </div>

            <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--border-light)' }}>
              <button className="w-full py-2 rounded-lg text-sm font-medium transition-colors report-btn" style={{ background: 'var(--accent-500)', color: 'var(--text-inverse)', boxShadow: 'var(--shadow-sm)' }}>
                Gerar Relatório Completo
              </button>
              <style>{`
                .report-btn:hover {
                  background: var(--accent-600) !important;
                  box-shadow: var(--shadow-md) !important;
                }
              `}</style>
            </div>
          </Card>
        </div>

      </section>
    </div>
  );
}
