<template>
  <div class="main-menu">
    <header class="menu-header">
      <h1>KIEROWCOWNIK</h1>
    </header>

    <div class="content-wrapper">
      <div class="side-image left">
        <img :src="leftImage" alt="Dekoracja lewa" />
      </div>

      <nav class="menu-actions">
        <router-link to="/egzamin" class="menu-btn">Rozpocznij test</router-link>
        <router-link to="/statystyki" class="menu-btn">Statystyki</router-link>
      </nav>

      <div class="side-image right">
        <img :src="rightImage" alt="Dekoracja prawa" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import leftImage from '../assets/znak-nauki-jazdy.png'
import rightImage from '../assets/kolo-zebate.png'
</script>

<style scoped>
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
  margin-bottom: 2rem;
  font-size: 5rem;
  text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.8);
}

.content-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  max-width: 1200px;
  margin-top: 2rem;
}

.side-image img {
  width: 250px;
  height: 250px;
  object-fit: contain;
  border-radius: 8px;
}

.side-image.right img {
  animation: spin 10s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 350px;
}

.menu-btn {
  width: 100%;
  box-sizing: border-box;
  text-align: center;
  padding: 24px 48px;
  background-color: #e53935;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.5rem;
  transition: background-color 0.2s ease, transform 0.1s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.menu-btn:hover {
  background-color: #b71c1c;
}

.menu-btn:active {
  transform: translateY(2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.menu-btn.router-link-active {
  background-color: #b71c1c;
}
</style>
