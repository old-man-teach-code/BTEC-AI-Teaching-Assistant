<template>
  <div class="d-flex flex-column align-items-center justify-content-center py-5">
    <i class="fas fa-folder-open fa-4x text-secondary mb-3"></i>
    <div class="fs-4 mb-2 text-secondary">No documents yet</div>
    <button class="btn btn-primary" @click="$emit('upload')">
      Upload first document
    </button>
  </div>
</template>

<script setup>
</script>