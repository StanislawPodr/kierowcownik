<template>
  <div class="main-menu">
    <header class="menu-header">
      <h1>KIEROWCOWNIK</h1>
    </header>

    <div class="content-wrapper">

      <div class="side-image left">
        <img src="/znak-nauki-jazdy.png" alt="Dekoracja lewa" />
      </div>

      <nav class="menu-actions">
        <router-link to="/strona-pierwsza" class="menu-btn">Rozpocznij test</router-link>
        <router-link to="/strona-druga" class="menu-btn">Statystyki</router-link>
      </nav>

      <div class="side-image right">
        <img src="/kolo-zebate.PNG" alt="Dekoracja prawa" />
      </div>

    </div>
  </div>
</template>

<script setup>
// Tutaj dodasz logikę
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


/* --- Podstawowe style dla obu obrazków (wielkość) --- */
.side-image img {
  width: 250px;
  height: 250px;
  object-fit: contain;
  /* Usunęliśmy stąd właściwość 'animation' */
}

/* --- NOWE: Animacja nałożona TYLKO na prawy obrazek --- */
.side-image.right img {
  animation: spin 10s linear infinite;
}

/* Definicja animacji obracania */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}


.side-image img {
  width: 250px;
  height: 250px;

  object-fit: contain;


  border-radius: 8px;
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
</style>