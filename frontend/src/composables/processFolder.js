
import { ref, computed, onMounted } from 'vue'
import api from '../api/http'
import { processDocument } from './processDocument' // sử dụng các ref & computed 
const fileInput = ref(null)
const folderUploadTarget = ref(null)

export function processFolder(folderFileInput, fetchDocumentsByFolder, documentsRef, selectedTypeRef) {
  const documents = documentsRef
  const selectedType = selectedTypeRef 

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
    sortBy,
  } = processDocument()

  // Local getFileType function to ensure consistency
  const getFileType = (file) => {
    // Nếu file là object với thuộc tính type (File object)
    if (file && typeof file === 'object' && file.type) {
      if (file.type.includes('pdf')) return 'PDF'
      if (file.type.includes('word') || file.type.includes('document')) return 'DOCX'
      if (file.type.includes('presentation')) return 'PPTX'
      if (file.type.includes('sheet')) return 'XLSX'
      return file.type
    }
    
    // Nếu file là string (file_type từ database hoặc filename)
    if (typeof file === 'string') {
      const lowerFile = file.toLowerCase()
      
      // Kiểm tra extension từ filename
      if (lowerFile.endsWith('.pdf')) return 'PDF'
      if (lowerFile.endsWith('.docx') || lowerFile.endsWith('.doc')) return 'DOCX'
      if (lowerFile.endsWith('.pptx') || lowerFile.endsWith('.ppt')) return 'PPTX'
      if (lowerFile.endsWith('.xlsx') || lowerFile.endsWith('.xls')) return 'XLSX'
      if (lowerFile.endsWith('.txt')) return 'TXT'
      if (lowerFile.endsWith('.jpg') || lowerFile.endsWith('.jpeg') || lowerFile.endsWith('.png')) return 'IMAGE'
      
      // Kiểm tra MIME type strings
      if (lowerFile.includes('pdf')) return 'PDF'
      if (lowerFile.includes('word') || lowerFile.includes('document')) return 'DOCX'
      if (lowerFile.includes('presentation')) return 'PPTX'
      if (lowerFile.includes('sheet')) return 'XLSX'
      
      return file.toUpperCase()
    }
    
    return ''
  }

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
  console.log('[sortedAndFilteredItems] selectedType:', selectedType.value)
  console.log('[sortedAndFilteredItems] selectedFolderId:', selectedFolderId.value)

  // Nếu đang trong 1 folder
  if (selectedFolderId.value) {
    // Nếu đang lọc "Folder" thì không hiển thị file trong folder
    if (selectedType.value === 'Folder') {
      return []
    }

    let filesInFolder = documents.value.filter(doc => doc.folder_id === selectedFolderId.value)

    // Filter theo selectedType
    if (selectedType.value !== 'all') {
      filesInFolder = filesInFolder.filter(doc => {
        const type = getFileType(doc.file_type) || getFileType(doc.original_name)
        console.log(`[processFolder-InFolder] Filtering: "${doc.original_name}" | file_type: "${doc.file_type}" | detected: "${type}" | selectedType: "${selectedType.value}" | match: ${type === selectedType.value}`)
        return type === selectedType.value
      })
    }

    // Sort trong folder
    switch (sortBy.value) {
      case 'latest':
        filesInFolder.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
        break
      case 'oldest':
        filesInFolder.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))
        break
      case 'size_asc':
        filesInFolder.sort((a, b) => (a.file_size || 0) - (b.file_size || 0))
        break
      case 'size_desc':
        filesInFolder.sort((a, b) => (b.file_size || 0) - (a.file_size || 0))
        break
      case 'name_az':
        filesInFolder.sort((a, b) => (a.original_name || '').localeCompare(b.original_name || ''))
        break
    }

    return filesInFolder.map(doc => ({
      ...doc,
      name: doc.original_name,
      type: 'file',
    }))
  }

  // Nếu KHÔNG trong folder → hiển thị folder + file chưa gán
let folders = []
let files = []

// Nếu lọc theo "Folder" → chỉ hiện danh sách folder
if (selectedType.value === 'Folder') {
  folders = foldersList.value.map(folder => ({
    id: folder.id,
    name: folder.name,
    size: '-',
    created_at: folder.created_at || null,
    type: 'folder',
  }))
} else {
  // Các loại file khác → hiện folder + file chưa gán vào folder
  if (selectedType.value === 'all') {
    folders = foldersList.value.map(folder => ({
      id: folder.id,
      name: folder.name,
      size: '-',
      created_at: folder.created_at || null,
      type: 'folder',
    }))
  }

  let filteredFiles = documents.value.filter(doc => !doc.folder_id)

  if (selectedType.value !== 'all') {
    filteredFiles = filteredFiles.filter(doc => {
      const type = getFileType(doc.file_type) || getFileType(doc.original_name)
      console.log(`[processFolder] Filtering: "${doc.original_name}" | file_type: "${doc.file_type}" | detected: "${type}" | selectedType: "${selectedType.value}" | match: ${type === selectedType.value}`)
      return type === selectedType.value
    })
  }

  files = filteredFiles.map(doc => ({
    ...doc,
    name: doc.original_name,
    type: 'file',
  }))
}


  let result = [...folders, ...files]

  // Sort toàn bộ danh sách
  switch (sortBy.value) {
    case 'latest':
      result.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
      break
    case 'oldest':
      result.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))
      break
    case 'size_asc':
      result.sort((a, b) => (a.file_size || 0) - (b.file_size || 0))
      break
    case 'size_desc':
      result.sort((a, b) => (b.file_size || 0) - (a.file_size || 0))
      break
    case 'name_az':
      result.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
      break
  }

  // folder luôn hiển thị trước file
  result.sort((a, b) => {
    if (a.type === 'folder' && b.type === 'file') return -1
    if (a.type === 'file' && b.type === 'folder') return 1
    return 0
  })

  return result
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
    console.log('File đã upload xong, documentId:', documentId)

    // 2. Gọi API move document vào folder
    await api.post(
      `/api/documents/${documentId}/move`,
      { folder_id: targetFolderId.value },
      { headers: { 'Content-Type': 'application/json' } }
    )
console.log('Assigned to folder:', targetFolderId.value)

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
