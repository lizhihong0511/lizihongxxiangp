<template>
  <div class="app-shell">
    <main class="app-content">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>
    <nav class="tab-bar">
      <router-link to="/dashboard" class="tab" active-class="tab--active">
        <span class="tab-icon">🏠</span>
        <span class="tab-label">首页</span>
      </router-link>
      <router-link to="/qa" class="tab" active-class="tab--active">
        <span class="tab-icon">💬</span>
        <span class="tab-label">问答</span>
      </router-link>
      <router-link to="/practice" class="tab" active-class="tab--active">
        <span class="tab-icon">✏️</span>
        <span class="tab-label">练习</span>
      </router-link>
      <router-link to="/bank" class="tab" active-class="tab--active">
        <span class="tab-icon">📋</span>
        <span class="tab-label">题库</span>
      </router-link>
      <router-link to="/wrong" class="tab" active-class="tab--active">
        <span class="tab-icon">📝</span>
        <span class="tab-label">错题</span>
      </router-link>
      <router-link to="/profile" class="tab" active-class="tab--active">
        <span class="tab-icon">👤</span>
        <span class="tab-label">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
:root {
  --primary: #4f46e5;
  --primary-light: #eef2ff;
  --correct: #16a34a;
  --wrong: #dc2626;
  --bg: #f5f5f5;
  --card: #fff;
  --text: #1a1a2e;
  --text-secondary: #64748b;
  --border: #e2e8f0;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 16px;
  color: var(--text);
  background: var(--bg);
  -webkit-tap-highlight-color: transparent;
}

.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  max-width: 480px;
  margin: 0 auto;
  background: var(--bg);
  position: relative;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.tab-bar {
  display: flex;
  background: var(--card);
  border-top: 1px solid var(--border);
  padding-bottom: env(safe-area-inset-bottom, 0);
  flex-shrink: 0;
}

.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 11px;
  transition: color 0.2s;
  -webkit-tap-highlight-color: transparent;
}

.tab--active {
  color: var(--primary);
}

.tab-icon {
  font-size: 22px;
  margin-bottom: 2px;
}

.tab-label {
  line-height: 1;
}
</style>
