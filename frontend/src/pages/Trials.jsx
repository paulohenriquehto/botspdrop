import { useState, useEffect } from 'react';
import { conversationsAPI } from '../services/api';
import { TestTube, CheckCircle, Clock, XCircle, TrendingUp } from 'lucide-react';
import { format, differenceInDays } from 'date-fns';

const STATUS_LABELS = {
  active: { label: 'Ativo', color: 'green', icon: CheckCircle },
  expired: { label: 'Expirado', color: 'red', icon: XCircle },
  converted: { label: 'Convertido', color: 'blue', icon: TrendingUp },
  cancelled: { label: 'Cancelado', color: 'gray', icon: XCircle },
};

export default function Trials() {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active');
  const [trials, setTrials] = useState([]);
  const [selectedTrial, setSelectedTrial] = useState(null);

  const loadTrials = async () => {
    setLoading(true);
    try {
      let response;
      if (activeTab === 'active') {
        response = await conversationsAPI.getActiveTrials();
      } else if (activeTab === 'expired') {
        response = await conversationsAPI.getExpiredTrials();
      } else {
        response = await conversationsAPI.getAllTrials(activeTab);
      }
      setTrials(response.data.trials);
    } catch (error) {
      console.error('Erro ao carregar trials:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrials();
  }, [activeTab]);

  const handleConvert = async (trialId) => {
    const planName = prompt('Digite o nome do plano:');
    if (!planName) return;

    try {
      await conversationsAPI.convertTrial(trialId, planName);
      alert('Trial convertido com sucesso!');
      loadTrials();
    } catch (error) {
      alert('Erro ao converter trial: ' + error.response?.data?.detail);
    }
  };

  const handleUpdateStatus = async (trialId, status) => {
    try {
      await conversationsAPI.updateTrialStatus(trialId, status);
      alert('Status atualizado!');
      loadTrials();
    } catch (error) {
      alert('Erro ao atualizar status: ' + error.response?.data?.detail);
    }
  };

  const tabs = [
    { key: 'active', label: 'Ativos', icon: Clock },
    { key: 'expired', label: 'Expirados', icon: XCircle },
    { key: 'converted', label: 'Convertidos', icon: TrendingUp },
    { key: 'all', label: 'Todos', icon: TestTube },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Testes Grátis 7 Dias</h1>
        <p className="text-gray-500 mt-1">Gerencie os testes gratuitos da plataforma</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === tab.key
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Trials List */}
      {!loading && (
        <div className="grid grid-cols-1 gap-4">
          {trials.length === 0 ? (
            <div className="card text-center py-12">
              <TestTube className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Nenhum teste encontrado</p>
            </div>
          ) : (
            trials.map((trial) => {
              const statusInfo = STATUS_LABELS[trial.status];
              const StatusIcon = statusInfo.icon;
              const daysRemaining = trial.days_remaining || 0;
              const daysExpired = trial.days_expired || 0;

              return (
                <div key={trial.id} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {trial.full_name}
                          </h3>
                          <p className="text-sm text-gray-500">{trial.customer_phone}</p>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium
                            ${statusInfo.color === 'green' ? 'bg-green-100 text-green-800' : ''}
                            ${statusInfo.color === 'red' ? 'bg-red-100 text-red-800' : ''}
                            ${statusInfo.color === 'blue' ? 'bg-blue-100 text-blue-800' : ''}
                            ${statusInfo.color === 'gray' ? 'bg-gray-100 text-gray-800' : ''}
                          `}
                        >
                          <StatusIcon className="w-3 h-3 inline mr-1" />
                          {statusInfo.label}
                        </span>
                      </div>

                      {/* Info Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-gray-500">Email</p>
                          <p className="text-sm font-medium text-gray-900">{trial.email}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">CPF</p>
                          <p className="text-sm font-medium text-gray-900">{trial.cpf}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Início</p>
                          <p className="text-sm font-medium text-gray-900">
                            {format(new Date(trial.trial_start_date), 'dd/MM/yyyy')}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Término</p>
                          <p className="text-sm font-medium text-gray-900">
                            {format(new Date(trial.trial_end_date), 'dd/MM/yyyy')}
                          </p>
                        </div>
                      </div>

                      {/* Days Info */}
                      {trial.status === 'active' && daysRemaining >= 0 && (
                        <div className="mb-3">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-orange-500" />
                            <span className="text-sm text-orange-600 font-medium">
                              {Math.floor(daysRemaining)} dias restantes
                            </span>
                          </div>
                          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-orange-500 h-2 rounded-full transition-all"
                              style={{ width: `${((7 - daysRemaining) / 7) * 100}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {trial.status === 'active' && daysExpired > 0 && (
                        <div className="flex items-center gap-2 mb-3">
                          <XCircle className="w-4 h-4 text-red-500" />
                          <span className="text-sm text-red-600 font-medium">
                            Expirado há {Math.floor(daysExpired)} dias
                          </span>
                        </div>
                      )}

                      {trial.status === 'converted' && trial.converted_to_plan && (
                        <div className="flex items-center gap-2 mb-3">
                          <TrendingUp className="w-4 h-4 text-green-500" />
                          <span className="text-sm text-green-600 font-medium">
                            Convertido para: {trial.converted_to_plan}
                          </span>
                        </div>
                      )}

                      {/* Notes */}
                      {trial.notes && (
                        <div className="bg-gray-50 rounded p-3 mb-3">
                          <p className="text-xs text-gray-500 mb-1">Observações:</p>
                          <p className="text-sm text-gray-700">{trial.notes}</p>
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex gap-2 flex-wrap">
                        {trial.status === 'active' && (
                          <>
                            <button
                              onClick={() => handleConvert(trial.id)}
                              className="btn-primary text-sm"
                            >
                              Converter para Pago
                            </button>
                            <button
                              onClick={() => handleUpdateStatus(trial.id, 'cancelled')}
                              className="btn-secondary text-sm"
                            >
                              Cancelar
                            </button>
                          </>
                        )}
                        {trial.status === 'expired' && (
                          <button
                            onClick={() => handleConvert(trial.id)}
                            className="btn-primary text-sm"
                          >
                            Converter para Pago
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
