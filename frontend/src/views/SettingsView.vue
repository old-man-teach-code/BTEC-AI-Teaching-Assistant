<template>
  <div class="page-wrapper">
    <SideBar />

    <main class="main-content">
      <div class="dashboard">
        <div class="dashboard-header">
        </div>

        <div class="settings-container">
          <!-- Profile Section -->
          <div class="settings-section">
            <div class="section-header">
              <h2>Profile</h2>
             <p>
              View and edit your personal profile information, including your name, profile picture,
              and role within the organization.
            </p>
            </div>
            <div class="profile-card">
              <div class="profile-info">
                <div class="profile-avatar">
                  <v-icon
                    class="mdi mdi-account"
                    size="70"
                    :title="userProfile.name || 'User'"
                  ></v-icon>
                </div>
                <div class="profile-details">
                  <h3>{{ userProfile.name || 'User' }}</h3>
                  <p class="role">{{ languageDisplayName }} • {{ userProfile.email || 'email@example.com' }}</p>
                </div>
                <button class="edit-btn" @click="toggleEditProfile">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Personal Information Section -->
          <div class="settings-section">
            <div class="section-header">
              <h2>Personal Information</h2>
              <p>Manage your basic information including name and email address.</p>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label for="name">Name</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    id="name"
                    v-model="userProfile.name"
                    :disabled="!editMode.personal"
                    placeholder="Enter your name"
                  />
                  <button class="edit-field-btn" @click="toggleEditField('personal')">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label for="email">Email</label>
                <div class="input-wrapper">
                  <input
                    type="email"
                    id="email"
                    v-model="userProfile.email"
                    :disabled="!editMode.personal"
                    placeholder="Enter email address"
                  />
                  <button class="edit-field-btn" @click="toggleEditField('personal')">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Section -->
          <div class="settings-section">
            <div class="section-header">
              <h2>Account</h2>
              <p>Update your Discord User ID and select your preferred language.</p>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label for="discord_user_id">Discord User ID</label>
                <div class="input-wrapper">
                  <input
                    type="text"
                    id="discord_user_id"
                    v-model="userProfile.discord_user_id"
                    :disabled="!editMode.account"
                    placeholder="Enter Discord User ID"
                  />
                  <button class="edit-field-btn" @click="toggleEditField('account')">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label for="language">Language</label>
                <div class="input-wrapper">
                  <select
                    id="language"
                    v-model="userProfile.language"
                    :disabled="!editMode.account"
                  >
                    <option value="en">🇺🇸 English</option>
                    <option value="vi">🇻🇳 Tiếng Việt</option>
                  </select>
                  <button class="edit-field-btn" @click="toggleEditField('account')">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Save Button -->
          <div class="save-section">
            <button v-if="hasChanges" class="reset-btn" @click="resetChanges" :disabled="isSaving">
              Reset Changes
            </button>
            <button class="save-btn" @click="saveSettings" :disabled="!hasChanges || isSaving">
              <span v-if="isSaving">Saving...</span>
              <span v-else>Save Changes</span>
            </button>
          </div>

          <!-- Loading Overlay -->
          <div v-if="isLoading" class="loading-overlay">
            <div class="loading-spinner"></div>
            <p>Loading user data...</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import SideBar from '@/views/SideBar.vue'
import { useSettings } from '@/composables'

// Use the Settings composable
const {
  // State
  userProfile,
  editMode,
  isLoading,
  isSaving,
  
  // Computed
  languageDisplayName,
  hasChanges,
  
  // Methods
  toggleEditProfile,
  toggleEditField,
  saveSettings,
  resetChanges,
  initSettings
} = useSettings()

onMounted(async () => {
  await initSettings()
})
</script>
<style scoped src="../assets/settings.css"></style>
