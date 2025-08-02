import api from './http'
export const getFolders = async (parentId = null) => {
  const params = {}
  if (parentId !== null) params.parent_id = parentId

  const res = await api.get("api/documents/folders/", { params })
  return res.data.data
}


export const createNewFolder = async (folderData) => {
  return await api.post("/api/documents/folders/", folderData)
}
