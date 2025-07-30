<template>
  <div class="page-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="collapse-icon">«</div>
      </div>
      <ul class="menu">
        <li v-for="item in sidebarItemsTop" :key="item.label">
          <v-icon>{{ item.icon }}</v-icon>

          <span>{{ item.label }}</span>
        </li>
      </ul>

      <ul class="menu menu-bottom">
        <li v-for="item in sidebarItemsBottom" :key="item.label" @click="handleSidebar(item)">
          <v-icon>{{ item.icon }}</v-icon>

          <span>{{ item.label }}</span>
        </li>
      </ul>
    </aside>

    <main class="main-content">
      <div class="documents-page">
        <div class="documents-header">
          <h2>Documents</h2>

          <div class="button-group">
            <v-menu offset-y>
              <template #activator="{ props }">
                <button class="btn-primary" v-bind="props">
                  <v-icon small class="mr-1">mdi-plus</v-icon>New
                </button>
              </template>

              <v-list>
                <v-list-item @click="triggerFileInput('file')">New file</v-list-item>
                <v-list-item @click="openCreateFolder('forder')">New folder</v-list-item>
              </v-list>
            </v-menu>
            <v-dialog v-model="createFolderDialog" width="400">
              <v-card>
                <v-card-title>New folder</v-card-title>
                <v-card-text>
                  <v-text-field v-model="newFolderName" label="Name Folder" />
                  <v-text-field v-model="newFolderDescription" label="Description" />
                  <input type="file" @change="onFileChange" />
                </v-card-text>
                <v-card-actions>
                  <v-btn @click="createFolderDialog = false">Cancel</v-btn>
                  <v-btn
                    @click="
                      () => {
                        createFolder()
                        createFolderDialog = false
                      }
                    "
                    color="primary"
                  >
                    Create
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
            <v-menu offset-y>
              <template #activator="{ props }">
                <button class="btn-secondary" v-bind="props">
                  <v-icon small class="mr-1">mdi-filter-menu-outline</v-icon> Filters
                </button>
              </template>

              <v-list>
                <v-list-item @click="filterByType('all')">All</v-list-item>
                <v-list-item @click="filterByType('PDF')">PDF</v-list-item>
                <v-list-item @click="filterByType('DOCX')">DOCX</v-list-item>
                <v-list-item @click="filterByType('PPTX')">PPTX</v-list-item>
                <v-list-item @click="filterByType('Folder')">Folder</v-list-item>
              </v-list>
            </v-menu>

            <v-menu offset-y>
              <template #activator="{ props }">
                <button class="btn-secondary" v-bind="props">
                  <v-icon small class="mr-1">mdi-sort</v-icon>Sort By
                </button>
              </template>

              <v-list>
                <v-list-item @click="sortBy = 'latest'">Latest</v-list-item>
                <v-list-item @click="sortBy = 'oldest'">Oldest</v-list-item>
                <v-list-item @click="sortBy = 'size_asc'">Small → Large</v-list-item>
                <v-list-item @click="sortBy = 'size_desc'">Large → Small</v-list-item>
                <v-list-item @click="sortBy = 'name_az'">Name A → Z</v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>

        <input
          type="file"
          accept=".pdf,.docx,.pptx"
          @change="handleFileSelect"
          style="display: none"
          ref="fileInput"
        />

        <div class="folders-section" v-if="foldersList.length">
          <div
            class="folder"
            v-for="folder in [...foldersList]
              .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
              .slice(0, 4)"
            :key="folder.id"
            @click="goToFolder(folder.id)"
          >
            <div class="folder-icon">
              <v-icon size="36" color="#6366f1">mdi-folder</v-icon>
            </div>
            <div class="folder-name">{{ folder.name }}</div>
            <div class="folder-meta">
              {{ folder.document_count || 0 }} Files ・ {{ formatSize(folder.total_size || 0) }}
            </div>
          </div>
        </div>

        <div class="recent-section" v-if="recentFiles.length">
          <h4>Recent</h4>
          <div class="recent-items">
            <div class="recent-card" v-for="r in recentFiles" :key="r.name">
              <div class="recent-card-content">
                <div class="icon-wrapper" @click="handleView(doc)" style="cursor: pointer">
                  <v-icon small>mdi-file-document-outline</v-icon>
                </div>
                <div class="recent-text">
                  <div class="recent-name">{{ r.name }}</div>
                  <div class="recent-meta">
                    <span>{{ r.date }}</span>
                    <span>・</span>
                    <span>{{ r.size }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="files-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Size</th>
                <th>Upload At</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="selectedFile">
                <td>{{ selectedFile.name }}</td>
                <td>{{ getFileType(selectedFile) }}</td>
              </tr>
              <tr v-for="item in sortedAndFilteredItems" :key="item.id">
                <td class="file-cell">
                  <div
                    class="file-content"
                    @click="item.type === 'folder' ? goToFolder(item.id) : handleView(item)"
                    style="cursor: pointer"
                  >
                    <v-icon small>
                      {{ item.type === 'folder' ? 'mdi-folder' : 'mdi-file-document-outline' }}
                    </v-icon>
                    <span class="file-name">{{ item.name }}</span>
                  </div>
                </td>
                <td>{{ item.type === 'folder' ? '-' : formatSize(item.file_size) }}</td>
                <td>{{ item.created_at ? formatDate(item.created_at) : '-' }}</td>
                <td class="action-icons">
                  <template v-if="item.type === 'file'">
                    <v-icon small class="mr-2" color="primary" @click="handleDownload(item)"
                      >mdi-cloud-download-outline</v-icon
                    >

                    <v-icon small class="mr-2" color="blue" @click="handleProcess(item)"
                      >mdi-autorenew</v-icon
                    >
                    <v-icon small color="red" @click="handleDelete(item)"
                      >mdi-delete-outline</v-icon
                    >
                  </template>
                  <template v-else>
                    <v-icon small class="mr-2" color="primary" @click="FolderUpfile(item)">
                      mdi-file-upload-outline
                    </v-icon>

                    <v-icon small class="mr-2" color="blue" @click="FolderProcess(item)"
                      >mdi-autorenew</v-icon
                    >
                    <v-icon small color="red" @click="FolderDelete(item)"
                      >mdi-delete-outline</v-icon
                    >
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
    <input type="file" ref="folderFileInput" style="display: none" @change="handleFolderUpload" />
  </div>
</template>

<script setup>
import { processDocument } from '../composables/processDocument'
import { processFolder } from '../composables/processFolder'
import { ref, onMounted } from 'vue'
const folderFileInput = ref(null)
const createFolderDialog = ref(false)

function openCreateFolder() {
  createFolderDialog.value = true
}
onMounted(() => {
  fetchDocumentsByFolder()
})
const {
  selectedFile,
  fileInput,
  sidebarItemsTop,
  sidebarItemsBottom,
  triggerFileInput,
  handleFileSelect,
  handleDownload,
  handleProcess,
  handleDelete,
  handleView,
  handleSidebar,
  formatSize,
  formatDate,
  getFileType,
  filterByType,
  sortBy,
  recentFiles,
  documents,
  fetchDocumentsByFolder,
  selectedType,
} = processDocument()
const {
  foldersList,
  newFolderName,
  newFolderDescription,
  sortedAndFilteredItems,
  goToFolder,
  createFolder,
  FolderDelete,
  onFileChange,
  FolderUpfile,
  handleFolderUpload,
} = processFolder(folderFileInput, fetchDocumentsByFolder, documents, selectedType)
</script>

<style scoped src="../assets/documents.css"></style>
