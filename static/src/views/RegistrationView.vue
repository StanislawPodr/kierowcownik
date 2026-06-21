<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser } from '../api/auth'
import type { RegisterPayload } from '../utils/auth'

const router = useRouter()

const username = ref('')
const password = ref('')
const passwordConfirm = ref('')

const isSubmitting = ref(false)
const successMsg = ref('')

const errors = ref({
  username: [] as string[],
  password: [] as string[],
  password_confirm: [] as string[],
  non_field_errors: [] as string[],
})

const clientErrors = computed(() => {
  const list: { field: 'username' | 'password' | 'password_confirm'; message: string }[] = []
  
  if (username.value && username.value.trim().length < 3) {
    list.push({ field: 'username', message: 'Nazwa użytkownika musi mieć co najmniej 3 znaki.' })
  }
  
  if (password.value && password.value.length < 8) {
    list.push({ field: 'password', message: 'Hasło musi mieć co najmniej 8 znaków.' })
  }
  
  if (password.value && passwordConfirm.value && password.value !== passwordConfirm.value) {
    list.push({ field: 'password_confirm', message: 'Hasła nie są identyczne.' })
  }
  
  return list
})

const isFormValid = computed(() => {
  return (
    username.value.trim().length >= 3 &&
    password.value.length >= 8 &&
    passwordConfirm.value.length >= 8 &&
    password.value === passwordConfirm.value &&
    !isSubmitting.value
  )
})

async function handleRegister() {
  if (!isFormValid.value) return

  // Reset errors
  errors.value = {
    username: [],
    password: [],
    password_confirm: [],
    non_field_errors: [],
  }
  isSubmitting.value = true
  successMsg.value = ''

  const payload: RegisterPayload = {
    username: username.value.trim(),
    password: password.value,
    password_confirm: passwordConfirm.value,
  }

  try {
    await registerUser(payload)
    successMsg.value = 'Konto zostało pomyślnie utworzone!'
    // Clear inputs
    username.value = ''
    password.value = ''
    passwordConfirm.value = ''
  } catch (err: any) {
    if (err && typeof err === 'object') {
      if (err.username) {
        errors.value.username = Array.isArray(err.username) ? err.username : [err.username]
      }
      if (err.password) {
        errors.value.password = Array.isArray(err.password) ? err.password : [err.password]
      }
      if (err.password_confirm) {
        errors.value.password_confirm = Array.isArray(err.password_confirm) ? err.password_confirm : [err.password_confirm]
      }
      if (err.non_field_errors) {
        errors.value.non_field_errors = Array.isArray(err.non_field_errors) ? err.non_field_errors : [err.non_field_errors]
      }
      
      // Fallback if no specific field key is found but we got an error object
      if (
        !err.username &&
        !err.password &&
        !err.password_confirm &&
        !err.non_field_errors &&
        err.detail
      ) {
        errors.value.non_field_errors = [err.detail]
      }
    } else {
      errors.value.non_field_errors = ['Wystąpił nieoczekiwany błąd rejestracji. Spróbuj ponownie.']
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="main-menu">
    <header class="menu-header">
      <h1>REJESTRACJA</h1>
      <p class="menu-user subtitle">Utwórz konto w portalu Kierowcownik</p>
    </header>

    <div class="content-wrapper">
      <div class="menu-actions">
        <div v-if="successMsg" class="success-alert">
          <div class="alert-icon">✓</div>
          <div class="alert-content">
            <h3>Sukces!</h3>
            <p>{{ successMsg }}</p>
          </div>
          <div class="alert-actions">
            <router-link to="/" class="menu-btn">
              Przejdź do menu głównego
            </router-link>
          </div>
        </div>

        <form v-else @submit.prevent="handleRegister" class="register-form">
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
                placeholder="np. młody_kierowca"
                required
                :disabled="isSubmitting"
                class="menu-input"
                :class="{ 'has-error': errors.username.length > 0 }"
              />
            </div>
            <span v-for="(err, idx) in errors.username" :key="idx" class="field-error">
              {{ err }}
            </span>
            <span v-if="username && username.trim().length < 3" class="field-info">
              Wymagane minimum 3 znaki.
            </span>
          </div>

          <div class="form-group">
            <label for="password">Hasło</label>
            <div class="input-wrapper">
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="••••••••"
                required
                :disabled="isSubmitting"
                class="menu-input"
                :class="{ 'has-error': errors.password.length > 0 }"
              />
            </div>
            <span v-for="(err, idx) in errors.password" :key="idx" class="field-error">
              {{ err }}
            </span>
            <span v-if="password && password.length < 8" class="field-info">
              Hasło musi zawierać minimum 8 znaków.
            </span>
          </div>

          <div class="form-group">
            <label for="password_confirm">Potwierdź hasło</label>
            <div class="input-wrapper">
              <input
                id="password_confirm"
                v-model="passwordConfirm"
                type="password"
                placeholder="••••••••"
                required
                :disabled="isSubmitting"
                class="menu-input"
                :class="{ 'has-error': errors.password_confirm.length > 0 || (passwordConfirm && password !== passwordConfirm) }"
              />
            </div>
            <span v-for="(err, idx) in errors.password_confirm" :key="idx" class="field-error">
              {{ err }}
            </span>
            <span v-if="passwordConfirm && password !== passwordConfirm" class="field-error">
              Hasła się nie zgadzają.
            </span>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="menu-btn"
              :disabled="!isFormValid || isSubmitting"
            >
              <span v-if="isSubmitting" class="spinner"></span>
              <span v-else>Zarejestruj się</span>
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
/* --- STYLIZACJA BAZOWA WSPÓLNA Z MAIN MENU --- */
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

/* --- STYLIZACJA FORMULARZA --- */
.register-form {
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
  color: #ff8a80;
  font-size: 0.95rem;
  font-weight: bold;
  margin-top: 4px;
  text-align: left;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.field-info {
  color: #e0e0e0;
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

/* --- KOMUNIKAT REJESTRACJI --- */
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
  background-color: #42b983;
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

/* --- PRZYCISKI --- */
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

/* --- SPINNER W PRZYCISKU --- */
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