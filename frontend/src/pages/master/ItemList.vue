<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 pb-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Quản lý sản phẩm</h1>
          <p class="text-gray-600 mt-1">Danh sách sản phẩm, nguyên vật liệu trong hệ thống</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="showGroupModal = true"
            class="group-item-btn px-4 py-2 rounded-lg transition-all duration-200 inline-flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span class="font-medium">Nhóm hàng</span>
          </button>
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-[#055568] text-white rounded-lg hover:bg-[#134e4a] transition-all duration-200 inline-flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Thêm sản phẩm
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="mt-4 flex flex-wrap gap-3">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Tìm theo mã, tên sản phẩm..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>
        <select
          v-model="filters.item_group"
          @change="loadItems"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary min-w-[180px]"
        >
          <option value="">Tất cả nhóm</option>
          <option 
            v-for="group in filterableGroups" 
            :key="group.name" 
            :value="group.name"
            :class="getGroupOptionClass(group)"
          >
            {{ getGroupDisplayName(group) }}
          </option>
        </select>
        <select
          v-model="filters.is_stock_item"
          @change="loadItems"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
        >
          <option value="">Tất cả loại</option>
          <option value="1">Hàng tồn kho</option>
          <option value="0">Dịch vụ</option>
        </select>
        <select
          v-model="filters.disabled"
          @change="loadItems"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
        >
          <option value="0">Đang hoạt động</option>
          <option value="1">Đã vô hiệu</option>
          <option value="">Tất cả</option>
        </select>
      </div>
    </div>

    <!-- Results -->
    <div class="flex-1 px-6 pb-6 overflow-auto">
      <div class="bg-white rounded-lg shadow h-full flex flex-col">
        <!-- Loading -->
        <div v-if="loading" class="flex-1 flex justify-center items-center">
          <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Empty state -->
        <div v-else-if="items.length === 0" class="flex-1 flex flex-col justify-center items-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-1">Chưa có sản phẩm</h3>
          <p class="text-gray-500 mb-4">Bắt đầu thêm sản phẩm vào hệ thống</p>
          <button
            @click="openCreateModal"
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark"
          >
            Thêm sản phẩm đầu tiên
          </button>
        </div>

        <!-- Table -->
        <div v-else class="flex-1 overflow-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mã SP</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tên sản phẩm</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nhóm</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">ĐVT</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Giá</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tồn kho</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Loại</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Thao tác</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="item in items" :key="item.item_code" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="font-medium text-primary">{{ item.item_code }}</span>
                  <span v-if="item.has_bom" class="ml-1 text-xs text-green-600" title="Có BOM">📋</span>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900">{{ item.item_name }}</div>
                  <div v-if="item.description" class="text-xs text-gray-500 truncate max-w-xs">{{ item.description }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ item.item_group }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center text-sm">
                  {{ formatUOM(item.stock_uom) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right text-sm">
                  {{ formatNumber(item.standard_rate || item.valuation_rate) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-right">
                  <span :class="item.total_qty > 0 ? 'text-green-600 font-medium' : 'text-gray-400'">
                    {{ formatNumber(item.total_qty) }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                  <div class="flex justify-center gap-1">
                    <span v-if="item.is_stock_item" class="px-1.5 py-0.5 text-xs bg-blue-100 text-blue-700 rounded" title="Hàng tồn kho">📦</span>
                    <span v-if="item.is_purchase_item" class="px-1.5 py-0.5 text-xs bg-orange-100 text-orange-700 rounded" title="Có thể mua">🛒</span>
                    <span v-if="item.is_sales_item" class="px-1.5 py-0.5 text-xs bg-green-100 text-green-700 rounded" title="Có thể bán">💰</span>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-center">
                  <div class="flex justify-center gap-1">
                    <button
                      @click="viewDetail(item)"
                      class="p-1.5 text-gray-400 hover:text-primary hover:bg-gray-100 rounded"
                      title="Xem chi tiết"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      @click="editItem(item)"
                      class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-gray-100 rounded"
                      title="Sửa"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="toggleStatus(item)"
                      :class="[
                        'p-1.5 hover:bg-gray-100 rounded',
                        item.disabled ? 'text-green-500 hover:text-green-600' : 'text-red-400 hover:text-red-600'
                      ]"
                      :title="item.disabled ? 'Kích hoạt' : 'Vô hiệu hóa'"
                    >
                      <svg v-if="item.disabled" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="items.length > 0" class="px-4 py-3 border-t flex items-center justify-between">
          <div class="text-sm text-gray-500">
            Hiển thị {{ (pagination.page - 1) * pagination.pageSize + 1 }} - 
            {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} / {{ pagination.total }} sản phẩm
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(pagination.page - 1)"
              :disabled="pagination.page <= 1"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Trước
            </button>
            <span class="px-3 py-1 text-sm">{{ pagination.page }} / {{ pagination.totalPages }}</span>
            <button
              @click="goToPage(pagination.page + 1)"
              :disabled="pagination.page >= pagination.totalPages"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Sau
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Item Modal -->
    <div v-if="showItemModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="closeItemModal"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          <!-- Modal Header -->
          <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
            <h3 class="text-lg font-semibold text-gray-900">
              {{ editingItem ? 'Sửa sản phẩm' : 'Thêm sản phẩm mới' }}
            </h3>
            <button @click="closeItemModal" class="p-2 hover:bg-gray-200 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- Modal Content -->
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Mã sản phẩm <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="formData.item_code"
                  type="text"
                  :disabled="!!editingItem"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-gray-100"
                  placeholder="VD: NVL-001"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Tên sản phẩm <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="formData.item_name"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="Tên sản phẩm"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Nhóm hàng <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="formData.item_group"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option value="">Chọn nhóm</option>
                  <option 
                    v-for="group in selectableGroupsForItem" 
                    :key="group.name" 
                    :value="group.name"
                  >
                    {{ group.item_group_name || group.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Đơn vị tính <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="formData.stock_uom"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                >
                  <option v-for="uom in uomList" :key="uom.name" :value="uom.name">
                    {{ uom.uom_name || uom.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Giá tiêu chuẩn</label>
                <input
                  v-model.number="formData.standard_rate"
                  type="number"
                  min="0"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="0"
                />
              </div>
              <div class="flex items-end gap-4">
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.is_stock_item" class="rounded border-gray-300 text-primary" />
                  <span class="text-sm">Hàng tồn kho</span>
                </label>
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.is_purchase_item" class="rounded border-gray-300 text-primary" />
                  <span class="text-sm">Có thể mua</span>
                </label>
                <label class="flex items-center gap-2">
                  <input type="checkbox" v-model="formData.is_sales_item" class="rounded border-gray-300 text-primary" />
                  <span class="text-sm">Có thể bán</span>
                </label>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
                <textarea
                  v-model="formData.description"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                  placeholder="Mô tả sản phẩm..."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
            <button @click="closeItemModal" class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100">
              Hủy
            </button>
            <button
              @click="saveItem"
              :disabled="saving"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 inline-flex items-center gap-2"
            >
              <svg v-if="saving" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ editingItem ? 'Cập nhật' : 'Tạo mới' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Item Detail Modal -->
    <div v-if="selectedItem" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="selectedItem = null"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
          <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ selectedItem.item_code }}</h3>
              <p class="text-sm text-gray-500">{{ selectedItem.item_name }}</p>
            </div>
            <button @click="selectedItem = null" class="p-2 hover:bg-gray-200 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
            <!-- Basic Info -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Nhóm hàng</div>
                <div class="font-medium">{{ selectedItem.item_group }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Đơn vị tính</div>
                <div class="font-medium">{{ formatUOM(selectedItem.stock_uom) }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Giá tiêu chuẩn</div>
                <div class="font-medium">{{ formatNumber(selectedItem.standard_rate) }} đ</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-sm text-gray-500">Giá tồn kho</div>
                <div class="font-medium">{{ formatNumber(selectedItem.valuation_rate) }} đ</div>
              </div>
            </div>

            <!-- Stock Info -->
            <div v-if="selectedItem.stock_info && selectedItem.stock_info.length > 0" class="mb-6">
              <h4 class="font-semibold text-gray-900 mb-3">Tồn kho theo kho</h4>
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">Kho</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Số lượng</th>
                    <th class="px-4 py-2 text-right text-xs font-medium text-gray-500">Giá trị</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="stock in selectedItem.stock_info" :key="stock.warehouse">
                    <td class="px-4 py-2 text-sm">{{ stock.warehouse_name || stock.warehouse }}</td>
                    <td class="px-4 py-2 text-sm text-right font-medium">{{ formatNumber(stock.actual_qty) }}</td>
                    <td class="px-4 py-2 text-sm text-right">{{ formatNumber(stock.stock_value) }} đ</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- BOMs -->
            <div v-if="selectedItem.boms && selectedItem.boms.length > 0">
              <h4 class="font-semibold text-gray-900 mb-3">Định mức sản xuất (BOM)</h4>
              <div class="space-y-2">
                <div v-for="bom in selectedItem.boms" :key="bom.name" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <span class="font-medium text-primary">{{ bom.name }}</span>
                    <span v-if="bom.is_default" class="ml-2 px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded">Mặc định</span>
                    <span v-if="!bom.is_active" class="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">Ngưng</span>
                  </div>
                  <div class="text-sm text-gray-500">
                    Chi phí: {{ formatNumber(bom.total_cost) }} đ/{{ bom.quantity }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Item Group Modal -->
    <div v-if="showGroupModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showGroupModal = false"></div>
        <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          <div class="px-6 py-4 border-b flex items-center justify-between bg-gray-50">
            <h3 class="text-lg font-semibold text-gray-900">Quản lý nhóm hàng</h3>
            <button @click="showGroupModal = false" class="p-2 hover:bg-gray-200 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            <!-- Add Group Form -->
            <div class="mb-6 p-4 bg-gray-50 rounded-lg">
              <h4 class="font-medium text-gray-900 mb-3">Thêm nhóm mới</h4>
              <div class="flex gap-3">
                <input
                  v-model="newGroupName"
                  type="text"
                  placeholder="Tên nhóm hàng..."
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                />
                <select
                  v-model="newGroupParent"
                  class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary min-w-[180px]"
                >
                  <option 
                    v-for="group in selectableParentGroups" 
                    :key="group.name" 
                    :value="group.name"
                  >
                    {{ group.item_group_name || group.name }}
                  </option>
                </select>
                <button
                  @click="createGroup"
                  :disabled="!newGroupName || savingGroup"
                  class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50"
                >
                  Thêm
                </button>
              </div>
            </div>

            <!-- Groups List -->
            <div class="space-y-2">
              <div
                v-for="group in itemGroups"
                :key="group.name"
                class="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                :class="getGroupRowClass(group)"
              >
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <!-- Edit mode -->
                  <template v-if="editingGroup === group.name">
                    <input
                      v-model="editGroupName"
                      type="text"
                      class="flex-1 px-2 py-1 border border-primary rounded focus:ring-2 focus:ring-primary text-sm"
                      @keyup.enter="saveGroupEdit(group)"
                      @keyup.escape="cancelGroupEdit"
                    />
                    <button
                      @click="saveGroupEdit(group)"
                      class="p-1 text-green-600 hover:bg-green-50 rounded"
                      title="Lưu"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </button>
                    <button
                      @click="cancelGroupEdit"
                      class="p-1 text-gray-500 hover:bg-gray-100 rounded"
                      title="Hủy"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </template>
                  <!-- View mode -->
                  <template v-else>
                    <span 
                      class="font-medium truncate"
                      :class="getGroupNameClass(group)"
                    >
                      {{ group.item_group_name || group.name }}
                    </span>
                    <span v-if="group.parent_item_group && !isRootGroup(group.parent_item_group)" class="text-sm text-gray-500 flex-shrink-0">
                      ({{ group.parent_item_group }})
                    </span>
                    <span class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded flex-shrink-0">
                      {{ group.item_count }} sản phẩm
                    </span>
                  </template>
                </div>
                <!-- Action buttons (only for non-root groups) -->
                <div v-if="canEditGroup(group) && editingGroup !== group.name" class="flex items-center gap-1 flex-shrink-0">
                  <button
                    @click="startEditGroup(group)"
                    class="p-1.5 text-blue-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                    title="Sửa tên"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="canDeleteGroup(group) && deleteGroup(group.name)"
                    :class="[
                      'p-1.5 rounded',
                      canDeleteGroup(group) 
                        ? 'text-red-400 hover:text-red-600 hover:bg-red-50 cursor-pointer' 
                        : 'text-gray-300 cursor-not-allowed'
                    ]"
                    :title="canDeleteGroup(group) ? 'Xóa' : 'Không thể xóa (có ' + group.item_count + ' sản phẩm)'"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div
      v-if="toast.show"
      :class="[
        'fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 z-[60]',
        toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { itemAPI, itemGroupAPI, uomAPI } from '@/api'

// Root groups that cannot be used directly for items
const ROOT_GROUPS = ['All Item Groups', 'Nguyên Vật Liệu', 'Thành Phẩm']
// Only these can be parent groups for new sub-groups
const ALLOWED_PARENT_GROUPS = ['Nguyên Vật Liệu', 'Thành Phẩm']

// State
const loading = ref(false)
const saving = ref(false)
const savingGroup = ref(false)
const items = ref([])
const itemGroups = ref([])
const uomList = ref([])
const selectedItem = ref(null)
const editingItem = ref(null)
const showItemModal = ref(false)
const showGroupModal = ref(false)

// Edit group state
const editingGroup = ref(null)
const editGroupName = ref('')

// Filters
const filters = reactive({
  search: '',
  item_group: '',
  is_stock_item: '',
  disabled: '0'
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 1
})

// Form
const formData = reactive({
  item_code: '',
  item_name: '',
  item_group: '',
  stock_uom: 'Nos',
  standard_rate: 0,
  is_stock_item: true,
  is_purchase_item: true,
  is_sales_item: false,
  description: ''
})

// New group form
const newGroupName = ref('')
const newGroupParent = ref('Nguyên Vật Liệu')

// Toast
const toast = reactive({ show: false, type: 'success', message: '' })

// UOM mapping
const UOM_MAP = {
  'Nos': 'Cái', 'Kg': 'Kg', 'Meter': 'Mét', 'Unit': 'Cái',
  'Box': 'Hộp', 'Set': 'Bộ', 'Pair': 'Cặp', 'Gram': 'Gram', 'Litre': 'Lít'
}

// Computed: Groups that can be used in filter dropdown (exclude All Item Groups)
const filterableGroups = computed(() => {
  return itemGroups.value.filter(g => g.name !== 'All Item Groups')
})

// Computed: Groups that can be selected for items (exclude root groups)
const selectableGroupsForItem = computed(() => {
  return itemGroups.value.filter(g => !ROOT_GROUPS.includes(g.name))
})

// Computed: Groups that can be parent of new groups (only Nguyên Vật Liệu or Thành Phẩm)
const selectableParentGroups = computed(() => {
  return itemGroups.value.filter(g => ALLOWED_PARENT_GROUPS.includes(g.name))
})

// Helper: Check if group is root level
const isRootGroup = (groupName) => {
  return ROOT_GROUPS.includes(groupName) || groupName === 'All Item Groups'
}

// Helper: Get group level (0 = root, 1 = level 1, 2 = level 2)
const getGroupLevel = (group) => {
  if (group.name === 'All Item Groups') return 0
  if (ALLOWED_PARENT_GROUPS.includes(group.name)) return 1
  if (ALLOWED_PARENT_GROUPS.includes(group.parent_item_group)) return 2
  return 3
}

// Helper: Get display name with indent based on level
const getGroupDisplayName = (group) => {
  const level = getGroupLevel(group)
  const name = group.item_group_name || group.name
  if (level === 1) return name
  if (level === 2) return `  └ ${name}`
  if (level >= 3) return `    └ ${name}`
  return name
}

// Helper: Get class for group option in select
const getGroupOptionClass = (group) => {
  const level = getGroupLevel(group)
  if (level === 1) return 'font-semibold text-gray-900'
  if (level === 2) return 'text-gray-700 pl-2'
  return 'text-gray-600 pl-4'
}

// Helper: Get class for group row in modal
const getGroupRowClass = (group) => {
  const level = getGroupLevel(group)
  if (level === 0) return 'bg-gray-100 border-gray-300'
  if (level === 1) return 'bg-blue-50 border-blue-200'
  if (level === 2) return 'bg-white border-gray-200 ml-4'
  return 'bg-white border-gray-200 ml-8'
}

// Helper: Get class for group name
const getGroupNameClass = (group) => {
  const level = getGroupLevel(group)
  if (level === 0) return 'text-gray-500'
  if (level === 1) return 'text-blue-700 font-semibold'
  return 'text-gray-900'
}

// Helper: Check if group can be deleted
const canDeleteGroup = (group) => {
  // Cannot delete root groups
  if (ROOT_GROUPS.includes(group.name)) return false
  // Cannot delete if has items or subgroups
  if (group.item_count > 0 || group.subgroup_count > 0) return false
  return true
}

// Helper: Check if group can be edited (only sub-groups, not root groups)
const canEditGroup = (group) => {
  // Cannot edit root groups (All Item Groups, Nguyên Vật Liệu, Thành Phẩm)
  return !ROOT_GROUPS.includes(group.name)
}

// Edit group methods
const startEditGroup = (group) => {
  editingGroup.value = group.name
  editGroupName.value = group.item_group_name || group.name
}

const cancelGroupEdit = () => {
  editingGroup.value = null
  editGroupName.value = ''
}

const saveGroupEdit = async (group) => {
  if (!editGroupName.value.trim()) {
    showToast('error', 'Tên nhóm không được để trống')
    return
  }
  
  if (editGroupName.value.trim() === (group.item_group_name || group.name)) {
    cancelGroupEdit()
    return
  }
  
  savingGroup.value = true
  try {
    const result = await itemGroupAPI.update(group.name, {
      item_group_name: editGroupName.value.trim()
    })
    if (result.success) {
      showToast('success', 'Đã cập nhật tên nhóm hàng')
      await loadItemGroups()
      cancelGroupEdit()
    } else {
      showToast('error', result.message || 'Không thể cập nhật nhóm hàng')
    }
  } catch (error) {
    console.error('Error updating group:', error)
    showToast('error', 'Lỗi khi cập nhật nhóm hàng')
  } finally {
    savingGroup.value = false
  }
}

// Debounce
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => loadItems(), 300)
}

// Methods
const formatNumber = (num) => {
  if (!num) return '0'
  return new Intl.NumberFormat('vi-VN').format(num)
}

const formatUOM = (uom) => UOM_MAP[uom] || uom || 'Cái'

const showToast = (type, message) => {
  toast.type = type
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

const loadItems = async () => {
  loading.value = true
  try {
    const res = await itemAPI.getList({
      search: filters.search,
      item_group: filters.item_group,
      is_stock_item: filters.is_stock_item,
      disabled: filters.disabled,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    items.value = res.data || []
    pagination.total = res.total || 0
    pagination.totalPages = res.total_pages || 1
  } catch (error) {
    console.error('Error loading items:', error)
    showToast('error', 'Không thể tải danh sách sản phẩm')
  } finally {
    loading.value = false
  }
}

const loadItemGroups = async () => {
  try {
    itemGroups.value = await itemGroupAPI.getList() || []
  } catch (error) {
    console.error('Error loading item groups:', error)
  }
}

const loadUOMs = async () => {
  try {
    uomList.value = await uomAPI.getList() || []
  } catch (error) {
    console.error('Error loading UOMs:', error)
    // Default UOMs
    uomList.value = [
      { name: 'Nos', uom_name: 'Cái' },
      { name: 'Kg', uom_name: 'Kg' },
      { name: 'Meter', uom_name: 'Mét' },
      { name: 'Box', uom_name: 'Hộp' },
      { name: 'Set', uom_name: 'Bộ' }
    ]
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= pagination.totalPages) {
    pagination.page = page
    loadItems()
  }
}

const openCreateModal = () => {
  editingItem.value = null
  formData.item_code = ''
  formData.item_name = ''
  // Select first valid group (not root groups)
  formData.item_group = selectableGroupsForItem.value[0]?.name || ''
  formData.stock_uom = 'Nos'
  formData.standard_rate = 0
  formData.is_stock_item = true
  formData.is_purchase_item = true
  formData.is_sales_item = false
  formData.description = ''
  showItemModal.value = true
}

const editItem = (item) => {
  editingItem.value = item
  formData.item_code = item.item_code
  formData.item_name = item.item_name
  formData.item_group = item.item_group
  formData.stock_uom = item.stock_uom
  formData.standard_rate = item.standard_rate || 0
  formData.is_stock_item = !!item.is_stock_item
  formData.is_purchase_item = !!item.is_purchase_item
  formData.is_sales_item = !!item.is_sales_item
  formData.description = item.description || ''
  showItemModal.value = true
}

const closeItemModal = () => {
  showItemModal.value = false
  editingItem.value = null
}

const saveItem = async () => {
  if (!formData.item_code || !formData.item_name || !formData.item_group) {
    showToast('error', 'Vui lòng điền đầy đủ thông tin bắt buộc')
    return
  }

  saving.value = true
  try {
    const data = {
      item_name: formData.item_name,
      item_group: formData.item_group,
      stock_uom: formData.stock_uom,
      standard_rate: formData.standard_rate,
      is_stock_item: formData.is_stock_item ? 1 : 0,
      is_purchase_item: formData.is_purchase_item ? 1 : 0,
      is_sales_item: formData.is_sales_item ? 1 : 0,
      description: formData.description
    }

    let result
    if (editingItem.value) {
      result = await itemAPI.update(formData.item_code, data)
    } else {
      result = await itemAPI.create({ item_code: formData.item_code, ...data })
    }

    if (result.success) {
      showToast('success', result.message)
      closeItemModal()
      loadItems()
    } else {
      showToast('error', result.message)
    }
  } catch (error) {
    console.error('Error saving item:', error)
    showToast('error', 'Không thể lưu sản phẩm')
  } finally {
    saving.value = false
  }
}

const viewDetail = async (item) => {
  try {
    const detail = await itemAPI.getDetail(item.item_code)
    if (detail.success) {
      selectedItem.value = detail
    } else {
      showToast('error', detail.message)
    }
  } catch (error) {
    console.error('Error loading item detail:', error)
    showToast('error', 'Không thể tải chi tiết sản phẩm')
  }
}

const toggleStatus = async (item) => {
  try {
    const result = await itemAPI.toggleStatus(item.item_code)
    if (result.success) {
      showToast('success', result.message)
      loadItems()
    } else {
      showToast('error', result.message)
    }
  } catch (error) {
    console.error('Error toggling item status:', error)
    showToast('error', 'Không thể thay đổi trạng thái')
  }
}

const createGroup = async () => {
  if (!newGroupName.value) return
  
  savingGroup.value = true
  try {
    const result = await itemGroupAPI.create({
      item_group_name: newGroupName.value,
      parent_item_group: newGroupParent.value
    })
    if (result.success) {
      showToast('success', result.message)
      newGroupName.value = ''
      loadItemGroups()
    } else {
      showToast('error', result.message)
    }
  } catch (error) {
    console.error('Error creating group:', error)
    showToast('error', 'Không thể tạo nhóm hàng')
  } finally {
    savingGroup.value = false
  }
}

const deleteGroup = async (name) => {
  if (!confirm(`Xóa nhóm hàng "${name}"?`)) return
  
  try {
    const result = await itemGroupAPI.delete(name)
    if (result.success) {
      showToast('success', result.message)
      loadItemGroups()
    } else {
      showToast('error', result.message)
    }
  } catch (error) {
    console.error('Error deleting group:', error)
    showToast('error', 'Không thể xóa nhóm hàng')
  }
}

// Initialize
onMounted(() => {
  loadItems()
  loadItemGroups()
  loadUOMs()
})
</script>

<style scoped>
.bg-primary { background-color: #055568; }
.bg-primary-dark { background-color: #044454; }
.text-primary { color: #055568; }
.border-primary { border-color: #055568; }
.hover\:bg-primary:hover { background-color: #055568; }
.hover\:bg-primary-dark:hover { background-color: #044454; }
.focus\:ring-primary:focus { --tw-ring-color: #055568; }
.focus\:border-primary:focus { border-color: #055568; }
</style>
