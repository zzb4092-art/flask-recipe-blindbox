<template>
  <div class="app-root">
    <!-- ===================================================== -->
    <!--  Header                                                  -->
    <!-- ===================================================== -->
    <header class="app-header" :class="{ 'header-scrolled': scrolled }">
      <div class="header-inner">
        <div class="header-brand" @click="goHome">
          <div class="brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7H6a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M10 12v8"/><path d="M14 12v8"/><path d="M4 12h16"/></svg>
          </div>
          <span class="brand-name">知味</span>
        </div>
        <div class="header-actions">
          <button v-if="!isLoggedIn" class="btn-login" @click="showLogin = true">登录 / 注册</button>
          <span v-else class="badge-logged">已登录</span>
          <div
            class="avatar-btn"
            @click="isLoggedIn ? setPage('user') : (showLogin = true)"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
        </div>
      </div>
    </header>

    <!-- ===================================================== -->
    <!--  Login Modal                                             -->
    <!-- ===================================================== -->
    <Teleport to="body">
      <div v-if="showLogin" class="login-overlay" @click.self="showLogin = false">
        <div class="login-card">
          <div class="login-bg-deco"></div>
          <button class="login-close" @click="showLogin = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
          <div class="login-icon-wrap">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7H6a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M10 12v8"/><path d="M14 12v8"/><path d="M4 12h16"/></svg>
          </div>
          <h2 class="login-title">{{ isLoginMode ? '欢迎回到知味' : '加入知味，探索美食' }}</h2>
          <p class="login-subtitle">{{ isLoginMode ? '登录以访问你的私人菜谱与常去餐馆' : '注册账号，定制你的专属美食数据库' }}</p>

          <div class="login-fields">
            <div class="login-input-wrap">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a8a29e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
              <input v-model="loginForm.username" type="text" placeholder="用户名" class="login-input" />
            </div>
            <div class="login-input-wrap">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a8a29e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              <input v-model="loginForm.password" type="password" placeholder="密码" class="login-input" @keydown.enter="handleLogin" />
            </div>
          </div>

          <button class="login-submit-btn" :disabled="loginLoading" @click="handleLogin">
            {{ loginLoading ? '请稍候…' : (isLoginMode ? '登 录' : '注 册') }}
          </button>

          <p class="login-switch">
            {{ isLoginMode ? '还没有账号？' : '已有账号？' }}
            <button @click="isLoginMode = !isLoginMode">{{ isLoginMode ? '立即注册' : '直接登录' }}</button>
          </p>
        </div>
      </div>
    </Teleport>

    <!-- ===================================================== -->
    <!--  Home Page                                               -->
    <!-- ===================================================== -->
    <template v-if="currentPage === 'home'">
      <!-- Hero -->
      <section class="hero">
        <div class="hero-glow hero-glow--top"></div>
        <div class="hero-glow hero-glow--side"></div>
        <div class="hero-float hero-float--tl">
          <svg viewBox="0 0 100 100" class="hero-svg" xmlns="http://www.w3.org/2000/svg">
            <path d="M50 15 Q60 5 70 20 Q55 25 50 20 Q45 25 30 20 Q40 5 50 15 Z" fill="#4ade80"/><circle cx="50" cy="55" r="35" fill="#ff7e67"/><circle cx="40" cy="40" r="8" fill="#ff9e8b" opacity="0.6"/><circle cx="40" cy="50" r="3.5" fill="#333"/><circle cx="60" cy="50" r="3.5" fill="#333"/><circle cx="32" cy="55" r="4" fill="#ff5a40" opacity="0.5"/><circle cx="68" cy="55" r="4" fill="#ff5a40" opacity="0.5"/><path d="M45 58 Q50 63 55 58" stroke="#333" strokeWidth="2" fill="none" strokeLinecap="round"/>
          </svg>
        </div>
        <div class="hero-float hero-float--tr">
          <svg viewBox="0 0 100 100" class="hero-svg" xmlns="http://www.w3.org/2000/svg">
            <path d="M50 20 C70 15,85 30,80 50 C75 75,60 85,40 80 C15 75,10 50,25 30 C35 15,40 25,50 20 Z" fill="#fff" filter="drop-shadow(0px 4px 4px rgba(0,0,0,0.05))"/><circle cx="45" cy="50" r="18" fill="#ffc75f"/><circle cx="40" cy="42" r="5" fill="#ffe099" opacity="0.8"/><circle cx="40" cy="48" r="2.5" fill="#555"/><circle cx="50" cy="48" r="2.5" fill="#555"/><path d="M42 53 Q45 56 48 53" stroke="#555" strokeWidth="1.5" fill="none" strokeLinecap="round"/><path d="M44 54 Q45 58 46 54 Z" fill="#ff7e67"/>
          </svg>
        </div>
        <div class="hero-float hero-float--bl">
          <svg viewBox="0 0 100 100" class="hero-svg hero-svg--sm" xmlns="http://www.w3.org/2000/svg">
            <rect x="25" y="30" width="50" height="45" rx="20" transform="rotate(-10 50 50)" fill="#e5aa70"/><circle cx="35" cy="40" r="3" fill="#c48a52" opacity="0.6"/><circle cx="65" cy="65" r="4" fill="#c48a52" opacity="0.6"/><circle cx="60" cy="35" r="2" fill="#c48a52" opacity="0.6"/><circle cx="35" cy="60" r="2.5" fill="#c48a52" opacity="0.6"/><circle cx="42" cy="50" r="3" fill="#4a3b2c"/><circle cx="58" cy="50" r="3" fill="#4a3b2c"/><circle cx="35" cy="55" r="4" fill="#ff8a66" opacity="0.4"/><circle cx="65" cy="55" r="4" fill="#ff8a66" opacity="0.4"/><path d="M47 55 Q50 58 53 55" stroke="#4a3b2c" strokeWidth="2" fill="none" strokeLinecap="round"/>
          </svg>
        </div>

        <div class="hero-content">
          <div class="hero-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#f97316" stroke="#f97316" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
            懂你的胃，更懂你的生活
          </div>
          <h1 class="hero-title">
            今天吃什么？<br />
            <span class="hero-title-accent">不再是每天的世纪难题</span>
          </h1>
          <p class="hero-desc">
            从冰箱剩余食材一键反查菜谱，到个性化盲盒摇号选餐厅。记录你的私房味道，打造属于你的智能美食指南。
          </p>
          <button class="hero-cta" @click="setPage('fridge')">
            开始探索美食
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </button>
        </div>
      </section>

      <!-- Feature Cards -->
      <section class="features">
        <div class="features-head">
          <h2>四大核心功能，满足你的味蕾</h2>
          <div class="features-divider"></div>
        </div>
        <div class="features-grid">
          <div class="feat-card feat-card--green" @click="setPage('fridge')">
            <div class="feat-card-deco"></div>
            <div class="feat-icon feat-icon--green">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </div>
            <h3>清空冰箱计划</h3>
            <p>输入已有食材（如：番茄、鸡蛋），智能检索相匹配的菜品。包含食材别名自动识别，并提供详细的用量与烹饪步骤。</p>
            <span class="feat-link feat-link--green">使用食材找菜谱 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
          </div>

          <div class="feat-card feat-card--orange" @click="setPage('blindbox')">
            <div class="feat-card-deco"></div>
            <div class="feat-icon feat-icon--orange">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="4"/><path d="M8 8h.01"/><path d="M16 8h.01"/><path d="M12 12h.01"/><path d="M8 16h.01"/><path d="M16 16h.01"/></svg>
            </div>
            <h3>命运转盘选餐厅</h3>
            <p>建立你的私人常去餐馆库。支持场景权重过滤（如不想吃辣、控制预算、夜宵推荐），趣味抽奖动画解决选择困难症。</p>
            <span class="feat-link feat-link--orange">开始抽取盲盒 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
          </div>

          <div class="feat-card feat-card--rose" @click="handleAuthGate('upload')">
            <div class="feat-card-deco"></div>
            <div class="feat-icon feat-icon--rose">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 18a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/><path d="M16 6H8a2 2 0 0 0-2 2v1"/></svg>
            </div>
            <h3>我的私房菜谱</h3>
            <p>上传你的独家秘方，记录菜名、所需食材及分量、详细步骤和成品图。你的私房菜谱将在检索时优先为你展现。</p>
            <span class="feat-link feat-link--rose">上传我的拿手菜 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
          </div>

          <div class="feat-card feat-card--blue" @click="handleAuthGate('user')">
            <div class="feat-card-deco"></div>
            <div class="feat-icon feat-icon--blue">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <h3>个人中心与买菜清单</h3>
            <p>一站式管理您的个人数据。保存收藏的餐馆、创建自动化的买菜清单，维护属于您的基础美食数据库。</p>
            <span class="feat-link feat-link--blue">进入个人中心 <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg></span>
          </div>
        </div>
      </section>
    </template>

    <!-- ===================================================== -->
    <!--  Fridge Plan Page                                        -->
    <!-- ===================================================== -->
    <template v-if="currentPage === 'fridge'">
      <section class="sub-page">
        <button class="back-btn" @click="goHome">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          返回主页
        </button>
        <div class="sub-head">
          <div class="sub-icon sub-icon--green">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          </div>
          <div>
            <h1>清空冰箱计划</h1>
            <p>输入你拥有的食材，发现能做什么美味大餐</p>
          </div>
        </div>

        <!-- Ingredient input -->
        <div class="white-card fridge-input-card">
          <h2 class="card-label">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7H6a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M10 12v8"/><path d="M14 12v8"/><path d="M4 12h16"/></svg>
            我有的食材
          </h2>
          <div class="fridge-input-row">
            <input
              v-model="fridgeInput"
              type="text"
              placeholder="输入食材，例如：土豆、牛肉..."
              class="fridge-text-input"
              @keydown.enter="addIngredient"
            />
            <button class="btn-green" @click="addIngredient">添加</button>
          </div>
          <div class="fridge-tags">
            <span
              v-for="ing in fridgeIngredients"
              :key="ing"
              class="fridge-tag"
            >
              {{ ing }}
              <button @click="removeIngredient(ing)"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></button>
            </span>
            <span v-if="fridgeIngredients.length === 0" class="fridge-empty-hint">还没有添加任何食材哦，快来输入吧～</span>
          </div>
          <div class="fridge-suggest">
            <span>猜你有：</span>
            <button v-for="s in suggestions" :key="s" @click="quickAdd(s)">+ {{ s }}</button>
          </div>
        </div>

        <!-- Results -->
        <div class="results-section">
          <h2 class="results-head">
            为你找到的菜谱
            <span class="results-badge" v-if="recipes.length">{{ recipes.length }} 个结果</span>
          </h2>
          <div v-if="searchLoading" class="loading-block">
            <div class="spinner"></div>
            <p>正在疯狂搜索附近美食...</p>
          </div>
          <div v-else-if="!searched" class="empty-block">
            <p>从上方添加食材，看看能做出什么好菜！</p>
          </div>
          <div v-else-if="recipes.length === 0" class="empty-block">
            <p>冰箱里的食材还不够…试试加点别的吧！</p>
          </div>
          <div v-else class="recipe-grid">
            <div v-for="r in recipes" :key="r.id" class="recipe-card">
              <div class="recipe-card-img">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#d6d3d1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7H6a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M10 12v8"/><path d="M14 12v8"/><path d="M4 12h16"/></svg>
              </div>
              <div class="recipe-card-body">
                <div class="recipe-card-top">
                  <h3>{{ r.title }}</h3>
                  <span class="match-badge" :class="r.match_count === r.total_ingredients ? 'match-full' : 'match-partial'">
                    匹配度 {{ Math.round((r.match_count / r.total_ingredients) * 100) }}%
                  </span>
                </div>
                <div class="recipe-ing-tags">
                  <span v-for="ing in r.ingredients" :key="ing" class="recipe-ing-tag">{{ ing }}</span>
                </div>
                <details class="recipe-steps-detail">
                  <summary>📝 查看烹饪步骤</summary>
                  <pre class="recipe-steps-text">{{ r.steps }}</pre>
                </details>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ===================================================== -->
    <!--  Restaurant Blindbox Page                                -->
    <!-- ===================================================== -->
    <template v-if="currentPage === 'blindbox'">
      <section class="sub-page">
        <button class="back-btn" @click="goHome">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          返回主页
        </button>
        <div class="sub-head sub-head--center">
          <div class="sub-icon sub-icon--orange sub-icon--tilt">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="4"/><path d="M8 8h.01"/><path d="M16 8h.01"/><path d="M12 12h.01"/><path d="M8 16h.01"/><path d="M16 16h.01"/></svg>
          </div>
          <div>
            <h1>命运转盘选餐厅</h1>
            <p>纠结吃什么？设定条件，把决定权交给命运吧！</p>
          </div>
        </div>

        <div class="white-card blindbox-card">
          <!-- Filters -->
          <div class="blindbox-filters">
            <div class="blindbox-tags">
              <h3>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                场景标签
              </h3>
              <div class="blindbox-tag-list">
                <button
                  v-for="tag in blindboxTags"
                  :key="tag"
                  :class="['blindbox-tag', { 'blindbox-tag--active': activeTags.includes(tag) }]"
                  @click="toggleTag(tag)"
                >{{ tag }}</button>
              </div>
            </div>
            <div class="blindbox-selects">
              <div class="blindbox-select-item">
                <label>💰 预算范围</label>
                <select v-model="budget" class="blindbox-native-select">
                  <option value="">不限</option>
                  <option value="low">人均 30 以下</option>
                  <option value="mid">人均 30 - 80</option>
                  <option value="high">人均 80 以上</option>
                </select>
              </div>
              <div class="blindbox-select-item">
                <label>🌤️ 当前天气</label>
                <select v-model="weather" class="blindbox-native-select">
                  <option value="">☀️ 晴天</option>
                  <option value="雨天">🌧️ 雨天</option>
                  <option value="寒冷">🥶 寒冷</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Draw area -->
          <div class="blindbox-draw-area">
            <div v-if="blindboxLoading" class="blindbox-spinning">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spin-icon"><rect width="18" height="18" x="3" y="3" rx="4"/><path d="M8 8h.01"/><path d="M16 8h.01"/><path d="M12 12h.01"/><path d="M8 16h.01"/><path d="M16 16h.01"/></svg>
              <p>正在疯狂搜索附近美食...</p>
            </div>
            <div v-else-if="luckyRestaurant" class="blindbox-result">
              <div class="blindbox-result-badge">命中注定就是它</div>
              <h2>{{ luckyRestaurant.name }}</h2>
              <p class="blindbox-result-desc">{{ luckyRestaurant.price_range || '丰俭由人' }}</p>
              <div class="blindbox-result-meta">
                <span v-for="t in luckyRestaurant.tags.split(',')" :key="t" class="blindbox-result-tag">{{ t }}</span>
              </div>
              <div v-if="luckyRestaurant.boosts.length" class="blindbox-boosts">
                <div v-for="(b, i) in luckyRestaurant.boosts" :key="i" class="blindbox-boost-item">{{ b }}</div>
              </div>
            </div>
            <div v-else class="blindbox-empty">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#d6d3d1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
              <p>点击下方按钮开始抽取</p>
            </div>
          </div>

          <!-- Buttons -->
          <div class="blindbox-btns">
            <button
              class="btn-draw"
              :class="{ 'btn-draw--disabled': blindboxLoading }"
              :disabled="blindboxLoading"
              @click="doBlindbox"
            >{{ luckyRestaurant ? '不满意，再抽一次' : '开 始 抽 取' }}</button>
            <button v-if="luckyRestaurant && !blindboxLoading" class="btn-confirm">就决定是你了！</button>
          </div>
        </div>
      </section>
    </template>

    <!-- ===================================================== -->
    <!--  Recipe Upload Page                                      -->
    <!-- ===================================================== -->
    <template v-if="currentPage === 'upload'">
      <section class="sub-page">
        <button class="back-btn" @click="goHome">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          返回主页
        </button>
        <div class="sub-head">
          <div class="sub-icon sub-icon--rose">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f43f5e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 18a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/><path d="M16 6H8a2 2 0 0 0-2 2v1"/></svg>
          </div>
          <div>
            <h1>上传私房菜谱</h1>
            <p>记录你的独家秘方，建立个人美食库</p>
          </div>
        </div>

        <div class="white-card upload-card">
          <div class="upload-form">
            <label class="upload-label">菜品名称</label>
            <input v-model="uploadForm.title" type="text" placeholder="例如：奶奶的红烧肉" class="upload-input" />

            <label class="upload-label">所需食材 <span class="upload-label-hint">（多个食材用逗号分隔）</span></label>
            <input v-model="uploadForm.ingredients" type="text" placeholder="例如：五花肉,冰糖,酱油" class="upload-input" />

            <label class="upload-label">烹饪步骤</label>
            <textarea v-model="uploadForm.steps" rows="6" placeholder="1. 五花肉切块焯水&#10;2. 炒糖色…&#10;3. …" class="upload-textarea"></textarea>

            <button class="btn-upload" :disabled="uploadLoading" @click="doUpload">
              {{ uploadLoading ? '上传中…' : '保存并发布菜谱' }}
            </button>
          </div>
        </div>
      </section>
    </template>

    <!-- ===================================================== -->
    <!--  User Center Page                                        -->
    <!-- ===================================================== -->
    <template v-if="currentPage === 'user'">
      <section class="sub-page">
        <button class="back-btn" @click="goHome">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          返回主页
        </button>

        <div class="user-layout">
          <div class="user-sidebar">
            <div class="user-avatar-card">
              <div class="user-avatar-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <h2>{{ loggedInUser }}</h2>
              <p>已加入</p>
              <div class="user-stats">
                <div><strong>{{ myRecipesCount }}</strong><span>贡献菜谱</span></div>
                <div><strong>{{ myRestaurantsCount }}</strong><span>收藏餐厅</span></div>
              </div>
            </div>
          </div>

          <div class="user-main">
            <div class="user-tabs">
              <button :class="['user-tab', { active: userTab === 'list' }]" @click="userTab = 'list'">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                我的菜谱
              </button>
              <button :class="['user-tab', { active: userTab === 'restaurants' }]" @click="userTab = 'restaurants'">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
                我的餐馆
              </button>
            </div>

            <div class="user-content-card">
              <template v-if="userTab === 'list'">
                <div v-if="myRecipes.length === 0" class="user-empty">
                  <p>还没有上传过私房菜谱</p>
                  <button class="btn-rose-outline" @click="setPage('upload')">去上传</button>
                </div>
                <div v-else class="user-recipe-list">
                  <div v-for="r in myRecipes" :key="r.id" class="user-recipe-item">
                    <span class="user-recipe-name">{{ r.title }}</span>
                    <span class="user-recipe-meta">{{ r.ingredients.join('、') }}</span>
                  </div>
                </div>
              </template>
              <template v-else>
                <div v-if="myRestaurants.length === 0" class="user-empty">
                  <p>还没有收藏餐厅哦</p>
                  <button class="btn-rose-outline" @click="setPage('blindbox')">去抽取</button>
                </div>
                <div v-else class="user-recipe-list">
                  <div v-for="r in myRestaurants" :key="r.id" class="user-recipe-item">
                    <span class="user-recipe-name">{{ r.name }}</span>
                    <span class="user-recipe-meta">{{ r.tags }}</span>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ===================================================== -->
    <!--  Footer                                                  -->
    <!-- ===================================================== -->
    <footer class="app-footer">
      <div class="footer-inner">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 7H6a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/><path d="M10 12v8"/><path d="M14 12v8"/><path d="M4 12h16"/></svg>
        <span>知味</span>
      </div>
      <p>© 2026 知味 - 智能美食与盲盒点餐系统</p>
    </footer>
  </div>
</template>

<!-- ================================================================ -->
<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// Types
interface RecipeItem {
  id: number; title: string; steps: string; is_custom: boolean
  user_id: number | null; match_count: number; total_ingredients: number
  ingredients: string[]
}
interface RestaurantItem {
  id: number; name: string; tags: string; is_spicy: boolean
  price_range: string; weight: number; boosts: string[]
}

// ═══════════════ App State ═══════════════
const scrolled = ref(false)
const currentPage = ref('home')
const showLogin = ref(false)
const isLoggedIn = ref(false)
const isLoginMode = ref(true)
const loggedInUser = ref('美食家_007')
const loginLoading = ref(false)
const loginForm = reactive({ username: '', password: '' })

const onScroll = () => { scrolled.value = window.scrollY > 20 }
onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

function goHome() { currentPage.value = 'home' }
function setPage(p: string) { currentPage.value = p; window.scrollTo(0, 0) }
function handleAuthGate(page: string) {
  if (!isLoggedIn.value) { showLogin.value = true; return }
  setPage(page)
}

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) return
  loginLoading.value = true
  try {
    const url = isLoginMode.value
      ? 'http://127.0.0.1:5000/api/auth/login'
      : 'http://127.0.0.1:5000/api/auth/register'
    const { data } = await axios.post(url, loginForm)
    if (data.code === 200) {
      isLoggedIn.value = true
      loggedInUser.value = loginForm.username
      showLogin.value = false
      loginForm.username = ''; loginForm.password = ''
    } else {
      alert(data.message)
    }
  } catch { alert('请求失败，请检查后端服务') }
  finally { loginLoading.value = false }
}

// ═══════════════ Fridge / Search ═══════════════
const fridgeInput = ref('')
const fridgeIngredients = ref<string[]>([])
const suggestions = ['洋葱', '大蒜', '青椒', '猪肉']
const recipes = ref<RecipeItem[]>([])
const searched = ref(false)
const searchLoading = ref(false)

function addIngredient() {
  const v = fridgeInput.value.trim()
  if (v && !fridgeIngredients.value.includes(v)) fridgeIngredients.value.push(v)
  fridgeInput.value = ''
}
function removeIngredient(item: string) {
  fridgeIngredients.value = fridgeIngredients.value.filter(i => i !== item)
}
function quickAdd(item: string) {
  if (!fridgeIngredients.value.includes(item)) fridgeIngredients.value.push(item)
}

async function fetchRecipes() {
  const q = fridgeIngredients.value.join(',')
  if (!q) return
  searchLoading.value = true
  try {
    const { data } = await axios.get<{ code: number; data: RecipeItem[] }>(
      'http://127.0.0.1:5000/api/recipes/search',
      { params: { ingredients: q, user_id: isLoggedIn.value ? 1 : undefined } },
    )
    if (data.code === 200) recipes.value = data.data
    searched.value = true
  } catch { alert('搜索失败，请检查后端服务') }
  finally { searchLoading.value = false }
}

// ═══════════════ Blindbox ═══════════════
const blindboxTags = ['今天不吃辣', '夜宵时段', '适合聚餐', '距离近', '随便对付']
const activeTags = ref<string[]>([])
const blindboxLoading = ref(false)
const luckyRestaurant = ref<RestaurantItem | null>(null)
const budget = ref('')
const weather = ref('')

function toggleTag(tag: string) {
  const i = activeTags.value.indexOf(tag)
  if (i >= 0) activeTags.value.splice(i, 1)
  else activeTags.value.push(tag)
}

async function doBlindbox() {
  blindboxLoading.value = true
  luckyRestaurant.value = null
  try {
    const excludeSpicy = activeTags.value.includes('今天不吃辣')
    const { data } = await axios.post<{ code: number; data: RestaurantItem | null; message?: string }>(
      'http://127.0.0.1:5000/api/restaurants/blindbox',
      {
        user_id: 1,
        exclude_spicy: excludeSpicy,
        user_weather: weather.value || null,
        budget: budget.value || null,
      },
    )
    if (data.code === 200 && data.data) {
      luckyRestaurant.value = data.data
    }
  } catch { alert('抽选失败，请检查后端服务') }
  finally { blindboxLoading.value = false }
}

// ═══════════════ Upload ═══════════════
const uploadForm = reactive({ title: '', ingredients: '', steps: '' })
const uploadLoading = ref(false)

async function doUpload() {
  if (!uploadForm.title || !uploadForm.ingredients || !uploadForm.steps) {
    alert('请填写完整信息'); return
  }
  uploadLoading.value = true
  try {
    const { data } = await axios.post<{ code: number; message: string }>(
      'http://127.0.0.1:5000/api/recipes/custom',
      { user_id: 1, ...uploadForm },
    )
    if (data.code === 201) {
      alert('私房菜谱上传成功！')
      uploadForm.title = ''; uploadForm.ingredients = ''; uploadForm.steps = ''
    } else { alert(data.message) }
  } catch { alert('上传失败，请检查后端服务') }
  finally { uploadLoading.value = false }
}

// ═══════════════ User Center ═══════════════
const userTab = ref('list')
// Load user's custom recipes & restaurants
const myRecipes = ref<RecipeItem[]>([])
const myRestaurants = ref<RestaurantItem[]>([])
const myRecipesCount = computed(() => myRecipes.value.length)
const myRestaurantsCount = computed(() => myRestaurants.value.length)

async function loadUserData() {
  try {
    // Search with user's custom recipes
    const { data: rData } = await axios.get('http://127.0.0.1:5000/api/recipes/search', {
      params: { ingredients: '', user_id: 1 },
    }).catch(() => ({ data: { data: [] } }))
    myRecipes.value = (rData.data || []).filter((r: RecipeItem) => r.is_custom)
  } catch { /* ignore */ }
}

// Watch page changes to auto-search / load data
import { watch } from 'vue'
watch(currentPage, (val) => {
  if (val === 'user' && isLoggedIn.value) loadUserData()
  if (val === 'fridge' && fridgeIngredients.value.length > 0) fetchRecipes()
})
// Auto-search when ingredients change
watch(fridgeIngredients, () => {
  if (fridgeIngredients.value.length > 0 && currentPage.value === 'fridge') {
    fetchRecipes()
  }
}, { deep: true })
</script>

<!-- ================================================================ -->
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;800;900&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;background:#FFFDF9;color:#292524;-webkit-font-smoothing:antialiased}
</style>

<style scoped>
/* ═══════════════ Root ═══════════════ */
.app-root{min-height:100vh;display:flex;flex-direction:column}

/* ═══════════════ Header ═══════════════ */
.app-header{position:fixed;top:0;width:100%;z-index:40;transition:all .3s;padding:20px 0;background:transparent}
.app-header.header-scrolled{background:rgba(255,255,255,.8);backdrop-filter:blur(12px);box-shadow:0 1px 8px rgba(0,0,0,.04);padding:12px 0}
.header-inner{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;justify-content:space-between;align-items:center}
.header-brand{display:flex;align-items:center;gap:8px;cursor:pointer}
.brand-icon{width:40px;height:40px;background:linear-gradient(135deg,#f97316,#ef4444);border-radius:12px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(249,115,22,.3)}
.brand-name{font-size:22px;font-weight:800;background:linear-gradient(135deg,#ea580c,#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:2px}
.header-actions{display:flex;align-items:center;gap:16px}
.btn-login{font-size:14px;font-weight:500;color:#78716c;background:none;border:none;cursor:pointer;transition:color .2s}
.btn-login:hover{color:#f97316}
.badge-logged{font-size:13px;font-weight:700;color:#f97316;background:#fff7ed;padding:4px 12px;border-radius:999px;display:none}
@media(min-width:640px){.badge-logged{display:block}}
.avatar-btn{width:40px;height:40px;background:#fff7ed;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#ea580c;cursor:pointer;border:2px solid transparent;transition:all .2s}
.avatar-btn:hover{background:#ffedd5;border-color:#fdba74}

/* ═══════════════ Login Modal ═══════════════ */
.login-overlay{position:fixed;inset:0;z-index:100;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(28,25,23,.15);backdrop-filter:blur(4px)}
.login-card{position:relative;width:100%;max-width:420px;background:#fff;border-radius:32px;box-shadow:0 25px 50px rgba(0,0,0,.15);padding:40px 32px;overflow:hidden}
.login-bg-deco{position:absolute;top:0;left:0;width:100%;height:120px;background:linear-gradient(180deg,#fff7ed,#fff1f2);z-index:0}
.login-close{position:absolute;top:16px;right:16px;padding:8px;border-radius:50%;background:rgba(255,255,255,.6);border:none;color:#a8a29e;cursor:pointer;z-index:1}
.login-close:hover{color:#44403c}
.login-icon-wrap{position:relative;z-index:1;width:64px;height:64px;background:#fff;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;box-shadow:0 4px 12px rgba(0,0,0,.06)}
.login-title{text-align:center;font-size:24px;font-weight:800;color:#292524;margin-bottom:4px;position:relative;z-index:1}
.login-subtitle{text-align:center;font-size:14px;color:#78716c;margin-bottom:24px;position:relative;z-index:1}
.login-fields{display:flex;flex-direction:column;gap:16px;margin-bottom:20px;position:relative;z-index:1}
.login-input-wrap{position:relative;display:flex;align-items:center}
.login-input-wrap svg{position:absolute;left:16px;pointer-events:none}
.login-input{width:100%;background:#fafaf9;border:1px solid #e7e5e4;border-radius:16px;padding:14px 16px 14px 48px;font-size:15px;color:#292524;outline:none;transition:all .2s}
.login-input:focus{border-color:#fdba74;box-shadow:0 0 0 4px rgba(251,146,60,.1)}
.login-submit-btn{width:100%;background:linear-gradient(135deg,#f97316,#ef4444);color:#fff;border:none;border-radius:16px;padding:15px;font-size:16px;font-weight:700;cursor:pointer;box-shadow:0 8px 24px rgba(249,115,22,.3);transition:all .2s;position:relative;z-index:1}
.login-submit-btn:hover{transform:translateY(-1px);box-shadow:0 12px 30px rgba(249,115,22,.4)}
.login-submit-btn:active{transform:scale(.97)}
.login-submit-btn:disabled{opacity:.6;cursor:not-allowed}
.login-switch{text-align:center;margin-top:20px;font-size:13px;color:#78716c}
.login-switch button{background:none;border:none;color:#f97316;font-weight:700;cursor:pointer;margin-left:4px}
.login-switch button:hover{text-decoration:underline}

/* ═══════════════ Hero ═══════════════ */
.hero{position:relative;padding:140px 24px 80px;overflow:hidden;text-align:center}
.hero-glow{position:absolute;border-radius:50%;filter:blur(80px);z-index:0}
.hero-glow--top{top:0;left:50%;transform:translateX(-50%);width:100%;max-width:900px;height:400px;background:rgba(255,237,213,.5);opacity:.7}
.hero-glow--side{top:80px;right:0;width:350px;height:350px;background:rgba(254,240,138,.4)}
.hero-float{position:absolute;z-index:1;display:none}
@media(min-width:768px){.hero-float{display:block}}
.hero-float--tl{top:100px;left:12%;animation:bounceFloat 4s ease-in-out infinite}
.hero-float--tr{top:60px;right:18%;animation:bounceFloat 5s ease-in-out infinite reverse}
.hero-float--bl{bottom:30px;left:22%;animation:bounceFloat 4.5s ease-in-out infinite}
.hero-svg{width:96px;height:96px;filter:drop-shadow(0 8px 16px rgba(0,0,0,.08));cursor:pointer;transition:transform .2s}
.hero-svg:hover{transform:scale(1.1)}
.hero-svg--sm{width:80px;height:80px}
@keyframes bounceFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-16px)}}
.hero-content{position:relative;z-index:2;max-width:720px;margin:0 auto}
.hero-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 18px;background:#fff7ed;border:1px solid #fed7aa;border-radius:999px;color:#c2410c;font-size:14px;font-weight:500;margin-bottom:24px}
.hero-title{font-size:40px;font-weight:900;color:#292524;line-height:1.2;margin-bottom:20px}
@media(min-width:768px){.hero-title{font-size:52px}}
@media(min-width:1024px){.hero-title{font-size:60px}}
.hero-title-accent{background:linear-gradient(135deg,#f97316,#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-desc{font-size:17px;color:#78716c;line-height:1.7;max-width:600px;margin:0 auto 36px}
.hero-cta{display:inline-flex;align-items:center;gap:8px;padding:16px 36px;background:linear-gradient(135deg,#f97316,#ef4444);color:#fff;border:none;border-radius:18px;font-size:18px;font-weight:700;cursor:pointer;box-shadow:0 10px 30px rgba(249,115,22,.35);transition:all .3s}
.hero-cta:hover{transform:translateY(-2px);box-shadow:0 16px 40px rgba(249,115,22,.45)}

/* ═══════════════ Features ═══════════════ */
.features{max-width:1200px;margin:0 auto;padding:0 24px 100px}
.features-head{text-align:center;margin-bottom:60px}
.features-head h2{font-size:30px;font-weight:800;color:#292524;margin-bottom:16px}
.features-divider{width:72px;height:6px;background:#f97316;border-radius:999px;margin:0 auto}
.features-grid{display:grid;grid-template-columns:1fr;gap:32px}
@media(min-width:768px){.features-grid{grid-template-columns:1fr 1fr}}
.feat-card{position:relative;background:#fff;border:1px solid #ffedd5;border-radius:28px;padding:32px;cursor:pointer;transition:all .3s;overflow:hidden}
.feat-card:hover{transform:translateY(-4px);box-shadow:0 20px 50px rgba(249,115,22,.1)}
.feat-card-deco{position:absolute;top:0;right:0;width:120px;height:120px;border-radius:0 0 0 120px;z-index:0}
.feat-card--green .feat-card-deco{background:linear-gradient(225deg,#f0fdf4,transparent)}
.feat-card--orange .feat-card-deco{background:linear-gradient(225deg,#fff7ed,transparent)}
.feat-card--rose .feat-card-deco{background:linear-gradient(225deg,#fff1f2,transparent)}
.feat-card--blue .feat-card-deco{background:linear-gradient(225deg,#eff6ff,transparent)}
.feat-card>*{position:relative;z-index:1}
.feat-icon{width:52px;height:52px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;transition:transform .3s}
.feat-card:hover .feat-icon{transform:scale(1.1)}
.feat-icon--green{background:#f0fdf4}
.feat-icon--orange{background:#fff7ed}
.feat-icon--rose{background:#fff1f2}
.feat-icon--blue{background:#eff6ff}
.feat-card h3{font-size:22px;font-weight:800;color:#292524;margin-bottom:10px}
.feat-card p{font-size:15px;color:#78716c;line-height:1.7;margin-bottom:20px}
.feat-link{display:inline-flex;align-items:center;gap:4px;font-size:14px;font-weight:600;transition:gap .2s}
.feat-card:hover .feat-link{gap:8px}
.feat-link--green{color:#16a34a}
.feat-link--orange{color:#ea580c}
.feat-link--rose{color:#f43f5e}
.feat-link--blue{color:#2563eb}

/* ═══════════════ Sub Pages ═══════════════ */
.sub-page{padding:120px 24px 80px;max-width:1000px;margin:0 auto;min-height:85vh}
.back-btn{display:inline-flex;align-items:center;gap:6px;color:#a8a29e;font-size:14px;font-weight:500;background:none;border:none;cursor:pointer;margin-bottom:32px;transition:color .2s}
.back-btn :deep(svg){transform:rotate(180deg)}
.back-btn:hover{color:#f97316}
.sub-head{display:flex;align-items:center;gap:16px;margin-bottom:36px}
.sub-head--center{text-align:center;flex-direction:column}
.sub-head--center h1{text-align:center}
.sub-icon{width:56px;height:56px;border-radius:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 12px rgba(0,0,0,.04)}
.sub-icon--tilt{transform:rotate(12deg)}
.sub-icon--green{background:#f0fdf4}
.sub-icon--orange{background:#fff7ed}
.sub-icon--rose{background:#fff1f2}
.sub-icon--blue{background:#eff6ff}
.sub-head h1{font-size:32px;font-weight:900;color:#292524;margin-bottom:4px}
.sub-head p{color:#78716c;font-size:15px}

/* ═══════════════ White Card ═══════════════ */
.white-card{background:#fff;border:1px solid #ffedd5;border-radius:28px;padding:28px 32px;box-shadow:0 8px 30px rgba(249,115,22,.04)}
.card-label{display:flex;align-items:center;gap:8px;font-size:17px;font-weight:700;color:#292524;margin-bottom:20px}

/* ═══════════════ Fridge ═══════════════ */
.fridge-input-row{display:flex;gap:12px;margin-bottom:20px}
.fridge-text-input{flex:1;background:#fafaf9;border:1px solid #e7e5e4;border-radius:16px;padding:14px 20px;font-size:15px;color:#292524;outline:none;transition:all .2s}
.fridge-text-input:focus{border-color:#86efac;box-shadow:0 0 0 4px rgba(134,239,172,.15)}
.btn-green{background:#22c55e;color:#fff;border:none;border-radius:16px;padding:14px 28px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 6px 16px rgba(34,197,94,.25);transition:all .2s;white-space:nowrap}
.btn-green:hover{background:#16a34a}
.fridge-tags{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px}
.fridge-tag{display:inline-flex;align-items:center;gap:6px;background:#fff7ed;border:1px solid #fed7aa;color:#c2410c;padding:6px 14px;border-radius:999px;font-size:14px;font-weight:500}
.fridge-tag button{background:none;border:none;color:inherit;cursor:pointer;padding:2px;display:flex;border-radius:50%;transition:all .2s}
.fridge-tag button:hover{color:#ef4444;background:rgba(239,68,68,.1)}
.fridge-empty-hint{color:#a8a29e;font-size:14px;padding:8px 0}
.fridge-suggest{display:flex;align-items:center;gap:8px;padding-top:20px;border-top:1px solid #f5f5f4;flex-wrap:wrap}
.fridge-suggest span{font-size:13px;color:#a8a29e}
.fridge-suggest button{font-size:13px;color:#78716c;background:none;border:none;padding:4px 8px;border-radius:8px;cursor:pointer;transition:all .2s}
.fridge-suggest button:hover{color:#16a34a;background:#f0fdf4}

/* ═══════════════ Results ═══════════════ */
.results-section{margin-top:32px}
.results-head{font-size:24px;font-weight:800;color:#292524;margin-bottom:24px;display:flex;align-items:center;gap:12px}
.results-badge{font-size:13px;font-weight:400;color:#fff;background:#22c55e;padding:4px 14px;border-radius:999px}
.loading-block,.empty-block{display:flex;flex-direction:column;align-items:center;padding:60px 0;color:#a8a29e}
.spinner{width:48px;height:48px;border:4px solid #ffedd5;border-top-color:#f97316;border-radius:50%;animation:spin .8s linear infinite;margin-bottom:16px}
@keyframes spin{to{transform:rotate(360deg)}}
.recipe-grid{display:flex;flex-direction:column;gap:20px}
.recipe-card{background:#fff;border:1px solid #f5f5f4;border-radius:24px;overflow:hidden;display:flex;transition:all .3s}
.recipe-card:hover{box-shadow:0 12px 36px rgba(249,115,22,.08);transform:translateY(-2px)}
.recipe-card-img{width:100px;background:linear-gradient(135deg,#fafaf9,#f5f5f4);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.recipe-card-body{flex:1;padding:20px}
.recipe-card-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.recipe-card-top h3{font-size:18px;font-weight:800;color:#292524}
.match-badge{font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;white-space:nowrap}
.match-full{background:#f0fdf4;color:#16a34a}
.match-partial{background:#fff7ed;color:#c2410c}
.recipe-ing-tags{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.recipe-ing-tag{font-size:12px;background:#fafaf9;border:1px solid #e7e5e4;padding:2px 10px;border-radius:999px;color:#78716c}
.recipe-steps-detail{margin-top:8px}
.recipe-steps-detail summary{font-size:13px;font-weight:600;color:#a8a29e;cursor:pointer}
.recipe-steps-text{white-space:pre-wrap;line-height:1.8;color:#57534e;font-size:13px;background:#fafaf9;padding:14px;border-radius:12px;margin-top:8px}

/* ═══════════════ Blindbox ═══════════════ */
.blindbox-card{border-color:#ffedd5}
.blindbox-filters{margin-bottom:28px}
.blindbox-tags{margin-bottom:18px}
.blindbox-tags h3{font-size:13px;font-weight:700;color:#a8a29e;text-transform:uppercase;letter-spacing:1px;display:flex;align-items:center;gap:6px;margin-bottom:12px}
.blindbox-tag-list{display:flex;flex-wrap:wrap;gap:10px}
.blindbox-tag{padding:8px 18px;border-radius:12px;font-size:14px;font-weight:500;background:#fafaf9;color:#78716c;border:none;cursor:pointer;transition:all .2s}
.blindbox-tag:hover{background:#fff7ed;color:#ea580c}
.blindbox-tag--active{background:#f97316;color:#fff;box-shadow:0 4px 12px rgba(249,115,22,.3)}
.blindbox-selects{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.blindbox-select-item{display:flex;flex-direction:column;gap:6px}
.blindbox-select-item label{font-size:13px;font-weight:700;color:#a8a29e}
.blindbox-native-select{width:100%;padding:12px 16px;background:#fafaf9;border:1px solid #e7e5e4;border-radius:14px;font-size:14px;color:#292524;outline:none;cursor:pointer;transition:all .2s;appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23a8a29e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;padding-right:40px}
.blindbox-native-select:focus{border-color:#fdba74;box-shadow:0 0 0 3px rgba(251,146,60,.1)}
.blindbox-draw-area{background:#fafaf9;border-radius:24px;padding:48px 24px;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:220px;margin-bottom:28px;border:1px solid #f5f5f4}
.blindbox-spinning,.blindbox-empty{text-align:center;color:#a8a29e}
.spin-icon{animation:spin .8s linear infinite;margin-bottom:16px}
.blindbox-result{text-align:center}
.blindbox-result-badge{display:inline-block;background:#fff7ed;color:#c2410c;padding:4px 14px;border-radius:999px;font-size:12px;font-weight:700;margin-bottom:12px}
.blindbox-result h2{font-size:28px;font-weight:900;color:#292524;margin-bottom:6px}
.blindbox-result-desc{color:#78716c;font-size:14px;margin-bottom:14px}
.blindbox-result-meta{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-bottom:12px}
.blindbox-result-tag{font-size:12px;color:#78716c;background:#fff;border:1px solid #e7e5e4;padding:2px 10px;border-radius:8px}
.blindbox-boosts{display:flex;flex-direction:column;gap:8px;margin-top:8px}
.blindbox-boost-item{font-size:13px;background:#f0fdf4;color:#16a34a;padding:8px 14px;border-radius:12px;border:1px solid #bbf7d0;text-align:center;font-weight:500}
.blindbox-btns{display:flex;justify-content:center;gap:16px;flex-wrap:wrap}
.btn-draw{padding:16px 40px;border-radius:18px;font-size:17px;font-weight:700;color:#fff;border:none;cursor:pointer;background:linear-gradient(135deg,#f97316,#ef4444);box-shadow:0 10px 30px rgba(249,115,22,.35);transition:all .3s}
.btn-draw:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 16px 40px rgba(249,115,22,.45)}
.btn-draw--disabled{background:#d6d3d1;box-shadow:none;cursor:not-allowed}
.btn-confirm{padding:16px 36px;border-radius:18px;font-size:17px;font-weight:700;color:#fff;border:none;cursor:pointer;background:#22c55e;box-shadow:0 10px 24px rgba(34,197,94,.25);transition:all .3s}
.btn-confirm:hover{transform:translateY(-2px);background:#16a34a}

/* ═══════════════ Upload ═══════════════ */
.upload-label{display:block;font-size:14px;font-weight:700;color:#292524;margin-bottom:6px;margin-top:20px}
.upload-label:first-child{margin-top:0}
.upload-label-hint{font-weight:400;color:#a8a29e;font-size:12px}
.upload-input{width:100%;background:#fafaf9;border:1px solid #e7e5e4;border-radius:14px;padding:14px 18px;font-size:15px;color:#292524;outline:none;transition:all .2s}
.upload-input:focus{border-color:#fda4af;box-shadow:0 0 0 4px rgba(251,113,133,.1)}
.upload-textarea{width:100%;background:#fafaf9;border:1px solid #e7e5e4;border-radius:14px;padding:14px 18px;font-size:15px;color:#292524;outline:none;resize:none;font-family:inherit;transition:all .2s}
.upload-textarea:focus{border-color:#fda4af;box-shadow:0 0 0 4px rgba(251,113,133,.1)}
.btn-upload{width:100%;margin-top:28px;padding:16px;border-radius:16px;font-size:17px;font-weight:700;color:#fff;border:none;cursor:pointer;background:linear-gradient(135deg,#f43f5e,#e11d48);box-shadow:0 8px 24px rgba(244,63,94,.25);transition:all .3s}
.btn-upload:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 14px 32px rgba(244,63,94,.35)}
.btn-upload:disabled{opacity:.6;cursor:not-allowed}

/* ═══════════════ User Center ═══════════════ */
.user-layout{display:grid;grid-template-columns:1fr;gap:24px}
@media(min-width:768px){.user-layout{grid-template-columns:280px 1fr}}
.user-avatar-card{background:#fff;border:1px solid #e7e5e4;border-radius:24px;padding:28px;text-align:center}
.user-avatar-icon{width:80px;height:80px;background:#eff6ff;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;border:3px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.06)}
.user-avatar-card h2{font-size:20px;font-weight:800;color:#292524}
.user-avatar-card>p{color:#a8a29e;font-size:13px;margin-bottom:20px}
.user-stats{display:flex;justify-content:space-around;border-top:1px solid #f5f5f4;padding-top:20px}
.user-stats div{text-align:center}
.user-stats strong{display:block;font-size:22px;font-weight:800;color:#292524}
.user-stats span{font-size:11px;color:#a8a29e}
.user-tabs{display:flex;gap:8px;background:#fff;border:1px solid #f5f5f4;border-radius:20px;padding:6px;margin-bottom:20px}
.user-tab{flex:1;padding:12px;border-radius:14px;font-size:14px;font-weight:600;color:#78716c;background:none;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;transition:all .2s}
.user-tab:hover{background:#fafaf9}
.user-tab.active{background:#eff6ff;color:#2563eb}
.user-content-card{background:#fff;border:1px solid #f5f5f4;border-radius:24px;padding:28px;min-height:300px}
.user-empty{text-align:center;padding:40px 0;color:#a8a29e}
.btn-rose-outline{margin-top:16px;padding:10px 24px;border-radius:14px;font-size:14px;font-weight:600;color:#f43f5e;background:#fff;border:1px solid #fecdd3;cursor:pointer;transition:all .2s}
.btn-rose-outline:hover{background:#fff1f2}
.user-recipe-list{display:flex;flex-direction:column;gap:12px}
.user-recipe-item{display:flex;justify-content:space-between;align-items:center;padding:16px;background:#fafaf9;border-radius:14px}
.user-recipe-name{font-weight:600;color:#292524}
.user-recipe-meta{font-size:12px;color:#a8a29e}

/* ═══════════════ Footer ═══════════════ */
.app-footer{background:#fff;border-top:1px solid #ffedd5;padding:32px 24px;text-align:center;margin-top:auto}
.footer-inner{display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:8px;font-size:18px;font-weight:700;color:#57534e}
.app-footer>p{font-size:13px;color:#a8a29e}
</style>
