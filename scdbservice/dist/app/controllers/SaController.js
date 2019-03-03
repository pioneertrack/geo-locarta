'use strict';
/* Load Task Data Access Object */

const SaDao = require('../dao/SaDao');

/* Load Controller Common function */
const ControllerCommon = require('./common/controllerCommon');

class SaController {

    constructor() {
        this.saDao = new SaDao();
        this.common = new ControllerCommon();
    }
    findById(req, res) {
        let id = req.params.id;
        this.saDao.findById(id).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }
    findAll(req, res) {
        this.saDao.findAll().then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }
    query(req, res) {
        let pageNum = req.query.pageNum;
        let pageCount = req.query.pageCount;
        if (!pageCount) {
            pageCount = 10;
        }
        if (!pageNum) {
            pageNum = 1;
        }
        this.saDao.findByPaging(pageNum, pageCount).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }
    nearst(req, res) {
        let n = req.query.n;
        if (!n) {
            n = 10;
        }
        let x = req.query.x;
        let y = req.query.y;
        if (!x || !y) {
            this.common.findError(res);
        } else {
            this.saDao.findByNearst(x, y, n).then(this.common.findSuccess(res)).catch(this.common.findError(res));
        }
    }
}
module.exports = SaController;