import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name:'Root',
    redirect:'/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: ()=>import('../views/LoginView.vue')
  },
  {
    path: '/imageObservation',
    name: 'imageObservation',
    component: ()=>import('../views/ImageObservationView.vue')
  },
  {
    path: '/home',
    name: 'home',
    component: () =>import('../views/HomeView.vue'),
    children: [
      {
        path: '/dataCharts',
        name: 'dataCharts',
        component: ()=>import('../views/StatisticsView.vue')
      },
      {
        path: '/analyses',
        name: 'AIAnalysis',
        component: ()=>import('../views/ImageAnalysisView.vue')
      },
      {
        path: '/case',
        name: 'CaseManagement',
        component: ()=>import('../views/CaseManageView.vue')
      },
      {
        path: '/userInform',
        name: 'userInform',
        component: ()=>import('../views/UserInformView.vue')
      }
    ]
  },
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
