import { ref } from 'vue'

export function useUI() {
  const isVisible = ref(false)
  const showDropdown = ref(false)
  const timeFilter = ref('weekly')

  const toggleDropdown = () => {
    showDropdown.value = !showDropdown.value
  }

  const setVisible = (visible) => {
    isVisible.value = visible
  }

  return {
    isVisible,
    showDropdown,
    timeFilter,
    toggleDropdown,
    setVisible
  }
}
