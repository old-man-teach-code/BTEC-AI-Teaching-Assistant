<template>
  <div class="documents-page">
    <div class="header-row">
      <h2>Your Documents</h2>
      <input type="file" accept=".pdf,.docx,.pptx" @change="handleFileSelect" style="display:none" ref="fileInput" />
      <button class="upload-btn" @click="triggerFileInput">Upload</button>
    </div>
    <table class="doc-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Size</th>
          <th>Uploaded At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <!-- Dòng preview file vừa chọn -->
        <tr v-if="selectedFile">
          <td>{{ selectedFile.name }}</td>
          <td>{{ getFileType(selectedFile) }}</td>
          <td>{{ formatSize(selectedFile.size) }}</td>
          <td>Not uploaded yet</td>
          <td>
  <div class="action-buttons">
    <button class="btn btn-success btn-sm btn-upload-preview" @click="uploadFile">Upload</button>
    <button class="btn btn-secondary btn-sm btn-cancel-preview" @click="cancelFile">Cancel</button>
  </div>
</td>

        </tr>
        <!-- Các dòng tài liệu đã upload -->
       <tr v-for="doc in documents" :key="doc.id">
  <td>{{ doc.original_name }}</td>
  <td>{{ getFileType(doc.file_type) }}</td>
  <td>{{ formatSize(doc.file_size) }}</td>
  <td>{{ formatDate(doc.created_at) }}</td>
  <td>
    <div class="dropdown">
      <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" :disabled="processing">
        Actions
      </button>
      <ul class="dropdown-menu">
        <li><button class="dropdown-item" @click="handleView(doc)" :disabled="processing">View</button></li>
        <li><button class="dropdown-item" @click="handleDownload(doc)" :disabled="processing">Download</button></li>
        <li><button class="dropdown-item" @click="handleProcess(doc)" :disabled="processing">Process</button></li>
        <li><button class="dropdown-item text-danger" @click="handleDelete(doc)" :disabled="processing">Delete</button></li>
      </ul>
    </div>
  </td>
</tr>

        <tr v-if="documents.length === 0 && !selectedFile">
          <td colspan="5" style="text-align:center; color:#888;">No documents available</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/http'
import '../assets/documents.css'

const documents = ref([])
const selectedFile = ref(null)
const fileInput = ref(null)
const processing = ref(false)

const triggerFileInput = () => fileInput.value.click()

function handleFileSelect(e) {
  const f = e.target.files[0]
  if (!f) return
  selectedFile.value = f
}

function getFileType(file) {
  // Nếu là object File (khi chọn file mới)
  if (file && typeof file === 'object' && file.type) {
    if (file.type.includes('pdf')) return 'PDF'
    if (file.type.includes('word')) return 'DOCX'
    if (file.type.includes('presentation')) return 'PPTX'
    return file.type
  }
  // Nếu là string (khi lấy từ backend)
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
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
}

function cancelFile() {
  selectedFile.value = null
  fileInput.value.value = null
}

async function uploadFile() {
  if (!selectedFile.value) return
  processing.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  try {
    await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    alert('Upload successful!')
    selectedFile.value = null
    fileInput.value.value = null
    fetchDocuments() // Refresh danh sách tài liệu sau khi upload thành công
  } catch (e) {
    console.error(e)
    alert('Upload failed!')
  }
  processing.value = false
}

const fetchDocuments = async () => {
  try {
    const res = await api.get('/api/documents')
    documents.value = res.data.items
  } catch  {
    documents.value = []
  }
}

async function handleView(doc) {
  // Nếu có URL public thì mở tab mới, nếu không thì có thể dùng API để lấy link
  window.open(doc.url || `/files/${doc.filename}`, '_blank')
}

async function handleDownload(doc) {
  processing.value = true
  try {
    const res = await api.get(`/files/${doc.filename}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', doc.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e)  {
    console.log(e)
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
    console.error(e)
    alert('Processing failed!')
  }
  processing.value = false
}

async function handleDelete(doc) {
  if (!confirm('Are you sure you want to delete this file?')) return
  processing.value = true
  try {
    await api.delete(`/api/documents/${doc.id}`)
    alert('File deleted!')
      documents.value = documents.value.filter(d => d.id !== doc.id)
  } catch (e) {
    console.log(e)
    alert('Delete failure!')
  }
  processing.value = false
}

onMounted(fetchDocuments)
</script>

