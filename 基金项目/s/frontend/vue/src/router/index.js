import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Crawler from '../views/Crawler.vue'
import Docs from '../views/Docs.vue'
import About from '../views/About.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'NYLG爬虫工具 - 首页'
    }
  },
  {
    path: '/crawler',
    name: 'Crawler',
    component: Crawler,
    meta: {
      title: 'NYLG爬虫工具 - 爬虫工具'
    }
  },
  {
    path: '/docs',
    name: 'Docs',
    component: Docs,
    meta: {
      title: 'NYLG爬虫工具 - 使用文档'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: {
      title: 'NYLG爬虫工具 - 关于'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router