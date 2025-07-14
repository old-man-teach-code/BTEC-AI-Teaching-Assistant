<template>
  <div class="documents-page">
    <div class="header-row">
      <h2>Your Documents</h2>
      <button class="upload-btn" @click="onUpload">Upload</button>
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
        <tr v-for="doc in documents" :key="doc.filename">
          <td>{{ doc.filename }}</td>
          <td>{{ doc.extension }}</td>
          <td>{{ formatSize(doc.size) }}</td>
          <td>{{ formatDate(doc.created_at) }}</td>
          <td>
            <div class="dropdown">
              <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" :disabled="processing">
                Actions
              </button>
              <ul class="dropdown-menu">
                <li>
                  <button class="dropdown-item" @click="handleView(doc)" :disabled="processing">View</button>
                </li>
                <li>
                  <button class="dropdown-item" @click="handleDownload(doc)" :disabled="processing">Download</button>
                </li>
                <li>
                  <button class="dropdown-item" @click="handleProcess(doc)" :disabled="processing">Process</button>
                </li>
                <li>
                  <button class="dropdown-item text-danger" @click="handleDelete(doc)" :disabled="processing">Delete</button>
                </li>
              </ul>
            </div>
          </td>
        </tr>
        <tr v-if="documents.length === 0">
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
const processing = ref(false)

const fetchDocuments = async () => {
  try {
    const res = await api.get('/documents')
    documents.value = res.data
  } catch  {
    documents.value = []
  }
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

const onUpload = () => {
  alert('The upload feature will be added soon!')
}

function handleView(doc) {
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
  } catch  {
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
    await api.delete(`/documents/${doc.id}`)
    alert('File deleted!')
    fetchDocuments()
  } catch  {
    alert('Delete failure!')
  }
  processing.value = false
}

onMounted(fetchDocuments)
</script>
