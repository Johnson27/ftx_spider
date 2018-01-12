const Koa = require('koa')
const Router = require('koa-router')
const json = require('koa-json')
const logger = require('koa-logger')
const body_parser = require('koa-bodyparser')
const time_console = require('./middlewares/execute-time')
const router_users = require('./routes/ftx')

const app = new Koa()
const router = new Router()

//增加中间件
app.use(body_parser());
app.use(json());
app.use(logger());
app.use(time_console());

//错误处理
app.on('error', (error, ctx) => {
    console.log('server error: %s --> with url %s', error, ctx.url);
});

//路由定义
router.use('/ftx', router_users.routes(), router_users.allowedMethods())
app.use(router.routes()).use(router.allowedMethods())

//端口定义
const port = 8999;

//启动app
app.listen(port, () => {
    console.log('server is running on port %s', port);
});

module.exports = app;




