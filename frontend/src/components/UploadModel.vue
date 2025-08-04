<template>
  <div class="modal fade" tabindex="-1" ref="modal" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <form @submit.prevent="uploadFile">
          <div class="modal-header">
            <h5 class="modal-title">Upload Document</h5>
            <button type="button" class="btn-close" @click="close"></button>
          </div>
          <div class="modal-body">
            <input
              type="file"
              class="form-control"
              accept=".pdf,.docx,.pptx"
              @change="handleFileSelect"
              :disabled="uploading"
            />
            <div v-if="file" class="mt-3">
              <div><b>File:</b> {{ file.name }}</div>
              <div><b>Size:</b> {{ formatSize(file.size) }}</div>
            </div>
            <div v-if="uploading" class="mt-3">
              <div class="progress">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="{ width: progress + '%' }"
                  :aria-valuenow="progress"
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  {{ progress }}%
                </div>
              </div>
            </div>
            <div v-if="success" class="alert alert-success mt-2">{{ success }}</div>
            <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close" :disabled="uploading">Close</button>
            <button type="submit" class="btn btn-primary" :disabled="!file || uploading">
              Upload
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/http'

const file = ref(null)
const uploading = ref(false)
const progress = ref(0)
const error = ref('')
const success = ref('')
const modal = ref(null)

const emit = defineEmits(['uploaded'])

function handleFileSelect(e) {
  error.value = ''
  success.value = ''
  const f = e.target.files[0]
  if (
    !f ||
    !['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'].includes(f.type)
  ) {
    error.value = 'Only PDF, DOCX, PPTX files are allowed.'
    file.value = null
    return
  }
  file.value = f
}

function formatSize(size) {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / 1024 / 1024).toFixed(2) + ' MB'
}

function open() {
  if (modal.value) window.bootstrap.Modal.getOrCreateInstance(modal.value).show()
}

function close() {
  if (modal.value) window.bootstrap.Modal.getOrCreateInstance(modal.value).hide()
  file.value = null
  progress.value = 0
  error.value = ''
  success.value = ''
}

async function uploadFile() {
  if (!file.value) return
  uploading.value = true
  error.value = ''
  success.value = ''
  progress.value = 0
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const res = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) progress.value = Math.round((e.loaded * 100) / e.total)
      }
    })
    uploading.value = false
    success.value = 'Upload successful!'
    emit('uploaded', res.data)
    setTimeout(() => {
      close()
      success.value = ''
    }, 1000)
  } catch (err) {
    uploading.value = false
    error.value = err?.response?.data?.message || 'Upload failed'
  }
}

defineExpose({ open, close })
</script>

<style scoped>
.progress-bar {
  transition: width 0.3s;
}
</style>