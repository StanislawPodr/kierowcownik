<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { loginUser } from '../api/auth'
import type { LoginPayload } from '../utils/auth'
import { useUserProgress } from '../composables/useUserProgress'

const router = useRouter()
const { loadProgress, saveProgress, clearAll } = useUserProgress()

const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const successMsg = ref('')

const loggedInUser = ref<string | null>(null)

const errors = ref({
  username: [] as string[],
  password: [] as string[],
  non_field_errors: [] as string[],
})

const isFormValid = computed(() => {
  return (
    username.value.trim().length > 0 &&
    password.value.length > 0 &&
    !isSubmitting.value
  )
})

onMounted(() => {
  loggedInUser.value = localStorage.getItem('username')
})

async function handleLogin() {
  if (!isFormValid.value) return

  // Reset errors
  errors.value = {
    username: [],
    password: [],
    non_field_errors: [],
  }
  isSubmitting.value = true
  successMsg.value = ''

  const payload: LoginPayload = {
    username: username.value.trim(),
    password: password.value,
  }

  try {
    const data = await loginUser(payload)
    
    // Store simplejwt tokens and user identity in localStorage
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('username', payload.username)
    
    loggedInUser.value = payload.username
    successMsg.value = 'Zalogowano pomyślnie!'
    
    await loadProgress()
    
    // Clear inputs
    username.value = ''
    password.value = ''
  } catch (err: any) {
    if (err && typeof err === 'object') {
      if (err.username) {
        errors.value.username = Array.isArray(err.username) ? err.username : [err.username]
      }
      if (err.password) {
        errors.value.password = Array.isArray(err.password) ? err.password : [err.password]
      }
      if (err.non_field_errors) {
        errors.value.non_field_errors = Array.isArray(err.non_field_errors) ? err.non_field_errors : [err.non_field_errors]
      }
      if (err.detail) {
        // Fallback for simplejwt standard authentication error responses
        errors.value.non_field_errors = [err.detail]
      }
      // If we got some other keys, treat as general
      if (!err.username && !err.password && !err.non_field_errors && !err.detail) {
        errors.value.non_field_errors = [JSON.stringify(err)]
      }
    } else {
      errors.value.non_field_errors = ['Błędna nazwa użytkownika lub hasło.']
    }
  } finally {
    isSubmitting.value = false
  }
}

async function handleLogout() {
  await saveProgress()
  clearAll()
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('username')
  loggedInUser.value = null
  successMsg.value = ''
}
</script>

<template>
  <div class="main-menu">
    <header class="menu-header">
      <h1>LOGOWANIE</h1>
      <p class="menu-user subtitle">Zaloguj się do portalu Kierowcownik</p>
    </header>

    <div class="content-wrapper">
      <div class="menu-actions">
        <div v-if="loggedInUser" class="success-alert">
          <div class="alert-icon">✓</div>
          <div class="alert-content">
            <h3>Zalogowano!</h3>
            <p>Jesteś zalogowany jako: <strong>{{ loggedInUser }}</strong></p>
          </div>
          <div class="alert-actions">
            <router-link to="/" class="menu-btn">
              Menu główne
            </router-link>
            <button @click="handleLogout" class="menu-btn logout-btn">
              Wyloguj się
            </button>
          </div>
        </div>

        <form v-else @submit.prevent="handleLogin" class="login-form">
          <div v-if="errors.non_field_errors.length > 0" class="error-alert">
            <ul>
              <li v-for="(err, idx) in errors.non_field_errors" :key="idx">{{ err }}</li>
            </ul>
          </div>

          <div class="form-group">
            <label for="username">Nazwa użytkownika</label>
            <div class="input-wrapper">
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="Wprowadź swoją nazwę"
                required
                :disabled="isSubmitting"
                class="menu-input"
                :class="{ 'has-error': errors.username.length > 0 }"
              />
            </div>
            <span v-for="(err, idx) in errors.username" :key="idx" class="field-error">
              {{ err }}
            </span>
          </div>

          <div class="form-group">
            <label for="password">Hasło</label>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="Wprowadź hasło"
                required
                :disabled="isSubmitting"
                class="menu-input"
                :class="{ 'has-error': errors.password.length > 0 }"
              />
            </div>
            <span v-for="(err, idx) in errors.password" :key="idx" class="field-error">
              {{ err }}
            </span>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="menu-btn"
              :disabled="!isFormValid || isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner"></span>
              <span v-else>Zaloguj się</span>
            </button>

            <router-link to="/" class="menu-btn secondary-btn">
              Wróć do menu
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- STYLIZACJA BAZOWA SKOPIOWANA Z MAIN MENU --- */
.main-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  font-family: Arial, sans-serif;
  background-color: #615d5d;
  background-image: repeating-linear-gradient(
      45deg,
      #434242,
      #434242 10px,
      #615d5d 10px,
      #615d5d 20px
  );
  min-height: 100vh;
  width: 100%;
}

.menu-header h1 {
  color: #000000;
  margin-bottom: 0.5rem;
  font-size: 5rem;
  text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.8);
  text-align: center;
}

.menu-user.subtitle {
  color: #fff;
  font-size: 1.2rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  margin-bottom: 2rem;
  text-align: center;
}

.content-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1200px;
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 450px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: bold;
  text-align: left;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
  margin-left: 4px;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

/* Pola tekstowe w stylu menu-select */
.menu-input {
  width: 100%;
  box-sizing: border-box;
  padding: 16px 24px;
  border-radius: 8px;
  border: none;
  font-size: 1.2rem;
  font-weight: bold;
  background-color: #ffffff;
  color: #333;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
  outline: none;
  transition: box-shadow 0.2s ease, transform 0.1s ease;
}

.menu-input:focus {
  box-shadow: 0 0 0 4px rgba(229, 57, 53, 0.4);
}

.menu-input.has-error {
  border: 2px solid #e53935;
}

/* --- OSTRZEŻENIA I BŁĘDY --- */
.field-error {
  color: #ff8a80; /* Jasny czerwony by był widoczny na szarym tle */
  font-size: 0.95rem;
  font-weight: bold;
  margin-top: 4px;
  text-align: left;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.error-alert {
  background: #ffffff;
  border-left: 6px solid #e53935;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.error-alert ul {
  margin: 0;
  padding-left: 20px;
  color: #b71c1c;
  font-size: 1rem;
  font-weight: bold;
}

/* --- KOMUNIKAT ZALOGOWANIA --- */
.success-alert {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: #ffffff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.alert-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #42b983; /* Zielony w stylu Vue */
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.alert-content h3 {
  color: #1a1a1a;
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  font-weight: bold;
}

.alert-content p {
  color: #333;
  margin: 0 0 2rem;
  font-size: 1.2rem;
}

.alert-actions {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 1rem;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.menu-btn {
  width: 100%;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 16px 24px;
  background-color: #e53935;
  color: white;
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.5rem;
  transition: background-color 0.2s ease, transform 0.1s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.menu-btn:hover:not(:disabled) {
  background-color: #b71c1c;
}

.menu-btn:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.menu-btn:disabled {
  background-color: #8c8c8c;
  color: #d1d1d1;
  cursor: not-allowed;
  box-shadow: none;
}

.secondary-btn {
  background-color: #434242;
  border: 2px solid #ffffff;
}

.secondary-btn:hover {
  background-color: #2c2c2c;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>