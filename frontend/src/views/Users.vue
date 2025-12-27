<template>
  <div class="h-full overflow-auto bg-surface p-8">
    <!-- 头部 -->
    <header class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">用户管理</h1>
        <p class="text-sm text-slate-500 mt-1">管理系统用户和角色权限</p>
      </div>
      <button
        @click="showCreateDialog = true"
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm flex items-center shadow-md transition-colors"
      >
        <el-icon class="mr-2"><Plus /></el-icon>
        新建用户
      </button>
    </header>

    <!-- 用户列表 -->
    <div class="bg-white rounded-2xl border border-slate-200/60 shadow-sm">
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="180" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-tooltip
              :content="getEditTooltip(row)"
              placement="top"
              :disabled="!isOtherAdmin(row)"
            >
              <el-button
                type="primary"
                size="small"
                link
                @click="handleEdit(row)"
                :disabled="isOtherAdmin(row)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
            </el-tooltip>
            <el-tooltip
              :content="getDeleteTooltip(row)"
              placement="top"
              :disabled="!shouldDisableDelete(row)"
            >
              <el-button
                type="danger"
                size="small"
                link
                @click="handleDelete(row)"
                :disabled="shouldDisableDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新建用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建用户"
      width="500px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="createForm.username"
            placeholder="请输入用户名"
            clearable
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="请输入密码（至少6位）"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="销售" value="SALES" />
            <el-option label="操作员" value="OPERATOR" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="createForm.is_active"
            active-text="激活"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑用户"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="用户名">
          <el-input :model-value="editingUser?.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="editForm.password"
            type="password"
            placeholder="留空则不修改密码"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="销售" value="SALES" />
            <el-option label="操作员" value="OPERATOR" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="editForm.is_active"
            active-text="激活"
            inactive-text="禁用"
            :disabled="editingUser?.id === currentUserId"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { getUsers, createUser, updateUser, deleteUser } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 当前用户ID
const currentUserId = computed(() => userStore.userInfo?.id)

// 用户列表
const users = ref([])
const loading = ref(false)

// 对话框显示状态
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const submitting = ref(false)

// 新建表单
const createFormRef = ref()
const createForm = ref({
  username: '',
  password: '',
  role: 'OPERATOR',
  is_active: true
})

const createRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 编辑表单
const editFormRef = ref()
const editingUser = ref(null)
const editForm = ref({
  password: '',
  role: '',
  is_active: true
})

const editRules = {
  password: [
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const response = await getUsers()
    if (response.code === 200) {
      users.value = response.data.users
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 创建用户
const handleCreate = async () => {
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const response = await createUser(createForm.value)
    if (response.code === 200) {
      ElMessage.success('用户创建成功')
      showCreateDialog.value = false
      createForm.value = {
        username: '',
        password: '',
        role: 'OPERATOR',
        is_active: true
      }
      loadUsers()
    }
  } catch (error) {
    console.error('创建用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建用户失败')
  } finally {
    submitting.value = false
  }
}

// 编辑用户
const handleEdit = (user) => {
  editingUser.value = user
  editForm.value = {
    password: '',
    role: user.role,
    is_active: user.is_active
  }
  showEditDialog.value = true
}

// 更新用户
const handleUpdate = async () => {
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const updateData = {
      role: editForm.value.role,
      is_active: editForm.value.is_active
    }
    // 只有输入了密码才更新密码
    if (editForm.value.password) {
      updateData.password = editForm.value.password
    }

    const response = await updateUser(editingUser.value.id, updateData)
    if (response.code === 200) {
      ElMessage.success('用户更新成功')
      showEditDialog.value = false
      loadUsers()
    }
  } catch (error) {
    console.error('更新用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新用户失败')
  } finally {
    submitting.value = false
  }
}

// 删除用户
const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const response = await deleteUser(user.id)
    if (response.code === 200) {
      ElMessage.success('用户删除成功')
      loadUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除用户失败')
    }
  }
}

// 角色标签类型
const getRoleTagType = (role) => {
  const typeMap = {
    'ADMIN': 'danger',
    'SALES': 'success',
    'OPERATOR': 'info'
  }
  return typeMap[role] || ''
}

// 角色标签文本
const getRoleLabel = (role) => {
  const labelMap = {
    'ADMIN': '管理员',
    'SALES': '销售',
    'OPERATOR': '操作员'
  }
  return labelMap[role] || role
}

// 判断是否是其他管理员（不是自己的管理员账号）
const isOtherAdmin = (user) => {
  return user.role === 'ADMIN' && user.id !== currentUserId.value
}

// 判断是否应该禁用删除按钮
const shouldDisableDelete = (user) => {
  // 不能删除自己
  if (user.id === currentUserId.value) {
    return true
  }
  // 不能删除其他管理员
  if (user.role === 'ADMIN') {
    return true
  }
  return false
}

// 获取编辑按钮的提示文本
const getEditTooltip = (user) => {
  if (isOtherAdmin(user)) {
    return '不能修改其他管理员的信息（安全保护）'
  }
  return ''
}

// 获取删除按钮的提示文本
const getDeleteTooltip = (user) => {
  if (user.id === currentUserId.value) {
    return '不能删除自己的账号'
  }
  if (user.role === 'ADMIN') {
    return '不能删除管理员账号（安全保护）'
  }
  return ''
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 挂载时加载数据
onMounted(() => {
  loadUsers()
})
</script>
