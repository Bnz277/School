// 全局变量
let selectedSpiderType = null;
let currentTaskId = null;
let currentResults = null;


// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeStats();
    showWelcomeTip();
    startFloatingTips();
});

// 统计功能
function initializeStats() {
    const today = new Date().toDateString();
    const todayCount = localStorage.getItem('todayCount_' + today) || 0;
    const totalCount = localStorage.getItem('totalCount') || 0;
    
    document.getElementById('todayCount').textContent = todayCount;
    document.getElementById('totalCount').textContent = totalCount;
}

function updateStats() {
    const today = new Date().toDateString();
    let todayCount = parseInt(localStorage.getItem('todayCount_' + today) || 0) + 1;
    let totalCount = parseInt(localStorage.getItem('totalCount') || 0) + 1;
    
    localStorage.setItem('todayCount_' + today, todayCount);
    localStorage.setItem('totalCount', totalCount);
    
    document.getElementById('todayCount').textContent = todayCount;
    document.getElementById('totalCount').textContent = totalCount;
}

function resetStats() {
    if (confirm('确定要重置统计数据吗？')) {
        localStorage.clear();
        document.getElementById('todayCount').textContent = '0';
        document.getElementById('totalCount').textContent = '0';
        showAlert('统计数据已重置', 'success');
    }
}

// 关于对话框
function showAbout() {
    const aboutHtml = `
        <div class="modal fade" id="aboutModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header" style="background: var(--primary-gradient); color: white;">
                        <h5 class="modal-title"><i class="bi bi-info-circle"></i> 关于智能网络爬虫工具</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center mb-4">
                            <div class="feature-icon mx-auto" style="background: var(--primary-gradient); width: 80px; height: 80px; font-size: 30px;">
                                <i class="bi bi-robot"></i>
                            </div>
                            <h4 class="mt-3">NYLG 智能爬虫工具 v2.0</h4>
                            <p class="text-muted">专业的网络数据采集解决方案</p>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="bi bi-gear"></i> 核心功能</h6>
                                <ul class="list-unstyled">
                                    <li><i class="bi bi-check-circle text-success"></i> 多平台数据采集</li>
                                    <li><i class="bi bi-check-circle text-success"></i> 智能内容解析</li>
                                    <li><i class="bi bi-check-circle text-success"></i> 多格式数据导出</li>
                                    <li><i class="bi bi-check-circle text-success"></i> 反爬虫策略</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="bi bi-people"></i> 开发团队</h6>
                                <p><strong>NYLG Team</strong></p>
                                <p class="text-muted">致力于为用户提供最优质的数据采集体验</p>
                                
                                <h6><i class="bi bi-envelope"></i> 联系我们</h6>
                                <p class="text-muted">如有问题或建议，欢迎反馈</p>
                            </div>
                        </div>
                        
                        <div class="alert alert-info mt-3">
                            <i class="bi bi-lightbulb"></i> 
                            <strong>使用提示：</strong>请遵守网站的robots.txt协议，合理使用爬虫功能，仅用于学习和研究目的。
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        <button type="button" class="btn btn-gradient" onclick="window.open('https://github.com', '_blank')">访问GitHub</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('aboutModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新的模态框
    document.body.insertAdjacentHTML('beforeend', aboutHtml);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('aboutModal'));
    modal.show();
}

// 浮动提示功能
function showWelcomeTip() {
    setTimeout(() => {
        addFloatingTip('🎉 欢迎使用智能爬虫工具！', 'success');
    }, 1000);
    
    setTimeout(() => {
        addFloatingTip('💡 选择爬虫类型开始您的数据采集之旅', 'info');
    }, 3000);
}

function startFloatingTips() {
    const tips = [
        { text: '🚀 支持批量数据导出', type: 'info' },
        { text: '🛡️ 内置反爬虫保护', type: 'warning' },
        { text: '⚡ 高速稳定的数据采集', type: 'success' },
        { text: '🎯 精准的内容提取算法', type: 'primary' }
    ];
    
    let tipIndex = 0;
    setInterval(() => {
        if (Math.random() > 0.7) { // 30%概率显示提示
            addFloatingTip(tips[tipIndex].text, tips[tipIndex].type);
            tipIndex = (tipIndex + 1) % tips.length;
        }
    }, 15000); // 每15秒检查一次
}

function addFloatingTip(text, type = 'info') {
    const tipId = 'tip-' + Date.now();
    const tipHtml = `
        <div id="${tipId}" class="tip-bubble alert alert-${type} alert-dismissible fade show" role="alert">
            ${text}
            <button type="button" class="btn-close btn-close-sm" onclick="removeFloatingTip('${tipId}')"></button>
        </div>
    `;
    
    const container = document.getElementById('floatingTips');
    container.insertAdjacentHTML('beforeend', tipHtml);
    
    // 5秒后自动移除
    setTimeout(() => {
        removeFloatingTip(tipId);
    }, 5000);
}

function removeFloatingTip(tipId) {
    const tip = document.getElementById(tipId);
    if (tip) {
        tip.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            tip.remove();
        }, 300);
    }
}

// 添加slideOut动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// 初始化应用
function initializeApp() {
    bindEventListeners();
}

// 绑定事件监听器
function bindEventListeners() {
    // 爬虫类型选择卡片
    const spiderCards = document.querySelectorAll('[data-type]');
    spiderCards.forEach(card => {
        card.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            selectSpiderType(type);
        });
    });
}

// 选择爬虫类型
function selectSpiderType(type) {
    selectedSpiderType = type;
    
    // 更新爬虫类型卡片选中状态
    const spiderCards = document.querySelectorAll('[data-type]');
    spiderCards.forEach(card => {
        card.classList.remove('selected');
    });
    
    const selectedCard = document.querySelector(`[data-type="${type}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // 显示参数输入区域
    showParameterSection(type);
    
    // 如果是URL爬取，显示智能识别提示
    const dataTypeSection = document.getElementById('data-type-section');
    if (type === 'url') {
        if (dataTypeSection) {
            dataTypeSection.style.display = 'block';
        }
    } else {
        if (dataTypeSection) {
            dataTypeSection.style.display = 'none';
        }
    }
    
    // 启用执行按钮
    const executeBtn = document.getElementById('execute-btn');
    if (executeBtn) {
        executeBtn.disabled = false;
    }
}

// 显示参数输入区域
function showParameterSection(type) {
    const parameterSection = document.getElementById('parameterSection');
    const parameterForm = document.getElementById('parameterForm');
    
    let formHtml = '';
    
    switch(type) {
        case 'baidu':
            formHtml = `
                <div class="mb-3">
                    <label for="keyword" class="form-label">搜索关键词</label>
                    <input type="text" class="form-control" id="keyword" placeholder="请输入搜索关键词" required>
                </div>
                <div class="mb-3">
                    <label for="maxResults" class="form-label">最大结果数</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="maxResults" value="20" min="1" max="500" placeholder="输入数量">
                        <span class="input-group-text">条</span>
                    </div>
                    <div class="form-text">建议范围：1-500条，数量过大可能影响性能</div>
                </div>
            `;
            break;
        case 'bilibili':
            formHtml = `
                <div class="mb-3">
                    <label for="keyword" class="form-label">搜索关键词</label>
                    <input type="text" class="form-control" id="keyword" placeholder="请输入搜索关键词" required>
                </div>
                <div class="mb-3">
                    <label for="maxResults" class="form-label">最大结果数</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="maxResults" value="20" min="1" max="500" placeholder="输入数量">
                        <span class="input-group-text">条</span>
                    </div>
                    <div class="form-text">建议范围：1-500条，数量过大可能影响性能</div>
                </div>
            `;
            break;
        case 'csdn':
            formHtml = `
                <div class="mb-3">
                    <label for="keyword" class="form-label">搜索关键词</label>
                    <input type="text" class="form-control" id="keyword" placeholder="请输入搜索关键词" required>
                </div>
                <div class="mb-3">
                    <label for="maxResults" class="form-label">最大结果数</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="maxResults" value="20" min="1" max="500" placeholder="输入数量">
                        <span class="input-group-text">条</span>
                    </div>
                    <div class="form-text">建议范围：1-500条，数量过大可能影响性能</div>
                </div>
            `;
            break;
        case 'url':
            formHtml = `
                <div class="mb-3">
                    <label for="url" class="form-label">目标URL</label>
                    <input type="url" class="form-control" id="url" placeholder="请输入要爬取的网页URL" required>
                </div>
            `;
            break;
    }
    
    parameterForm.innerHTML = formHtml;
    parameterSection.style.display = 'block';
}

// 执行爬取
async function executeCrawl() {
    console.log('开始执行爬取任务...');
    console.log('选中的爬虫类型:', selectedSpiderType);
    
    if (!selectedSpiderType) {
        showAlert('请先选择爬虫类型', 'warning');
        return;
    }
    
    const params = getFormParameters();
    console.log('获取的参数:', params);
    if (!params) {
        return;
    }
    
    // 显示加载状态
    showLoading('正在执行爬取任务...');
    
    try {
        const requestData = {
            spider_type: selectedSpiderType,
            ...params
        };
        console.log('发送的请求数据:', requestData);
        
        const response = await fetch('/api/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('响应状态:', response.status);
        const result = await response.json();
        console.log('API响应结果:', result);
        
        hideLoading();
        
        if (result.success) {
            currentTaskId = result.task_id;
            updateStats();
            showAlert('爬取任务完成！', 'success');
            console.log('准备显示结果:', result.results);
            // 直接显示结果
            displayResults(result.results || []);
        } else {
            console.error('爬取失败:', result.message);
            showAlert(result.message || '爬取任务失败', 'danger');
        }
    } catch (error) {
        console.error('执行爬取失败:', error);
        hideLoading();
        showAlert('网络错误，请检查连接', 'danger');
    }
}

// 获取表单参数
function getFormParameters() {
    const params = {};
    
    if (selectedSpiderType === 'url') {
        const url = document.getElementById('url')?.value;
        
        if (!url) {
            showAlert('请输入目标URL', 'warning');
            return null;
        }
        
        params.url = url;
    } else {
        const keyword = document.getElementById('keyword')?.value;
        const maxResults = document.getElementById('maxResults')?.value;
        
        if (!keyword) {
            showAlert('请输入搜索关键词', 'warning');
            return null;
        }
        
        params.keyword = keyword;
        params.max_results = parseInt(maxResults) || 20;
    }
    
    return params;
}



// 全局变量存储当前结果
let currentSpiderType = null;

// 显示结果
function displayResults(results) {
    const resultCard = document.getElementById('crawl-result');
    const resultContent = document.getElementById('result-content');
    
    // 保存当前结果用于导出
    currentResults = results;
    currentSpiderType = selectedSpiderType;
    
    if (!results || results.length === 0) {
        resultContent.innerHTML = '<p class="text-muted">没有找到相关结果</p>';
    } else {
        let html = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span>共找到 <strong>${results.length}</strong> 条结果</span>
                <div class="btn-group" role="group">
                    <button type="button" class="export-btn json" onclick="exportResults('json')">
                        <i class="bi bi-filetype-json"></i> JSON
                    </button>
                    <button type="button" class="export-btn csv" onclick="exportResults('csv')">
                        <i class="bi bi-filetype-csv"></i> CSV
                    </button>
                    <button type="button" class="export-btn txt" onclick="exportResults('txt')">
                        <i class="bi bi-filetype-txt"></i> TXT
                    </button>
                    <button type="button" class="export-btn markdown" onclick="exportResults('markdown')">
                        <i class="bi bi-markdown"></i> Markdown
                    </button>
                </div>
            </div>
        `;
        
        if (typeof results === 'string') {
            // URL爬取结果（纯文本）
            html += `
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">1. 网页内容</h6>
                    </div>
                    <div class="card-body">
                        <pre class="text-wrap" style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">${results}</pre>
                    </div>
                </div>
            `;
        } else {
            // 搜索结果（数组）
            html += '<div class="list-group">';
            
            results.forEach((item, index) => {
                const itemType = item.type || 'web';
                
                html += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">
                                <span class="badge bg-primary me-2">${index + 1}</span>
                                ${itemType === 'image' ? '<i class="bi bi-image text-success me-1"></i>' : ''}
                                ${itemType === 'video' ? '<i class="bi bi-play-circle text-warning me-1"></i>' : ''}
                                ${itemType === 'web' ? '<i class="bi bi-globe text-info me-1"></i>' : ''}
                                ${item.title || '无标题'}
                            </h6>
                            <small class="text-muted">${item.author || ''}</small>
                        </div>
                        
                        ${itemType === 'image' && item.thumbnail ? `
                            <div class="mb-2">
                                <img src="${item.thumbnail}" alt="${item.title}" class="img-thumbnail" style="max-width: 200px; max-height: 150px; object-fit: cover;" 
                                     onerror="this.style.display='none'" onclick="window.open('${item.url || item.thumbnail}', '_blank')">
                            </div>
                        ` : ''}
                        
                        ${itemType === 'video' && item.thumbnail ? `
                            <div class="mb-2 position-relative" style="display: inline-block;">
                                <img src="${item.thumbnail}" alt="${item.title}" class="img-thumbnail" style="max-width: 200px; max-height: 150px; object-fit: cover;" 
                                     onerror="this.style.display='none'" onclick="window.open('${item.url}', '_blank')">
                                <div class="position-absolute top-50 start-50 translate-middle" style="pointer-events: none;">
                                    <i class="bi bi-play-circle-fill text-white" style="font-size: 2rem; text-shadow: 0 0 10px rgba(0,0,0,0.8);"></i>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${item.url ? `<p class="mb-1"><a href="${item.url}" target="_blank" class="text-decoration-none"><i class="bi bi-link-45deg"></i> ${item.url}</a></p>` : ''}
                        ${item.content ? `<p class="mb-1 text-muted">${item.content.substring(0, 200)}${item.content.length > 200 ? '...' : ''}</p>` : ''}
                        
                        <div class="d-flex flex-wrap gap-2 mt-2">
                            ${item.views || item.play ? `<small class="text-info"><i class="bi bi-eye"></i> ${item.views || item.play}</small>` : ''}
                            ${item.date || item.publish_time ? `<small class="text-secondary"><i class="bi bi-calendar"></i> ${item.date || item.publish_time}</small>` : ''}
                            ${item.duration ? `<small class="text-warning"><i class="bi bi-clock"></i> ${item.duration}</small>` : ''}
                            ${item.up ? `<small class="text-primary"><i class="bi bi-person"></i> ${item.up}</small>` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        resultContent.innerHTML = html;
    }
    
    resultCard.style.display = 'block';
}

// 导出结果
function exportResults(format) {
    if (!currentResults) {
        showAlert('没有可导出的结果', 'warning');
        return;
    }
    
    let content = '';
    let filename = '';
    let mimeType = '';
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    
    switch (format) {
        case 'json':
            content = JSON.stringify(currentResults, null, 2);
            filename = `crawl_results_${currentSpiderType}_${timestamp}.json`;
            mimeType = 'application/json';
            break;
            
        case 'csv':
            if (typeof currentResults === 'string') {
                content = `"序号","内容"\n"1","${currentResults.replace(/"/g, '""')}"`;
            } else {
                const headers = ['序号', '标题', '链接', '作者', '内容', '浏览量', '日期'];
                content = headers.join(',') + '\n';
                currentResults.forEach((item, index) => {
                    const row = [
                        index + 1,
                        `"${(item.title || '').replace(/"/g, '""')}"`,
                        `"${(item.url || '').replace(/"/g, '""')}"`,
                        `"${(item.author || '').replace(/"/g, '""')}"`,
                        `"${(item.content || '').replace(/"/g, '""')}"`,
                        `"${(item.views || '').replace(/"/g, '""')}"`,
                        `"${(item.date || '').replace(/"/g, '""')}"`
                    ];
                    content += row.join(',') + '\n';
                });
            }
            filename = `crawl_results_${currentSpiderType}_${timestamp}.csv`;
            mimeType = 'text/csv';
            break;
            
        case 'txt':
            if (typeof currentResults === 'string') {
                content = `1. 网页内容\n\n${currentResults}`;
            } else {
                content = `爬取结果 - ${currentSpiderType}\n`;
                content += `时间: ${new Date().toLocaleString()}\n`;
                content += `共 ${currentResults.length} 条结果\n\n`;
                content += '=' * 50 + '\n\n';
                
                currentResults.forEach((item, index) => {
                    content += `${index + 1}. ${item.title || '无标题'}\n`;
                    if (item.author) content += `作者: ${item.author}\n`;
                    if (item.url) content += `链接: ${item.url}\n`;
                    if (item.content) content += `内容: ${item.content}\n`;
                    if (item.views) content += `浏览量: ${item.views}\n`;
                    if (item.date) content += `日期: ${item.date}\n`;
                    content += '\n' + '-' * 30 + '\n\n';
                });
            }
            filename = `crawl_results_${currentSpiderType}_${timestamp}.txt`;
            mimeType = 'text/plain';
            break;
            
        case 'markdown':
            if (typeof currentResults === 'string') {
                content = `# 网页内容\n\n${currentResults}`;
            } else {
                content = `# 爬取结果 - ${currentSpiderType}\n\n`;
                content += `**时间**: ${new Date().toLocaleString()}  \n`;
                content += `**结果数量**: ${currentResults.length} 条\n\n`;
                content += '---\n\n';
                
                currentResults.forEach((item, index) => {
                    content += `## ${index + 1}. ${item.title || '无标题'}\n\n`;
                    if (item.author) content += `**作者**: ${item.author}  \n`;
                    if (item.views) content += `**浏览量**: ${item.views}  \n`;
                    if (item.date) content += `**日期**: ${item.date}  \n`;
                    if (item.url) content += `**链接**: [${item.url}](${item.url})  \n`;
                    if (item.content) content += `\n**内容摘要**: ${item.content}\n`;
                    content += '\n---\n\n';
                });
            }
            filename = `crawl_results_${currentSpiderType}_${timestamp}.md`;
            mimeType = 'text/markdown';
            break;
    }
    
    // 创建下载链接
    const blob = new Blob([content], { type: mimeType + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showAlert(`已导出为 ${format.toUpperCase()} 格式`, 'success');
}

// 显示警告信息
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // 4秒后开始淡出动画
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.classList.add('fade-out');
            // 动画完成后移除元素
            setTimeout(() => {
                if (alert) {
                    alert.remove();
                }
            }, 300); // 等待淡出动画完成
        }
    }, 4000);
}

// 显示加载状态
function showLoading(text = '加载中...') {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingText) {
        loadingText.textContent = text;
    }
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

// 隐藏加载状态
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}