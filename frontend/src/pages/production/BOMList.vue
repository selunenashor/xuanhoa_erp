<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Định mức nguyên vật liệu (BOM)</h1>
        <p class="text-gray-600">Quản lý công thức sản xuất sản phẩm</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center gap-2 px-4 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Tạo BOM mới
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Tìm kiếm</label>
          <div class="relative">
            <input
              type="text"
              v-model="filters.search"
              @input="debouncedSearch"
              placeholder="Nhập mã BOM hoặc tên sản phẩm..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <!-- Item Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Sản phẩm</label>
          <select
            v-model="filters.item_code"
            @change="loadBOMs"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">Tất cả sản phẩm</option>
            <option v-for="item in items" :key="item.item_code" :value="item.item_code">
              {{ item.item_name || item.item_code }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Trạng thái</label>
          <select
            v-model="filters.is_active"
            @change="loadBOMs"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="">Tất cả</option>
            <option value="1">Đang hoạt động</option>
            <option value="0">Ngưng hoạt động</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div class="bg-white rounded-lg shadow">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Empty state -->
      <div v-else-if="boms.length === 0" class="text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có BOM nào</h3>
        <p class="text-gray-500 mb-4">Bắt đầu bằng việc tạo BOM mới</p>
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center gap-2 px-4 py-2 text-white bg-primary rounded-lg hover:bg-primary-dark"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Tạo BOM mới
        </button>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mã BOM
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sản phẩm
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Số lượng
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Số NVL
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Chi phí NVL
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trạng thái
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Thao tác
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="bom in boms" 
              :key="bom.name"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewDetail(bom.name)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-sm font-medium text-primary">{{ bom.name }}</span>
                <span v-if="bom.is_default" class="ml-2 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">
                  Mặc định
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ bom.item }}</div>
                <div class="text-sm text-gray-500">{{ bom.item_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{ formatNumber(bom.quantity) }}</span>
                <span class="text-sm text-gray-500 ml-1">{{ formatUOM(bom.uom) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span class="text-sm text-gray-900">{{ bom.item_count || 0 }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(bom.raw_material_cost || bom.total_cost) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  :class="[
                    'px-2 py-1 text-xs rounded-full',
                    bom.is_active 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-gray-100 text-gray-700'
                  ]"
                >
                  {{ bom.is_active ? 'Hoạt động' : 'Ngưng' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center" @click.stop>
                <div class="flex justify-center gap-2">
                  <button
                    @click="viewDetail(bom.name)"
                    class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 rounded transition-colors"
                    title="Xem chi tiết"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    @click="editBOM(bom)"
                    class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="Chỉnh sửa"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="confirmDelete(bom)"
                    class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Xóa"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="boms.length > 0 && pagination.totalPages > 1" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-500">
            Hiển thị {{ (pagination.page - 1) * pagination.pageSize + 1 }} - 
            {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} / {{ pagination.total }} BOM
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Trước
            </button>
            <span class="px-3 py-1 text-sm text-gray-600">
              Trang {{ pagination.page }} / {{ pagination.totalPages }}
            </span>
            <button
              @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page >= pagination.totalPages"
              class="px-3 py-1 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- BOM Detail Modal -->
    <div v-if="selectedBOM" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="selectedBOM = null"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          <!-- Modal Header -->
          <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ selectedBOM.name }}</h3>
              <p class="text-sm text-gray-500">{{ selectedBOM.item_name }}</p>
            </div>
            <button @click="selectedBOM = null" class="p-2 hover:bg-gray-200 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Modal Content -->
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            <!-- BOM Info -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Sản phẩm</div>
                <div class="font-medium">{{ selectedBOM.item }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Số lượng</div>
                <div class="font-medium">{{ formatNumber(selectedBOM.quantity) }} {{ formatUOM(selectedBOM.uom) }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Chi phí NVL</div>
                <div class="font-medium">{{ formatCurrency(selectedBOM.raw_material_cost || 0) }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Trạng thái</div>
                <div class="font-medium">
                  <span :class="selectedBOM.is_active ? 'text-green-600' : 'text-gray-600'">
                    {{ selectedBOM.is_active ? 'Hoạt động' : 'Ngưng' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- BOM Items -->
            <h4 class="font-semibold text-gray-900 mb-3">Danh sách nguyên vật liệu</h4>
            <div v-if="loadingDetail" class="flex justify-center py-8">
              <svg class="animate-spin h-6 w-6 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <table v-else class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">STT</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Mã NVL</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Tên NVL</th>
                  <th class="px-4 py-2 text-center text-xs font-medium text-gray-500">Số lượng</th>
                  <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Đơn giá</th>
                  <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Thành tiền</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(item, index) in bomItems" :key="item.item_code">
                  <td class="px-4 py-2 text-sm text-gray-500">{{ index + 1 }}</td>
                  <td class="px-4 py-2 text-sm font-medium text-gray-900">{{ item.item_code }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700">{{ item.item_name }}</td>
                  <td class="px-4 py-2 text-sm text-center">
                    {{ formatNumber(item.qty) }} {{ formatUOM(item.uom) }}
                  </td>
                  <td class="px-4 py-2 text-sm text-right">{{ formatCurrency(item.rate) }}</td>
                  <td class="px-4 py-2 text-sm text-right font-medium">{{ formatCurrency(item.amount) }}</td>
                </tr>
              </tbody>
              <tfoot class="bg-gray-50">
                <tr>
                  <td colspan="5" class="px-4 py-2 text-sm font-medium text-right">Tổng chi phí NVL:</td>
                  <td class="px-4 py-2 text-sm font-bold text-right text-primary">
                    {{ formatCurrency(selectedBOM.raw_material_cost || 0) }}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit BOM Modal -->
    <div v-if="showCreateModal || editingBOM" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="closeCreateModal"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          <!-- Modal Header -->
          <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingBOM ? 'Chỉnh sửa BOM' : 'Tạo BOM mới' }}
            </h3>
            <button @click="closeCreateModal" class="p-2 hover:bg-gray-200 rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Modal Content -->
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
            <!-- Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Sản phẩm <span class="text-red-500">*</span></label>
                <select
                  v-model="formData.item"
                  @change="onProductSelect"
                  :disabled="!!editingBOM"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-gray-100"
                >
                  <option value="">Chọn sản phẩm</option>
                  <option v-for="item in productItems" :key="item.item_code" :value="item.item_code">
                    {{ item.item_name || item.item_code }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Số lượng <span class="text-red-500">*</span></label>
                <input
                  type="number"
                  v-model.number="formData.quantity"
                  min="1"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Đơn vị tính</label>
                <input
                  type="text"
                  :value="formatUOM(formData.uom)"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary bg-gray-50"
                  readonly
                />
              </div>
              <div class="flex items-end gap-4">
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.is_active" class="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span class="text-sm text-gray-700">Hoạt động</span>
                </label>
                <label class="flex items-center gap-2 group relative">
                  <input type="checkbox" v-model="formData.is_default" class="rounded border-gray-300 text-primary focus:ring-primary" />
                  <span class="text-sm text-gray-700">Mặc định</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400 cursor-help" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div class="absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <strong>BOM Mặc định:</strong> Khi tạo Lệnh sản xuất cho sản phẩm này, hệ thống sẽ tự động sử dụng BOM mặc định. Mỗi sản phẩm chỉ có 1 BOM mặc định.
                  </div>
                </label>
              </div>
            </div>

            <!-- BOM Items -->
            <div class="mb-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-semibold text-gray-900">Danh sách nguyên vật liệu</h4>
                <button
                  @click="addBOMItem"
                  class="inline-flex items-center gap-1 px-3 py-1.5 text-sm text-primary border border-primary rounded-lg hover:bg-primary hover:text-white transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  Thêm NVL
                </button>
              </div>
              
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Nguyên vật liệu</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 w-32">Số lượng</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 w-24">ĐVT</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 w-16"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="(item, index) in formData.items" :key="index">
                    <td class="px-3 py-2">
                      <select
                        v-model="item.item_code"
                        @change="onItemSelect(index)"
                        class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-primary focus:border-primary"
                      >
                        <option value="">Chọn NVL</option>
                        <option v-for="mat in rawMaterials" :key="mat.item_code" :value="mat.item_code">
                          {{ mat.item_name || mat.item_code }}
                        </option>
                      </select>
                    </td>
                    <td class="px-3 py-2">
                      <input
                        type="number"
                        v-model.number="item.qty"
                        min="0.001"
                        step="0.001"
                        class="w-full px-2 py-1.5 text-sm text-center border border-gray-300 rounded focus:ring-2 focus:ring-primary focus:border-primary"
                      />
                    </td>
                    <td class="px-3 py-2 text-center text-sm text-gray-500">
                      {{ formatUOM(item.uom) }}
                    </td>
                    <td class="px-3 py-2 text-center">
                      <button
                        @click="removeBOMItem(index)"
                        class="p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                  <tr v-if="formData.items.length === 0">
                    <td colspan="4" class="px-3 py-8 text-center text-gray-500">
                      Chưa có nguyên vật liệu. Nhấn "Thêm NVL" để bắt đầu.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
            <button
              @click="closeCreateModal"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Hủy
            </button>
            <button
              @click="saveBOM"
              :disabled="saving"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 inline-flex items-center gap-2"
            >
              <svg v-if="saving" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ editingBOM ? 'Cập nhật' : 'Tạo BOM' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingBOM" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="deletingBOM = null"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div class="text-center">
            <div class="w-12 h-12 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Xác nhận xóa BOM</h3>
            <p class="text-gray-500 mb-6">
              Bạn có chắc chắn muốn xóa BOM <strong>{{ deletingBOM.name }}</strong>?<br>
              Hành động này không thể hoàn tác.
            </p>
            <div class="flex justify-center gap-3">
              <button
                @click="deletingBOM = null"
                class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Hủy
              </button>
              <button
                @click="deleteBOM"
                :disabled="deleting"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 inline-flex items-center gap-2"
              >
                <svg v-if="deleting" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Xóa
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 z-[60] transition-all',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { bomAPI, stockAPI } from '@/api'

// State
const loading = ref(false)
const loadingDetail = ref(false)
const saving = ref(false)
const deleting = ref(false)
const boms = ref([])
const items = ref([])
const selectedBOM = ref(null)
const bomItems = ref([])
const showCreateModal = ref(false)
const editingBOM = ref(null)
const deletingBOM = ref(null)

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 1
})

// Filters
const filters = reactive({
  search: '',
  item_code: '',
  is_active: ''
})

// Form data
const formData = reactive({
  item: '',
  quantity: 1,
  uom: 'Cái',
  is_active: true,
  is_default: false,
  items: []
})

// Toast
const toast = reactive({
  show: false,
  type: 'success',
  message: ''
})

// Computed
const productItems = computed(() => {
  // Tất cả item có thể là sản phẩm (thành phẩm, bán thành phẩm)
  return items.value.filter(i => 
    i.item_group === 'Thành phẩm' || 
    i.item_group === 'Bán thành phẩm' ||
    i.item_group === 'Đèn Chiếu Sáng' ||
    i.item_group === 'Bóng Đèn LED' ||
    i.is_stock_item
  )
})

const rawMaterials = computed(() => {
  // Tất cả item có thể là NVL
  return items.value
})

// Debounce timer
let searchTimeout = null

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatCurrency = (num) => {
  if (!num) return '0 ₫'
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(num)
}

const formatUOM = (uom) => {
  if (!uom) return 'Cái'
  const uomMap = {
    'Nos': 'Cái',
    'Kg': 'Kg',
    'Meter': 'Mét',
    'Unit': 'Đơn vị',
    'Box': 'Hộp',
    'Pair': 'Cặp',
    'Set': 'Bộ',
    'Litre': 'Lít',
    'Gram': 'Gram'
  }
  return uomMap[uom] || uom
}

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

const debouncedSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.page = 1
    loadBOMs()
  }, 300)
}

const loadItems = async () => {
  try {
    const result = await stockAPI.getItems()
    items.value = result || []
  } catch (error) {
    console.error('Error loading items:', error)
  }
}

const loadBOMs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    
    if (filters.search) params.search = filters.search
    if (filters.item_code) params.item = filters.item_code
    if (filters.is_active !== '') params.is_active = parseInt(filters.is_active)
    
    const result = await bomAPI.getList(params)
    
    if (Array.isArray(result)) {
      boms.value = result
      pagination.total = result.length
      pagination.totalPages = 1
    } else {
      boms.value = result.data || []
      pagination.total = result.total || 0
      pagination.totalPages = result.total_pages || 1
      pagination.page = result.page || 1
    }
  } catch (error) {
    console.error('Error loading BOMs:', error)
    showToast('error', 'Không thể tải danh sách BOM')
  } finally {
    loading.value = false
  }
}

const viewDetail = async (name) => {
  loadingDetail.value = true
  bomItems.value = []
  
  // Find BOM in list first
  const bom = boms.value.find(b => b.name === name)
  if (bom) {
    selectedBOM.value = bom
  }
  
  try {
    const result = await bomAPI.getDetail(name)
    selectedBOM.value = result
    bomItems.value = result.items || []
  } catch (error) {
    console.error('Error loading BOM detail:', error)
    showToast('error', 'Không thể tải chi tiết BOM')
  } finally {
    loadingDetail.value = false
  }
}

const editBOM = async (bom) => {
  loadingDetail.value = true
  try {
    const result = await bomAPI.getDetail(bom.name)
    editingBOM.value = result
    
    formData.item = result.item
    formData.quantity = result.quantity
    formData.uom = result.uom || 'Cái'
    formData.is_active = !!result.is_active
    formData.is_default = !!result.is_default
    formData.items = (result.items || []).map(item => ({
      item_code: item.item_code,
      qty: item.qty,
      uom: item.uom || 'Cái'
    }))
  } catch (error) {
    console.error('Error loading BOM for edit:', error)
    showToast('error', 'Không thể tải BOM để chỉnh sửa')
  } finally {
    loadingDetail.value = false
  }
}

const confirmDelete = (bom) => {
  deletingBOM.value = bom
}

const deleteBOM = async () => {
  if (!deletingBOM.value) return
  
  deleting.value = true
  try {
    await bomAPI.delete(deletingBOM.value.name)
    showToast('success', 'Đã xóa BOM thành công')
    deletingBOM.value = null
    loadBOMs()
  } catch (error) {
    console.error('Error deleting BOM:', error)
    showToast('error', error.response?.data?.message || 'Không thể xóa BOM')
  } finally {
    deleting.value = false
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingBOM.value = null
  resetForm()
}

const resetForm = () => {
  formData.item = ''
  formData.quantity = 1
  formData.uom = 'Cái'
  formData.is_active = true
  formData.is_default = false
  formData.items = []
}

const addBOMItem = () => {
  formData.items.push({
    item_code: '',
    qty: 1,
    uom: 'Cái'
  })
}

const removeBOMItem = (index) => {
  formData.items.splice(index, 1)
}

const onItemSelect = (index) => {
  const selectedItem = items.value.find(i => i.item_code === formData.items[index].item_code)
  if (selectedItem) {
    formData.items[index].uom = selectedItem.stock_uom || 'Cái'
  }
}

const onProductSelect = () => {
  const selectedItem = items.value.find(i => i.item_code === formData.item)
  if (selectedItem) {
    formData.uom = selectedItem.stock_uom || 'Cái'
  }
}

const saveBOM = async () => {
  // Validation
  if (!formData.item) {
    showToast('error', 'Vui lòng chọn sản phẩm')
    return
  }
  if (!formData.quantity || formData.quantity <= 0) {
    showToast('error', 'Số lượng phải lớn hơn 0')
    return
  }
  if (formData.items.length === 0) {
    showToast('error', 'Vui lòng thêm ít nhất một nguyên vật liệu')
    return
  }
  
  const invalidItems = formData.items.filter(i => !i.item_code || !i.qty || i.qty <= 0)
  if (invalidItems.length > 0) {
    showToast('error', 'Vui lòng điền đầy đủ thông tin nguyên vật liệu')
    return
  }
  
  saving.value = true
  try {
    const data = {
      item: formData.item,
      quantity: formData.quantity,
      uom: formData.uom,
      is_active: formData.is_active ? 1 : 0,
      is_default: formData.is_default ? 1 : 0,
      items: formData.items.map(i => ({
        item_code: i.item_code,
        qty: i.qty
      }))
    }
    
    if (editingBOM.value) {
      await bomAPI.update(editingBOM.value.name, data)
      showToast('success', 'Đã cập nhật BOM thành công')
    } else {
      await bomAPI.create(data)
      showToast('success', 'Đã tạo BOM mới thành công')
    }
    
    closeCreateModal()
    loadBOMs()
  } catch (error) {
    console.error('Error saving BOM:', error)
    showToast('error', error.response?.data?.message || 'Không thể lưu BOM')
  } finally {
    saving.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.page = page
    loadBOMs()
  }
}

// Initialize
onMounted(() => {
  loadItems()
  loadBOMs()
})
</script>

<style scoped>
.bg-primary {
  background-color: #055568;
}
.bg-primary-dark {
  background-color: #044454;
}
.text-primary {
  color: #055568;
}
.border-primary {
  border-color: #055568;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #055568;
}
.focus\:border-primary:focus {
  border-color: #055568;
}
.hover\:bg-primary:hover {
  background-color: #055568;
}
.hover\:bg-primary-dark:hover {
  background-color: #044454;
}
</style>
