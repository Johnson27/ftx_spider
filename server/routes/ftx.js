const Router = require("koa-router");
const router = new Router();
const Api = require('../controler/api');

router.get("/getTargetHouse", Api.getTargetHouse);
router.get("/getRencentPreSaleHouse", Api.getRencentPreSaleHouse);
router.get("/getRencentOpenHouse", Api.getRencentOpenHouse);

module.exports = router;
