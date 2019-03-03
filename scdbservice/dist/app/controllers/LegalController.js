'use strict';
/* Load Task Data Access Object */

const LegalDao = require('../dao/LegalDao');

/* Load Controller Common function */
const ControllerCommon = require('./common/controllerCommon');

class LegalController {

    constructor() {
        this.legalDao = new LegalDao();
        this.common = new ControllerCommon();
    }
    findById(req, res) {
        let id = req.params.id;
        this.legalDao.findById(id).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }

    query(req, res) {
        let state = req.query.state;
        let lot = req.query.lot;
        let plan = req.query.plan;

        this.legalDao.findByLegalLotPlan(lot, plan, state).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }

}
module.exports = LegalController;