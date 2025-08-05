import { ref, computed, onMounted } from 'vue'
import api from '../api/http'
import { useRouter } from 'vue-router'

export function processTrash() {
  const documents = ref([])
  const search = ref('')
  const router = useRouter()
  const processing = ref(false)

  const sidebarItemsTop = [
    { label: 'Home', icon: 'mdi-home-outline', route: '/dashboardhome' },
    { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
    { label: 'Calendar', icon: 'mdi-calendar-clock-outline', route: '/calendar' },
    { label: 'Notifications', icon: 'mdi-bell-outline' },
    { label: 'Statistical', icon: 'mdi-chart-line' },
  ]

  const sidebarItemsBottom = [
    { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash' },
    { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
    { label: 'Setting', icon: 'mdi-cog-outline', action: 'setting' },
    { label: 'Logout', icon: 'mdi-logout', action: 'logout' },
  ]

  const getFileType = (file) => {
    if (file && typeof file === 'object' && file.type) {
      if (file.type.includes('pdf')) return 'PDF'
      if (file.type.includes('word')) return 'DOCX'
      if (file.type.includes('presentation')) return 'PPTX'
      return file.type
    }
    if (typeof file === 'string') {
      if (file.includes('pdf')) return 'PDF'
      if (file.includes('word')) return 'DOCX'
      if (file.includes('presentation')) return 'PPTX'
      return file
    }
    return ''
  }

  const formatSize = (size) => {
    if (size >= 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB'
    if (size >= 1024) return (size / 1024).toFixed(1) + ' KB'
    return size + ' B'
  }

  const formatDate = (dateStr) =>
    new Date(dateStr).toLocaleDateString('vi-VN')

  function getAutoDeleteInfo(deletedAt, mode = 'date') {
    const deletedDate = new Date(deletedAt)
    const autoDeleteDate = new Date(deletedDate)
    autoDeleteDate.setDate(autoDeleteDate.getDate() + 30)

    const today = new Date()
    const diff = Math.ceil((autoDeleteDate - today) / (1000 * 60 * 60 * 24))

    if (mode === 'remaining') {
      if (diff <= 0) return 'Expired'
      if (diff === 1) return '1 day left'
      return `${diff} day left`
    }

    if (mode === 'date') {
      return autoDeleteDate.toLocaleDateString('vi-VN')
    }

    return ''
  }

  const fetchDocuments = async () => {
    try {
      const [docRes, folderRes] = await Promise.all([
        api.get('/api/documents/trash'),
        api.get('/api/documents/folders/trash'),
      ])

      const docItems = docRes.data.items.map(doc => ({
        ...doc,
        type: 'document'
      }))

      const folderItems = folderRes.data.items.map(folder => ({
        ...folder,
        type: 'folder'
      }))

      documents.value = [...docItems, ...folderItems]
    } catch (err) {
      console.error('Lỗi khi lấy dữ liệu trash:', err)
      documents.value = []
    }
  }

  const handleRestore = async (item) => {
    try {
      if (item.type === 'folder') {
        await api.post(`/api/documents/folders/${item.id}/restore`)
      } else {
        await api.post(`/api/documents/${item.id}/restore`)
      }
      await fetchDocuments()
    } catch (err) {
      alert('Failed to restore item')
      console.error(err)
    }
  }

  const handlehardDelete = async (item) => {
    try {
      await api.delete(`/api/trash/items`, {
        data: {
          items: [
            {
              id: item.id,
              type: item.type
            }
          ]
        }
      })
      alert('Đã xoá vĩnh viễn')
      documents.value = documents.value.filter((d) => d.id !== item.id)
    } catch (e) {
      console.error(e)
      alert('Xoá thất bại!')
    }
  }

  const filteredDocuments = computed(() =>
    documents.value.filter((item) => {
      const name = item.type === 'folder' ? item.name : item.original_name
      return name?.toLowerCase().includes(search.value.toLowerCase())
    })
  )

  const handleSidebar = (item) => {
    if (item.route) {
      console.log('route: ', item.route)
      router.push(item.route)
    } else if (item.action === 'logout') {
      router.push({ path: '/home' })
    }
  }

  onMounted(fetchDocuments)

  return {
    documents,
    sidebarItemsTop,
    sidebarItemsBottom,
    handleSidebar,
    fetchDocuments,
    formatSize,
    formatDate,
    getAutoDeleteInfo,
    getFileType,
    filteredDocuments,
    handleRestore,
    handlehardDelete,
    search,
    processing
  }
}
