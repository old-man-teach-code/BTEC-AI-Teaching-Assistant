
import { ref, computed, onMounted } from 'vue'
import api from '../api/http'
import { processDocument } from './processDocument' // sử dụng các ref & computed 
const fileInput = ref(null)
const folderUploadTarget = ref(null)

export function processFolder(folderFileInput,fetchDocumentsByFolder, documents) {
  // 📁 Folder state
  const foldersList = ref([])
  const newFolderName = ref('')
  const newFolderDescription = ref('')
  const loading = ref(false)
  const selectedFolderId = ref(null)
  const showAddFileDialog = ref(false)
  const currentFolderId = ref(null)
  const newFolderFile = ref(null)         
  const selectedFolderFile = ref(null)            
  const targetFolderId = ref(null)                

  const {
    sortedAndFilteredDocuments,
    selectedType,
    sortBy,
  } = processDocument()

  const fetchFolders = async () => {
    loading.value = true
    try {
      const res = await api.get('/api/documents/folders/')
      foldersList.value = res.data.items || []
    } catch (e) {
      console.error('Lỗi khi lấy folders:', e)
      foldersList.value = []
    }
    loading.value = false
  }

const createFolder = async () => {
  if (!newFolderName.value.trim()) {
    alert('Vui lòng nhập tên thư mục');
    return;
  }

  try {
    const res = await api.post('/api/documents/folders/', {
      name: newFolderName.value,
      description: newFolderDescription.value,
    });
    
    const folderId = res.data.folder.id;
    console.log('Folder mới tạo có ID:', folderId);

    const file = newFolderFile.value;

    if (file && file instanceof File) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const uploadRes = await api.post('/api/documents/upload', formData);
        const documentId = uploadRes.data.id;
        console.log('File upload xong, có documentId:', documentId);

        const moveRes = await api.post(
          `/api/documents/${documentId}/move`,
          { folder_id: folderId },
          { headers: { 'Content-Type': 'application/json' } }
        );
        console.log('Gán document vào folder xong:', moveRes.data);

        alert('Folder created and file uploaded successfully!');
        newFolderFile.value = null;

      } catch (e) {
        console.error('Lỗi khi tải file hoặc gán vào thư mục:')
        if (e.response) {
          console.error('Response data:', JSON.stringify(e.response.data, null, 2));
          console.error('Status:', e.response.status);
        } else {
          console.error('Không có phản hồi từ server:', e.message);
        }
        alert('Failed to upload file or assign to folder!');
      }
    } else {
      alert('Folder was created successfully without any attached file.');
    }

    newFolderName.value = '';
    newFolderDescription.value = '';
    await fetchFolders();
    await fetchDocumentsByFolder();

  } catch (e) {
    console.error('Tạo thư mục thất bại:', e);
    alert('Unable to create folder!');
  }
};

const onFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    newFolderFile.value = file
  }
}
function goToFolder(folderId) {
  selectedFolderId.value = folderId
  fetchDocumentsByFolder(folderId)
    console.log('Mở folder ID:', folderId)
  }
const sortedAndFilteredItems = computed(() => {
  if (selectedFolderId.value) {
    const filesInFolder = documents.value.filter(doc => doc.folder_id === selectedFolderId.value)

    console.log('selectedFolderId:', selectedFolderId.value)
    console.log('documents.value:', documents.value)
    console.log('filesInFolder:', filesInFolder)

    return filesInFolder.map(doc => ({
      ...doc,
      name: doc.original_name,
      type: 'file',
    })).sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  }

  // Nếu không chọn folder nào: hiển thị folder + file chưa gán folder
  const folders = foldersList.value.map(folder => ({
    id: folder.id,
    name: folder.name,
    size: '-',
    created_at: folder.created_at || null,
    type: 'folder',
  }))

  const files = documents.value
    .filter(doc => !doc.folder_id)
    .map(doc => ({
      ...doc,
      name: doc.original_name,
      type: 'file',
    }))

  return [...folders, ...files].sort((a, b) => {
    if (a.type === 'folder' && b.type === 'file') return -1
    if (a.type === 'file' && b.type === 'folder') return 1
    return new Date(b.created_at || 0) - new Date(a.created_at || 0)
  })
})




const FolderDelete = async (item) => {
  if (!item?.id) return alert('Cannot find the folder to delete')
  try {
    await api.delete(`/api/documents/folders/${item.id}`, {
      params: { hard_delete: false }
    })
    alert('Folder has been moved to the trash')
    foldersList.value = foldersList.value.filter(f => f.id !== item.id)
  } catch (e) {
    alert('"Failed to delete the folder !')
    console.error(e)
  }
}
function FolderUpfile(folder) {
  console.log('Clicked icon to upload into folder:', folder)

  targetFolderId.value = folder.id

  if (folderFileInput.value) {
    console.log('folderFileInput found, triggering file input click')
    folderFileInput.value.click()
  } else {
    console.warn('folderFileInput NOT found')
  }
}


// Khi file được chọn từ hộp thoại folder
async function handleFolderUpload(event) {
  const file = event.target.files[0]
  if (!file || !targetFolderId.value) return
  selectedFolderFile.value = file
  await uploadFileToFolder()
}

// Upload file vào folder
async function uploadFileToFolder() {
  if (!selectedFolderFile.value || !targetFolderId.value) {
    console.warn('File or folderId is missing')
    return
  }

  console.log('Pending File:', selectedFolderFile.value.name)
  console.log('Folder ID:', targetFolderId.value)

  const formData = new FormData()
  formData.append('file', selectedFolderFile.value)

  try {
    // 1. Upload file
    const uploadRes = await api.post('/api/documents/upload', formData)
    const documentId = uploadRes.data.id
    console.log('📄 File đã upload xong, documentId:', documentId)

    // 2. Gọi API move document vào folder
    await api.post(
      `/api/documents/${documentId}/move`,
      { folder_id: targetFolderId.value },
      { headers: { 'Content-Type': 'application/json' } }
    )
console.log('📦 Assigned to folder:', targetFolderId.value)

alert('Upload & assign to folder successful!')

// 3. Reset
selectedFolderFile.value = null
folderFileInput.value.value = null
targetFolderId.value = null

await fetchDocumentsByFolder?.()
await fetchFolders?.()
} catch (e) {
  console.error('Upload or folder assignment failed:', e)
  alert('Error during upload or folder assignment!')
}

}



  onMounted(() => {
    fetchFolders()
    fetchDocumentsByFolder()
  })

  return {
    foldersList,
    newFolderName,
    newFolderDescription,
    loading,
    fetchFolders,
    createFolder,
    goToFolder,
    sortedAndFilteredItems,
    selectedType,
    sortBy,
    FolderDelete,
    newFolderFile,
    onFileChange,
    FolderUpfile,
    uploadFileToFolder,
    handleFolderUpload,
    folderFileInput,
  }
}
