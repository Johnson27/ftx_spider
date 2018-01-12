const Sequelize = require('sequelize');
const newsSequelize = new Sequelize('sqlite:/Users/yifengliu/rh/github/ftx_spider/ftx_xf.db');
const Config = require('../common/config');

const News = newsSequelize.define('news', {
    id: {
        type: Sequelize.INTEGER,
        allowNull: false, // 是否允许为NULL
        primaryKey: true, // 主键
        autoIncrement: true // 是否自增
    },
    news_time: {
        type: Sequelize.TEXT,
    },
    type: {
        type: Sequelize.TEXT,
    },
    house_name: {
        type: Sequelize.TEXT,
    },
    title: {
        type: Sequelize.TEXT,
    },
    content: {
        type: Sequelize.TEXT,
    },
}, {
    timestamps: false,
    freezeTableName: true,
});

async function getRecentSaleNews() {
    return await getRecentNewsByStatus('sale');
}

//type: 1已开盘 2预测开盘
async function getRecentOpenNews() {
    const newsList = await getRecentNewsByStatus('open');
    if(!newsList) return null;
    for(let news of newsList) {
        news.type = new Date(news.time).getTime() > new Date().getTime() ? 2 : 1;
    }
    return newsList;
}

async function getRecentNewsByStatus(status) {
    const news = await News.findAll({
        where: {
            type: status,
        }
    });
    if(!news || !news.length) return null;
    return filterNewsByDate(news);
}

function filterNewsByDate(newsList) {
    const tempObj = {}
        resultList = [];
    for(let news of newsList) {
        const { dataValues } = news;
        if(!dataValues) continue;
        const startTime = new Date().getTime() - Config.RECENT_DAYS_LENGTH * 24 * 60 * 60 * 1000;
        if(new Date(dataValues.news_time).getTime() >= startTime) {
            if(!tempObj[dataValues.house_name]) {
                tempObj[dataValues.house_name] = dataValues.news_time;
            } else {
                if(new Date(dataValues.news_time).getTime() > new Date(tempObj[dataValues.house_name]).getTime()) {
                    tempObj[dataValues.house_name] = dataValues.news_time;
                }
            }
        }
    }
    for(let key in tempObj) {
        resultList.push({
            name: key,
            time: tempObj[key],
        });
    }
    resultList.sort((a, b) => {
        return new Date(b.time).getTime() - new Date(a.time).getTime();
    });
    return resultList;
}

module.exports = {
    getRecentOpenNews,
    getRecentSaleNews,
};