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
  <div class="register-container">
    <div class="register-card">
      <header class="card-header">
        <h1 class="title">REJESTRACJA</h1>
        <p class="subtitle">Utwórz konto w portalu Kierowcownik</p>
      </header>

      <!-- Success message view -->
      <div v-if="successMsg" class="success-alert">
        <div class="alert-icon">✓</div>
        <div class="alert-content">
          <h3>Sukces!</h3>
          <p>{{ successMsg }}</p>
        </div>
        <router-link to="/" class="btn-primary back-to-menu-btn">
          Przejdź do menu głównego
        </router-link>
      </div>

      <!-- Main form view -->
      <form v-else @submit.prevent="handleRegister" class="register-form">
        <!-- General errors -->
        <div v-if="errors.non_field_errors.length > 0" class="error-alert">
          <ul>
            <li v-for="(err, idx) in errors.non_field_errors" :key="idx">{{ err }}</li>
          </ul>
        </div>

        <!-- Username Input -->
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
              :class="{ 'has-error': errors.username.length > 0 }"
            />
          </div>
          <!-- Field error displays -->
          <span v-for="(err, idx) in errors.username" :key="idx" class="field-error">
            {{ err }}
          </span>
          <span v-if="username && username.trim().length < 3" class="field-info">
            Wymagane minimum 3 znaki.
          </span>
        </div>

        <!-- Password Input -->
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

        <!-- Password Confirm Input -->
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

        <!-- Form Actions -->
        <div class="form-actions">
          <button
            type="submit"
            class="btn-primary submit-btn"
            :disabled="!isFormValid || isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner"></span>
            <span v-else>Zarejestruj się</span>
          </button>
          
          <router-link to="/" class="btn-secondary back-btn">
            Wróć do menu
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 32px);
  width: 100%;
  padding: 1rem;
}

.register-card {
  width: 100%;
  max-width: 500px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  transition: transform 0.3s ease;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.title {
  font-family: Arial, sans-serif;
  color: #1a1a1a;
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 0.5rem;
  letter-spacing: 1px;
}

.subtitle {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

/* Forms and Inputs styling */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #333;
  font-size: 0.95rem;
  font-weight: 600;
  text-align: left;
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 8px;
  border: 2px solid #ccc;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background-color: #fff;
  color: #1a1a1a;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #e53935;
  box-shadow: 0 0 0 4px rgba(229, 57, 53, 0.15);
}

.input-wrapper input.has-error {
  border-color: #d32f2f;
}

.input-wrapper input.has-error:focus {
  box-shadow: 0 0 0 4px rgba(211, 47, 47, 0.15);
}

/* Warnings and errors */
.field-error {
  color: #d32f2f;
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 2px;
  text-align: left;
}

.field-info {
  color: #666;
  font-size: 0.85rem;
  margin-top: 2px;
  text-align: left;
}

.error-alert {
  background: #fde8e8;
  border-left: 4px solid #e53935;
  border-radius: 6px;
  padding: 10px 16px;
  margin-bottom: 1rem;
}

.error-alert ul {
  margin: 0;
  padding-left: 20px;
  color: #9b1c1c;
  font-size: 0.9rem;
}

.success-alert {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background: #def7ec;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid #bcf0da;
}

.alert-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #31c48d;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

.alert-content h3 {
  color: #03543f;
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

.alert-content p {
  color: #046c4e;
  margin: 0 0 2rem;
  font-size: 1.1rem;
}

/* Buttons styling */
.form-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background-color: #e53935;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.15rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease, transform 0.1s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
  text-decoration: none;
  text-align: center;
}

.btn-primary:hover:not(:disabled) {
  background-color: #b71c1c;
}

.btn-primary:active:not(:disabled) {
  transform: translateY(1px);
}

.btn-primary:disabled {
  background-color: #e0e0e0;
  color: #a0a0a0;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-secondary {
  width: 100%;
  padding: 12px;
  background-color: transparent;
  color: #4a4a4a;
  border: 2px solid #ccc;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: #f0f0f0;
  color: #1a1a1a;
  border-color: #888;
}

.back-to-menu-btn {
  margin-top: 1rem;
  max-width: 300px;
}

/* Spinner */
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
