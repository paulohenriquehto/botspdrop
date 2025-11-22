import { useState, useEffect } from 'react';
import { qrcodeAPI } from '../services/api';
import { QrCode, CheckCircle, XCircle, RefreshCw, Power } from 'lucide-react';

export default function QRCodePage() {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [qrCodeUrl, setQrCodeUrl] = useState(null);
  const [generatingQR, setGeneratingQR] = useState(false);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const response = await qrcodeAPI.getStatus();
      setStatus(response.data.whatsapp_status || response.data);
    } catch (error) {
      console.error('Erro ao carregar status:', error);
      setStatus({ connected: false, ready: false, error: 'Erro ao conectar' });
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async () => {
    setGeneratingQR(true);
    try {
      const response = await qrcodeAPI.generate();
      const blob = response.data;
      const url = URL.createObjectURL(blob);
      setQrCodeUrl(url);
    } catch (error) {
      if (error.response?.status === 400) {
        alert('WhatsApp já está conectado!');
      } else {
        alert('Erro ao gerar QR Code: ' + error.response?.data?.detail);
      }
    } finally {
      setGeneratingQR(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm('Deseja desconectar o WhatsApp?')) return;

    try {
      await qrcodeAPI.disconnect();
      alert('WhatsApp desconectado com sucesso!');
      setQrCodeUrl(null);
      loadStatus();
    } catch (error) {
      alert('Erro ao desconectar: ' + error.response?.data?.detail);
    }
  };

  const handleRestart = async () => {
    if (!confirm('Deseja reiniciar o serviço WhatsApp?')) return;

    try {
      await qrcodeAPI.restart();
      alert('Serviço reiniciado!');
      setTimeout(loadStatus, 3000);
    } catch (error) {
      alert('Erro ao reiniciar: ' + error.response?.data?.detail);
    }
  };

  useEffect(() => {
    loadStatus();
    // Atualizar status a cada 10 segundos
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const isConnected = status?.connected && status?.ready;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">QR Code WhatsApp</h1>
        <p className="text-gray-500 mt-1">Gerencie a conexão do bot com WhatsApp</p>
      </div>

      {/* Status Card */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Status da Conexão
            </h2>
            <div className="flex items-center gap-3">
              {isConnected ? (
                <>
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <span className="text-lg font-medium text-green-600">
                    Conectado
                  </span>
                </>
              ) : (
                <>
                  <XCircle className="w-6 h-6 text-red-500" />
                  <span className="text-lg font-medium text-red-600">
                    Desconectado
                  </span>
                </>
              )}
            </div>
            {status?.phone && (
              <p className="text-sm text-gray-600 mt-2">
                Número: {status.phone}
              </p>
            )}
          </div>
          <button
            onClick={loadStatus}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Atualizar
          </button>
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={generateQRCode}
          disabled={generatingQR || isConnected}
          className="card hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex flex-col items-center text-center p-4">
            <QrCode className="w-12 h-12 text-primary-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Gerar QR Code
            </h3>
            <p className="text-sm text-gray-500">
              {isConnected
                ? 'WhatsApp já conectado'
                : 'Escanear para conectar'}
            </p>
          </div>
        </button>

        <button
          onClick={handleDisconnect}
          disabled={!isConnected}
          className="card hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="flex flex-col items-center text-center p-4">
            <Power className="w-12 h-12 text-red-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Desconectar
            </h3>
            <p className="text-sm text-gray-500">
              Fazer logout do WhatsApp
            </p>
          </div>
        </button>

        <button
          onClick={handleRestart}
          className="card hover:shadow-lg transition-shadow"
        >
          <div className="flex flex-col items-center text-center p-4">
            <RefreshCw className="w-12 h-12 text-orange-600 mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Reiniciar Serviço
            </h3>
            <p className="text-sm text-gray-500">
              Reiniciar serviço WhatsApp
            </p>
          </div>
        </button>
      </div>

      {/* QR Code Display */}
      {qrCodeUrl && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">
            Escaneie o QR Code
          </h2>
          <div className="flex flex-col items-center">
            <img
              src={qrCodeUrl}
              alt="QR Code WhatsApp"
              className="max-w-md w-full border-4 border-gray-200 rounded-lg"
            />
            <div className="mt-6 max-w-md text-center">
              <h3 className="font-semibold text-gray-900 mb-2">
                Como conectar:
              </h3>
              <ol className="text-left text-sm text-gray-600 space-y-2">
                <li>1. Abra o WhatsApp no seu celular</li>
                <li>2. Toque em Menu (⋮) ou Configurações</li>
                <li>3. Toque em &quot;Aparelhos conectados&quot;</li>
                <li>4. Toque em &quot;Conectar um aparelho&quot;</li>
                <li>5. Aponte o celular para esta tela para escanear o código</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!isConnected && !qrCodeUrl && (
        <div className="card bg-blue-50 border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Informações</h3>
          <p className="text-sm text-blue-800">
            Para conectar o bot ao WhatsApp, clique em &quot;Gerar QR Code&quot; e escaneie
            o código com seu celular. A conexão ficará ativa até que você desconecte
            manualmente.
          </p>
        </div>
      )}
    </div>
  );
}
