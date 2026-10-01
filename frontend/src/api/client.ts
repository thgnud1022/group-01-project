/**
 * Centralized API Client with Real Supabase JWT Bearer Token Injection.
 * Enforces:
 * - Target Architecture: Login -> Supabase signInWithPassword -> real access_token -> /api/auth/me -> Application User.
 * - HD-02: Zero-Trust Client, token passed via Authorization: Bearer <real_supabase_access_token>.
 * - HD-12: Backend verifies ES256 JWT via JWKS and resolves user role from database where authUserId == sub.
 * - 401: Clears Supabase session and triggers redirect to Login.
 * - 403: Displays Forbidden error without logging out.
 * - No mock login, no fake JWT, no client-side role override.
 */

import { supabase, isSupabaseConfigured, getCurrentAccessToken } from '../lib/supabase';

export interface AuthenticatedUser {
  id: string;
  email: string;
  name: string;
  role: 'EMPLOYEE' | 'MANAGER' | 'PROCUREMENT' | 'FINANCE' | 'ADMIN';
  departmentId: string;
  auth_sub?: string;
}

export interface AuthSession {
  token: string;
  user: AuthenticatedUser;
}

class ApiClient {
  private currentUser: AuthenticatedUser | null = null;
  private onUnauthorizedCallbacks: Array<() => void> = [];

  constructor() {
    // Supabase client manages token persistence automatically in localStorage
  }

  public getUser(): AuthenticatedUser | null {
    return this.currentUser;
  }

  public setUser(user: AuthenticatedUser | null) {
    this.currentUser = user;
  }

  public onUnauthorized(callback: () => void) {
    this.onUnauthorizedCallbacks.push(callback);
    return () => {
      this.onUnauthorizedCallbacks = this.onUnauthorizedCallbacks.filter(cb => cb !== callback);
    };
  }

  public async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers || {});

    // Attach Content-Type if not set and body exists
    if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    // Attach real Supabase Bearer token if session exists
    const accessToken = await getCurrentAccessToken();
    if (accessToken && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${accessToken}`);
    }

    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // 401: Unauthorized - session expired, invalid signature, or unbound user
      this.currentUser = null;
      try {
        await supabase.auth.signOut();
      } catch {}
      this.onUnauthorizedCallbacks.forEach(cb => cb());

      let errorMsg = 'Phiên đăng nhập đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại (401).';
      try {
        const errJson = await response.json();
        if (errJson.detail) errorMsg = errJson.detail;
      } catch {
        // use default
      }
      throw new Error(errorMsg);
    }

    if (response.status === 403) {
      // 403: Forbidden - valid identity but insufficient RBAC role
      // Do NOT sign out on 403
      let errorMsg = 'Bạn không có quyền thực hiện thao tác này (RBAC 403 Forbidden).';
      try {
        const errJson = await response.json();
        if (errJson.detail) errorMsg = errJson.detail;
      } catch {
        // use default
      }
      throw new Error(errorMsg);
    }

    if (!response.ok) {
      let errorMsg = `Lỗi hệ thống (${response.status}): ${response.statusText}`;
      try {
        const errJson = await response.json();
        if (errJson.detail) {
          errorMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        // use default
      }
      throw new Error(errorMsg);
    }

    const text = await response.text();
    if (!text) {
      return {} as T;
    }
    return JSON.parse(text) as T;
  }

  // Real Supabase Login Flow (No mock, no fake JWT)
  public async login(email: string, password: string): Promise<AuthSession> {
    if (!isSupabaseConfigured) {
      throw new Error(
        'AUTH E2E BLOCKER: VITE_SUPABASE_ANON_KEY chưa được cấu hình trong frontend .env. ' +
        'Vui lòng hoàn tất thiết lập 5 tài khoản Supabase Auth và cấu hình biến môi trường trước khi kiểm thử.'
      );
    }

    // 1. Authenticate with real Supabase Auth
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });

    if (error || !data.session) {
      throw new Error(`Đăng nhập Supabase Auth thất bại: ${error?.message || 'Không thể tạo phiên làm việc.'}`);
    }

    const token = data.session.access_token;

    // 2. Resolve Application User by verified JWT sub -> User.authUserId (HD-12)
    try {
      const user = await this.request<AuthenticatedUser>('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      this.currentUser = user;
      return { token, user };
    } catch (err: any) {
      // If /api/auth/me rejects with 401 because User.authUserId is not mapped, clean up and fail closed
      await supabase.auth.signOut();
      this.currentUser = null;
      throw new Error(
        `Xác thực danh tính ứng dụng thất bại (/api/auth/me): ${err.message}. ` +
        `Cần ánh xạ UUID '${data.user.id}' vào trường User.authUserId trong PostgreSQL.`
      );
    }
  }

  // Restore existing session on browser reload
  public async restoreSession(): Promise<AuthenticatedUser | null> {
    if (!isSupabaseConfigured) return null;
    const token = await getCurrentAccessToken();
    if (!token) return null;

    try {
      const user = await this.request<AuthenticatedUser>('/api/auth/me');
      this.currentUser = user;
      return user;
    } catch {
      await supabase.auth.signOut();
      this.currentUser = null;
      return null;
    }
  }

  // Sign out cleanly
  public async logout(): Promise<void> {
    this.currentUser = null;
    try {
      await supabase.auth.signOut();
    } catch {}
  }

  public async clearSession(): Promise<void> {
    return this.logout();
  }

  public async getMe(): Promise<AuthenticatedUser> {
    return this.request<AuthenticatedUser>('/api/auth/me');
  }

  // PR endpoints
  public async listPRs() {
    return this.request<any[]>('/api/pr');
  }

  public async createPR(data: { departmentId: string; title: string; items: any[] }) {
    return this.request<any>('/api/pr', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async approvePR(prId: string, comments: string = 'Phê duyệt PR') {
    return this.request<any>(`/api/pr/${prId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    });
  }

  public async rejectPR(prId: string, comments: string) {
    return this.request<any>(`/api/pr/${prId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    });
  }

  public async requestRevision(prId: string, comments: string) {
    return this.request<any>(`/api/pr/${prId}/revision`, {
      method: 'POST',
      body: JSON.stringify({ comments }),
    });
  }

  public async resubmitPR(prId: string, data?: { title?: string; description?: string; items?: any[]; comments?: string }) {
    return this.request<any>(`/api/pr/${prId}/resubmit`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }

  public async closePR(prId: string) {
    return this.request<any>(`/api/pr/${prId}/close`, {
      method: 'POST',
    });
  }


  public async getPR(prId: string) {
    return this.request<any>(`/api/pr/${prId}`);
  }

  // Budget endpoints
  public async getBudget(deptId: string = 'DEPT-IT') {
    return this.request<any>(`/api/budget/${deptId}`);
  }

  public async listBudgets() {
    return this.request<any[]>('/api/budget');
  }

  // AI Assistant endpoints
  public async standardizePR(rawText: string) {
    return this.request<any>('/api/assistant/standardize-pr', {
      method: 'POST',
      body: JSON.stringify({ raw_text: rawText }),
    });
  }

  public async recommendQuotations(data: {
    purchase_request_id: string;
    total_estimated_value: number;
    quotations: any[];
  }) {
    return this.request<any>('/api/assistant/recommend-quotations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Sourcing & Suppliers
  public async listSuppliers() {
    return this.request<any[]>('/api/suppliers');
  }

  public async getSupplier(supplierId: string) {
    return this.request<any>(`/api/suppliers/${encodeURIComponent(supplierId)}`);
  }

  public async createSupplier(data: { name: string; taxCode?: string; contact?: string }) {
    return this.request<any>('/api/suppliers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Quotations
  public async listQuotations(prId?: string) {
    const url = prId ? `/api/quotations?purchaseRequestId=${encodeURIComponent(prId)}` : '/api/quotations';
    return this.request<any[]>(url);
  }

  public async getQuotation(quotationId: string) {
    return this.request<any>(`/api/quotations/${encodeURIComponent(quotationId)}`);
  }

  public async listQuotationsForPR(prId: string) {
    return this.request<any[]>(`/api/purchase-requests/${encodeURIComponent(prId)}/quotations`);
  }

  public async createQuotation(data: {
    purchaseRequestId: string;
    supplierId: string;
    totalAmount: number;
    quantity: number;
    deliveryDays: number;
    warrantyTerms?: string;
    fileUrl?: string;
  }) {
    return this.request<any>('/api/quotations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async compareQuotations(purchaseRequestId: string) {
    return this.request<any[]>('/api/quotations/compare', {
      method: 'POST',
      body: JSON.stringify({ purchaseRequestId }),
    });
  }

  // Purchase Orders & Receiving
  public async createPO(data: { purchaseRequestId: string; quotationId: string }) {
    return this.request<any>('/api/po', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async listPOs() {
    return this.request<any[]>('/api/po');
  }

  public async receiveGoods(data: {
    purchaseOrderId: string;
    receivedQty: number;
    fileUrl?: string;
    receivedItems?: string;
  }) {
    return this.request<any>('/api/receiving', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async listReceivings(purchaseOrderId?: string) {
    const url = purchaseOrderId ? `/api/receiving?purchaseOrderId=${encodeURIComponent(purchaseOrderId)}` : '/api/receiving';
    return this.request<any[]>(url);
  }
}

export const api = new ApiClient();
