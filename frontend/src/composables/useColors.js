export function useColors() {
  const getTypeColor = (type) => {
    const colors = {
      // Document types
      'PDF': 'red',
      'DOC': 'blue',
      'DOCX': 'blue',
      'TXT': 'grey',
      
      // Spreadsheet types  
      'XLS': 'green',
      'XLSX': 'green',
      'CSV': 'green',
      
      // Presentation types
      'PPT': 'orange',
      'PPTX': 'orange',
      
      // Image types
      'JPG': 'purple',
      'JPEG': 'purple', 
      'PNG': 'purple',
      'GIF': 'purple',
      'SVG': 'purple',
      
      // Archive types
      'ZIP': 'brown',
      'RAR': 'brown',
      '7Z': 'brown',
      
      // Code types
      'JS': 'yellow',
      'TS': 'blue-darken-2',
      'CSS': 'cyan',
      'HTML': 'orange-darken-2',
      
      // Other activity types
      'MEETING': 'indigo',
      'SYSTEM': 'cyan',
      'MESSAGE': 'teal',
      'DEADLINE': 'red'
    }
    return colors[type] || 'grey'
  }

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'orange',
      'DONE': 'green',
      'IN_PROGRESS': 'blue',
      'CANCELLED': 'grey'
    }
    return colors[status] || 'grey'
  }

  const getPriorityColor = (priority) => {
    const colors = {
      'HIGH': 'red',
      'MEDIUM': 'orange',
      'LOW': 'green'
    }
    return colors[priority] || 'grey'
  }

  return {
    getTypeColor,
    getStatusColor,
    getPriorityColor
  }
}
