<template>
  <div class="main-menu">
    <header class="menu-header">
      <h1>KIEROWCOWNIK</h1>
    </header>

    <div class="content-wrapper">
      <div class="side-image left">
        <img :src="leftImage" alt="Dekoracja lewa"/>
      </div>

      <nav class="menu-actions">
        <div ref="sekcjaEgzaminRef" class="action-group" :class="{ 'z-index-top': czyListaEgzaminOtwarta }">
          <router-link
              :to="`/egzamin/${wybranaKategoriaEgzamin}`"
              class="menu-btn start-btn"
          >
            Rozpocznij test
          </router-link>

          <div class="custom-select-wrapper">
            <button
                @click="toggleListaEgzamin"
                class="menu-select-btn"
                type="button"
            >
              {{ wybranaKategoriaEgzamin }}
            </button>

            <div v-if="czyListaEgzaminOtwarta" class="custom-dropdown">
              <div
                  v-for="opcja in listaOpcji"
                  :key="opcja.id"
                  @click="wybierzEgzamin(opcja.symbol)"
                  class="dropdown-item"
                  :class="{ 'active': wybranaKategoriaEgzamin === opcja.symbol }"
              >
                {{ opcja.symbol }}
              </div>
            </div>
          </div>
        </div>

        <router-link to="/statystyki" class="menu-btn">Statystyki</router-link>

        <div ref="sekcjaNaukiRef" class="action-group" :class="{ 'z-index-top': czyListaNaukaOtwarta }">
          <router-link 
              :to="`/nauka/${wybranaKategoriaNauka}`" 
              class="menu-btn start-btn"
          >
            Tryb nauki
          </router-link>
          
          <div class="custom-select-wrapper">
            <button 
                @click="toggleListaNauka" 
                class="menu-select-btn" 
                type="button"
            >
              {{ wybranaKategoriaNauka }}
            </button>
            
            <div v-if="czyListaNaukaOtwarta" class="custom-dropdown">
              <div 
                  v-for="opcja in listaOpcji" 
                  :key="opcja.id"
                  @click="wybierzNauke(opcja.symbol)"
                  class="dropdown-item"
                  :class="{ 'active': wybranaKategoriaNauka === opcja.symbol }"
              >
                {{ opcja.symbol }}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div class="side-image right">
        <img :src="rightImage" alt="Dekoracja prawa"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import leftImage from '../assets/znak-nauki-jazdy.png'
import rightImage from '../assets/kolo-zebate.png'

import { fetchCategories } from "../api/categories";
import { Categories } from "../utils/categories";

const listaOpcji = ref<Categories[]>([])

const wybranaKategoriaEgzamin = ref<string>('')
const wybranaKategoriaNauka = ref<string>('')

const czyListaEgzaminOtwarta = ref<boolean>(false)
const czyListaNaukaOtwarta = ref<boolean>(false)


function toggleListaEgzamin() {
  czyListaEgzaminOtwarta.value = !czyListaEgzaminOtwarta.value
  if (czyListaEgzaminOtwarta.value) czyListaNaukaOtwarta.value = false
}

function toggleListaNauka() {
  czyListaNaukaOtwarta.value = !czyListaNaukaOtwarta.value
  if (czyListaNaukaOtwarta.value) czyListaEgzaminOtwarta.value = false
}

function wybierzEgzamin(symbol: string) {
  wybranaKategoriaEgzamin.value = symbol
  czyListaEgzaminOtwarta.value = false
}

function wybierzNauke(symbol: string) {
  wybranaKategoriaNauka.value = symbol
  czyListaNaukaOtwarta.value = false
}


onMounted(async () => {
  try {
    listaOpcji.value = await fetchCategories()
    if (listaOpcji.value.length > 0) {
      wybranaKategoriaEgzamin.value = listaOpcji.value[0].symbol
      wybranaKategoriaNauka.value = listaOpcji.value[0].symbol
    }
  } catch (error) {
    console.error('Wystąpił błąd podczas pobierania kategorii:', error)
  }
})
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
  justify-content: center;
  gap: 3rem;
  width: 100%;
  max-width: 1200px;
  margin-top: 2rem;
}

.side-image {
  display: flex;
  justify-content: center;
}

.side-image img {
  width: 100%;
  max-width: 200px;
  aspect-ratio: 1 / 1;
  object-fit: contain;
  border-radius: 8px;
}

.side-image.right img {
  animation: spin 10s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 450px;
}

.action-group {
  position: relative;
  width: 100%;
  z-index: 1; 
}

.z-index-top {
  z-index: 1000 !important;
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
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.5rem;
  transition: background-color 0.2s ease, transform 0.1s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.start-btn {
  padding: 16px 24px !important;
}

.menu-btn:hover { background-color: #b71c1c; }
.menu-btn:active { transform: translateY(2px); box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
.menu-btn.router-link-active { background-color: #b71c1c; }

.custom-select-wrapper {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

.menu-select-btn {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background-color: #b71c1c;
  border: 2px solid #ffffff;
  color: white;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  outline: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-select-btn:hover {
  background-color: #8e1515;
}

.custom-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);

  z-index: 1001; 
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  width: 160px;
}

.dropdown-item {
  padding: 8px 4px;
  text-align: center;
  background-color: #f0f0f0;
  color: #333333;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1.1rem;
  transition: background-color 0.1s ease;
}

.dropdown-item:hover {
  background-color: #dcdcdc;
}

.dropdown-item.active {
  background-color: #e53935;
  color: white;
}
</style>