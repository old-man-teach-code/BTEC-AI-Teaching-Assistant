import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '../api/http'
import { useRouter } from 'vue-router'

export function processDocument() {
  const router = useRouter()
  const documents = ref([])
  const selectedFile = ref(null)
  const fileInput = ref(null)
  const foldersList = ref([]) 
  const selectedFolderId = ref(null)
  const processing = ref(false)
  const selectedType = ref('all')
  const sortBy = ref('latest') 
  
  // Debug watch để kiểm tra
  watch(sortBy, (newValue, oldValue) => {
    console.log(`[processDocument] sortBy changed: "${oldValue}" -> "${newValue}"`)
  })
  
  const sidebarItemsTop = [
    { label: 'Home', icon: 'mdi-home-outline', route: '/dashboardhome' },
    { label: 'Document', icon: 'mdi-file-document-outline', route: '/documents' },
    { label: 'Calendar', icon: 'mdi-calendar-clock-outline', route: '/calendar' },
    { label: 'Statistical', icon: 'mdi-chart-line', route: '/chart' },
  ]

  const sidebarItemsBottom = [
    { label: 'Trash', icon: 'mdi-delete-clock-outline', route: '/trash' },
    { label: 'Help Centre', icon: 'mdi-help-circle-outline' },
    { label: 'Setting', icon: 'mdi-cog-outline', route: '/settings' },
    { label: 'Return', icon: 'mdi-logout', route: '/dashboardhome' },
  ]

  const triggerFileInput = () => fileInput.value.click()

  const getFileType = (file) => {
    // Nếu file là object với thuộc tính type (File object)
    if (file && typeof file === 'object' && file.type) {
      if (file.type.includes('pdf')) return 'PDF'
      if (file.type.includes('word') || file.type.includes('document')) return 'DOCX'
      if (file.type.includes('presentation')) return 'PPTX'
      if (file.type.includes('sheet')) return 'XLSX'
      return file.type
    }
    
    // Nếu file là string (file_type từ database hoặc filename)
    if (typeof file === 'string') {
      const lowerFile = file.toLowerCase()
      
      // Kiểm tra extension từ filename
      if (lowerFile.endsWith('.pdf')) return 'PDF'
      if (lowerFile.endsWith('.docx') || lowerFile.endsWith('.doc')) return 'DOCX'
      if (lowerFile.endsWith('.pptx') || lowerFile.endsWith('.ppt')) return 'PPTX'
      if (lowerFile.endsWith('.xlsx') || lowerFile.endsWith('.xls')) return 'XLSX'
      if (lowerFile.endsWith('.txt')) return 'TXT'
      if (lowerFile.endsWith('.jpg') || lowerFile.endsWith('.jpeg') || lowerFile.endsWith('.png')) return 'IMAGE'
      
      // Kiểm tra MIME type strings
      if (lowerFile.includes('pdf')) return 'PDF'
      if (lowerFile.includes('word') || lowerFile.includes('document')) return 'DOCX'
      if (lowerFile.includes('presentation')) return 'PPTX'
      if (lowerFile.includes('sheet')) return 'XLSX'
      
      return file.toUpperCase()
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

  const truncateFileName = (fileName, maxLength = 25) => {
    if (!fileName) return ''
    if (fileName.length <= maxLength) return fileName
    
    // Tách tên file và extension
    const lastDotIndex = fileName.lastIndexOf('.')
    if (lastDotIndex === -1) {
      // Không có extension
      return fileName.substring(0, maxLength - 3) + '...'
    }
    
    const name = fileName.substring(0, lastDotIndex)
    const extension = fileName.substring(lastDotIndex)
    
    // Nếu extension quá dài thì cắt cả extension
    if (extension.length > 8) {
      return fileName.substring(0, maxLength - 3) + '...'
    }
    
    // Cắt tên nhưng giữ extension
    const maxNameLength = maxLength - extension.length - 3
    if (name.length > maxNameLength) {
      return name.substring(0, maxNameLength) + '...' + extension
    }
    
    return fileName
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
      await fetchDocumentsByFolder()
    } catch (e) {
      console.error(e)
      alert('Upload failed!')
    }
    processing.value = false
  }

const fetchDocumentsByFolder = async (folderId) => {
  try {
    const res = await api.get('/api/documents', {
      params: { folder_id: folderId }
    })
    console.log('[fetchDocumentsByFolder] folderId:', folderId)
    console.log('[fetchDocumentsByFolder] files:', res.data.items)
    documents.value = res.data.items.filter(doc => doc.status === 'uploaded' || doc.status === 'ready')
  } catch (err) {
    console.error('Lỗi khi lấy documents theo folder:', err)
    documents.value = []
  }
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

  async function handleDelete(doc) {
    processing.value = true
    try {
      await api.delete(`/api/documents/${doc.id}?hard_delete=false`)
      alert('File has been moved to trash')
      documents.value = documents.value.filter((d) => d.id !== doc.id)
      
      // Trigger event để báo cho ChartView biết cần refresh
      window.dispatchEvent(new CustomEvent('document-deleted', { 
        detail: { 
          id: doc.id,
          name: doc.original_name
        } 
      }))
      
    } catch {
      alert('Delete failure!')
    }
    processing.value = false
  }

 function handleSidebar(item) {
  if (item.route) {
    router.push(item.route) 
  } else if (item.action === 'logout') {
     router.push({ path: '/dashboardhome' })

  }
}

const recentFiles = computed(() => {
  let list = [...documents.value]

  if (selectedType.value !== 'all' && selectedType.value !== 'Folder') {
    list = list.filter(doc => {
      const fileType = getFileType(doc.file_type) || getFileType(doc.original_name)
      return fileType === selectedType.value
    })
  }

  return list
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 4)
    .map((doc) => ({
      ...doc,
      name: truncateFileName(doc.original_name, 20), // Truncate tên file với max 30 ký tự
      fullName: doc.original_name, // Giữ tên đầy đủ để có thể hiển thị tooltip
      date: formatDate(doc.created_at),
      size: formatSize(doc.file_size),
    }))
})


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
  console.log('Gọi filterByType:', type)
  selectedType.value = type
  
  // Debug: Log tất cả documents và type của chúng
  console.log('=== DEBUG FILTER BY TYPE ===')
  documents.value.forEach(doc => {
    const detectedType = getFileType(doc.file_type) || getFileType(doc.original_name)
    console.log(`File: "${doc.original_name}" | file_type: "${doc.file_type}" | detected: "${detectedType}" | match filter "${type}": ${detectedType === type}`)
  })
  console.log('=============================')
}

  

  const sortedAndFilteredDocuments = computed(() => {
    let list = [...documents.value]
    if (selectedType.value !== 'all') {
      list = list.filter((doc) => {
        // Thử lấy type từ file_type trước, nếu không có thì từ original_name
        const fileType = getFileType(doc.file_type) || getFileType(doc.original_name)
        console.log(`Filtering doc: "${doc.original_name}" | file_type: "${doc.file_type}" | detected: "${fileType}" | selectedType: "${selectedType.value}"`)
        return fileType === selectedType.value
      })
    }
    switch (sortBy.value) {
      case 'latest':
        list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        break
      case 'oldest':
        list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        break
    }
    return list
  })

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
    handleDelete,
    // handleView,
    handleSidebar,
    selectedFolderId,
    fetchDocumentsByFolder,
    formatSize,
    formatDate,
    truncateFileName,
    getFileType,
    filterByType,
    selectedType,
    sortBy,
    folders,
    foldersList,
    recentFiles,
    sortedAndFilteredDocuments,
  }
}
