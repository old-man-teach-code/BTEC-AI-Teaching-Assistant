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

</td>

        </tr>
        <!-- Các dòng tài liệu đã upload -->
 <tr v-for="doc in documents" :key="doc.id" @mouseleave="activeDropdown = null">
    <td>{{ doc.original_name }}</td>
    <td>{{ getFileType(doc.file_type) }}</td>
    <td>{{ formatSize(doc.file_size) }}</td>
    <td>{{ formatDate(doc.created_at) }}</td>

    <td class="hover-action-cell" @mouseenter="activeDropdown = doc.id">
      ☰
      <ul v-if="activeDropdown === doc.id" class="hover-dropdown">
        <li @click="handleView(doc)">View</li>
        <li @click="handleDownload(doc)">Download</li>
        <li @click="handleProcess(doc)">Process</li>
        <li class="danger" @click="handleDelete(doc)">Delete</li>
      </ul>
    </td>
  </tr>

<!-- View result below row -->
<tr v-if="viewingDoc && viewingDoc.id === doc.id">
  <td colspan="5" class="view-box">
     You are viewing file: <strong>{{ viewingDoc.original_name }}</strong>
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

async function handleFileSelect(e) {
  const f = e.target.files[0]
  if (!f) return
  selectedFile.value = f
  await uploadFile() 
} 


function getFileType(file) {

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
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
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
      documents.value = res.data.items.filter(doc => doc.status === 'uploaded')
  } catch  {
    documents.value = []
  }
}

async function handleView(doc) {
  window.open(doc.url || `/files/${doc.filename}`, '_blank')
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
const activeDropdown = ref(null)
const viewingDoc = ref(null)

</script>

