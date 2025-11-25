// Types for منهج AI Mini App

export interface User {
  id: string;
  telegram_id: number;
  name: string;
  education_stage: string;
  country: string;
  verification_code: string;
  points: number;
  riyal: number;
  is_premium: boolean;
  is_gift_premium: boolean;
  is_manager: boolean;
  successful_referrals: number;
  referral_code?: string;
  questions_count: number;
  ads_response_count: number;
  last_activity: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  link: string;
  description: string;
  points: number;
  is_active: boolean;
  created_at: string;
  completion_count?: number;
}

export interface CompletedTask {
  id: string;
  user_id: number;
  task_id: number;
  completed_at: string;
}

export interface Question {
  id: string;
  user_id: number;
  question: string;
  question_type: string;
  created_at: string;
}

export interface Transfer {
  id: string;
  sender_id: number;
  receiver_id: number;
  amount: number;
  transfer_type: 'riyal' | 'points';
  created_at: string;
}

export interface SupportMessage {
  id: string;
  user_id: number;
  message: string;
  reply?: string;
  is_answered: boolean;
  created_at: string;
  replied_at?: string;
}

export interface AppSettings {
  id: number;
  setting_key: string;
  setting_value: string;
  description?: string;
  updated_at: string;
}

export interface LeaderboardEntry {
  name: string;
  points: number;
  riyal: number;
  successful_referrals: number;
  questions_count: number;
  rank: number;
}

export interface AppStatistics {
  total_users: number;
  premium_users: number;
  new_users_today: number;
  total_points: number;
  total_riyal: number;
  total_questions: number;
  total_completed_tasks: number;
}

// Store States
export interface UserStore {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  updateUser: (updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  login: (telegramUser: any) => Promise<void>;
  logout: () => void;
}

export interface AppStore {
  theme: 'light' | 'dark';
  language: 'ar';
  currentScreen: string;
  isOnline: boolean;
  statistics: AppStatistics | null;
  settings: Record<string, string>;
  setTheme: (theme: 'light' | 'dark') => void;
  setCurrentScreen: (screen: string) => void;
  setOnlineStatus: (online: boolean) => void;
  setStatistics: (stats: AppStatistics) => void;
  setSettings: (settings: Record<string, string>) => void;
}

export interface TasksStore {
  tasks: Task[];
  completedTaskIds: number[];
  isLoading: boolean;
  setTasks: (tasks: Task[]) => void;
  setCompletedTasks: (taskIds: number[]) => void;
  completeTask: (taskId: number) => Promise<boolean>;
  setLoading: (loading: boolean) => void;
}

export interface ChatStore {
  messages: ChatMessage[];
  isTyping: boolean;
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  setTyping: (typing: boolean) => void;
  setLoading: (loading: boolean) => void;
  sendQuestion: (question: string) => Promise<void>;
  clearMessages: () => void;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: number;
  isError?: boolean;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ConvertPointsRequest {
  user_id: number;
  points: number;
}

export interface TransferRiyalRequest {
  sender_id: number;
  receiver_code: string;
  amount: number;
}

export interface BuyPremiumRequest {
  user_id: number;
}

export interface CompleteTaskRequest {
  user_id: number;
  task_id: number;
}

// Telegram WebApp Types
export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    start_param?: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: {
    bg_color: string;
    text_color: string;
    hint_color: string;
    link_color: string;
    button_color: string;
    button_text_color: string;
  };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  isClosingConfirmationEnabled: boolean;
  BackButton: {
    isVisible: boolean;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
  };
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText: (text: string) => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
  };
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  ready: () => void;
  expand: () => void;
  close: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  onEvent: (eventType: string, eventHandler: () => void) => void;
  offEvent: (eventType: string, eventHandler: () => void) => void;
  sendData: (data: string) => void;
  openLink: (url: string) => void;
  openTelegramLink: (url: string) => void;
  openInvoice: (url: string, callback?: (status: string) => void) => void;
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}