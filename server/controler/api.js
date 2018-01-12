const House = require('../models/houses');
const News = require('../models/news');

class FtxAPI {
    async getTargetHouse(ctx) {
        try {
            const houseList = await House.getTargetHouses();
            ctx.body = {
                houseList: houseList,
            }
        } catch (err) {
            if (err.name === 'CastError' || err.name === 'NotFoundError') {
                ctx.throw(404);
            }
            ctx.throw(500);
        }
    }

    async getRencentPreSaleHouse(ctx) {
        try {
            const newsList = await News.getRecentSaleNews();
            const preSaleList = await Promise.all(newsList.map(async news => {
                return await House.getHouseByName(news.name);
            }));
            ctx.body = {
                preSaleList: preSaleList.filter(item => item)
            }
        } catch (err) {
            console.log(err)
            if (err.name === 'CastError' || err.name === 'NotFoundError') {
                ctx.throw(404);
            }
            ctx.throw(500);
        }
    }

    async getRencentOpenHouse(ctx) {
        try {
            const newsList = await News.getRecentOpenNews();
            const hasOpened = [], willOpen = [];
            for(let news of newsList) {
                const house = await House.getHouseByName(news.name);
                news.type === 1 ? hasOpened.push(house) : willOpen.push(house);
            }
            ctx.body = {
                result: 0,
                willOpenList: willOpen,
                hasOpenedList: hasOpened,
            }
        } catch (err) {
            console.log(err)
            if (err.name === 'CastError' || err.name === 'NotFoundError') {
                ctx.throw(404);
            }
            ctx.throw(500);
        }
    }
}

module.exports = new FtxAPI();