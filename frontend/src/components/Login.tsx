import React, { useState } from 'react';
import { Eye, EyeOff, Shield, AlertCircle, CheckCircle2, UserCheck } from 'lucide-react';
import { api, AuthenticatedUser } from '../api/client';

interface LoginProps {
  onLoginSuccess: (user: AuthenticatedUser) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('employee@company.com');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAccounts = [
    { email: 'employee@company.com', role: 'EMPLOYEE', label: 'Nhân viên (Employee)' },
    { email: 'manager@company.com', role: 'MANAGER', label: 'Quản lý (Manager)' },
    { email: 'procurement@company.com', role: 'PROCUREMENT', label: 'Mua sắm (Procurement)' },
    { email: 'finance@company.com', role: 'FINANCE', label: 'Tài chính (Finance)' },
    { email: 'admin@company.com', role: 'ADMIN', label: 'Quản trị (Admin)' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Vui lòng nhập đầy đủ email và mật khẩu.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const session = await api.login(email.trim(), password);
      onLoginSuccess(session.user);
    } catch (err: any) {
      setError(err.message || 'Đăng nhập không thành công. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const selectTestAccount = (accEmail: string) => {
    setEmail(accEmail);
    setPassword('password123');
    setError(null);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#f5f6f8',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        boxSizing: 'border-box',
      }}
      data-testid="login-container"
    >
      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          border: '0.667px solid #e4e7ec',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
          padding: '36px 32px',
          boxSizing: 'border-box',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '8px',
              backgroundColor: '#eef1ff',
              color: '#2f3789',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '12px',
            }}
          >
            <Shield size={24} />
          </div>
          <h1
            style={{
              fontSize: '20px',
              fontWeight: 700,
              color: '#12161c',
              margin: '0 0 6px 0',
              letterSpacing: '-0.4px',
            }}
          >
            Hệ Thống Mua Sắm & Phê Duyệt AI
          </h1>
          <p style={{ margin: 0, fontSize: '13px', color: '#5a6472' }}>
            Đăng nhập tài khoản định danh doanh nghiệp
          </p>
        </div>

        {/* Error Alert Banner */}
        {error && (
          <div
            style={{
              backgroundColor: '#fdecec',
              border: '0.667px solid #f4c2c2',
              borderRadius: '6px',
              padding: '10px 12px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '8px',
              color: '#8e1e1e',
              fontSize: '12px',
              lineHeight: '18px',
            }}
            data-testid="login-error-banner"
          >
            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '1px' }} />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: 600,
                color: '#12161c',
                marginBottom: '6px',
              }}
            >
              Email công ty
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              required
              style={{
                width: '100%',
                height: '38px',
                padding: '0 12px',
                borderRadius: '4px',
                border: '0.667px solid #e4e7ec',
                fontSize: '14px',
                fontFamily: 'inherit',
                color: '#12161c',
                boxSizing: 'border-box',
                outline: 'none',
              }}
              data-testid="input-email"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label
                style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#12161c',
                }}
              >
                Mật khẩu
              </label>
            </div>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Nhập mật khẩu"
                required
                style={{
                  width: '100%',
                  height: '38px',
                  padding: '0 36px 0 12px',
                  borderRadius: '4px',
                  border: '0.667px solid #e4e7ec',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  color: '#12161c',
                  boxSizing: 'border-box',
                  outline: 'none',
                }}
                data-testid="input-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '8px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: '#8a929e',
                  cursor: 'pointer',
                  padding: '4px',
                  display: 'flex',
                  alignItems: 'center',
                }}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', height: '40px', fontSize: '14px' }}
            data-testid="login-submit-button"
          >
            {loading ? 'Đang xác thực...' : 'Đăng nhập'}
          </button>
        </form>

        {/* Quick Test Accounts Picker */}
        <div style={{ marginTop: '24px', borderTop: '0.667px solid #f0f2f5', paddingTop: '16px' }}>
          <div
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: '#8a929e',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <UserCheck size={12} />
            <span>Tài khoản mẫu kiểm thử (HD-12 Seed)</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {testAccounts.map((acc) => (
              <button
                key={acc.email}
                type="button"
                onClick={() => selectTestAccount(acc.email)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '6px 10px',
                  borderRadius: '4px',
                  border: '0.667px solid #e4e7ec',
                  backgroundColor: email === acc.email ? '#eef1ff' : '#fcfdfe',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '12px',
                  color: email === acc.email ? '#2f3789' : '#5a6472',
                  transition: 'background-color 0.1s ease',
                }}
                onMouseEnter={(e) => {
                  if (email !== acc.email) e.currentTarget.style.backgroundColor = '#f8fafc';
                }}
                onMouseLeave={(e) => {
                  if (email !== acc.email) e.currentTarget.style.backgroundColor = '#fcfdfe';
                }}
                data-testid={`test-acc-${acc.role.toLowerCase()}`}
              >
                <span>{acc.label}</span>
                <span
                  style={{
                    fontSize: '10px',
                    color: '#8a929e',
                    fontFamily: 'monospace',
                  }}
                >
                  {acc.email.split('@')[0]}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Security Notice */}
        <div
          style={{
            marginTop: '20px',
            padding: '10px',
            borderRadius: '4px',
            backgroundColor: '#f5f6f8',
            fontSize: '11px',
            color: '#8a929e',
            lineHeight: '15px',
            textAlign: 'center',
          }}
        >
          Quy chuẩn bảo mật <b>Zero-Trust (HD-02 / HD-12)</b>: Vai trò &amp; thẩm quyền được truy xuất trực tiếp từ CSDL máy chủ, không tin cậy dữ liệu client.
        </div>
      </div>
    </div>
  );
};
