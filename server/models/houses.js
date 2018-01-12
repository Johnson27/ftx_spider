const Sequelize = require('sequelize');
const houseSequelize = new Sequelize('sqlite:/Users/yifengliu/rh/github/ftx_spider/ftx_xf.db');
const Config = require('../common/config');

const Houses = houseSequelize.define('xf_info', {
    name: {
        type: Sequelize.TEXT,
        allowNull: false, // 是否允许为NULL
        primaryKey: true, // 主键
    },
    status: {
        type: Sequelize.TEXT,
    },
    price: {
        type: Sequelize.TEXT,
    },
    location: {
        type: Sequelize.TEXT,
    },
    phone: {
        type: Sequelize.TEXT,
    },
    size: {
        type: Sequelize.TEXT,
    },
    area: {
        type: Sequelize.TEXT,
    },
    decoration: {
        type: Sequelize.TEXT,
    },
    park_num: {
        type: Sequelize.TEXT,
    },
    house_num: {
        type: Sequelize.TEXT,
    },
    service_fee: {
        type: Sequelize.TEXT,
    },
    service_company: {
        type: Sequelize.TEXT,
    },
    tree: {
        type: Sequelize.TEXT,
    },
}, {
    timestamps: false,
    freezeTableName: true,
});

async function getTargetHouses() {
    const targetObject = Config.TARGET_HOUSES;
    const targetList = [];
    for(let key in targetObject) {
        let house = await Houses.findOne({
            where: {
                name: targetObject[key],
            }
        });
        if(house) {
            targetList.push(house.dataValues)
        }
    }
    return targetList;
}

async function getHouseByName(name) {
    let house = await Houses.findOne({
        where: {
            name,
        },
    });
    return house ? house.dataValues : null;
}

module.exports = {
    getTargetHouses,
    getHouseByName,
};