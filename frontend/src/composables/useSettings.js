import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useSettings() {
  const authStore = useAuthStore()

  // Reactive data - sẽ được load từ API
  const userProfile = reactive({
    name: '',
    email: '',
    discord_user_id: '',
    language: 'en', // Default to English
  })

  // Original data for comparison
  const originalProfile = reactive({})

  // Edit modes
  const editMode = reactive({
    personal: false,
    account: false,
  })

  // Computed property để hiển thị tên ngôn ngữ
  const languageDisplayName = computed(() => {
    return userProfile.language === 'vi' ? '🇻🇳 Tiếng Việt' : '🇺🇸 English'
  })

  // Loading state
  const isLoading = ref(false)
  const isSaving = ref(false)

  // Load dữ liệu user vào form
  const loadUserData = (userData) => {
    userProfile.name = userData.name || ''
    userProfile.email = userData.email || ''
    userProfile.discord_user_id = userData.discord_user_id || ''
    
    // Load language từ localStorage thay vì database
    userProfile.language = localStorage.getItem('user_language') || 'en'

    // Save original data
    Object.assign(originalProfile, userProfile)
  }

  // Methods
  const toggleEditProfile = () => {
    editMode.personal = !editMode.personal
    editMode.account = !editMode.account
  }

  const toggleEditField = (section) => {
    editMode[section] = !editMode[section]
  }

  const hasChanges = computed(() => {
    return JSON.stringify(userProfile) !== JSON.stringify(originalProfile)
  })

  const saveSettings = async () => {
    try {
      isSaving.value = true

      // Lưu language vào localStorage
      localStorage.setItem('user_language', userProfile.language)

      // Prepare data để gửi lên API - chỉ những field backend hỗ trợ
      const updateData = {
        name: userProfile.name,
        email: userProfile.email,
        discord_user_id: userProfile.discord_user_id,
      }

      // Gọi API để cập nhật thông qua auth store
      const updatedUser = await authStore.updateUser(updateData)

      // Update local data với dữ liệu mới
      loadUserData(updatedUser)

      // Reset edit modes
      editMode.personal = false
      editMode.account = false

      // Show success message
      alert('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings. Please try again.')
    } finally {
      isSaving.value = false
    }
  }

  // Reset changes
  const resetChanges = () => {
    Object.assign(userProfile, originalProfile)
    editMode.personal = false
    editMode.account = false
  }

  // Initialize settings - load user data
  const initSettings = async () => {
    if (authStore.user) {
      loadUserData(authStore.user)
    } else {
      // Fetch user data nếu chưa có trong store
      try {
        isLoading.value = true
        await authStore.fetchUser()
        if (authStore.user) {
          loadUserData(authStore.user)
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error)
      } finally {
        isLoading.value = false
      }
    }
  }

  return {
    // State
    userProfile,
    originalProfile,
    editMode,
    isLoading,
    isSaving,
    
    // Computed
    languageDisplayName,
    hasChanges,
    
    // Methods
    loadUserData,
    toggleEditProfile,
    toggleEditField,
    saveSettings,
    resetChanges,
    initSettings
  }
}
