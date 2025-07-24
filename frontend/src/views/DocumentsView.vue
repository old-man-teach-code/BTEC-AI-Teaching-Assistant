<template>
  <div class="page-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="collapse-icon">«</div>
      </div>
      <ul class="menu">
        <li v-for="item in sidebarItemsTop" :key="item.label"
>          <v-icon>{{ item.icon }}</v-icon>

          <span>{{ item.label }}</span>
        </li>
      </ul>

      <ul class="menu menu-bottom">
        <li v-for="item in sidebarItemsBottom" :key="item.label"
          @click="handleSidebar(item)">
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
            <button class="btn-primary" @click="triggerFileInput">
              <v-icon small class="mr-1">mdi-plus</v-icon>
              New
            </button>

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

        <div class="folders-section" v-if="folders.length">
          <div class="folder" v-for="folder in folders" :key="folder.name">
            <div class="folder-icon" />
            <div class="folder-name">{{ folder.name }}</div>
            <div class="folder-meta">{{ folder.files }} Files ・ {{ folder.size }}</div>
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
                <th>Upload By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="selectedFile">
                <td>{{ selectedFile.name }}</td>
                <td>{{ getFileType(selectedFile) }}</td>
              </tr>
              <tr v-for="doc in sortedAndFilteredDocuments" :key="doc.id">
                <td class="file-cell">
                  <div class="file-content">
                    <div class="icon-wrapper" @click="handleView(doc)" style="cursor: pointer">
                      <v-icon small>mdi-file-document-outline</v-icon>
                    </div>
                    <span class="file-name">{{ doc.original_name }}</span>
                  </div>
                </td>
                <td>{{ formatSize(doc.file_size) }}</td>
                <td>{{ formatDate(doc.created_at) }}</td>
                <td>{{ doc.upload_by || 'Unknown' }}</td>
                <td class="action-icons">
                  <v-icon small class="mr-2" color="primary" @click="handleDownload(doc)"
                    >mdi-cloud-download-outline</v-icon
                  >
                  <v-icon small class="mr-2" color="blue" @click="handleProcess(doc)"
                    >mdi-autorenew</v-icon
                  >
                  <v-icon small color="red" @click="handleDelete(doc)">mdi-delete-outline</v-icon>
                </td>
              </tr>
              <tr v-if="sortedAndFilteredDocuments.length === 0 && !selectedFile">
                <td colspan="5" class="empty-text">No documents available</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { processDocument }  from '../composables/processDocument'

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
  folders,
  recentFiles,
  sortedAndFilteredDocuments,
} = processDocument()
</script>


<style scoped src="../assets/documents.css"></style>
