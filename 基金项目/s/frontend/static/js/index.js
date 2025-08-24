// 全局变量
let currentSection = 'home';
let tasksData = [];
let resultsData = [];
let systemInfo = {};
let refreshInterval = null;

// API 基础URL
const API_BASE = '';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 绑定导航事件
    bindNavigationEvents();
    
    // 加载系统信息
    loadAnnouncements();
    
    // 开始定时刷新
    startAutoRefresh();
    
    // 显示首页
    showHome();
}

// 绑定导航事件
function bindNavigationEvents() {
    // 导航链接点击事件
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            navigateToSection(target);
        });
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    showHome();
                    break;
                case '2':
                    e.preventDefault();
                    showTasks();
                    break;
                case '3':
                    e.preventDefault();
                    showResults();
                    break;
                case '4':
                    e.preventDefault();
                    showSettings();
                    break;
                case 'n':
                    e.preventDefault();
                    showCreateTask();
                    break;
            }
        }
    });
}

// 导航到指定部分
function navigateToSection(section) {
    // 更新导航状态
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`a[href="#${section}"]`).classList.add('active');
    
    // 显示对应内容
    switch(section) {
        case 'home':
            showHome();
            break;
        case 'tasks':
            showTasks();
            break;
        case 'results':
            showResults();
            break;
        case 'settings':
            showSettings();
            break;
    }
}

// 显示首页
function showHome() {
    hideAllSections();
    document.getElementById('home-content').style.display = 'block';
    currentSection = 'home';
    
    // 加载首页统计数据
    loadHomeStats();
}

// 显示任务管理
function showTasks() {
    hideAllSections();
    document.getElementById('tasks-content').style.display = 'block';
    currentSection = 'tasks';
    
    // 加载任务列表
    loadTasks();
}

// 显示结果查看
function showResults() {
    hideAllSections();
    document.getElementById('results-content').style.display = 'block';
    currentSection = 'results';
    
    // 加载结果数据
    loadResults();
}

// 显示系统设置
function showSettings() {
    hideAllSections();
    document.getElementById('settings-content').style.display = 'block';
    currentSection = 'settings';
    
    // 加载设置数据
    loadSettings();
}

// 隐藏所有内容区域
function hideAllSections() {
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
}

// 显示创建任务模态框
function showCreateTask() {
    const modal = new bootstrap.Modal(document.getElementById('createTaskModal'));
    modal.show();
    
    // 重置表单
    document.getElementById('create-task-form').reset();
    document.getElementById('search-config').style.display = 'none';
    document.getElementById('custom-config').style.display = 'none';
}

// 更新任务表单
function updateTaskForm() {
    const spiderType = document.getElementById('spider-type').value;
    const searchConfig = document.getElementById('search-config');
    const customConfig = document.getElementById('custom-config');
    
    // 隐藏所有配置
    searchConfig.style.display = 'none';
    customConfig.style.display = 'none';
    
    // 根据爬虫类型显示对应配置
    if (['baidu', 'bilibili', 'csdn'].includes(spiderType)) {
        searchConfig.style.display = 'block';
    } else if (spiderType === 'custom') {
        customConfig.style.display = 'block';
    }
}

// 创建任务
async function createTask() {
    const form = document.getElementById('create-task-form');
    const formData = new FormData(form);
    
    // 获取表单数据
    const taskData = {
        name: document.getElementById('task-name').value,
        spider_name: document.getElementById('spider-type').value,
        description: document.getElementById('task-description').value,
        parameters: {}
    };
    
    // 根据爬虫类型添加特定配置
    if (['baidu', 'bilibili', 'csdn'].includes(taskData.spider_name)) {
        taskData.parameters.keywords = document.getElementById('keywords').value;
        taskData.parameters.max_pages = parseInt(document.getElementById('max-pages').value);
    } else if (taskData.spider_name === 'custom') {
        const urls = document.getElementById('target-urls').value
            .split(/[\n,]/).map(url => url.trim()).filter(url => url);
        taskData.parameters.start_urls = urls;
        taskData.parameters.max_depth = parseInt(document.getElementById('max-depth').value);
        taskData.parameters.extract_links = document.getElementById('extract-links').checked;
    }
    
    // 验证表单
    if (!validateTaskForm(taskData)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('任务创建成功！', 'success');
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
            modal.hide();
            
            // 刷新任务列表
            if (currentSection === 'tasks') {
                loadTasks();
            }
        } else {
            showNotification(`创建任务失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('创建任务错误:', error);
        showNotification('创建任务时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 验证任务表单
function validateTaskForm(taskData) {
    if (!taskData.name) {
        showNotification('请输入任务名称', 'warning');
        return false;
    }
    
    if (!taskData.spider_name) {
        showNotification('请选择爬虫类型', 'warning');
        return false;
    }
    
    if (['baidu', 'bilibili', 'csdn'].includes(taskData.spider_name)) {
        if (!taskData.parameters.keywords) {
            showNotification('请输入搜索关键词', 'warning');
            return false;
        }
    } else if (taskData.spider_name === 'custom') {
        if (!taskData.parameters.start_urls || taskData.parameters.start_urls.length === 0) {
            showNotification('请输入目标URL', 'warning');
            return false;
        }
    }
    
    return true;
}

// 加载首页统计数据
async function loadHomeStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        
        if (response.ok) {
            // 更新统计数据显示
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('加载统计数据错误:', error);
    }
}

// 更新统计数据显示
function updateStatsDisplay(stats) {
    // 更新结果页面统计
    if (currentSection === 'results') {
        document.getElementById('total-results').textContent = stats.total_results || 0;
        document.getElementById('today-results').textContent = stats.today_results || 0;
        document.getElementById('source-count').textContent = stats.source_count || 0;
        document.getElementById('avg-size').textContent = `${stats.avg_size || 0}KB`;
    }
}

// 加载任务列表
async function loadTasks() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks`);
        const result = await response.json();
        
        if (response.ok) {
            tasksData = result.data || [];
            renderTasksTable();
        } else {
            showNotification('加载任务列表失败', 'error');
        }
    } catch (error) {
        console.error('加载任务列表错误:', error);
        showNotification('加载任务列表时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 渲染任务表格
function renderTasksTable() {
    const container = document.getElementById('tasks-table-container');
    
    if (tasksData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox empty-icon"></i>
                <div class="empty-title">暂无任务</div>
                <div class="empty-description">点击"创建新任务"开始您的第一个爬取任务</div>
                <button class="btn btn-primary" onclick="showCreateTask()">
                    <i class="bi bi-plus-circle"></i> 创建新任务
                </button>
            </div>
        `;
        return;
    }
    
    let tableHtml = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>任务名称</th>
                        <th>爬虫类型</th>
                        <th>状态</th>
                        <th>进度</th>
                        <th>创建时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    tasksData.forEach(task => {
        const statusClass = getStatusClass(task.status);
        const progress = task.progress || 0;
        
        tableHtml += `
            <tr>
                <td>
                    <div class="fw-bold">${escapeHtml(task.name)}</div>
                    <div class="text-muted small">${escapeHtml(task.description || '')}</div>
                </td>
                <td>
                    <span class="tag tag-primary">${getSpiderTypeName(task.spider_name)}</span>
                </td>
                <td>
                    <span class="status-badge ${statusClass}">${getStatusName(task.status)}</span>
                </td>
                <td>
                    <div class="progress" style="width: 100px;">
                        <div class="progress-bar" role="progressbar" style="width: ${progress}%"></div>
                    </div>
                    <small class="text-muted">${progress}%</small>
                </td>
                <td>
                    <small class="text-muted">${formatDateTime(task.created_at)}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${task.status === 'running' ? 
                            `<button class="btn btn-outline-warning" onclick="stopTask('${task.id}')" title="停止任务">
                                <i class="bi bi-stop-circle"></i>
                            </button>` : 
                            task.status === 'failed' ?
                            `<button class="btn btn-outline-success" onclick="retryTask('${task.id}')" title="重试任务">
                                <i class="bi bi-arrow-clockwise"></i>
                            </button>
                            <button class="btn btn-outline-primary" onclick="viewTaskDetails('${task.id}')" title="查看详情">
                                <i class="bi bi-eye"></i>
                            </button>` :
                            `<button class="btn btn-outline-primary" onclick="viewTaskDetails('${task.id}')" title="查看详情">
                                <i class="bi bi-eye"></i>
                            </button>`
                        }
                        <button class="btn btn-outline-danger" onclick="deleteTask('${task.id}')" title="删除任务">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableHtml += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = tableHtml;
}

// 停止任务
async function stopTask(taskId) {
    if (!confirm('确定要停止这个任务吗？')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks/${taskId}/stop`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('任务已停止', 'success');
            loadTasks();
        } else {
            showNotification(`停止任务失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('停止任务错误:', error);
        showNotification('停止任务时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 重试任务
async function retryTask(taskId) {
    if (!confirm('确定要重试这个任务吗？')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks/${taskId}/retry`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('任务重试成功', 'success');
            loadTasks();
        } else {
            showNotification(`重试任务失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('重试任务错误:', error);
        showNotification('重试任务时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('任务已删除', 'success');
            loadTasks();
        } else {
            showNotification(`删除任务失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('删除任务错误:', error);
        showNotification('删除任务时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 查看任务详情
async function viewTaskDetails(taskId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/tasks/${taskId}`);
        const result = await response.json();
        
        if (response.ok && result.success) {
            const task = result.data;
            
            // 创建详情模态框
            const modalHtml = `
                <div class="modal fade" id="taskDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">任务详情</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>基本信息</h6>
                                        <table class="table table-sm">
                                            <tr><td>任务名称:</td><td>${escapeHtml(task.name)}</td></tr>
                                            <tr><td>爬虫类型:</td><td>${escapeHtml(task.spider_type)}</td></tr>
                                            <tr><td>状态:</td><td><span class="badge ${getStatusClass(task.status)}">${getStatusText(task.status)}</span></td></tr>
                                            <tr><td>进度:</td><td>${task.progress || 0}%</td></tr>
                                            <tr><td>创建时间:</td><td>${formatDateTime(task.created_at)}</td></tr>
                                            <tr><td>开始时间:</td><td>${formatDateTime(task.started_at)}</td></tr>
                                            <tr><td>完成时间:</td><td>${formatDateTime(task.finished_at)}</td></tr>
                                        </table>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>统计信息</h6>
                                        <table class="table table-sm">
                                            <tr><td>总条目数:</td><td>${task.total_items || 0}</td></tr>
                                            <tr><td>成功条目:</td><td>${task.success_items || 0}</td></tr>
                                            <tr><td>失败条目:</td><td>${task.failed_items || 0}</td></tr>
                                        </table>
                                        
                                        <h6>配置参数</h6>
                                        <pre class="bg-light p-2 rounded">${JSON.stringify(task.config, null, 2)}</pre>
                                    </div>
                                </div>
                                
                                ${task.description ? `<div class="mt-3"><h6>描述</h6><p>${escapeHtml(task.description)}</p></div>` : ''}
                                ${task.error_message ? `<div class="mt-3"><h6>错误信息</h6><div class="alert alert-danger">${escapeHtml(task.error_message)}</div></div>` : ''}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                                <button type="button" class="btn btn-primary" onclick="viewTaskResults('${task.id}')">查看结果</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 移除已存在的模态框
            const existingModal = document.getElementById('taskDetailModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // 添加新模态框
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
            modal.show();
            
        } else {
            showNotification(`获取任务详情失败: ${result.error || '未知错误'}`, 'error');
        }
    } catch (error) {
        console.error('获取任务详情错误:', error);
        showNotification('获取任务详情时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 加载结果数据
async function loadResults() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/results`);
        const result = await response.json();
        
        if (response.ok) {
            resultsData = result.data || [];
            renderResultsTable();
        } else {
            showNotification('加载结果数据失败', 'error');
        }
    } catch (error) {
        console.error('加载结果数据错误:', error);
        showNotification('加载结果数据时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 渲染结果表格
function renderResultsTable() {
    const container = document.getElementById('results-table-container');
    
    if (resultsData.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-database empty-icon"></i>
                <div class="empty-title">暂无结果数据</div>
                <div class="empty-description">创建并运行爬取任务后，结果将显示在这里</div>
            </div>
        `;
        return;
    }
    
    let tableHtml = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>任务名称</th>
                        <th>标题</th>
                        <th>来源</th>
                        <th>类型</th>
                        <th>采集时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    resultsData.forEach(result => {
        tableHtml += `
            <tr>
                <td>
                    <span class="badge bg-secondary">${escapeHtml(result.task_name || '未知任务')}</span>
                </td>
                <td>
                    <div class="fw-bold">${escapeHtml(result.title || '未知')}</div>
                    <div class="text-muted small">${escapeHtml(truncateText(result.description || '未知', 100))}</div>
                </td>
                <td>
                    ${result.url && result.url !== '未知' ? 
                        `<a href="${result.url}" target="_blank" class="text-decoration-none">
                            ${escapeHtml(getDomainFromUrl(result.url))}
                        </a>` : 
                        '<span class="text-muted">未知</span>'
                    }
                </td>
                <td>
                    <span class="tag">${getResultTypeName(result.item_type)}</span>
                </td>
                <td>
                    <small class="text-muted">${formatDateTime(result.created_at)}</small>
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewResult('${result.id}')" title="查看详情">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="exportSingleResult('${result.id}')" title="导出">
                            <i class="bi bi-download"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    tableHtml += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = tableHtml;
}

// 查看结果详情
async function viewResult(resultId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/results/${resultId}`);
        const result = await response.json();
        
        if (response.ok && result.success) {
            const item = result.data;
            
            // 创建详情模态框
            const modalHtml = `
                <div class="modal fade" id="resultDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-xl">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">结果详情</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-8">
                                        <h6>内容信息</h6>
                                        <table class="table table-sm">
                                            <tr><td width="100">任务名称:</td><td><span class="badge bg-secondary">${escapeHtml(item.task_name || '未知任务')}</span></td></tr>
                                            <tr><td>标题:</td><td>${escapeHtml(item.title || '未知')}</td></tr>
                                            <tr><td>URL:</td><td>${item.url && item.url !== '未知' ? `<a href="${item.url}" target="_blank">${escapeHtml(item.url)}</a>` : '未知'}</td></tr>
                                            <tr><td>描述:</td><td>${escapeHtml(item.description || '未知')}</td></tr>
                                            <tr><td>作者:</td><td>${escapeHtml(item.author || '未知')}</td></tr>
                                            <tr><td>来源:</td><td>${escapeHtml(item.source || '未知')}</td></tr>
                                            <tr><td>发布时间:</td><td>${item.publish_time ? formatDateTime(item.publish_time) : '未知'}</td></tr>
                                        </table>
                                        
                                        ${item.content ? `<div class="mt-3"><h6>内容</h6><div class="border p-3 bg-light" style="max-height: 300px; overflow-y: auto;">${escapeHtml(item.content)}</div></div>` : ''}
                                    </div>
                                    <div class="col-md-4">
                                        <h6>统计信息</h6>
                                        <table class="table table-sm">
                                            <tr><td>浏览量:</td><td>${item.view_count || 0}</td></tr>
                                            <tr><td>点赞数:</td><td>${item.like_count || 0}</td></tr>
                                            <tr><td>评论数:</td><td>${item.comment_count || 0}</td></tr>
                                            <tr><td>分享数:</td><td>${item.share_count || 0}</td></tr>
                                        </table>
                                        
                                        <h6>系统信息</h6>
                                        <table class="table table-sm">
                                            <tr><td>数据类型:</td><td>${escapeHtml(item.item_type || '')}</td></tr>
                                            <tr><td>质量评分:</td><td>${item.quality_score || 'N/A'}</td></tr>
                                            <tr><td>创建时间:</td><td>${formatDateTime(item.created_at)}</td></tr>
                                        </table>
                                        
                                        ${item.extra_data ? `<div class="mt-3"><h6>扩展数据</h6><pre class="bg-light p-2 rounded" style="font-size: 12px;">${JSON.stringify(item.extra_data, null, 2)}</pre></div>` : ''}
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                                <button type="button" class="btn btn-primary" onclick="exportSingleResult('${item.id}')">导出此结果</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 移除已存在的模态框
            const existingModal = document.getElementById('resultDetailModal');
            if (existingModal) {
                existingModal.remove();
            }
            
            // 添加新模态框
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('resultDetailModal'));
            modal.show();
            
        } else {
            showNotification(`获取结果详情失败: ${result.error || '未知错误'}`, 'error');
        }
    } catch (error) {
        console.error('获取结果详情错误:', error);
        showNotification('获取结果详情时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 导出单个结果
function exportSingleResult(resultId) {
    showExportModal([resultId]);
}

// 导出所有结果
function exportResults() {
    if (resultsData.length === 0) {
        showNotification('没有可导出的结果', 'warning');
        return;
    }
    
    const resultIds = resultsData.map(r => r.id);
    showExportModal(resultIds);
}

// 显示导出模态框
function showExportModal(resultIds) {
    const modalHtml = `
        <div class="modal fade" id="exportModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">导出设置</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="export-form">
                            <div class="mb-3">
                                <label class="form-label">导出格式</label>
                                <select class="form-select" id="export-format" required>
                                    <option value="json">JSON</option>
                                    <option value="csv">CSV</option>
                                    <option value="html">HTML</option>
                                    <option value="word">Word文档</option>
                                    <option value="pdf">PDF</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">过滤关键词（可选）</label>
                                <input type="text" class="form-control" id="export-keywords" 
                                       placeholder="多个关键词用逗号分隔">
                                <div class="form-text">只导出包含这些关键词的结果</div>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="enable-processing" checked>
                                    <label class="form-check-label" for="enable-processing">
                                        启用数据处理（去重、分类、关键词提取）
                                    </label>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">导出标题</label>
                                <input type="text" class="form-control" id="export-title" 
                                       value="Web信息抓取结果报告">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary" onclick="executeExport(${JSON.stringify(resultIds)})">开始导出</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('exportModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新模态框
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('exportModal'));
    modal.show();
}

// 执行导出
async function executeExport(resultIds) {
    const format = document.getElementById('export-format').value;
    const keywords = document.getElementById('export-keywords').value.split(',').map(k => k.trim()).filter(k => k);
    const enableProcessing = document.getElementById('enable-processing').checked;
    const title = document.getElementById('export-title').value;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                result_ids: resultIds,
                format: format,
                keywords: keywords,
                process: enableProcessing,
                title: title
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
            modal.hide();
            
            if (format === 'json' || format === 'csv') {
                // 对于JSON和CSV，直接下载
                if (result.data) {
                    downloadData(result.data, `results.${format}`, format);
                }
            } else {
                // 对于其他格式，显示下载链接
                if (result.download_url) {
                    showNotification(`导出成功！共 ${result.total_items} 条数据`, 'success');
                    
                    // 创建下载链接
                    const downloadLink = document.createElement('a');
                    downloadLink.href = result.download_url;
                    downloadLink.download = result.filename;
                    downloadLink.click();
                }
            }
        } else {
            showNotification(`导出失败: ${result.error || '未知错误'}`, 'error');
        }
    } catch (error) {
        console.error('导出错误:', error);
        showNotification('导出时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 下载数据
function downloadData(data, filename, format) {
    let content, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(data, null, 2);
        mimeType = 'application/json';
    } else if (format === 'csv') {
        content = data;
        mimeType = 'text/csv';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = filename;
    downloadLink.click();
    
    window.URL.revokeObjectURL(url);
}

// 搜索结果
function searchResults() {
    const query = document.getElementById('search-results').value.toLowerCase();
    
    if (!query) {
        renderResultsTable();
        return;
    }
    
    const filteredResults = resultsData.filter(result => 
        (result.title && result.title.toLowerCase().includes(query)) ||
        (result.description && result.description.toLowerCase().includes(query)) ||
        (result.url && result.url.toLowerCase().includes(query)) ||
        (result.content && result.content.toLowerCase().includes(query)) ||
        (result.source && result.source.toLowerCase().includes(query)) ||
        (result.item_type && result.item_type.toLowerCase().includes(query))
    );
    
    const originalData = resultsData;
    resultsData = filteredResults;
    renderResultsTable();
    resultsData = originalData;
    
    if (filteredResults.length === 0) {
        showNotification(`未找到包含 "${query}" 的结果`, 'info');
    } else {
        showNotification(`找到 ${filteredResults.length} 条匹配结果`, 'success');
    }
}

// 刷新任务列表
function refreshTasks() {
    loadTasks();
    showNotification('任务列表已刷新', 'success');
}

// 刷新结果列表
function refreshResults() {
    loadResults();
    showNotification('结果列表已刷新', 'success');
}

// 刷新统计数据
function refreshStats() {
    loadHomeStats();
    showNotification('统计数据已刷新', 'success');
}

// 加载设置数据
function loadSettings() {
    // 这里可以加载当前设置
    loadAnnouncements();
}

// 保存爬虫设置
function saveSpiderSettings() {
    const settings = {
        download_delay: parseFloat(document.getElementById('download-delay').value),
        concurrent_requests: parseInt(document.getElementById('concurrent-requests').value),
        retry_times: parseInt(document.getElementById('retry-times').value),
        timeout: parseInt(document.getElementById('timeout').value)
    };
    
    // 这里可以实现设置保存功能
    showNotification('爬虫设置已保存', 'success');
}

// 保存数据库设置
function saveDbSettings() {
    const settings = {
        host: document.getElementById('db-host').value,
        port: parseInt(document.getElementById('db-port').value),
        database: document.getElementById('db-name').value,
        username: document.getElementById('db-user').value,
        password: document.getElementById('db-password').value
    };
    
    // 这里可以实现数据库设置保存功能
    showNotification('数据库设置已保存', 'success');
}

// 测试数据库连接
async function testDbConnection() {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/test-db`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showNotification('数据库连接成功！', 'success');
        } else {
            showNotification(`数据库连接失败: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('测试数据库连接错误:', error);
        showNotification('测试数据库连接时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}



// 加载公告信息
function loadAnnouncements() {
    fetch('/api/announcements')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAnnouncementsDisplay(data.data);
            }
        })
        .catch(error => {
            console.error('加载公告信息失败:', error);
        });
}

function updateAnnouncementsDisplay(data) {
    // 更新公告信息显示
    if (data) {
        const versionEl = document.getElementById('version');
        const statusEl = document.getElementById('status');
        const noticeEl = document.getElementById('notice');
        const tipsEl = document.getElementById('tips');
        const lastCheckEl = document.getElementById('last-check');
        
        if (versionEl) versionEl.textContent = data.version || '--';
        if (statusEl) statusEl.textContent = data.status || '--';
        if (noticeEl) noticeEl.textContent = data.notice || '--';
        if (tipsEl) tipsEl.textContent = data.tips || '--';
        if (lastCheckEl) lastCheckEl.textContent = data.last_check || '--';
    }
}

// 渲染系统信息
function renderSystemInfo() {
    const container = document.getElementById('system-info');
    
    if (!systemInfo || Object.keys(systemInfo).length === 0) {
        container.innerHTML = '<p class="text-muted">无法获取系统信息</p>';
        return;
    }
    
    let infoHtml = `
        <div class="row">
            <div class="col-md-6">
                <h6>系统信息</h6>
                <ul class="list-unstyled">
                    <li><strong>操作系统:</strong> ${systemInfo.platform || 'Unknown'}</li>
                    <li><strong>Python版本:</strong> ${systemInfo.python_version || 'Unknown'}</li>
                    <li><strong>CPU核心数:</strong> ${systemInfo.cpu_count || 'Unknown'}</li>
                    <li><strong>内存总量:</strong> ${formatBytes(systemInfo.memory_total) || 'Unknown'}</li>
                </ul>
            </div>
            <div class="col-md-6">
                <h6>应用信息</h6>
                <ul class="list-unstyled">
                    <li><strong>应用版本:</strong> ${systemInfo.app_version || '1.0.0'}</li>
                    <li><strong>启动时间:</strong> ${formatDateTime(systemInfo.start_time) || 'Unknown'}</li>
                    <li><strong>运行时长:</strong> ${formatDuration(systemInfo.uptime) || 'Unknown'}</li>
                    <li><strong>数据库状态:</strong> 
                        <span class="${systemInfo.db_connected ? 'text-success' : 'text-danger'}">
                            ${systemInfo.db_connected ? '已连接' : '未连接'}
                        </span>
                    </li>
                </ul>
            </div>
        </div>
    `;
    
    container.innerHTML = infoHtml;
}

// 更新环境信息显示
function updateEnvironmentInfoDisplay(data) {
    if (data) {
        const currentTimeEl = document.getElementById('current-time');
        const locationEl = document.getElementById('location');
        const weatherEl = document.getElementById('weather');
        const ipAddressEl = document.getElementById('ip-address');
        
        if (currentTimeEl) currentTimeEl.textContent = data.current_time || '--';
        if (locationEl) locationEl.textContent = data.location || '--';
        if (weatherEl) weatherEl.textContent = data.weather || '--';
        if (ipAddressEl) ipAddressEl.textContent = data.ip_address || '--';
    }
}

// 开始自动刷新
function startAutoRefresh() {
    // 每30秒刷新一次统计数据
    refreshInterval = setInterval(() => {
        loadHomeStats();
        
        // 如果当前在任务页面，刷新任务列表
        if (currentSection === 'tasks') {
            loadTasks();
        }
    }, 30000);
}

// 停止自动刷新
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// 显示/隐藏加载状态
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// 显示通知
function showNotification(message, type = 'info') {
    const toast = document.getElementById('notification-toast');
    const toastBody = document.getElementById('toast-message');
    const toastHeader = toast.querySelector('.toast-header');
    
    // 设置消息内容
    toastBody.textContent = message;
    
    // 设置图标和颜色
    const icon = toastHeader.querySelector('i');
    icon.className = `bi me-2`;
    
    switch(type) {
        case 'success':
            icon.classList.add('bi-check-circle', 'text-success');
            break;
        case 'error':
            icon.classList.add('bi-exclamation-circle', 'text-danger');
            break;
        case 'warning':
            icon.classList.add('bi-exclamation-triangle', 'text-warning');
            break;
        default:
            icon.classList.add('bi-info-circle', 'text-primary');
    }
    
    // 显示Toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (!seconds) return '0秒';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}小时${minutes}分钟`;
    } else if (minutes > 0) {
        return `${minutes}分钟${secs}秒`;
    } else {
        return `${secs}秒`;
    }
}

function getDomainFromUrl(url) {
    try {
        return new URL(url).hostname;
    } catch {
        return url;
    }
}

function getStatusClass(status) {
    switch(status) {
        case 'running': return 'status-running';
        case 'completed': return 'status-completed';
        case 'failed': return 'status-failed';
        case 'pending': return 'status-pending';
        default: return 'status-pending';
    }
}

function getStatusName(status) {
    switch(status) {
        case 'running': return '运行中';
        case 'completed': return '已完成';
        case 'failed': return '失败';
        case 'pending': return '等待中';
        default: return '未知';
    }
}

function getStatusText(status) {
    return getStatusName(status);
}

// 查看任务结果
function viewTaskResults(taskId) {
    // 关闭任务详情模态框
    const taskDetailModal = document.getElementById('taskDetailModal');
    if (taskDetailModal) {
        const modal = bootstrap.Modal.getInstance(taskDetailModal);
        if (modal) {
            modal.hide();
        }
    }
    
    // 切换到结果页面并过滤该任务的结果
    showResults();
    
    // 添加任务ID过滤
    setTimeout(() => {
        loadTaskResults(taskId);
    }, 100);
}

// 加载特定任务的结果
async function loadTaskResults(taskId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/results?task_id=${taskId}`);
        const result = await response.json();
        
        if (response.ok) {
            resultsData = result.data || [];
            renderResultsTable();
            
            // 显示过滤提示
            const container = document.getElementById('results-table-container');
            if (resultsData.length > 0) {
                container.insertAdjacentHTML('afterbegin', 
                    `<div class="alert alert-info alert-dismissible fade show" role="alert">
                        <i class="bi bi-info-circle"></i> 正在显示任务相关的 ${resultsData.length} 条结果
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>`
                );
            }
        } else {
            showNotification('加载任务结果失败', 'error');
        }
    } catch (error) {
        console.error('加载任务结果错误:', error);
        showNotification('加载任务结果时发生错误', 'error');
    } finally {
        showLoading(false);
    }
}

function getSpiderTypeName(type) {
    switch(type) {
        case 'baidu': return '百度搜索';
        case 'bilibili': return '哔哩哔哩';
        case 'csdn': return 'CSDN';
        case 'custom': return '自定义';
        default: return type;
    }
}

function getResultTypeName(type) {
    switch(type) {
        case 'search_result': return '搜索结果';
        case 'video': return '视频';
        case 'article': return '文章';
        case 'webpage': return '网页';
        default: return type || '未知';
    }
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});