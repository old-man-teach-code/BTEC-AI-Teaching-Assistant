<template>
  <div class="page-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="collapse-icon">«</div>
      </div>
      <ul class="menu">
        <li v-for="item in sidebarItemsTop" :key="item.label" @click="handleSidebar(item)">
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

    <!-- Main -->
    <main class="main-content">
      <div class="documents-page">
        <!-- Header -->
        <div class="documents-header d-flex align-center justify-space-between flex-wrap mb-4">
          <div class="d-flex align-center">
            <v-icon class="me-2 icon-title">mdi-delete-variant</v-icon>
            <div>
              <h2 class="mb-1 title-text">Recycle Bin</h2>
              <div class="text-caption text-grey description-text">
                When you delete something we’ll keep it here for 30 days, just in case you regret.
              </div>
            </div>
          </div>
          <v-text-field
            v-model="search"
            placeholder="Search bin..."
            prepend-inner-icon="mdi-magnify"
            density="comfortable"
            hide-details
            class="white-search-input"
            style="max-width: 300px"
          />
        </div>

        <div class="files-table">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Size</th>
                <th>Auto Delete In</th>
                <th>Expected date</th>
                <th>Options</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in filteredDocuments" :key="doc.id">
                <td class="file-cell">
                  <div class="file-content">
                    <v-icon small class="me-1">
                      {{ doc.type === 'folder' ? 'mdi-folder' : 'mdi-file-document-outline' }}
                    </v-icon>
                    <span class="file-name">
                      {{ doc.type === 'folder' ? doc.name : doc.original_name }}
                    </span>
                  </div>
                </td>
                <td>
                  {{ doc.type === 'folder' ? '-' : formatSize(doc.file_size) }}
                </td>
                <td>{{ getAutoDeleteInfo(doc.deleted_at, 'remaining') }}</td>
                <td>{{ getAutoDeleteInfo(doc.deleted_at, 'date') }}</td>
                <td class="action-icons">
                  <v-icon small class="mr-2" color="blue" @click="handleRestore(doc)">
                    mdi-history
                  </v-icon>
                  <v-icon small color="red" @click="handlehardDelete(doc)">
                    mdi-delete-outline
                  </v-icon>
                </td>
              </tr>
              <tr v-if="filteredDocuments.length === 0">
                <td colspan="5" class="empty-text">No deleted documents or folders</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>


<script setup>
import { processTrash } from '../composables/processTrash'
const {
  handleSidebar,
  formatSize,
  filteredDocuments,
  sidebarItemsTop,
  sidebarItemsBottom,
  handleRestore,
  getAutoDeleteInfo,
  handlehardDelete,
} = processTrash()
</script>
<style scoped src="../assets/trash.css"></style>
