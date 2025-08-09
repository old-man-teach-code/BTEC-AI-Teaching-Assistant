<template>
  <div class="page-wrapper">
    <SideBar />

    <!-- Main -->
    <main class="main-content">
      <div class="documents-page">
        <div class="trash-header">
          <div class="header-left">

              <v-icon class="trash-icon">mdi-delete-variant</v-icon>

            <div class="header-text">
              <h1 class="header-title">Recycle Bin</h1>
              <div class="header-description">
                <span>When you delete something we'll keep it here for 30 days, just in case you regret.</span>
                <v-icon class="info-icon" size="16">mdi-information-outline</v-icon>
              </div>
            </div>
          </div>
          
          <div class="header-right">
            <v-text-field
              v-model="search"
              placeholder="Search bin..."
              prepend-inner-icon="mdi-magnify"
              density="comfortable"
              hide-details
              variant="outlined"
              class="search-input"
            />
          </div>
        </div>

        <!-- Bulk Actions Bar -->
        <div v-if="selectedDocuments.length > 0" class="bulk-actions-bar">
          <div class="selected-count">
            {{ selectedDocuments.length }} item{{ selectedDocuments.length > 1 ? 's' : '' }} selected
          </div>
          <div class="bulk-actions">
            <v-btn
              variant="outlined"
              color="blue"
              size="small"
              @click="handleBulkRestore"
              class="mr-2"
            >
              <v-icon size="16" class="mr-1">mdi-history</v-icon>
              Restore Selected
            </v-btn>
            <v-btn
              variant="outlined"
              color="red"
              size="small"
              @click="handleBulkDelete"
            >
              <v-icon size="16" class="mr-1">mdi-delete-outline</v-icon>
              Delete Selected
            </v-btn>
          </div>
        </div>

        <div class="files-table">
          <table>
            <thead>
              <tr>
                <th>
                  <v-checkbox
                    v-model="selectAll"
                    @change="toggleSelectAll"
                    density="compact"
                    hide-details
                    color="primary"
                  />
                </th>
                <th>Name</th>
                <th>Size</th>
                <th>Auto Delete In</th>
                <th>Expected date</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in filteredDocuments" :key="doc.id">
                <td data-label="Select">
                  <v-checkbox
                    v-model="selectedDocuments"
                    :value="doc.id"
                    density="compact"
                    hide-details
                    color="primary"
                  />
                </td>
                <td class="file-cell" data-label="Name">
                  <div class="file-content">
                    <v-icon small class="me-1">
                      {{ doc.type === 'folder' ? 'mdi-folder' : 'mdi-file-document-outline' }}
                    </v-icon>
                    <span class="file-name">
                      {{ doc.type === 'folder' ? doc.name : doc.original_name }}
                    </span>
                  </div>
                </td>
                <td data-label="Size">
                  {{ doc.type === 'folder' ? '-' : formatSize(doc.file_size) }}
                </td>
                <td data-label="Auto Delete In">{{ getAutoDeleteInfo(doc.deleted_at, 'remaining') }}</td>
                <td data-label="Expected Date">{{ getAutoDeleteInfo(doc.deleted_at, 'date') }}</td>
                <td class="action-icons" data-label="Actions">
                  <v-icon small class="mr-2" color="blue" @click="handleRestore(doc)">
                    mdi-history
                  </v-icon>
                  <v-icon small color="red" @click="handlehardDelete(doc)">
                    mdi-delete-outline
                  </v-icon>
                </td>
              </tr>
              <tr v-if="filteredDocuments.length === 0">
                <td colspan="6" class="empty-text">No deleted documents or folders</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import SideBar from './SideBar.vue'
import { ref, watch } from 'vue'
import { processTrash } from '../composables/processTrash'

const search = ref('')
const selectedDocuments = ref([])
const selectAll = ref(false)

const {
  formatSize,
  filteredDocuments,
  handleRestore,
  handleRestoreBulk,
  getAutoDeleteInfo,
  handlehardDelete,
  handlehardDeleteBulk,
} = processTrash()

// Function to toggle select all
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedDocuments.value = filteredDocuments.value.map(doc => doc.id)
  } else {
    selectedDocuments.value = []
  }
}

// Watch for changes in selected documents to update selectAll checkbox
watch([selectedDocuments, filteredDocuments], () => {
  if (filteredDocuments.value.length === 0) {
    selectAll.value = false
    return
  }
  
  const allSelected = filteredDocuments.value.length > 0 && 
                     filteredDocuments.value.every(doc => selectedDocuments.value.includes(doc.id))
  
  if (selectAll.value !== allSelected) {
    selectAll.value = allSelected
  }
}, { deep: true })

// Watch search changes to clear selections if needed
watch(search, () => {
  // Clear selections when search changes
  selectedDocuments.value = []
  selectAll.value = false
})

// Bulk actions
const handleBulkRestore = async () => {
  if (selectedDocuments.value.length === 0) return
  
  try {
    // Get the actual document objects
    const itemsToRestore = filteredDocuments.value.filter(doc => 
      selectedDocuments.value.includes(doc.id)
    )
    
    // Use bulk restore function
    const result = await handleRestoreBulk(itemsToRestore)
    
    // Show result message
    if (result.successCount > 0) {
      let message = `${result.successCount} item(s) have been restored.`
      if (result.failCount > 0) {
        message += ` ${result.failCount} item(s) failed to restore.`
      }
      alert(message)
    } else {
      alert('Failed to restore items!')
    }
    
    selectedDocuments.value = []
    selectAll.value = false
  } catch (error) {
    console.error('Error restoring documents:', error)
    alert('Failed to restore items!')
  }
}

const handleBulkDelete = async () => {
  if (selectedDocuments.value.length === 0) return
  
  if (confirm(`Are you sure you want to permanently delete ${selectedDocuments.value.length} item(s)?`)) {
    try {
      // Get the actual document objects
      const itemsToDelete = filteredDocuments.value.filter(doc => 
        selectedDocuments.value.includes(doc.id)
      )
      
      // Use bulk delete function
      const result = await handlehardDeleteBulk(itemsToDelete)
      
      // Show single success message
      if (result.success) {
        alert(`${result.count} item(s) have been permanently deleted.`)
      }
      
      selectedDocuments.value = []
      selectAll.value = false
    } catch (error) {
      console.error('Error deleting documents:', error)
      alert('Failed to delete some items!')
    }
  }
}
</script>

<style scoped src="../assets/trash.css"></style>
