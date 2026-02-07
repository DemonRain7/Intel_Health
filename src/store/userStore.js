import { defineStore } from 'pinia';
import { supabase } from '../utils/supabase';

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    profile: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    tempUserId: null
  }),

  getters: {
    userId: (state) => state.user?.id || state.tempUserId || null,
    username: (state) =>
      state.user?.user_metadata?.username ||
      state.user?.email ||
      '访客用户'
  },

  actions: {
    async login(credentials) {
      this.loading = true;
      this.error = null;

      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: credentials.email,
          password: credentials.password
        });
        if (error) throw error;

        await this._setSession(data.session);
        return { success: true };
      } catch (err) {
        this.error = err.message || '登录失败，请稍后再试';
        return { success: false, message: this.error };
      } finally {
        this.loading = false;
      }
    },

    async register(userData) {
      this.loading = true;
      this.error = null;

      try {
        const { data, error } = await supabase.auth.signUp({
          email: userData.email,
          password: userData.password,
          options: { data: { username: userData.username } }
        });
        if (error) throw error;

        if (data.user) {
          await this._ensureProfile(data.user);
        }

        if (data.session) {
          await this._setSession(data.session);
        } else {
          this.user = data.user;
          this.isAuthenticated = false;
        }

        return { success: true };
      } catch (err) {
        this.error = err.message || '注册失败，请稍后再试';
        return { success: false, message: this.error };
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      await supabase.auth.signOut();
      this.user = null;
      this.profile = null;
      this.isAuthenticated = false;
      localStorage.removeItem('tempUserId');
    },

    async initAuth() {
      const { data } = await supabase.auth.getSession();

      if (data?.session?.user) {
        await this._setSession(data.session);
      } else {
        this.user = null;
        this.profile = null;
        this.isAuthenticated = false;
      }

      if (!this.user && !this.tempUserId) {
        const stored = localStorage.getItem('tempUserId');
        if (stored) {
          this.tempUserId = parseInt(stored, 10);
        } else {
          this.setTempUserId(Math.floor(Math.random() * 100000));
        }
      }
    },

    async _setSession(session) {
      this.user = session?.user || null;
      this.isAuthenticated = Boolean(session?.access_token);
      if (this.user) {
        await this._loadProfile(this.user);
      }
    },

    async _loadProfile(user) {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .single();

      if (!error && data) {
        this.profile = data;
      } else {
        this.profile = null;
      }
    },

    async _ensureProfile(user) {
      const { data } = await supabase
        .from('profiles')
        .select('user_id')
        .eq('user_id', user.id)
        .single();

      if (!data) {
        await supabase.from('profiles').insert({
          user_id: user.id
        });
      }
    },

    setTempUserId(id) {
      this.tempUserId = id;
      localStorage.setItem('tempUserId', id.toString());
    }
  }
});
