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
            <button class="action-btn">View</button>
            <button class="action-btn">Download</button>
            <button class="action-btn">Delete</button>
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

onMounted(fetchDocuments)
</script>
