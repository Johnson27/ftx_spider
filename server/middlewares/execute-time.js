function logExecuteTime() {
    return async function(ctx, next) {
        const startTime = new Date().getTime();
        await next();
        const endTime = new Date().getTime();
        console.log('%s %s - %s', ctx.method, ctx.url, endTime - startTime);
    }
}

module.exports = logExecuteTime;