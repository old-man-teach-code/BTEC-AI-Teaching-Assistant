
import { ref, computed, onMounted } from 'vue'
import api from '../api/http'
import { useRouter } from 'vue-router'

export function processDocument() {
  const router = useRouter()
  const documents = ref([])
  const selectedFile = ref(null)
  const fileInput = ref(null)
  const processing = ref(false)
  const selectedType = ref('all')
  const sortBy = ref('latest')

  const sidebarItemsTop = [
    { label: 'Welcome', icon: 'mdi-home-outline' },
    { label: 'Document', icon: 'mdi-file-document-outline' },
    { label: 'Calendar', icon: 'mdi-calendar-clock-outline' },
    { label: 'Class', icon: 'mdi-account-group-outline' },
    { label: 'Statistical', icon: 'mdi-chart-line' },
  ]

  const sidebarItemsBottom = [
    { label: 'Trash', icon: 'mdi-delete-clock-outline' },
    { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
    { label: 'Setting', icon: 'mdi-cog-outline', action: 'setting' },
    { label: 'Logout', icon: 'mdi-logout', action: 'logout' },
  ]

  const triggerFileInput = () => fileInput.value.click()

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

  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  async function handleFileSelect(e) {
    const f = e.target.files[0]
    if (!f) return
    selectedFile.value = f
    await uploadFile()
  }

  async function uploadFile() {
    if (!selectedFile.value) return
    processing.value = true
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    try {
      await api.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      alert('Upload successful!')
      selectedFile.value = null
      fileInput.value.value = null
      fetchDocuments()
    } catch (e) {
      console.error(e)
      alert('Upload failed!')
    }
    processing.value = false
  }

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/api/documents')
      documents.value = res.data.items.filter((doc) => doc.status === 'uploaded')
    } catch {
      documents.value = []
    }
  }

  const handleView = (doc) => {
    if (!doc.filename) return alert('File không hợp lệ')
    window.open(`/files/${doc.filename}`, '_blank')
  }

  async function handleDownload(doc) {
    processing.value = true
    try {
      const res = await api.get(`/api/documents/${doc.id}/download`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', doc.original_name || doc.filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      alert('Download failed!')
    }
    processing.value = false
  }

  async function handleProcess(doc) {
    processing.value = true
    try {
      await api.post(`/documents/process/${doc.id}`)
      alert('Processing successful!')
    } catch (e) {
      alert('Processing failed!')
    }
    processing.value = false
  }

  async function handleDelete(doc) {
    if (!confirm('Are you sure you want to delete this file?')) return
    processing.value = true
    try {
      await api.delete(`/api/documents/${doc.id}?hard_delete=true`)
      alert('File deleted!')
      documents.value = documents.value.filter((d) => d.id !== doc.id)
    } catch {
      alert('Delete failure!')
    }
    processing.value = false
  }

  const handleSidebar = (item) => {
    if (item.action === 'logout') {
      router.push({ path: '/home' })
    }
  }

  const recentFiles = computed(() =>
    documents.value
      .slice()
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 4)
      .map((doc) => ({
        ...doc,
        name: doc.original_name,
        date: formatDate(doc.created_at),
        size: formatSize(doc.file_size),
      }))
  )

  const folders = computed(() => {
    const groups = {}
    documents.value.forEach((doc) => {
      const year = new Date(doc.created_at).getFullYear()
      if (!groups[year]) groups[year] = { files: 0, size: 0 }
      groups[year].files += 1
      groups[year].size += doc.file_size
    })
    return Object.entries(groups).map(([year, data]) => ({
      name: `Year ${year}`,
      files: data.files,
      size: formatSize(data.size),
    }))
  })

  const filterByType = (type) => {
    selectedType.value = type
  }

  const sortedAndFilteredDocuments = computed(() => {
    let list = [...documents.value]
    if (selectedType.value !== 'all') {
      list = list.filter((doc) => getFileType(doc.file_type) === selectedType.value)
    }
    switch (sortBy.value) {
      case 'latest':
        list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        break
      case 'oldest':
        list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        break
      case 'size_asc':
        list.sort((a, b) => a.file_size - b.file_size)
        break
      case 'size_desc':
        list.sort((a, b) => b.file_size - a.file_size)
        break
      case 'name_az':
        list.sort((a, b) => a.original_name.localeCompare(b.original_name))
        break
    }
    return list
  })

  onMounted(fetchDocuments)

  return {
    documents,
    selectedFile,
    fileInput,
    processing,
    sidebarItemsTop,
    sidebarItemsBottom,
    triggerFileInput,
    handleFileSelect,
    handleDownload,
    handleProcess,
    handleDelete,
    handleView,
    handleSidebar,
    fetchDocuments,
    formatSize,
    formatDate,
    getFileType,
    filterByType,
    selectedType,
    sortBy,
    folders,
    recentFiles,
    sortedAndFilteredDocuments,
  }
}
